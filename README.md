# FDA Pipeline — US-listed / ADR pharma & biotech

`build_fda_pipeline.py` generates `FDA_Pipeline_US_Listed.xlsx`, a curated snapshot of
US-listed and ADR-tradable companies with drugs under FDA review or in late-stage trials.

Sheets:
1. **Pipeline** — one row per drug candidate: company, ticker, exchange, listing type, drug, mechanism, indication, therapeutic area, FDA stage, designations, catalyst timing, TAM (US$ bn), probability of success (PoS) and its basis.
2. **Company Summary** — per-company roll-up.
3. **FDA Decisions Pending** — NDA/BLA under review, with PoS, TAM and cap tier beside the ticker, catalysts split into occurred vs pending, and a 36-month (2025-09 → 2028-08) schedule grid: 12 past months shaded by outcome polarity (green positive / blue procedural / orange negative / yellow unverified) and 24 future months shaded by date precision. Column widths on this sheet follow the user's hand-tuned layout.
4. **Methodology & Notes** — stage definitions, PoS base rates and adjustments, TAM definition, linking convention, disclaimer.
5. **Ticker Watchlist** — one row per unique ticker with a roll-up of its pipeline.

Every ticker cell is a hyperlink to a TradingView chart:
`https://www.tradingview.com/chart/Q1c5VWwD/?symbol=<ticker lowercased>`

Rebuild:
```bash
pip install openpyxl
python3 build_fda_pipeline.py
# optional: also save a second copy under your own filename
python3 build_fda_pipeline.py "My Watchlist.xlsx"
```
Data is curated as of mid-2026 (rows marked "verify" need checking against FDA/company announcements).

## Third-party review adjudication

`build_review_doc.js` generates a Word report adjudicating the Gemini and Grok
critiques of the watchlist against the spreadsheet's own data — the obstacle
taxonomy, the PoS spread between rows with and without a known regulatory
obstacle, and which dated PDUFA events had actually already passed.

```bash
npm install docx
node build_review_doc.js
```

## Critical review of the pending tab

`build_pending_review.py` holds the row-by-row review of every asset on the
"FDA Decisions Pending" tab, verified against FDA / company / EMA sources by web
search, and writes a six-sheet workbook: per-row review (Phase 1–3 milestones,
FDA history, other regulators, current status, what the watchlist said, issue
type, next catalyst, confidence, risk, sources), issue summary, status counts,
forward catalyst calendar, methodology, and a comparison of three third-party
reviews (Gemini, Grok, GPT-6) against the verified findings.

```bash
python3 build_pending_review.py "My Review.xlsx"
```
