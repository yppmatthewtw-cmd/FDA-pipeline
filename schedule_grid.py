# -*- coding: utf-8 -*-
"""Map a pending-catalyst string onto a month grid.

Each clause becomes a span of months plus a precision level, because the source
text ranges from an exact PDUFA date to a bare year. Precision is preserved in the
output so the sheet can shade a firm date differently from a whole-year guess.
"""
import re

MONTHS = {m: i for i, m in enumerate(
    "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(), 1)}
_MN = "|".join(MONTHS)

GRID_START = (2026, 9)
GRID_MONTHS = 24


def idx(year, month):
    return (year - GRID_START[0]) * 12 + (month - GRID_START[1])


def months():
    return [((GRID_START[0] * 12 + GRID_START[1] - 1 + i) // 12,
             (GRID_START[0] * 12 + GRID_START[1] - 1 + i) % 12 + 1)
            for i in range(GRID_MONTHS)]


# label keywords, most specific first
LABELS = [
    (r"\bPDUFA\b", "PDUFA"),
    (r"\bCVOT\b", "CVOT"),
    (r"\bs?BLA\b", "BLA"),
    (r"\bs?NDA\b", "NDA"),
    (r"\bdecisions?\b", "決定"),
    (r"\bfiling\b|\bfile\b", "遞交"),
    (r"\bresubmissions?\b", "重交"),
    (r"\breadout\b|\btopline\b", "數據"),
    (r"\bPh3\b|\bPhase 3\b", "Ph3"),
    (r"\bapprovals?\b", "批核"),
]

PREC = {"month": 4, "part": 3, "year": 2, "range": 1}

RE_DAY = re.compile(r"\b(%s)\s+\d{1,2},?\s+(\d{4})\b" % _MN, re.I)
RE_MON = re.compile(r"\b(%s)\s+(\d{4})\b" % _MN, re.I)
RE_PART = re.compile(r"\b(early|mid|late|H1|H2|1H|2H|Q1|Q2|Q3|Q4)\s+(20\d{2})\b", re.I)
RE_RANGE = re.compile(r"\b(20\d{2})\s*[-/]\s*(\d{2}|20\d{2})\b")
RE_YEAR = re.compile(r"\b(20\d{2})\b")

PARTS = {"early": (1, 4), "mid": (5, 8), "late": (9, 12), "h1": (1, 6), "1h": (1, 6),
         "h2": (7, 12), "2h": (7, 12), "q1": (1, 3), "q2": (4, 6), "q3": (7, 9),
         "q4": (10, 12)}


def label_for(clause):
    for pat, lab in LABELS:
        if re.search(pat, clause, re.I):
            return lab
    return "事件"


def span(clause):
    """-> (start_idx, end_idx, precision) clipped to the grid, or None."""
    m = RE_DAY.search(clause) or RE_MON.search(clause)
    if m:
        y, mo = int(m.group(2)), MONTHS[m.group(1).title()]
        s = e = idx(y, mo)
        prec = "month"
    else:
        # a range wins over a bare part/year: "late 2026/2027" spans both years
        r = RE_RANGE.search(clause)
        if r:
            y1 = int(r.group(1))
            tail = r.group(2)
            y2 = int(tail) if len(tail) == 4 else int(str(y1)[:2] + tail)
            s, e, prec = idx(y1, 1), idx(y2, 12), "range"
        else:
            p = RE_PART.search(clause)
            if p:
                y = int(p.group(2)); a, b = PARTS[p.group(1).lower()]
                s, e, prec = idx(y, a), idx(y, b), "part"
            else:
                yr = RE_YEAR.search(clause)
                if not yr:
                    return None
                y = int(yr.group(1))
                s, e, prec = idx(y, 1), idx(y, 12), "year"
    s, e = max(s, 0), min(e, GRID_MONTHS - 1)
    if e < 0 or s > GRID_MONTHS - 1 or s > e:
        return None
    return s, e, prec


def raw_span(clause):
    """Unclipped span, so callers can tell 'overdue' from 'off-grid future'."""
    m = RE_DAY.search(clause) or RE_MON.search(clause)
    if m:
        y, mo = int(m.group(2)), MONTHS[m.group(1).title()]
        return idx(y, mo), idx(y, mo)
    r = RE_RANGE.search(clause)
    if r:
        y1 = int(r.group(1)); tail = r.group(2)
        y2 = int(tail) if len(tail) == 4 else int(str(y1)[:2] + tail)
        return idx(y1, 1), idx(y2, 12)
    p = RE_PART.search(clause)
    if p:
        y = int(p.group(2)); a, b = PARTS[p.group(1).lower()]
        return idx(y, a), idx(y, b)
    yr = RE_YEAR.search(clause)
    if yr:
        y = int(yr.group(1))
        return idx(y, 1), idx(y, 12)
    return None


def schedule(pending_text):
    """-> ({month_index: (label, precision, is_span_start)}, status_text)"""
    out = {}
    if not pending_text or pending_text == "—":
        return out, "無待發生項目"
    overdue, undated = [], []
    for clause in re.split(r";\s*", pending_text):
        clause = clause.strip()
        if not clause:
            continue
        raw = raw_span(clause)
        if raw is None:
            undated.append(label_for(clause))
            continue
        if raw[1] < 0:
            overdue.append(label_for(clause))
            continue
        sp = span(clause)
        if not sp:
            continue
        st, en, prec = sp
        lab = label_for(clause)
        for i in range(st, en + 1):
            prev = out.get(i)
            # a firmer clause overwrites a vaguer one in the same cell
            if prev and PREC[prev[1]] >= PREC[prec]:
                continue
            out[i] = (lab, prec, i == st)
    notes = []
    if overdue:
        notes.append("逾期未發生: " + "/".join(dict.fromkeys(overdue)))
    if undated:
        notes.append("無明確日期: " + "/".join(dict.fromkeys(undated)))
    return out, "; ".join(notes)
