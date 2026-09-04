# FDA Pipeline — US-listed / ADR pharma & biotech

`build_fda_pipeline.py` generates `FDA_Pipeline_US_Listed.xlsx`, a curated snapshot of
US-listed and ADR-tradable companies with drugs under FDA review or in late-stage trials.

Sheets:
1. **Pipeline** — one row per drug candidate: company, ticker, exchange, listing type, drug, mechanism, indication, therapeutic area, FDA stage, designations, catalyst timing, TAM (US$ bn), probability of success (PoS) and its basis.
2. **Company Summary** — per-company roll-up.
3. **FDA Decisions Pending** — NDA/BLA currently under review.
4. **Methodology & Notes** — stage definitions, PoS base rates and adjustments, TAM definition, disclaimer.

Rebuild:
```bash
pip install openpyxl
python3 build_fda_pipeline.py
```
Data is curated as of mid-2026 (rows marked "verify" need checking against FDA/company announcements).
