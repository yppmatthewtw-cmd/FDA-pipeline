# -*- coding: utf-8 -*-
"""
Rebuild the "FDA Decisions Pending" tab in its original R4 layout, but with every
row's status, dates and catalysts replaced by the verified findings from the
2026-09-05 review (build_pending_review.py) plus the workflow refresh.

Layout is deliberately identical to R4: same 12 columns at the same hand-tuned
widths, same 36-month grid, same freeze pane -- only the content changes.
"""
import io, re, sys, json, datetime
from collections import defaultdict
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import ColorScaleRule

AS_OF = datetime.date(2026, 9, 5)
TV = "https://www.tradingview.com/chart/Q1c5VWwD/?symbol="

# ---- R4 layout constants (unchanged) ----
WIDTHS = [10, 9, 6.5703125, 7, 12, 13.5703125, 18.5703125, 15.42578125,
          17.28515625, 17.42578125, 26.5703125, 10.5703125]
GRID_W = 4.140625
GRID_START = (2025, 9)
GRID_N = 36
TODAY_IDX = (2026 - GRID_START[0]) * 12 + (9 - GRID_START[1])

MONTHS = {m: i for i, m in enumerate(
    "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(), 1)}


def gidx(y, m):
    return (y - GRID_START[0]) * 12 + (m - GRID_START[1])


def grid_months():
    base = GRID_START[0] * 12 + GRID_START[1] - 1
    return [((base + i) // 12, (base + i) % 12 + 1) for i in range(GRID_N)]


# ---- load the verified review + the original TAM / cap tier / notes ----
def load(path, split_at):
    src = io.open(path, encoding="utf-8").read()
    ns = {}
    exec(compile(src.split(split_at)[0], path, "exec"), ns)
    return ns


REVIEW = load("build_pending_review.py", "# ---------- styling ----------")["REVIEW"]
PIPE = [r for r in load("build_fda_pipeline.py", "thin = Side")["ROWS"]
        if r[10].startswith("NDA/BLA")]
assert len(REVIEW) == len(PIPE) == 82
assert all(REVIEW[i][1] == PIPE[i][1] for i in range(82)), "row order drifted"

# ---- workflow refresh overrides, keyed by row index ----
OVERRIDES = {}
if len(sys.argv) > 2 and sys.argv[2]:
    OVERRIDES = {int(k): v for k, v in json.load(io.open(sys.argv[2], encoding="utf-8")).items()}

# ---- probability of success, re-rated against verified status ----
# Approved is settled; everything else is scored on what the review actually found.
POS_BASE = {"已獲批": 100, "審批中(有PDUFA)": 85, "審批中(無PDUFA)": 80,
            "CRL": 35, "撤回或終止": 5, "未遞交": 60, "不明": 40}
POS_OVERRIDE = {           # ticker+drug-prefix -> (PoS, why)
    ("SMMT", "Ivonescimab"): (45, "HARMONi OS 未達統計顯著，FDA 要求 OS 顯著"),
    ("CAPR", "Deramiocel"): (25, "CTGTAC 2026-07-29 以 3:9 反對療效證據"),
    ("ANNX", "Tanruprubart"): (55, "BLA 未遞交；單一地區 Ph3 + 外部對照"),
    ("NAMS", "Obicetrapib"): (55, "美國 NDA 未遞交，繫於 PREVAIL 期中"),
    ("QURE", "AMT-130"): (55, "BLA 未遞交；外部對照仍可能被審評員質疑"),
    ("RGNX", "RGX-121"): (10, "CRL + 2026-08-24 第二次 clinical hold，短期不重交"),
    ("IRON", "Bitopertin"): (35, "替代終點路徑失敗，改繫於 APOLLO Ph3"),
    ("ATRA", "Tab-cel"): (20, "第二次 CRL 由生產轉為療效標準，需新研究"),
    ("PTCT", "Vatiquinone"): (12, "CRL 要求全新研究，PROVE-FA 24 個月追蹤"),
    ("ZLDPF", "Glepaglutide"): (25, "CRL 要求新樞紐試驗，招募中"),
    ("ACHV", "Cytisinicline"): (70, "CRL 純屬 CMC/標籤，已換 Adare 廠"),
    ("SVRA", "Molgramostim"): (80, "延期無安全/療效/生產疑慮"),
    ("SRRK", "Apitegromab"): (80, "CMC 已換廠但替代廠仍須 FDA 接受"),
    ("TLX", "(1) Pixclara"): (60, "Pixclara 重交在審；Zircaix 尚未重交"),
    ("AXSM", "AXS-14"): (45, "RTF 後退回 Ph3，FORWARD 讀數未出"),
    ("DSNKY", "Patritumab"): (5, "BLA 已自願撤回"),
    ("AMGN", "Rocatinlimab"): (5, "全球試驗因惡性腫瘤訊號暫停"),
    ("PFE", "Sasanlimab"): (15, "美歐申請均已撤回"),
    ("REGN", "Odronextamab"): (45, "第二次 CRL，Catalent 廠問題未解"),
    ("REGN", "Dupixent"): (65, "CPUO 仍在 Ph3，2027 才申報"),
    ("ABBV", "Tavapadon"): (70, "指引窗口已過而無公開結果"),
    ("GSK", "Depemokimab"): (55, "哮喘已獲批；CRSwNP 收 CRL 待重交，海外四地已批為正面訊號"),
    ("CORT", "Relacorilant"): (75, "卵巢癌已獲批；庫欣 CRL 後僅補分析重交，PDUFA 12/17"),
}


def pos_for(idx, status):
    tk = REVIEW[idx][1]
    drug = REVIEW[idx][2]
    for (t, pre), (v, why) in POS_OVERRIDE.items():
        if t == tk and drug.startswith(pre):
            return v, why
    # A row can carry two states ("approved for X; CRL for Y"). Score the live
    # one -- the settled half has no catalyst left to handicap.
    parts = [p.strip() for p in status.split("；")]
    live = next((p for p in parts if not p.startswith("已獲批")), parts[0])
    key = next((k for k in POS_BASE if live.startswith(k)), None)
    if key is None:
        key = next((k for k in POS_BASE if status.startswith(k)), "不明")
    return POS_BASE[key], f"依核實狀態「{key}」之基準率" + (
        "（同行另有已獲批適應症，此分數針對仍待決者）" if len(parts) > 1 else "")


# ---- grid events ----
POS_WORDS = ("獲批", "批准", "達標", "陽性", "提前")
NEG_WORDS = ("CRL", "RTF", "撤回", "暫停", "hold", "未達", "不顯著", "延期", "拒絕", "反對")

RE_YMD = re.compile(r"(20\d{2})-(\d{2})-(\d{2})")
RE_YM = re.compile(r"(20\d{2})-(\d{2})(?!-\d)")
RE_Q = re.compile(r"(20\d{2})\s*Q([1-4])")
RE_Y = re.compile(r"\b(20\d{2})\b")


NON_EVENT = re.compile(r"查無|無公開|未見|未查得|尚未|截至\s*20\d{2}|不予採信|無.{0,6}紀錄")


def label_of(text, field_lead=""):
    """Map a dated clause to a short grid label + polarity.

    field_lead carries the status word the clause belongs to, so a bare-date
    fragment ("；2026-05-15 (早期 x2)") inherits its parent's meaning.
    """
    t = text
    if "clinical hold" in t or "hold" in t: return "暫停", "neg"
    if "CRL" in t: return "CRL", "neg"
    if "RTF" in t or "拒絕受理" in t: return "RTF", "neg"
    if "撤回" in t: return "撤回", "neg"
    if "獲批" in t or "批准" in t: return "獲批", "pos"
    if "上市" in t or "供應" in t: return "上市", "neu"
    if "AdCom" in t or "ODAC" in t or "CTGTAC" in t or "諮詢委員會" in t or "投票" in t:
        return "AdCom", ("neg" if "反對" in t else "pos")
    if "PDUFA" in t: return "PDUFA", "fut"
    if "受理" in t: return "受理", "neu"
    if "遞交" in t or "重交" in t: return "遞交", "neu"
    if "達標" in t or "陽性" in t: return "P3+", "pos"
    if "決定" in t: return "決定", "fut"
    if "讀數" in t or "數據" in t: return "數據", "fut"
    if "終止" in t or "交還" in t or "停止" in t: return "終止", "neg"
    if "延至" in t or "延期" in t or "延後" in t: return "延期", "neg"
    if "BTD" in t or "突破" in t or "優先審查" in t: return "資格", "pos"
    if "收購" in t or "併購" in t: return "收購", "neu"
    if "Type A" in t or "Type B" in t or "Type C" in t or "會議" in t: return "會議", "neu"
    if "廠" in t: return "換廠", "neu"
    if "權利金" in t or "里程碑" in t: return "里程碑", "neu"
    if "期中" in t: return "數據", "fut"
    if "研究" in t or "試驗" in t or "Ph3" in t or "擴充" in t or "啟動" in t:
        return "研究", "neu"
    if "滲透" in t or "放量" in t or "商業化" in t or "夥伴" in t: return "上市", "neu"
    if field_lead.startswith("已獲批"): return "獲批", "pos"
    if field_lead.startswith("CRL"): return "CRL", "neg"
    return "事件", "neu"


COMMERCIAL = ("上市", "持續", "商業化", "權利金", "放量", "採用", "供應", "交割")


def past_events(idx):
    """Dated facts from the verified FDA-history and status fields."""
    r = REVIEW[idx]
    out = {}
    for field in (r[5], r[7]):          # fda_history, status_now
        # split on arrows and full stops too: one history field chains several
        # distinct actions ("CRL ... -> resubmit ... -> AdCom ... -> approval")
        for seg in re.split(r"[；;。]|→|->", field):
            # "no approval or CRL on record" and "as of 2026-07 still under
            # review" are statements about absence, not dated events
            if NON_EVENT.search(seg):
                continue
            for m in RE_YMD.finditer(seg):
                y, mo = int(m.group(1)), int(m.group(2))
                i = gidx(y, mo)
                if 0 <= i < GRID_N:
                    lab, cat = label_of(seg, field)
                    if cat == "fut" and i > TODAY_IDX:
                        continue
                    cat = cat if cat != "fut" else "neu"
                    prev = out.get(i)
                    if prev:
                        if prev[1] in ("pos", "neg") and cat == "neu":
                            continue
                        # an approval and a rejection landing in the same month
                        # is a real event, not a collision to silently resolve
                        if {prev[1], cat} == {"pos", "neg"}:
                            out[i] = (f"{prev[0]}/{lab}", "mix")
                            continue
                    out[i] = (lab, cat)
            if not RE_YMD.search(seg):
                for m in RE_YM.finditer(seg):
                    y, mo = int(m.group(1)), int(m.group(2))
                    i = gidx(y, mo)
                    if not (0 <= i <= TODAY_IDX):
                        continue
                    lab, cat = label_of(seg, field)
                    if cat == "fut":
                        continue
                    prev = out.get(i)
                    if prev:
                        if {prev[1], cat} == {"pos", "neg"}:
                            out[i] = (f"{prev[0]}/{lab}", "mix")
                        continue
                    out[i] = (lab, cat)
    # An approval settles the row: procedural marks dated after it are moot
    # (e.g. a PDUFA date the drug was approved ahead of).
    appr = [i for i, (lab, _) in out.items() if lab == "獲批"]
    if appr:
        last = max(appr)
        out = {i: v for i, v in out.items()
               if i <= last or v[0] not in ("PDUFA", "受理", "遞交")}
    return out


def future_span(text):
    """-> (start_idx, end_idx, precision) for a forward-looking date string.

    Parenthetical asides carry stale years ("(公司 2025-12 管線指引)") and year
    ranges look like months ("2027-28"), so strip the former and validate the
    latter before trusting any match.
    """
    text = re.sub(r"[（(][^）)]*[）)]", " ", text)
    m = RE_YMD.search(text)
    if m and 1 <= int(m.group(2)) <= 12:
        i = gidx(int(m.group(1)), int(m.group(2)))
        return i, i, "day"
    for m in RE_YM.finditer(text):
        mo = int(m.group(2))
        if 1 <= mo <= 12:                      # "2027-28" is a year range, not a month
            i = gidx(int(m.group(1)), mo)
            return i, i, "month"
    m = RE_Q.search(text)
    if m:
        y, q = int(m.group(1)), int(m.group(2))
        return gidx(y, q * 3 - 2), gidx(y, q * 3), "part"
    if "H1" in text or "上半" in text:
        m = RE_Y.search(text)
        if m:
            y = int(m.group(1)); return gidx(y, 1), gidx(y, 6), "part"
    if "H2" in text or "下半" in text or "年底" in text:
        m = RE_Y.search(text)
        if m:
            y = int(m.group(1)); return gidx(y, 7), gidx(y, 12), "part"
    ys = [int(x) for x in RE_Y.findall(text)]
    if ys:
        return gidx(min(ys), 1), gidx(max(ys), 12), "year"
    return None


FUT_FILL = {"day": ("1F4E78", "FFFFFF", True), "month": ("1F4E78", "FFFFFF", True),
            "part": ("2E75B6", "FFFFFF", False), "year": ("9DC3E6", "1F1F1F", False)}
PAST_FILL = {"pos": ("C6E0B4", "375623"), "neu": ("BDD7EE", "1F3864"),
             "neg": ("F8CBAD", "833C0C"), "mix": ("FFE699", "7F6000")}


def build(out_path):
    thin = Side(style="thin", color="BFBFBF")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    year_edge = Border(left=Side(style="medium", color="7F7F7F"), right=thin,
                       top=thin, bottom=thin)
    hdr_fill = PatternFill("solid", fgColor="1F4E78")
    hdr_font = Font(bold=True, color="FFFFFF")
    wrap = Alignment(wrap_text=True, vertical="top")
    link_font = Font(color="0563C1", underline="single")

    wb = Workbook()
    ws = wb.active
    ws.title = "FDA Decisions Pending"
    ws.append(["公司 Company", "代號 Ticker", "成功機會 PoS (%)", "TAM (US$ bn)",
               "巿值級別 Cap tier", "藥物 Drug", "適應症 Indication", "FDA階段 Stage",
               f"已發生催化劑/PDUFA (截至 {AS_OF:%Y-%m-%d})", "待發生催化劑/PDUFA (未來)",
               "備註 Notes", "排程狀態 Schedule status"])

    rows_meta, rows_sched = [], []
    for i, r in enumerate(REVIEW):
        co, tk, drug, ind, ph, fda, other, status, r4, issue, note, nxt, ndate, conf, risk, src = r
        ov = OVERRIDES.get(i, {})
        status = ov.get("status", status)
        nxt = ov.get("next", nxt)
        ndate = ov.get("date", ndate)
        other = ov.get("ex_us", other)
        risk = ov.get("risk", risk)
        conf = ov.get("conf", conf)
        pos, why = pos_for(i, status)
        if "pos" in ov:
            pos, why = ov["pos"], ov.get("why", why)
        tam = PIPE[i][13]
        cap = PIPE[i][5]

        past = f"{fda}"
        future = "—" if nxt in ("", "無") else f"{nxt}（{ndate}）"
        notes = "；".join(x for x in [
            f"海外：{other}" if other else "",
            f"風險：{risk}" if risk else "",
            f"附件 R4 問題：{issue}—{note}" if issue != "一致" else "附件 R4 與現況一致",
        ] if x)
        sched = f"信心度 {conf}"
        if issue in ("錯誤", "過時"):
            sched = f"已更新（{issue}）· 信心度 {conf}"
        rows_sched.append((i, sched))
        ws.append([co, tk, pos, float(tam) if tam else None, cap, drug, ind, status,
                   past, future, notes, sched])
        rows_meta.append((i, status, ndate, conf, issue, why, nxt))

    for c, w in enumerate(WIDTHS, 1):
        ws.column_dimensions[get_column_letter(c)].width = w
    for cell in ws[1]:
        cell.fill = hdr_fill; cell.font = hdr_font; cell.border = border
        cell.alignment = Alignment(wrap_text=True, vertical="center")
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.border = border; cell.alignment = wrap
        row[2].number_format = "0"
        row[3].number_format = "0.0"
        t = row[1]; t.hyperlink = TV + str(t.value).lower(); t.font = link_font

    # status colouring on the Stage column, same palette as the grid
    SFILL = {"已獲批": "C6E0B4", "審批中(有PDUFA)": "BDD7EE", "審批中(無PDUFA)": "DEEBF7",
             "CRL": "F8CBAD", "撤回或終止": "D9D9D9", "未遞交": "E7E6E6", "不明": "FFE699"}
    for n, (i, status, ndate, conf, issue, why, nxt) in enumerate(rows_meta, start=2):
        key = next((k for k in SFILL if status.startswith(k)), "不明")
        ws.cell(n, 8).fill = PatternFill("solid", fgColor=SFILL[key])

    # ---- 36-month grid, columns M.. ----
    first = 13
    for off, (y, m) in enumerate(grid_months()):
        c = ws.cell(1, first + off, f"{y}-{m:02d}")
        shade = "C00000" if off == TODAY_IDX else ("808080" if off < TODAY_IDX else "404040")
        c.fill = PatternFill("solid", fgColor=shade)
        c.font = Font(bold=True, color="FFFFFF", size=8)
        c.alignment = Alignment(text_rotation=90, horizontal="center", vertical="bottom")
        c.border = year_edge if m == 1 else border
        ws.column_dimensions[get_column_letter(first + off)].width = GRID_W

    for n, (i, status, ndate, conf, issue, why, nxt) in enumerate(rows_meta, start=2):
        cells = dict(past_events(i))
        nxt_text = nxt or ""
        commercial_only = (status.startswith("已獲批")
                           and any(w in nxt_text for w in COMMERCIAL)
                           and not any(w in nxt_text for w in ("PDUFA", "決定", "遞交", "申報", "sNDA", "sBLA", "NDA", "BLA")))
        sp = (None if commercial_only or not ndate or ndate in ("不明", "持續", "無")
              else future_span(ndate))
        if sp:
            s, e, prec = sp
            s, e = max(s, TODAY_IDX), min(e, GRID_N - 1)
            for k in range(s, e + 1):
                if k not in cells:
                    cells[k] = ("__FUT__", prec, k == s)
        for off in range(GRID_N):
            _, mth = grid_months()[off]
            cell = ws.cell(n, first + off)
            cell.border = year_edge if mth == 1 else border
            hit = cells.get(off)
            if not hit:
                continue
            if hit[0] == "__FUT__":
                bg, fg, bold = FUT_FILL[hit[1]]
                # parentheses hold subordinate asides ("...才會決定是否遞交"),
                # which otherwise hijack the label away from the real event
                nt = re.sub(r"[（(][^）)]*[）)]", " ", nxt or "")
                # a regulatory decision outranks whatever else the catalyst
                # text mentions; otherwise reuse the shared label vocabulary
                lab = ("PDUFA" if "PDUFA" in nt
                       else "決定" if "決定" in nt
                       else "遞交" if ("遞交" in nt or "重交" in nt or "申報" in nt
                                     or "sNDA" in nt or "sBLA" in nt or "NDA" in nt or "BLA" in nt)
                       else label_of(nt)[0])
                show = hit[2]
            else:
                lab, cat = hit
                bg, fg = PAST_FILL[cat]; bold = cat in ("pos", "neg", "mix"); show = True
            cell.fill = PatternFill("solid", fgColor=bg)
            if show:
                cell.value = lab
                cell.font = Font(color=fg, bold=bold, size=8)
                cell.alignment = Alignment(horizontal="center", vertical="center",
                                           text_rotation=90)

    # Rows whose whole history predates the grid would otherwise read as "no
    # events"; say so in the schedule column rather than leaving a blank band.
    for n in range(2, ws.max_row + 1):
        if not any(ws.cell(n, first + o).fill.fgColor.rgb not in (None, "00000000")
                   for o in range(GRID_N)):
            cur = ws.cell(n, 12)
            cur.value = f"{cur.value}．格線外（事件早於 2025-09 或無日期）"
            cur.font = Font(color="833C0C")

    ws.freeze_panes = "C2"
    ws.auto_filter.ref = f"A1:L{ws.max_row}"
    ws.row_dimensions[1].height = 72
    ws.conditional_formatting.add(
        f"C2:C{ws.max_row}",
        ColorScaleRule(start_type="num", start_value=0, start_color="F8CBAD",
                       mid_type="num", mid_value=60, mid_color="FFE699",
                       end_type="num", end_value=100, end_color="C6E0B4"))

    # ---- change log ----
    ws2 = wb.create_sheet("R4 → R6 變更")
    ws2.append(["#", "公司", "代號", "藥物", "R4 所載", "R6 核實狀態", "變更類型",
                "說明", "PoS R4→R6", "PoS 依據", "核實來源"])
    for i, r in enumerate(REVIEW, 1):
        pos, why = pos_for(i - 1, OVERRIDES.get(i - 1, {}).get("status", r[7]))
        old = re.search(r"PoS (\d+)", r[8])
        ws2.append([i, r[0], r[1], r[2], r[8], OVERRIDES.get(i - 1, {}).get("status", r[7]),
                    r[9], r[10], f"{old.group(1) if old else '—'} → {pos}", why, r[15]])
    for c, w in enumerate([4, 14, 8, 24, 30, 26, 8, 40, 12, 34, 34], 1):
        ws2.column_dimensions[get_column_letter(c)].width = w
    for cell in ws2[1]:
        cell.fill = hdr_fill; cell.font = hdr_font
        cell.alignment = Alignment(wrap_text=True, vertical="center"); cell.border = border
    IFILL = {"錯誤": "FF7C80", "過時": "FFC000", "缺漏": "FFE699",
             "不確定": "D9B3FF", "一致": "C6E0B4"}
    for row in ws2.iter_rows(min_row=2):
        for cell in row: cell.border = border; cell.alignment = wrap
        row[6].fill = PatternFill("solid", fgColor=IFILL.get(row[6].value, "FFFFFF"))
        row[6].font = Font(bold=True)
        t = row[2]; t.hyperlink = TV + str(t.value).lower(); t.font = link_font
    ws2.freeze_panes = "D2"; ws2.auto_filter.ref = ws2.dimensions
    ws2.row_dimensions[1].height = 40

    # ---- legend / methodology ----
    ws3 = wb.create_sheet("圖例與方法")
    L = [
     ["FDA Decisions Pending — R6（核實版）"],
     [""],
     ["版面", "與 R4 完全相同：A–L 欄同寬、M–AJ 為 2025-09 至 2028-08 的 36 個月格線、凍結窗格 C2、標題列高 72。只有內容更新。"],
     ["核實日期", str(AS_OF)],
     ["核實方法", "82 行逐項以 WebSearch 對 FDA.gov、公司 IR/新聞稿、SEC 8-K/10-Q/6-K、EMA/EC/MHRA/PMDA/NMPA 官方文件及主要醫藥媒體查證；另交叉比對 Gemini、Grok、GPT-6 三份第三方審閱，逐條複核後採納或駁回。"],
     [""],
     ["H 欄「FDA階段」的分類", ""],
     ["已獲批", "FDA 已批准（含加速批准）。日期為 FDA 行動日；公司新聞稿常晚一日。"],
     ["審批中(有PDUFA)", "申請已受理且 PDUFA 目標日已公開。"],
     ["審批中(無PDUFA)", "已遞交/受理但 PDUFA 未公開。日期為按審查時鐘推算，標示「估算」。"],
     ["CRL", "最近一次 FDA 行動為 Complete Response Letter 或 Refuse-to-File，尚未重交或尚無新 PDUFA。"],
     ["撤回或終止", "申請已撤回、計劃已暫停，或退回較早期臨床階段。"],
     ["未遞交", "R4 列為審批中，但美國申請實際尚未遞交。"],
     [""],
     ["C 欄 PoS 的重新評分", "R4 的 PoS 為階段基準率乘治療領域係數，與個案實況脫節。R6 改以核實狀態重新評分：已獲批 = 100；有 PDUFA 者 85；無 PDUFA 者 80；CRL 35；撤回/終止 5；未遞交 60。再按個案已知障礙人手下調（見「R4 → R6 變更」分頁的 PoS 依據欄）。這是分析判斷，不是經驗證的機率。"],
     [""],
     ["格線顏色 — 已發生（2025-09 至 2026-09）", ""],
     ["  綠", "正面事實：獲批、Ph3 達標、AdCom 支持、資格認定。"],
     ["  藍", "程序事實：遞交、受理、重交、上市、換廠、會議、里程碑。"],
     ["  橙", "負面事實：CRL、RTF、撤回、暫停(clinical hold)、延期、AdCom 反對、計劃終止。"],
     ["  黃", "同月同時有正面與負面事實（例如 GSK 哮喘獲批、CRSwNP 同月收 CRL）。"],
     ["格線顏色 — 待發生（2026-09 之後）", ""],
     ["  深藍", "有明確年月或日期的預定事件。"],
     ["  中藍", "半年或季精度。"],
     ["  淺藍", "只有年份精度，填該年全部月份。"],
     ["標題列", "紅色那格為當月 2026-09；每年 1 月左方有粗線分隔。"],
     [""],
     ["L 欄「排程狀態」", "標示該行相對 R4 的變更類型與資訊信心度。「格線外」= 該標的全部事件早於 2025-09 或無日期可定位，非無事件。"],
     [""],
     ["信心度", "高＝結果/日期由 FDA 或公司一手來源確認；中＝狀態確認但日期未公開或為推算；低＝公開資料不足或指引窗口已過而無披露。此為資訊信心度，非批准機率。"],
     [""],
     ["免責聲明", "僅供研究參考，不構成投資建議。PDUFA 為目標行動日，可提前、延期或收到 CRL，不保證批准。"],
    ]
    for r in L: ws3.append(r)
    ws3.column_dimensions["A"].width = 30
    ws3.column_dimensions["B"].width = 140
    ws3["A1"].font = Font(bold=True, size=14)
    for row in ws3.iter_rows(min_row=2):
        for cell in row: cell.alignment = wrap
        if row[0].value and not row[1].value: row[0].font = Font(bold=True)

    wb.save(out_path)
    counts = defaultdict(int)
    for _, s, *_ in rows_meta:
        counts[next((k for k in SFILL if s.startswith(k)), "不明")] += 1
    print("saved", out_path)
    print("status:", dict(counts))
    print("overrides applied:", len(OVERRIDES))


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "FDA_Decisions_Pending_R6.xlsx")
