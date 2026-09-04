# -*- coding: utf-8 -*-
"""Split a catalyst string into (already-occurred, still-pending) halves.

"Occurred" is decided by what the clause ASSERTS, not by what we know the outcome
was: a clause naming a completed action (filed / positive / CRL / approved) is past,
and a scheduled action whose date has now passed is also past -- but flagged, since
this dataset's knowledge cutoff predates that date and the outcome is unverified.
"""
import re, datetime

TODAY = datetime.date(2026, 9, 4)
CUTOFF = datetime.date(2026, 6, 1)          # dataset knowledge cutoff
MONTHS = {m: i for i, m in enumerate(
    "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(), 1)}

# clause asserts a completed action
DONE = re.compile(r"""\b(
    positive | filed | submitted | accepted | approved | resubmit\w* | resubmission
  | CRL | RTF | done | withdraw\w* | disputed | missed | stopped\ early
  | not\ stat-sig | not\ significant | basis | interim
)\b""", re.I | re.X)

# clause asserts a scheduled / anticipated action
FUTURE = re.compile(r"""\b(
    decision | PDUFA | readout | topline | filing | expected | pending
  | uncertain | exposure | start\w* | planned | confirmatory
)\b""", re.I | re.X)

DATED = re.compile(r"\b(%s)\s+(\d{1,2}),?\s+(\d{4})\b" % "|".join(MONTHS), re.I)
MON_YR = re.compile(r"\b(%s)\s+(\d{4})\b" % "|".join(MONTHS), re.I)
YEAR = re.compile(r"\b(20\d{2})\b")
YR_RANGE = re.compile(r"\b(20\d{2})\s*[-/]\s*(\d{2}|20\d{2})\b")


def clause_date(c):
    """Best-effort date for a clause; returns (date, precision) or (None, None)."""
    m = DATED.search(c)
    if m:
        return datetime.date(int(m.group(3)), MONTHS[m.group(1).title()], int(m.group(2))), "day"
    m = MON_YR.search(c)
    if m:
        return datetime.date(int(m.group(2)), MONTHS[m.group(1).title()], 15), "month"
    m = YR_RANGE.search(c)
    if m:
        end = m.group(2)
        yr = int(end) if len(end) == 4 else int(m.group(1)[:2] + end)
        return datetime.date(yr, 12, 31), "range"
    m = YEAR.search(c)
    if m:
        return datetime.date(int(m.group(1)), 12, 31), "year"
    return None, None


def classify(c):
    """-> ('past'|'future', annotated clause)"""
    c = c.strip()
    d, prec = clause_date(c)
    done, fut = DONE.search(c), FUTURE.search(c)

    # A scheduled event (PDUFA / decision) whose date has demonstrably passed.
    if fut and not done and d and prec == "day" and d <= TODAY:
        tag = c
        if d > CUTOFF:
            tag += "  [日期已過，結果待核實]"
        return "past", tag
    # Completed action wins whenever it is asserted.
    if done and not fut:
        return "past", c
    if done and fut:
        # e.g. "NDA filed 2025; decision 2026" already split by ';' -- here both in
        # one clause, e.g. "resubmitted; PDUFA Apr 10 2026". Date decides.
        if d and prec == "day" and d <= TODAY:
            return "past", c + ("  [日期已過，結果待核實]" if d > CUTOFF else "")
        return "past", c
    if fut:
        if d and prec == "day" and d <= TODAY:
            return "past", c + ("  [日期已過，結果待核實]" if d > CUTOFF else "")
        # A scheduled event whose whole year/window has elapsed already happened.
        if d and prec in ("year", "range") and d < TODAY:
            return "past", c
        return "future", c
    # No verb signal: date decides, else treat as pending context.
    if d and d < TODAY and prec in ("day", "month"):
        return "past", c
    return "future", c


def split_catalyst(text):
    if not text or text == "—":
        return "", ""
    past, fut = [], []
    for clause in re.split(r";\s*", text):
        if not clause.strip():
            continue
        kind, tagged = classify(clause)
        (past if kind == "past" else fut).append(tagged)
    return "; ".join(past), "; ".join(fut)


# Clauses the rules read wrongly; keyed by the exact source string.
OVERRIDES = {
    "PDUFA extended to Dec 28 2025; then further delayed - verify":
        ("PDUFA extended to Dec 28 2025; then further delayed", "重新排期未公佈 - 待核實"),
    "mRNA-1010 P304 positive (Jun 2025); BLA; combo withdrawn pending flu efficacy":
        ("mRNA-1010 P304 positive (Jun 2025); BLA filed; flu+COVID combo withdrawn (2025)",
         "mRNA-1010 BLA decision 待定 (FDA 疫苗政策不確定)"),
    "Royalty/milestone exposure":
        ("", "隨 J&J icotrokinra 之 FDA 決定收取權利金/里程碑 (無獨立 PDUFA)"),
}

_plain = split_catalyst


def split_catalyst(text):  # noqa: F811 - wraps the rule-based splitter
    if text in OVERRIDES:
        return OVERRIDES[text]
    return _plain(text)
