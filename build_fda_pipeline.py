# -*- coding: utf-8 -*-
"""
Build FDA_Pipeline_US_Listed.xlsx
Curated snapshot (knowledge as of mid-2026) of US-listed / ADR-tradable pharma & biotech
companies with late-stage FDA pipeline candidates (NDA/BLA under review, Phase 3, key Phase 2).
Live openFDA / ClinicalTrials.gov access is blocked in this environment, so data is curated.
"""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

# Industry base-rate probability of approval (PoS) by stage, from BIO/Informa/QLS
# "Clinical Development Success Rates 2011-2020" and subsequent updates.
BASE_POS = {
    "Approved (recent)": 100,
    "NDA/BLA under review": 90,
    "NDA/BLA under review (CRL history)": 75,
    "Phase 3 (positive readout, filing pending)": 85,
    "Phase 3": 55,
    "Phase 2/3": 40,
    "Phase 2 (positive readout)": 35,
    "Phase 2": 25,
    "Phase 1/2": 15,
}
# Therapeutic-area adjustment (multiplicative) — oncology & CNS historically below average,
# hematology / rare disease / infectious disease above average.
TA_ADJ = {
    "Oncology": 0.85, "CNS/Psychiatry": 0.80, "Neurology": 0.85, "Cardiovascular": 0.95,
    "Metabolic/Obesity": 1.00, "Immunology": 1.00, "Rare disease": 1.10, "Hematology": 1.10,
    "Infectious disease/Vaccine": 1.05, "Ophthalmology": 0.95, "Respiratory": 0.95,
    "Nephrology": 0.95, "Dermatology": 1.00, "Gastroenterology": 0.95, "Endocrinology": 1.00,
    "Women's health": 1.00, "Hepatology": 0.90,
}

# Columns:
# company, ticker, exchange, listing, hq, cap_tier, drug, moa, indication, ta, stage,
# designations, catalyst, tam_bn, tam_note, pos_override(None or %), notes
ROWS = [
# ---------------- LARGE-CAP US ----------------
("Eli Lilly","LLY","NYSE","US common","US","Mega (>$500bn)","Orforglipron","Oral small-molecule GLP-1 agonist","Obesity / T2D","Metabolic/Obesity","NDA/BLA under review","Priority review voucher used (obesity)","FDA decision expected 2026; T2D filing to follow","150","Global GLP-1 obesity+T2D market est. $150bn by 2030 (Lilly/Novo guidance, sell-side)",None,"First oral non-peptide GLP-1; ACHIEVE/ATTAIN Ph3 positive"),
("Eli Lilly","LLY","NYSE","US common","US","Mega (>$500bn)","Retatrutide","GIP/GLP-1/glucagon triple agonist","Obesity, T2D, OSA, knee OA","Metabolic/Obesity","Phase 3","—","TRIUMPH Ph3 readouts 2025-2026; filing 2026-27","150","Shares obesity TAM; ~24% weight loss in Ph2",None,"Potential best-in-class efficacy"),
("Eli Lilly","LLY","NYSE","US common","US","Mega (>$500bn)","Olomorasib","KRAS G12C inhibitor","NSCLC (1L combo w/ pembrolizumab)","Oncology","Phase 3","Fast Track","SUNRAY-01 Ph3 readout 2026-27","8","KRAS G12C NSCLC + CRC ~$8bn peak class TAM",None,""),
("Eli Lilly","LLY","NYSE","US common","US","Mega (>$500bn)","Lepodisiran","siRNA vs Lp(a)","Cardiovascular risk reduction (elevated Lp(a))","Cardiovascular","Phase 3","—","ACCLAIM-Lp(a) outcomes ~2029","15","~64m US adults w/ high Lp(a); class TAM $10-20bn",None,"Competes with Novartis pelacarsen, Amgen olpasiran"),
("Eli Lilly","LLY","NYSE","US common","US","Mega (>$500bn)","Imlunestrant","Oral SERD","ER+/HER2- breast cancer (ESR1m)","Oncology","Approved (recent)","—","Approved as Inluriyo Sep 2025 (EMBER-3); label expansion trials ongoing","4","Oral SERD class ~$4-6bn",None,"驗證標籤範圍"),
("Pfizer","PFE","NYSE","US common","US","Large ($100-500bn)","Sasanlimab","Subcutaneous PD-1","BCG-unresponsive NMIBC (w/ BCG)","Oncology","NDA/BLA under review","—","CREST Ph3 positive; FDA decision 2026","3","NMIBC ~$3bn",None,""),
("Pfizer","PFE","NYSE","US common","US","Large ($100-500bn)","Vepdegestrant (w/ Arvinas)","PROTAC estrogen receptor degrader","ER+/HER2- ESR1m breast cancer","Oncology","NDA/BLA under review","Fast Track","PDUFA Jun 5 2026 (VERITAC-2)","3","ESR1m 2L BC segment",None,"Partnered with Arvinas (ARVN)"),
("Pfizer","PFE","NYSE","US common","US","Large ($100-500bn)","Sigvotatug vedotin","B6A-directed ADC","NSCLC 2L","Oncology","Phase 3","—","Be6A Lung-01 Ph3 readout 2026-27","5","2L NSCLC ADC segment",None,"From Seagen acquisition"),
("Pfizer","PFE","NYSE","US common","US","Large ($100-500bn)","Atirmociclib","Selective CDK4 inhibitor","HR+/HER2- breast cancer 1L","Oncology","Phase 3","—","FOURLIGHT-3 readout 2027","10","CDK4/6 class ~$15bn",None,""),
("Pfizer","PFE","NYSE","US common","US","Large ($100-500bn)","Mevrometostat","EZH2 inhibitor","mCRPC (w/ enzalutamide)","Oncology","Phase 3","—","MEVPRO-1/2 readouts 2026","4","mCRPC $12bn market",None,""),
("Pfizer","PFE","NYSE","US common","US","Large ($100-500bn)","Ponsegromab","GDF-15 antibody","Cancer cachexia","Oncology","Phase 3","Breakthrough","Ph3 start 2025; readout 2027","3","No approved therapy; ~$3bn est.",None,""),
("Merck & Co.","MRK","NYSE","US common","US","Large ($100-500bn)","Enlicitide (MK-0616)","Oral PCSK9 inhibitor (macrocyclic peptide)","Hypercholesterolemia","Cardiovascular","NDA/BLA under review","—","CORALreef Ph3 positive 2025; FDA decision 2026","10","Oral PCSK9 could expand $5bn injectable class to $10bn+",None,"First oral PCSK9"),
("Merck & Co.","MRK","NYSE","US common","US","Large ($100-500bn)","Sac-TMT (sacituzumab tirumotecan, w/ Kelun)","TROP2 ADC","NSCLC, breast, endometrial","Oncology","Phase 3","—","Multiple TroFuse Ph3 readouts 2026-27","10","TROP2 ADC class $10bn+",None,""),
("Merck & Co.","MRK","NYSE","US common","US","Large ($100-500bn)","Tulisokibart (MK-7240)","TL1A antibody","Ulcerative colitis, Crohn's","Immunology","Phase 3","—","ATLAS-UC / ARES-CD readouts 2026-27","15","TL1A class est. $10-15bn; IBD market $25bn",None,"From Prometheus acquisition"),
("Merck & Co.","MRK","NYSE","US common","US","Large ($100-500bn)","Clesrovimab (Enflonsia)","RSV monoclonal antibody (infant)","RSV prevention in infants","Infectious disease/Vaccine","Approved (recent)","—","Approved Jun 2025; launch season 2025-26","3","Infant RSV mAb ~$3bn (vs Beyfortus)",None,""),
("Merck & Co.","MRK","NYSE","US common","US","Large ($100-500bn)","Subcutaneous pembrolizumab (w/ berahyaluronidase)","SC PD-1","Multiple solid tumors","Oncology","Approved (recent)","—","Approved Sep 2025 as Keytruda Qlex","30","Keytruda franchise defense ($30bn) ahead of 2028 LOE",None,""),
("Merck & Co.","MRK","NYSE","US common","US","Large ($100-500bn)","Winrevair (sotatercept) expansion","Activin signaling inhibitor","PAH (HYPERION/CADENCE label expansion)","Cardiovascular","NDA/BLA under review","Breakthrough","sNDA decisions 2026","7","PAH $7-8bn",None,""),
("Johnson & Johnson","JNJ","NYSE","US common","US","Large ($100-500bn)","Icotrokinra (JNJ-2113)","Oral IL-23R peptide antagonist","Plaque psoriasis, UC","Immunology","NDA/BLA under review","—","NDA filed 2025 (psoriasis); FDA decision 2026","10","Oral psoriasis/IBD; $10bn peak potential (JNJ guidance $5bn+)",None,"First oral IL-23"),
("Johnson & Johnson","JNJ","NYSE","US common","US","Large ($100-500bn)","TAR-200 (Inlexzo)","Intravesical gemcitabine releasing system","BCG-unresponsive NMIBC","Oncology","Approved (recent)","Breakthrough","Approved Sep 2025; further Ph3 (SunRISe-3/5)","3","NMIBC $3bn",None,""),
("Johnson & Johnson","JNJ","NYSE","US common","US","Large ($100-500bn)","Nipocalimab (Imaavy)","FcRn blocker","gMG approved; CIDP, HDFN, Sjogren's in Ph3","Immunology","Phase 3","Breakthrough (HDFN)","Label expansions 2026-28","5","FcRn class $8-10bn (vs Vyvgart)",None,""),
("Johnson & Johnson","JNJ","NYSE","US common","US","Large ($100-500bn)","Rybrevant + Lazcluze SC / expansions","EGFR/MET bispecific","EGFRm NSCLC","Oncology","NDA/BLA under review","—","SC formulation decision 2025-26 (PALOMA)","5","EGFRm NSCLC $5bn+ (JNJ target)",None,""),
("Johnson & Johnson","JNJ","NYSE","US common","US","Large ($100-500bn)","Aticaprant","Kappa opioid receptor antagonist","Major depressive disorder (adjunct)","CNS/Psychiatry","Phase 3","—","VENTURA Ph3 readouts 2026","5","Adjunctive MDD $5bn",None,""),
("AbbVie","ABBV","NYSE","US common","US","Large ($100-500bn)","Tavapadon","D1/D5 partial agonist","Parkinson's disease","Neurology","NDA/BLA under review","—","NDA filed 2025; FDA decision 2026","3","PD adjunct $3bn",None,"From Cerevel acquisition"),
("AbbVie","ABBV","NYSE","US common","US","Large ($100-500bn)","Emraclidine","M4 PAM","Schizophrenia","CNS/Psychiatry","Phase 2","—","Failed EMPOWER Ph2 (Nov 2024); re-evaluating","6","Schizophrenia $6bn",10,"High risk after failure"),
("AbbVie","ABBV","NYSE","US common","US","Large ($100-500bn)","Telisotuzumab vedotin (Emrelis)","c-Met ADC","c-Met overexpressing NSCLC","Oncology","Approved (recent)","Breakthrough","Accelerated approval May 2025; confirmatory Ph3","2","c-Met OE NSCLC ~$2bn",None,""),
("AbbVie","ABBV","NYSE","US common","US","Large ($100-500bn)","Pivekimab sunirine (Pivek)","CD123 ADC","BPDCN","Hematology","NDA/BLA under review","Breakthrough, Orphan","BLA under review 2025-26","0.3","Ultra-rare",None,""),
("AbbVie","ABBV","NYSE","US common","US","Large ($100-500bn)","Lutikizumab","IL-1a/b bispecific","Hidradenitis suppurativa","Immunology","Phase 3","—","Ph3 started 2025","5","HS $5bn+",None,""),
("Bristol Myers Squibb","BMY","NYSE","US common","US","Large ($100-500bn)","Cobenfy (KarXT) adjunctive / AD psychosis","M1/M4 muscarinic agonist","Adjunctive schizophrenia; Alzheimer's psychosis","CNS/Psychiatry","Phase 3","—","ADEPT Ph3 (ADP) readouts 2026; ARISE adjunct missed (Apr 2025)","6","Expansion beyond monotherapy schizophrenia; ADP no approved drugs",None,"Adjunctive trial missed endpoint"),
("Bristol Myers Squibb","BMY","NYSE","US common","US","Large ($100-500bn)","Milvexian (w/ J&J)","Oral Factor XIa inhibitor","AF stroke prevention, ACS, secondary stroke","Cardiovascular","Phase 3","Fast Track","LIBREXIA Ph3 readouts 2026","10","FXIa class $5-10bn if AF succeeds",None,"Bayer's asundexian failed AF Ph3 (OCEANIC-AF)"),
("Bristol Myers Squibb","BMY","NYSE","US common","US","Large ($100-500bn)","Iberdomide / Mezigdomide","CELMoDs","Multiple myeloma","Hematology","Phase 3","—","EXCALIBER / SUCCESSOR readouts 2026","5","MM $25bn market",None,""),
("Bristol Myers Squibb","BMY","NYSE","US common","US","Large ($100-500bn)","BMS-986365 (Izalontamab brengitecan, w/ SystImmune)","EGFR x HER3 bispecific ADC","NSCLC, breast","Oncology","Phase 3","Breakthrough","Ph3 readouts 2026-27","6","",None,""),
("Amgen","AMGN","NASDAQ","US common","US","Large ($100-500bn)","MariTide (maridebart cafraglutide)","GLP-1 agonist / GIPR antagonist, monthly","Obesity / T2D","Metabolic/Obesity","Phase 3","—","MARITIME Ph3 readouts 2026-27","150","Obesity TAM shared",None,"Monthly dosing differentiation; tolerability questions"),
("Amgen","AMGN","NASDAQ","US common","US","Large ($100-500bn)","Olpasiran","siRNA vs Lp(a)","ASCVD with elevated Lp(a)","Cardiovascular","Phase 3","—","OCEAN(a)-Outcomes readout 2026-27","15","Lp(a) class",None,""),
("Amgen","AMGN","NASDAQ","US common","US","Large ($100-500bn)","Bemarituzumab","FGFR2b antibody","FGFR2b+ gastric cancer 1L","Oncology","Phase 3","Breakthrough","FORTITUDE-101 positive (2025); filing 2026","2","FGFR2b+ gastric ~$2bn",None,""),
("Amgen","AMGN","NASDAQ","US common","US","Large ($100-500bn)","Rocatinlimab (w/ Kyowa Kirin)","OX40 antibody","Atopic dermatitis","Immunology","NDA/BLA under review","—","ROCKET Ph3 done; filing 2025-26","5","AD biologics $15bn",None,"Modest efficacy vs Dupixent"),
("Amgen","AMGN","NASDAQ","US common","US","Large ($100-500bn)","Uplizna (inebilizumab) expansions","CD19 antibody","IgG4-RD (approved Apr 2025), gMG","Immunology","Approved (recent)","Orphan","gMG sBLA decision 2025-26","2","",None,""),
("Gilead Sciences","GILD","NASDAQ","US common","US","Large ($100-500bn)","Yeztugo (lenacapavir) PrEP","Capsid inhibitor, twice-yearly","HIV pre-exposure prophylaxis","Infectious disease/Vaccine","Approved (recent)","Breakthrough","Approved Jun 2025; launch ramp 2026","5","PrEP market $5bn+; long-term $8bn",None,""),
("Gilead Sciences","GILD","NASDAQ","US common","US","Large ($100-500bn)","Anito-cel (anitocabtagene autoleucel, w/ Arcellx)","BCMA CAR-T","R/R multiple myeloma","Hematology","NDA/BLA under review","Breakthrough, Orphan","BLA filed 2025; FDA decision 2026","4","BCMA CAR-T $4bn+ (vs Carvykti)",None,"Partner: Arcellx (ACLX)"),
("Gilead Sciences","GILD","NASDAQ","US common","US","Large ($100-500bn)","Trodelvy 1L TNBC (ASCENT-04/03)","TROP2 ADC","1L mTNBC","Oncology","NDA/BLA under review","—","sBLA decisions 2026","4","",None,""),
("Regeneron","REGN","NASDAQ","US common","US","Large ($100-500bn)","Lynozyfic (linvoseltamab)","BCMA x CD3 bispecific","R/R multiple myeloma","Hematology","Approved (recent)","Orphan","Accelerated approval Jul 2025","3","BCMA bispecific segment",None,""),
("Regeneron","REGN","NASDAQ","US common","US","Large ($100-500bn)","Odronextamab (Lynozyfic-class)","CD20 x CD3 bispecific","FL, DLBCL","Hematology","NDA/BLA under review","Orphan","FL approved Jul 2025 (accelerated); DLBCL pending","3","",None,""),
("Regeneron","REGN","NASDAQ","US common","US","Large ($100-500bn)","Dupixent CSU / BP / CPUO expansions","IL-4Ra antibody","Bullous pemphigoid, CPUO","Immunology","NDA/BLA under review","—","BP approved Jun 2025; CPUO filing 2026","20","Dupixent franchise $20bn",None,""),
("Regeneron","REGN","NASDAQ","US common","US","Large ($100-500bn)","Itepekimab (w/ Sanofi)","IL-33 antibody","COPD","Respiratory","Phase 3","—","AERIFY-1 positive / AERIFY-2 missed (May 2025); path unclear","8","COPD biologics $8bn+",30,"Mixed Ph3 results"),
("Regeneron","REGN","NASDAQ","US common","US","Large ($100-500bn)","Trevogrumab + garetosmab + semaglutide","Myostatin / activin A antibodies","Obesity (muscle preservation)","Metabolic/Obesity","Phase 2","—","COURAGE Ph2 data 2025-26","20","Muscle-sparing obesity adjunct",None,""),
("Regeneron","REGN","NASDAQ","US common","US","Large ($100-500bn)","DB-OTO","Otoferlin gene therapy","Genetic deafness (OTOF)","Rare disease","Phase 1/2","Breakthrough, Orphan, RMAT","Pivotal data 2026","0.5","Ultra-rare",None,""),
("Vertex Pharmaceuticals","VRTX","NASDAQ","US common","US","Large ($100-500bn)","Journavx (suzetrigine) expansions","NaV1.8 inhibitor","Acute pain (approved Jan 2025); DPN, LSR chronic pain","Neurology","Phase 3","Breakthrough, Fast Track","DPN Ph3 readouts 2026-27","10","Non-opioid pain $5-10bn",None,""),
("Vertex Pharmaceuticals","VRTX","NASDAQ","US common","US","Large ($100-500bn)","Povetacicept","APRIL/BAFF dual antagonist","IgA nephropathy, pMN","Nephrology","Phase 3","Breakthrough","RAINIER interim for accelerated approval 2026","5","IgAN $5bn class",None,"From Alpine Immune Sciences"),
("Vertex Pharmaceuticals","VRTX","NASDAQ","US common","US","Large ($100-500bn)","Zimislecel (VX-880)","Stem-cell derived islet cells","Type 1 diabetes (severe hypoglycemia)","Endocrinology","Phase 3","RMAT, Orphan","Filing planned 2026","3","Initial ~60k severe T1D; broader later",None,""),
("Vertex Pharmaceuticals","VRTX","NASDAQ","US common","US","Large ($100-500bn)","Inaxaplin (VX-147)","APOL1 inhibitor","APOL1-mediated kidney disease","Nephrology","Phase 3","Breakthrough","AMPLITUDE Ph2/3 readout 2026","3","~100k US patients",None,""),
# ---------------- LARGE-CAP ADR (Europe / Japan / Australia) ----------------
("Novo Nordisk","NVO","NYSE","ADR","Denmark","Large ($100-500bn)","CagriSema","Cagrilintide (amylin) + semaglutide","Obesity / T2D","Metabolic/Obesity","NDA/BLA under review","—","Filing early 2026 (REDEFINE 1/2); FDA decision late 2026/2027","150","Obesity TAM",None,"~20-22% weight loss; below 25% target"),
("Novo Nordisk","NVO","NYSE","ADR","Denmark","Large ($100-500bn)","Oral semaglutide 25mg (Wegovy pill)","Oral GLP-1","Obesity","Metabolic/Obesity","Approved (recent)","—","Approved Dec 2025; launch 2026","150","",None,"Verify approval status"),
("Novo Nordisk","NVO","NYSE","ADR","Denmark","Large ($100-500bn)","Amycretin","GLP-1/amylin co-agonist (oral & SC)","Obesity","Metabolic/Obesity","Phase 3","—","Ph3 start 2026","150","",None,""),
("Novo Nordisk","NVO","NYSE","ADR","Denmark","Large ($100-500bn)","Mim8 (denecimig)","FVIIIa mimetic bispecific","Hemophilia A","Hematology","NDA/BLA under review","Orphan","FRONTIER Ph3 done; filing 2025-26","4","Hem A prophylaxis $8bn (vs Hemlibra)",None,""),
("Novo Nordisk","NVO","NYSE","ADR","Denmark","Large ($100-500bn)","Ziltivekimab","IL-6 antibody","ASCVD w/ inflammation, HFpEF","Cardiovascular","Phase 3","—","ZEUS outcomes readout 2026-27","8","",None,""),
("AstraZeneca","AZN","NASDAQ","ADR","UK","Large ($100-500bn)","Baxdrostat","Aldosterone synthase inhibitor","Uncontrolled / resistant hypertension","Cardiovascular","NDA/BLA under review","—","BaxHTN Ph3 positive (Aug 2025); NDA filed; decision 2026","5","AZ peak sales guidance $5bn+",None,""),
("AstraZeneca","AZN","NASDAQ","ADR","UK","Large ($100-500bn)","Camizestrant","Oral SERD","ER+/HER2- BC (SERENA-6 switch strategy)","Oncology","NDA/BLA under review","—","SERENA-6 positive; NDA filed 2025","5","",None,""),
("AstraZeneca","AZN","NASDAQ","ADR","UK","Large ($100-500bn)","Datroway (Dato-DXd, w/ Daiichi)","TROP2 ADC","HR+ BC (approved Jan 2025), EGFRm NSCLC (Jun 2025), further","Oncology","Approved (recent)","Breakthrough","TROPION-Lung Ph3 expansions 2026","8","",None,""),
("AstraZeneca","AZN","NASDAQ","ADR","UK","Large ($100-500bn)","Eneboparatide","PTH1 receptor agonist","Hypoparathyroidism","Endocrinology","Phase 3","Orphan","CALYPSO Ph3 positive 2025; filing 2026","2","Hypopara $2-3bn (vs Yorvipath)",None,"From Amolyt acquisition"),
("AstraZeneca","AZN","NASDAQ","ADR","UK","Large ($100-500bn)","Anselamimab","Amyloid fibril antibody","AL amyloidosis","Hematology","Phase 3","Orphan","Ph3 missed primary but Mayo stage IIIb subgroup positive (2025)","2","",35,""),
("AstraZeneca","AZN","NASDAQ","ADR","UK","Large ($100-500bn)","AZD0780","Oral PCSK9 inhibitor","Hypercholesterolemia","Cardiovascular","Phase 3","—","Ph3 start 2025-26","10","",None,""),
("AstraZeneca","AZN","NASDAQ","ADR","UK","Large ($100-500bn)","Tozorakimab","IL-33 antibody","COPD","Respiratory","Phase 3","—","OBERON/TITANIA readouts 2026","8","",None,""),
("Novartis","NVS","NYSE","ADR","Switzerland","Large ($100-500bn)","Pelacarsen","Antisense vs Lp(a)","ASCVD with elevated Lp(a)","Cardiovascular","Phase 3","—","Lp(a)HORIZON outcomes readout 2026","15","First-mover in Lp(a) class",None,"Partner Ionis (IONS)"),
("Novartis","NVS","NYSE","ADR","Switzerland","Large ($100-500bn)","Remibrutinib (Rhapsido)","Oral BTK inhibitor","CSU approved Sep 2025; CINDU, HS, MS in Ph3","Immunology","Approved (recent)","—","MS Ph3 readouts 2026-27","5","",None,""),
("Novartis","NVS","NYSE","ADR","Switzerland","Large ($100-500bn)","Ianalumab","BAFF-R antibody","Sjogren's disease, ITP, SLE","Immunology","NDA/BLA under review","—","NEPTUNUS Ph3 positive 2025; filing 2026","4","Sjogren's - no approved biologic",None,""),
("Novartis","NVS","NYSE","ADR","Switzerland","Large ($100-500bn)","Atrasentan (Vanrafia)","Endothelin A antagonist","IgA nephropathy","Nephrology","Approved (recent)","—","Accelerated approval Apr 2025","2","",None,""),
("Novartis","NVS","NYSE","ADR","Switzerland","Large ($100-500bn)","Pluvicto expansions (PSMAddition)","PSMA radioligand","mHSPC","Oncology","NDA/BLA under review","—","sNDA filed 2025","5","Pluvicto peak $5bn+",None,""),
("Novartis","NVS","NYSE","ADR","Switzerland","Large ($100-500bn)","OAV101 IT (intrathecal Zolgensma)","SMN1 gene therapy","SMA (older patients)","Rare disease","NDA/BLA under review","Orphan","STEER Ph3 positive; FDA decision 2025-26","2","",None,""),
("Roche","RHHBY","OTC","ADR","Switzerland","Large ($100-500bn)","Giredestrant","Oral SERD","ER+ BC (evERA, persevERA)","Oncology","NDA/BLA under review","—","evERA positive 2025; filing 2026","5","",None,""),
("Roche","RHHBY","OTC","ADR","Switzerland","Large ($100-500bn)","Fenebrutinib","BTK inhibitor","RMS & PPMS","Neurology","Phase 3","—","FENhance/FENtrepid readouts late 2025-2026","5","MS $25bn market",None,""),
("Roche","RHHBY","OTC","ADR","Switzerland","Large ($100-500bn)","Trontinemab","Brainshuttle anti-amyloid","Early Alzheimer's","Neurology","Phase 3","—","TRONTIER 1/2 Ph3 started 2025; readout 2028","15","AD anti-amyloid $10-15bn",None,""),
("Roche","RHHBY","OTC","ADR","Switzerland","Large ($100-500bn)","Petrelintide (w/ Zealand)","Amylin analog","Obesity","Metabolic/Obesity","Phase 2","—","Ph2 data 2026","150","",None,""),
("Roche","RHHBY","OTC","ADR","Switzerland","Large ($100-500bn)","Vamikibart","IL-6 antibody (intravitreal)","Uveitic macular edema","Ophthalmology","Phase 3","—","MEERKAT/SANDCAT mixed 2025","1","",35,""),
("Roche","RHHBY","OTC","ADR","Switzerland","Large ($100-500bn)","Sefaxersen / NXT007","FVIII-mimetic next-gen","Hemophilia A","Hematology","Phase 3","—","Ph3 2026","8","",None,""),
("Sanofi","SNY","NASDAQ","ADR","France","Large ($100-500bn)","Tolebrutinib","Brain-penetrant BTK inhibitor","nrSPMS (HERCULES positive), RMS (GEMINI missed)","Neurology","NDA/BLA under review (CRL history)","Breakthrough","PDUFA extended to Dec 28 2025; then further delayed - verify","4","nrSPMS no approved therapy; $3-5bn",60,"Liver safety concerns; regulatory uncertainty"),
("Sanofi","SNY","NASDAQ","ADR","France","Large ($100-500bn)","Amlitelimab","OX40L antibody","Atopic dermatitis, asthma","Immunology","Phase 3","—","COAST/SHORE Ph3 readouts 2025-26 (COAST-1 modest)","5","Sanofi peak sales guidance EUR5bn+",None,""),
("Sanofi","SNY","NASDAQ","ADR","France","Large ($100-500bn)","Rilzabrutinib (Wayrilz)","Oral BTK inhibitor","Immune thrombocytopenia","Hematology","Approved (recent)","Orphan, Fast Track","Approved Aug 2025","1","ITP $1-2bn",None,""),
("Sanofi","SNY","NASDAQ","ADR","France","Large ($100-500bn)","Fitusiran (Qfitlia)","Antithrombin siRNA","Hemophilia A/B","Hematology","Approved (recent)","Orphan","Approved Mar 2025","2","",None,""),
("Sanofi","SNY","NASDAQ","ADR","France","Large ($100-500bn)","Frexalimab","CD40L antibody","RMS, nrSPMS, T1D","Immunology","Phase 3","—","FREXALT/FREVIVA readouts 2027","5","",None,""),
("GSK","GSK","NYSE","ADR","UK","Large ($100-500bn)","Depemokimab","Ultra-long-acting IL-5 antibody","Severe asthma, CRSwNP","Respiratory","NDA/BLA under review","—","PDUFA Dec 16 2025 (SWIFT/ANCHOR) - verify","3","GSK peak >GBP3bn",None,""),
("GSK","GSK","NYSE","ADR","UK","Large ($100-500bn)","Blenrep (belantamab mafodotin)","BCMA ADC","R/R multiple myeloma (DREAMM-7/8)","Hematology","Approved (recent)","Orphan","Re-approved Oct 2025 (restricted label)","3","",None,"CRL/delay history in 2025"),
("GSK","GSK","NYSE","ADR","UK","Large ($100-500bn)","Camlipixant","P2X3 antagonist","Refractory chronic cough","Respiratory","Phase 3","—","CALM-1 mixed/ CALM-2 readout 2026","2","RCC ~$2-3bn (Merck gefapixant precedent)",None,""),
("GSK","GSK","NYSE","ADR","UK","Large ($100-500bn)","Tebipenem HBr (w/ Spero)","Oral carbapenem","Complicated UTI","Infectious disease/Vaccine","NDA/BLA under review","QIDP, Fast Track","PIVOT-PO stopped early for efficacy (2025); NDA 2026","1","",None,""),
("GSK","GSK","NYSE","ADR","UK","Large ($100-500bn)","Bepirovirsen","Antisense vs HBV","Chronic hepatitis B functional cure","Hepatology","Phase 3","Fast Track","B-Well 1/2 readouts 2026","5","CHB functional cure $5bn+",None,""),
("Bayer","BAYRY","OTC","ADR","Germany","Mid ($10-100bn)","Elinzanetant (Lynkuet)","NK1/NK3 antagonist","Vasomotor symptoms (menopause)","Women's health","Approved (recent)","—","Approved Oct 2025 after delay","2","VMS non-hormonal $2-3bn",None,""),
("Bayer","BAYRY","OTC","ADR","Germany","Mid ($10-100bn)","Asundexian","Oral FXIa inhibitor","Secondary stroke prevention (OCEANIC-STROKE)","Cardiovascular","Phase 3","—","OCEANIC-STROKE positive (Nov 2025); filing 2026","3","",None,"OCEANIC-AF failed 2023"),
("Bayer","BAYRY","OTC","ADR","Germany","Mid ($10-100bn)","Sevabertinib (Hyrnuo)","HER2 TKI","HER2-mutant NSCLC","Oncology","Approved (recent)","Breakthrough","Accelerated approval Nov 2025","1","",None,""),
("Takeda","TAK","NYSE","ADR","Japan","Mid ($10-100bn)","Oveporexton (TAK-861)","Orexin-2 receptor agonist","Narcolepsy type 1","Neurology","NDA/BLA under review","Breakthrough","FirstLight/RadiantLight positive (Jul 2025); NDA filed; decision 2026","3","NT1 $2-3bn; broader orexin class larger",None,"First-in-class orexin agonist"),
("Takeda","TAK","NYSE","ADR","Japan","Mid ($10-100bn)","Zasocitinib (TAK-279)","Oral TYK2 inhibitor","Psoriasis, PsA","Immunology","Phase 3","—","Ph3 psoriasis readouts 2025-26; filing 2026","5","Oral psoriasis (vs Sotyktu, icotrokinra)",None,""),
("Takeda","TAK","NYSE","ADR","Japan","Mid ($10-100bn)","Rusfertide (w/ Protagonist)","Hepcidin mimetic","Polycythemia vera","Hematology","NDA/BLA under review","Breakthrough, Orphan","VERIFY Ph3 positive (Mar 2025); NDA filed 2025","1.5","PV $1-2bn",None,"Partner Protagonist (PTGX)"),
("Takeda","TAK","NYSE","ADR","Japan","Mid ($10-100bn)","Fazirsiran (w/ Arrowhead)","siRNA vs Z-AAT","AATD liver disease","Hepatology","Phase 3","Breakthrough, Orphan","Ph3 readout 2026-27","2","",None,""),
("Astellas","ALPMY","OTC","ADR","Japan","Mid ($10-100bn)","Zolbetuximab (Vyloy) expansions","Claudin18.2 antibody","Gastric cancer (approved Oct 2024), pancreatic","Oncology","Approved (recent)","—","Pancreatic Ph2","2","",None,""),
("Astellas","ALPMY","OTC","ADR","Japan","Mid ($10-100bn)","Avacincaptad pegol (Izervay) / AT-132","—","GA, XLMTM","Ophthalmology","Approved (recent)","—","","2","",None,""),
("Daiichi Sankyo","DSNKY","OTC","ADR","Japan","Mid ($10-100bn)","Ifinatamab deruxtecan (I-DXd, w/ Merck)","B7-H3 ADC","ES-SCLC","Oncology","NDA/BLA under review","Breakthrough, Orphan","IDeate-Lung01 basis; BLA accepted 2025-26","3","SCLC 2L+ $3bn",None,""),
("Daiichi Sankyo","DSNKY","OTC","ADR","Japan","Mid ($10-100bn)","Patritumab deruxtecan (HER3-DXd, w/ Merck)","HER3 ADC","EGFRm NSCLC","Oncology","NDA/BLA under review (CRL history)","Breakthrough","CRL Jun 2024 (manufacturing); HERTHENA-Lung02 OS not significant; path uncertain","3","",40,""),
("Daiichi Sankyo","DSNKY","OTC","ADR","Japan","Mid ($10-100bn)","Enhertu DESTINY-Breast09/11","HER2 ADC","1L HER2+ MBC; neoadjuvant","Oncology","NDA/BLA under review","Breakthrough","sBLA decisions 2026","15","Enhertu peak $15bn+",None,"Partner AstraZeneca"),
("Argenx","ARGX","NASDAQ","ADR","Netherlands","Mid ($10-100bn)","Vyvgart (efgartigimod) PFS & new indications","FcRn blocker","gMG, CIDP (approved); ocular MG, myositis, TED, Sjogren's","Immunology","Phase 3","Orphan","PFS approved Apr 2025; myositis/TED Ph3 readouts 2026","10","Vyvgart peak $10bn+",None,""),
("Argenx","ARGX","NASDAQ","ADR","Netherlands","Mid ($10-100bn)","Empasiprubart","C2 antibody","MMN, CIDP, DGF","Immunology","Phase 3","Orphan","MMN Ph3 readout 2026","2","",None,""),
("Alnylam","ALNY","NASDAQ","US common","US","Mid ($10-100bn)","Amvuttra (vutrisiran) ATTR-CM","TTR siRNA","ATTR cardiomyopathy","Cardiovascular","Approved (recent)","—","Approved Mar 2025 (HELIOS-B)","10","ATTR-CM $10bn+ (vs tafamidis, acoramidis)",None,""),
("Alnylam","ALNY","NASDAQ","US common","US","Mid ($10-100bn)","Nucresiran","Next-gen TTR siRNA (biannual/annual)","ATTR","Cardiovascular","Phase 3","—","TRITON-CM Ph3 started 2025","10","",None,""),
("Alnylam","ALNY","NASDAQ","US common","US","Mid ($10-100bn)","Zilebesiran (w/ Roche)","Angiotensinogen siRNA","Hypertension (CV outcomes)","Cardiovascular","Phase 3","—","ZENITH outcomes trial; readout ~2028","10","Twice-yearly antihypertensive; large TAM",None,""),
("Alnylam","ALNY","NASDAQ","US common","US","Mid ($10-100bn)","Mivelsiran","APP siRNA","CAA, Alzheimer's","Neurology","Phase 2","—","Ph2 data 2026","3","",None,""),
("BioNTech","BNTX","NASDAQ","ADR","Germany","Mid ($10-100bn)","Pumitamig (BNT327, w/ BMS)","PD-L1 x VEGF-A bispecific","SCLC, NSCLC, TNBC","Oncology","Phase 3","—","ROSETTA Ph3 readouts 2026-27","20","PD-1/VEGF bispecific class could challenge $40bn PD-1 market",None,"BMS paid $1.5bn upfront (Jun 2025)"),
("BioNTech","BNTX","NASDAQ","ADR","Germany","Mid ($10-100bn)","Autogene cevumeran (w/ Genentech)","Individualized mRNA neoantigen vaccine","Adjuvant pancreatic cancer, CRC","Oncology","Phase 2","—","Ph2 IMCODE003 readout 2026","5","",None,""),
("BioNTech","BNTX","NASDAQ","ADR","Germany","Mid ($10-100bn)","Trastuzumab pamirtecan (BNT323/DB-1303, w/ DualityBio)","HER2 ADC","HER2+ endometrial, HR+/HER2-low BC","Oncology","Phase 3","Breakthrough","Endometrial BLA possible 2026","3","",None,""),
("CSL","CSLLY","OTC","ADR","Australia","Mid ($10-100bn)","Garadacimab (Andembry)","FXIIa antibody","Hereditary angioedema prophylaxis","Rare disease","Approved (recent)","Orphan","Approved Jun 2025","3","HAE $3-4bn",None,""),
("CSL","CSLLY","OTC","ADR","Australia","Mid ($10-100bn)","Clazakizumab","IL-6 antibody","CV risk in dialysis (POSIBIL6ESKD)","Cardiovascular","Phase 3","—","Readout 2027","3","",None,""),
("UCB","UCBJY","OTC","ADR","Belgium","Mid ($10-100bn)","Bimzelx (bimekizumab) HS & expansions","IL-17A/F antibody","HS (approved Nov 2024), further","Immunology","Approved (recent)","—","","6","",None,""),
("UCB","UCBJY","OTC","ADR","Belgium","Mid ($10-100bn)","Fenfluramine / Staccato alprazolam / bepranemab","Various","Epilepsy, Alzheimer's (tau)","Neurology","Phase 2","—","Bepranemab Ph2 mixed 2024; Ph3 planning","5","",None,""),
("Novo Holdings/Others - skip","","","","","","","","","","","","","","",None,""),
# ---------------- MID / SMALL CAP US BIOTECH ----------------
("Madrigal Pharmaceuticals","MDGL","NASDAQ","US common","US","Mid ($10-100bn)","Rezdiffra (resmetirom) compensated cirrhosis (F4c)","THR-beta agonist","MASH F4c","Hepatology","Phase 3","Breakthrough","MAESTRO-NASH OUTCOMES readout 2027","10","MASH $10-15bn; Rezdiffra F2-F3 approved Mar 2024",None,""),
("Insmed","INSM","NASDAQ","US common","US","Mid ($10-100bn)","Brinsupri (brensocatib)","DPP1 inhibitor","Non-CF bronchiectasis","Respiratory","Approved (recent)","Breakthrough","Approved Aug 12 2025; CRSsNP Ph2 positive; HS Ph2","5","NCFB no prior therapy; $5bn+ peak",None,""),
("Insmed","INSM","NASDAQ","US common","US","Mid ($10-100bn)","TPIP (treprostinil palmitil inhalation powder)","Prostanoid, once daily","PAH, PH-ILD","Cardiovascular","Phase 3","Orphan","Ph2b PAH positive (Jun 2025); Ph3 2026","3","",None,""),
("Cytokinetics","CYTK","NASDAQ","US common","US","Mid ($10-100bn)","Aficamten (Myqorzo)","Cardiac myosin inhibitor","Obstructive HCM","Cardiovascular","Approved (recent)","Breakthrough, Orphan","Approved Dec 2025 (PDUFA Dec 26 2025) - verify; nHCM ACACIA Ph3 2026","4","HCM $4-5bn (vs Camzyos)",None,""),
("Cytokinetics","CYTK","NASDAQ","US common","US","Mid ($10-100bn)","Omecamtiv mecarbil","Cardiac myosin activator","HFrEF","Cardiovascular","Phase 3","—","COMET-HF Ph3 readout 2027","3","",40,"Prior CRL 2023"),
("Summit Therapeutics","SMMT","NASDAQ","US common","US","Mid ($10-100bn)","Ivonescimab (w/ Akeso)","PD-1 x VEGF bispecific","EGFRm NSCLC post-TKI (HARMONi), 1L PD-L1+ NSCLC (HARMONi-3)","Oncology","NDA/BLA under review","Fast Track","HARMONi OS not stat-sig (May 2025); BLA submitted late 2025; HARMONi-3 2026-27","20","PD-1/VEGF class",55,"OS immaturity is key FDA risk"),
("Viking Therapeutics","VKTX","NASDAQ","US common","US","Small ($1-10bn)","VK2735 (SC & oral)","GLP-1/GIP dual agonist","Obesity","Metabolic/Obesity","Phase 3","—","VANQUISH Ph3 SC readouts 2026; oral Ph2 (Aug 2025) high dropout","150","",None,"Oral tolerability concern"),
("Structure Therapeutics","GPCR","NASDAQ","ADR","US/China","Small ($1-10bn)","Aleniglipron (GSBR-1290)","Oral small-molecule GLP-1","Obesity","Metabolic/Obesity","Phase 2","—","ACCESS Ph2b readout late 2025","150","",None,""),
("Arrowhead Pharmaceuticals","ARWR","NASDAQ","US common","US","Small ($1-10bn)","Plozasiran (Redemplo)","APOC3 siRNA","FCS (approved Nov 2025); sHTG (SHASTA-3/4)","Cardiovascular","Approved (recent)","Breakthrough, Orphan","sHTG Ph3 readouts 2026; sNDA","3","sHTG ~3m US pts; $3bn",None,""),
("Ionis Pharmaceuticals","IONS","NASDAQ","US common","US","Small ($1-10bn)","Olezarsen (Tryngolza)","APOC3 antisense","FCS approved Dec 2024; sHTG (CORE/CORE2 positive Sep 2025)","Cardiovascular","NDA/BLA under review","Breakthrough, Orphan","sHTG sNDA filed late 2025; decision 2026","3","",None,""),
("Ionis Pharmaceuticals","IONS","NASDAQ","US common","US","Small ($1-10bn)","Donidalorsen (Dawnzera)","Prekallikrein antisense","HAE prophylaxis","Rare disease","Approved (recent)","Orphan","Approved Aug 2025","3","",None,""),
("Ionis Pharmaceuticals","IONS","NASDAQ","US common","US","Small ($1-10bn)","Zilganersen","GFAP antisense","Alexander disease","Rare disease","Phase 3","Orphan","Positive Ph3 (Sep 2025); NDA 2026","0.3","Ultra-rare",None,""),
("Ionis Pharmaceuticals","IONS","NASDAQ","US common","US","Small ($1-10bn)","Ulefnersen","FUS antisense","FUS-ALS","Neurology","Phase 3","Orphan","Ph3 readout 2026","0.3","",None,""),
("Sarepta Therapeutics","SRPT","NASDAQ","US common","US","Small ($1-10bn)","Elevidys (delandistrogene) label / safety","Micro-dystrophin gene therapy","DMD","Rare disease","Approved (recent)","Orphan","Non-ambulatory label paused after deaths (2025); black box; ENVISION Ph3","3","",None,"High regulatory & safety risk"),
("Sarepta Therapeutics","SRPT","NASDAQ","US common","US","Small ($1-10bn)","SRP-1003 / siRNA (w/ Arrowhead)","siRNA","FSHD, DM1","Rare disease","Phase 1/2","Orphan","Data 2026","2","",None,""),
("BridgeBio Pharma","BBIO","NASDAQ","US common","US","Small ($1-10bn)","Attruby (acoramidis)","TTR stabilizer","ATTR-CM","Cardiovascular","Approved (recent)","Orphan","Approved Nov 2024; launch ramp","10","",None,""),
("BridgeBio Pharma","BBIO","NASDAQ","US common","US","Small ($1-10bn)","Encaleret","CaSR antagonist","ADH1 (hypoparathyroidism)","Endocrinology","NDA/BLA under review","Orphan, Breakthrough","CALIBRATE Ph3 positive (Jul 2025); NDA filed; decision 2026","1","",None,""),
("BridgeBio Pharma","BBIO","NASDAQ","US common","US","Small ($1-10bn)","Infigratinib","FGFR1-3 inhibitor","Achondroplasia","Rare disease","Phase 3","Orphan, Breakthrough","PROPEL 3 Ph3 readout late 2025/early 2026","2","Achondroplasia $2bn+ (vs Voxzogo)",None,""),
("BridgeBio Pharma","BBIO","NASDAQ","US common","US","Small ($1-10bn)","BBP-418","Glycosylation substrate","LGMD2I/R9","Rare disease","Phase 3","Orphan","FORTIFY interim 2025-26; accelerated approval path","1","",None,""),
("Ascendis Pharma","ASND","NASDAQ","ADR","Denmark","Small ($1-10bn)","TransCon CNP (navepegritide, Palsonify)","Long-acting CNP","Achondroplasia","Rare disease","Approved (recent)","Orphan","Approved Nov 2025 (after PDUFA extension)","2","",None,""),
("Ascendis Pharma","ASND","NASDAQ","ADR","Denmark","Small ($1-10bn)","Yorvipath (palopegteriparatide)","Long-acting PTH","Hypoparathyroidism","Endocrinology","Approved (recent)","Orphan","Approved Aug 2024; ramp","2","",None,""),
("Ascendis Pharma","ASND","NASDAQ","ADR","Denmark","Small ($1-10bn)","TransCon hGH + CNP combo","—","Achondroplasia","Rare disease","Phase 2","Orphan","","1","",None,""),
("Apellis Pharmaceuticals","APLS","NASDAQ","US common","US","Small ($1-10bn)","Empaveli (pegcetacoplan) C3G/IC-MPGN","C3 inhibitor","C3G / IC-MPGN","Nephrology","Approved (recent)","Orphan","Approved Jul 2025 (VALIANT)","1.5","",None,""),
("Amicus Therapeutics","FOLD","NASDAQ","US common","US","Small ($1-10bn)","Pombiliti+Opfolda expansions","ERT + chaperone","Late-onset Pompe","Rare disease","Approved (recent)","Orphan","","1","",None,""),
("Axsome Therapeutics","AXSM","NASDAQ","US common","US","Small ($1-10bn)","AXS-05 (Auvelity) Alzheimer's agitation","NMDA antagonist / bupropion","AD agitation","CNS/Psychiatry","NDA/BLA under review","Breakthrough","sNDA filed 2025; FDA decision 2026","3","AD agitation $3bn",None,"One of three Ph3 missed"),
("Axsome Therapeutics","AXSM","NASDAQ","US common","US","Small ($1-10bn)","AXS-07 (Symbravo)","Meloxicam + rizatriptan","Acute migraine","Neurology","Approved (recent)","—","Approved Jan 2025","1","",None,""),
("Axsome Therapeutics","AXSM","NASDAQ","US common","US","Small ($1-10bn)","AXS-12 (reboxetine)","NRI","Narcolepsy (cataplexy)","Neurology","NDA/BLA under review","Orphan","NDA filed 2025","1","",None,""),
("Axsome Therapeutics","AXSM","NASDAQ","US common","US","Small ($1-10bn)","AXS-14 (esreboxetine)","NRI","Fibromyalgia","Neurology","NDA/BLA under review","—","NDA filing 2025-26","2","",None,""),
("Intra-Cellular (acq. by J&J 2025) - see JNJ","","","","","","","","","","","","","","",None,""),
("Neurocrine Biosciences","NBIX","NASDAQ","US common","US","Mid ($10-100bn)","Osavampator (NBI-1065845)","AMPA PAM","Major depressive disorder (adjunct)","CNS/Psychiatry","Phase 3","—","Ph3 started 2025; readout 2027","5","",None,""),
("Neurocrine Biosciences","NBIX","NASDAQ","US common","US","Mid ($10-100bn)","Crinecerfont (Crenessity)","CRF1 antagonist","Congenital adrenal hyperplasia","Endocrinology","Approved (recent)","Orphan, Breakthrough","Approved Dec 2024","1.5","",None,""),
("Neurocrine Biosciences","NBIX","NASDAQ","US common","US","Mid ($10-100bn)","NBI-1117568","M4 agonist","Schizophrenia","CNS/Psychiatry","Phase 3","—","Ph3 started 2025","6","",None,""),
("Alkermes","ALKS","NASDAQ","US common","Ireland/US","Small ($1-10bn)","Alixorexton (ALKS 2680)","Orexin-2 agonist","Narcolepsy type 1/2, IH","Neurology","Phase 3","Orphan","Vibrance-1 Ph2 positive (Jul 2025); Ph3 2026","3","Orexin class",None,""),
("Alkermes","ALKS","NASDAQ","US common","Ireland/US","Small ($1-10bn)","Avadel LUMRYZ (acq. 2025)","Once-nightly sodium oxybate","Narcolepsy","Neurology","Approved (recent)","Orphan","IH sNDA","1.5","",None,"Avadel acquisition"),
("Jazz Pharmaceuticals","JAZZ","NASDAQ","US common","Ireland","Small ($1-10bn)","Zanidatamab (Ziihera)","HER2 bispecific","BTC approved Nov 2024; GEA 1L (HERIZON-GEA-01 positive 2025)","Oncology","NDA/BLA under review","Breakthrough","GEA sBLA 2026","2","",None,""),
("Jazz Pharmaceuticals","JAZZ","NASDAQ","US common","Ireland","Small ($1-10bn)","Dordaviprone (Modeyso)","Imipridone","H3 K27M diffuse midline glioma","Oncology","Approved (recent)","Orphan, Breakthrough","Accelerated approval Aug 2025 (from Chimerix)","0.5","",None,""),
("Exelixis","EXEL","NASDAQ","US common","US","Small ($1-10bn)","Zanzalintinib","Multi-TKI (MET/VEGFR/AXL)","mCRC (STELLAR-303 positive), RCC, NET","Oncology","NDA/BLA under review","—","NDA filed 2025; FDA decision 2026","2","",None,""),
("Exelixis","EXEL","NASDAQ","US common","US","Small ($1-10bn)","Cabometyx NET","Multi-TKI","Neuroendocrine tumors","Oncology","Approved (recent)","—","Approved Mar 2025","1","",None,""),
("Incyte","INCY","NASDAQ","US common","US","Mid ($10-100bn)","Povorcitinib","Oral JAK1 inhibitor","Hidradenitis suppurativa, vitiligo, PN","Immunology","Phase 3","—","STOP-HS positive (Mar 2025); NDA 2026","3","",None,""),
("Incyte","INCY","NASDAQ","US common","US","Mid ($10-100bn)","INCA033989","Mutant CALR antibody","Myelofibrosis / ET","Hematology","Phase 2","—","Data 2025-26","3","",None,""),
("Incyte","INCY","NASDAQ","US common","US","Mid ($10-100bn)","Tafasitamab (Monjuvi) FL","CD19 antibody","Follicular lymphoma","Hematology","Approved (recent)","—","Approved Jun 2025 (inMIND)","1","",None,""),
("United Therapeutics","UTHR","NASDAQ","US common","US","Mid ($10-100bn)","Ralinepag","Oral IP receptor agonist","PAH","Cardiovascular","Phase 3","Orphan","ADVANCE OUTCOMES readout 2026","3","",None,""),
("United Therapeutics","UTHR","NASDAQ","US common","US","Mid ($10-100bn)","Tyvaso (TETON IPF)","Inhaled treprostinil","Idiopathic pulmonary fibrosis","Respiratory","NDA/BLA under review","Orphan","TETON-2 positive (Sep 2025); sNDA 2026","4","IPF $4bn+",None,""),
("Ultragenyx","RARE","NASDAQ","US common","US","Small ($1-10bn)","UX111 (ABO-102)","AAV gene therapy","MPS IIIA (Sanfilippo A)","Rare disease","NDA/BLA under review (CRL history)","Orphan, RMAT","CRL Jul 2025 (CMC); resubmission; decision 2026","0.5","",None,""),
("Ultragenyx","RARE","NASDAQ","US common","US","Small ($1-10bn)","Setrusumab (w/ Mereo)","Sclerostin antibody","Osteogenesis imperfecta","Rare disease","Phase 3","Orphan","Orbit/Cosmic Ph3 readout late 2025","2","",None,""),
("Ultragenyx","RARE","NASDAQ","US common","US","Small ($1-10bn)","DTX401","AAV gene therapy","GSDIa","Rare disease","NDA/BLA under review","Orphan","BLA filed 2025","0.5","",None,""),
("Ultragenyx","RARE","NASDAQ","US common","US","Small ($1-10bn)","GTX-102","Antisense","Angelman syndrome","Rare disease","Phase 3","Orphan","Aspire Ph3 readout 2026","2","",None,""),
("Ionis/Biogen etc. see individual","","","","","","","","","","","","","","",None,""),
("Biogen","BIIB","NASDAQ","US common","US","Mid ($10-100bn)","Felzartamab","CD38 antibody","Antibody-mediated rejection, IgAN, PMN","Nephrology","Phase 3","Breakthrough, Orphan","Ph3 readouts 2026-27","3","",None,"From HI-Bio"),
("Biogen","BIIB","NASDAQ","US common","US","Mid ($10-100bn)","Salanersen (BIIB115)","Next-gen SMN2 antisense","SMA","Rare disease","Phase 3","Orphan","Ph3 start 2025-26","3","",None,""),
("Biogen","BIIB","NASDAQ","US common","US","Mid ($10-100bn)","Leqembi SC autoinjector (w/ Eisai)","Anti-amyloid antibody","Early Alzheimer's","Neurology","Approved (recent)","—","SC maintenance approved Aug 2025; SC initiation filed","10","",None,""),
("Biogen","BIIB","NASDAQ","US common","US","Mid ($10-100bn)","Litifilimab","BDCA2 antibody","SLE, CLE","Immunology","Phase 3","—","TOPAZ readouts 2026-27","3","",None,""),
("Biogen","BIIB","NASDAQ","US common","US","Mid ($10-100bn)","Zorevunersen (w/ Stoke)","SCN1A antisense","Dravet syndrome","Neurology","Phase 3","Orphan, Breakthrough","EMPEROR Ph3 readout 2027","2","",None,""),
("Moderna","MRNA","NASDAQ","US common","US","Small ($1-10bn)","mRNA-4157 / intismeran (w/ Merck)","Individualized neoantigen therapy","Adjuvant melanoma, NSCLC","Oncology","Phase 3","Breakthrough","INTerpath-001 melanoma readout 2026","5","",None,""),
("Moderna","MRNA","NASDAQ","US common","US","Small ($1-10bn)","mRNA-1010 flu / mRNA-1083 flu+COVID","mRNA vaccines","Seasonal influenza","Infectious disease/Vaccine","NDA/BLA under review","—","mRNA-1010 P304 positive (Jun 2025); BLA; combo withdrawn pending flu efficacy","5","Flu vaccine $7bn",60,"FDA vaccine policy uncertainty"),
("Moderna","MRNA","NASDAQ","US common","US","Small ($1-10bn)","mNEXSPIKE (mRNA-1283)","Next-gen COVID vaccine","COVID-19 (65+ / high risk)","Infectious disease/Vaccine","Approved (recent)","—","Approved May 2025 (restricted)","3","",None,""),
("Moderna","MRNA","NASDAQ","US common","US","Small ($1-10bn)","mRNA-3927","Propionic acidemia mRNA therapy","Propionic acidemia","Rare disease","Phase 1/2","Orphan","Pivotal 2026","0.3","",None,""),
("Novavax","NVAX","NASDAQ","US common","US","Micro (<$1bn)","Nuvaxovid","Protein COVID vaccine","COVID-19","Infectious disease/Vaccine","Approved (recent)","—","Full BLA approved May 2025 (restricted; Sanofi partnered)","1","",None,""),
("Vaxcyte","PCVX","NASDAQ","US common","US","Small ($1-10bn)","VAX-31","31-valent pneumococcal conjugate vaccine","Pneumococcal disease (adults, infants)","Infectious disease/Vaccine","Phase 3","Breakthrough","Adult Ph3 started 2025; infant Ph2 data 2026","10","PCV market $8-10bn (Prevnar)",None,""),
("Vaxcyte","PCVX","NASDAQ","US common","US","Small ($1-10bn)","VAX-24","24-valent PCV","Pneumococcal (infants)","Infectious disease/Vaccine","Phase 2","Breakthrough","Infant Ph2 topline mid-2025 mixed","10","",None,""),
("Madrigal/Akero/89bio (acq. by Roche 2025) - see Roche","","","","","","","","","","","","","","",None,""),
("Akero Therapeutics (acq. by Novo Nordisk, 2025)","","","","","","","","","","","","","","",None,""),
("Rhythm Pharmaceuticals","RYTM","NASDAQ","US common","US","Small ($1-10bn)","Imcivree (setmelanotide) hypothalamic obesity","MC4R agonist","Acquired hypothalamic obesity","Metabolic/Obesity","NDA/BLA under review","Breakthrough, Orphan","TRANSCEND Ph3 positive (Apr 2025); PDUFA Dec 20 2025 (extended) - verify","1.5","",None,""),
("Rhythm Pharmaceuticals","RYTM","NASDAQ","US common","US","Small ($1-10bn)","Bivamelagon (oral MC4R)","Oral MC4R agonist","Hypothalamic obesity","Metabolic/Obesity","Phase 2","—","Ph2 positive (Jul 2025); Ph3 2026","1.5","",None,""),
("Soleno Therapeutics","SLNO","NASDAQ","US common","US","Small ($1-10bn)","Vykat XR (DCCR)","K-ATP channel opener","Prader-Willi hyperphagia","Rare disease","Approved (recent)","Orphan","Approved Mar 2025","1","",None,""),
("Krystal Biotech","KRYS","NASDAQ","US common","US","Small ($1-10bn)","KB407 / KB408","Inhaled HSV-1 gene therapy","Cystic fibrosis, AATD","Rare disease","Phase 1/2","Orphan","Data 2026","2","",None,""),
("Krystal Biotech","KRYS","NASDAQ","US common","US","Small ($1-10bn)","Vyjuvek ophthalmic (B-VEC eye drops)","HSV-1 gene therapy","DEB ocular complications","Rare disease","Phase 3","Orphan","Filing 2026","0.5","",None,""),
("Blueprint Medicines (acq. by Sanofi Jul 2025) - see SNY","","","","","","","","","","","","","","",None,""),
("Revolution Medicines","RVMD","NASDAQ","US common","US","Mid ($10-100bn)","Daraxonrasib (RMC-6236)","RAS(ON) multi-selective inhibitor","2L PDAC (RASolute 302), 1L PDAC, NSCLC","Oncology","Phase 3","Breakthrough","RASolute 302 readout 2026","10","Pancreatic cancer no effective 2L; RAS class $10bn+",None,"Highest-profile oncology readout of 2026"),
("Revolution Medicines","RVMD","NASDAQ","US common","US","Mid ($10-100bn)","Elironrasib (RMC-6291) / Zoldonrasib (RMC-9805)","KRAS G12C / G12D (ON) inhibitors","NSCLC, PDAC","Oncology","Phase 2","Breakthrough","Registrational data 2026-27","5","",None,""),
("Arvinas","ARVN","NASDAQ","US common","US","Small ($1-10bn)","Vepdegestrant (w/ Pfizer)","PROTAC ER degrader","ESR1m ER+ BC","Oncology","NDA/BLA under review","Fast Track","PDUFA Jun 5 2026","3","",None,"Seeking commercialization partner"),
("Arcellx","ACLX","NASDAQ","US common","US","Small ($1-10bn)","Anito-cel (w/ Gilead/Kite)","BCMA CAR-T","R/R MM","Hematology","NDA/BLA under review","Breakthrough, Orphan","FDA decision 2026","4","",None,""),
("Protagonist Therapeutics","PTGX","NASDAQ","US common","US","Small ($1-10bn)","Rusfertide (w/ Takeda)","Hepcidin mimetic","Polycythemia vera","Hematology","NDA/BLA under review","Breakthrough, Orphan","FDA decision 2026","1.5","",None,""),
("Protagonist Therapeutics","PTGX","NASDAQ","US common","US","Small ($1-10bn)","Icotrokinra (w/ J&J)","Oral IL-23R antagonist","Psoriasis, UC","Immunology","NDA/BLA under review","—","Royalty/milestone exposure","10","",None,""),
("Protagonist Therapeutics","PTGX","NASDAQ","US common","US","Small ($1-10bn)","PN-477","Oral GLP-1/GIP/glucagon triple agonist","Obesity","Metabolic/Obesity","Phase 1","—","Ph1 data 2026","150","",None,""),
("Cerevel/Karuna - acquired; see ABBV/BMY","","","","","","","","","","","","","","",None,""),
("Denali Therapeutics","DNLI","NASDAQ","US common","US","Small ($1-10bn)","Tividenofusp alfa (DNL310)","Enzyme transport vehicle IDS","Hunter syndrome (MPS II)","Rare disease","NDA/BLA under review","Breakthrough, Orphan","PDUFA Jan 5 2026 (extended) - verify","1","",None,"Accelerated approval on CSF HS biomarker"),
("Denali Therapeutics","DNLI","NASDAQ","US common","US","Small ($1-10bn)","DNL126","ETV:SGSH","MPS IIIA","Rare disease","Phase 1/2","Orphan","Accelerated approval path 2026-27","0.5","",None,""),
("Praxis Precision Medicines","PRAX","NASDAQ","US common","US","Small ($1-10bn)","Ulixacaltamide","T-type Ca channel blocker","Essential tremor","Neurology","NDA/BLA under review","—","Essential3 positive (2025); NDA 2026","3","ET ~7m US patients; no new drug in decades",None,""),
("Praxis Precision Medicines","PRAX","NASDAQ","US common","US","Small ($1-10bn)","Relutrigine (PRAX-562)","NaV persistent current blocker","DEE (SCN2A/SCN8A)","Neurology","Phase 3","Orphan, Breakthrough","EMBOLD registrational 2026","1","",None,""),
("Praxis Precision Medicines","PRAX","NASDAQ","US common","US","Small ($1-10bn)","Vormatrigine","NaV blocker","Focal epilepsy","Neurology","Phase 3","—","POWER1 readout 2026","3","",None,""),
("Cytokinetics/Others","","","","","","","","","","","","","","",None,""),
("Milestone Pharmaceuticals","MIST","NASDAQ","US common","Canada","Micro (<$1bn)","Cardamyst (etripamil nasal spray)","Nasal calcium channel blocker","PSVT","Cardiovascular","Approved (recent)","—","Approved Dec 2025 after 2 CRLs - verify","1","",None,""),
("Corcept Therapeutics","CORT","NASDAQ","US common","US","Small ($1-10bn)","Relacorilant","Selective GR antagonist","Cushing's syndrome; platinum-resistant ovarian cancer","Endocrinology","NDA/BLA under review (CRL history)","Orphan","Cushing's PDUFA Dec 30 2025 - verify; ovarian (ROSELLA) NDA 2025-26","2","Cushing's $2bn (Korlym franchise)",None,""),
("Travere Therapeutics","TVTX","NASDAQ","US common","US","Small ($1-10bn)","Filspari (sparsentan) FSGS","Dual ET/AT1 antagonist","FSGS","Nephrology","NDA/BLA under review","Orphan","sNDA PDUFA Jan 13 2026 - verify","1.5","FSGS no approved therapy",None,""),
("Travere Therapeutics","TVTX","NASDAQ","US common","US","Small ($1-10bn)","Pegtibatinase","Enzyme therapy","Classical homocystinuria","Rare disease","Phase 3","Orphan, Breakthrough","HARMONY Ph3 restarted 2025","0.5","",None,""),
("Vera Therapeutics","VERA","NASDAQ","US common","US","Small ($1-10bn)","Atacicept","BAFF/APRIL fusion protein","IgA nephropathy","Nephrology","NDA/BLA under review","Breakthrough","ORIGIN 3 positive (Jun 2025); BLA filed; accelerated approval decision 2026","5","",None,""),
("Otsuka Holdings","OTSKY","OTC","ADR","Japan","Mid ($10-100bn)","Sibeprenlimab (Voyxact)","APRIL antibody","IgA nephropathy","Nephrology","Approved (recent)","Breakthrough","Approved Nov 2025 (accelerated) - verify","5","",None,""),
("Kymera Therapeutics","KYMR","NASDAQ","US common","US","Small ($1-10bn)","KT-621","Oral STAT6 degrader","Atopic dermatitis, asthma","Immunology","Phase 2","—","BROADEN2 AD Ph2b readout 2026","15","Oral Dupixent-like",None,""),
("Kymera Therapeutics","KYMR","NASDAQ","US common","US","Small ($1-10bn)","KT-474 (w/ Sanofi)","IRAK4 degrader","HS, AD","Immunology","Phase 2","—","Ph2 readouts 2026","5","",None,""),
("Nuvalent","NUVL","NASDAQ","US common","US","Small ($1-10bn)","Zidesamtinib","ROS1 TKI","ROS1+ NSCLC","Oncology","NDA/BLA under review","Breakthrough, Orphan","NDA filed 2025; PDUFA Sep 18 2026","1","ROS1+ NSCLC ~$1bn",None,""),
("Nuvalent","NUVL","NASDAQ","US common","US","Small ($1-10bn)","Neladalkib","ALK TKI","ALK+ NSCLC (TKI-pretreated & 1L ALKAZAR)","Oncology","Phase 3","Breakthrough","Pivotal data 2025-26; NDA 2026","3","ALK+ NSCLC $3-4bn",None,""),
("Immunovant","IMVT","NASDAQ","US common","US","Small ($1-10bn)","IMVT-1402 / batoclimab","FcRn antibodies","Graves' disease, MG, CIDP","Immunology","Phase 3","—","Graves' pivotal 2026","5","",None,"Roivant subsidiary"),
("Roivant Sciences","ROIV","NASDAQ","US common","UK/US","Small ($1-10bn)","Brepocitinib","TYK2/JAK1 inhibitor","Dermatomyositis, NIU","Immunology","NDA/BLA under review","Orphan","VALOR Ph3 positive (May 2025); NDA 2026","2","",None,"Via Priovant"),
("Madrigal/others end","","","","","","","","","","","","","","",None,""),
("Iovance Biotherapeutics","IOVA","NASDAQ","US common","US","Micro (<$1bn)","Amtagvi (lifileucel) NSCLC","TIL therapy","Advanced NSCLC","Oncology","Phase 2","RMAT","Registrational TILVANCE-301 readout 2026","2","",None,""),
("Geron","GERN","NASDAQ","US common","US","Micro (<$1bn)","Rytelo (imetelstat) MF","Telomerase inhibitor","Myelofibrosis (relapsed)","Hematology","Phase 3","Orphan","IMpactMF interim 2026","1.5","",None,""),
("Syndax Pharmaceuticals","SNDX","NASDAQ","US common","US","Small ($1-10bn)","Revuforj (revumenib) expansions","Menin inhibitor","NPM1m AML (approved Oct 2025), combos","Hematology","Approved (recent)","Orphan, Breakthrough","1L combos Ph3","2","",None,""),
("Kura Oncology","KURA","NASDAQ","US common","US","Micro (<$1bn)","Ziftomenib (Komzifti)","Menin inhibitor","NPM1m R/R AML","Hematology","Approved (recent)","Orphan, Breakthrough","Approved Nov 2025 - verify; combo Ph3","2","",None,"Partner Kyowa Kirin"),
("Disc Medicine","IRON","NASDAQ","US common","US","Small ($1-10bn)","Bitopertin","GlyT1 inhibitor","Erythropoietic protoporphyria","Rare disease","NDA/BLA under review","Breakthrough, Orphan","Accelerated approval NDA filed 2025; PDUFA 2026","1","",None,"FDA priority voucher program"),
("Scholar Rock","SRRK","NASDAQ","US common","US","Small ($1-10bn)","Apitegromab","Myostatin antibody","Spinal muscular atrophy","Rare disease","NDA/BLA under review (CRL history)","Orphan, Breakthrough","CRL Sep 2025 (third-party fill-finish site); resubmission; decision 2026","2","",None,"CRL due to manufacturing site (Catalent), not efficacy"),
("Scholar Rock","SRRK","NASDAQ","US common","US","Small ($1-10bn)","SRK-439 / apitegromab obesity","Myostatin antibody","Obesity (muscle preservation w/ tirzepatide)","Metabolic/Obesity","Phase 2","—","EMBRAZE Ph2 positive (Jun 2025)","20","",None,""),
("Capricor Therapeutics","CAPR","NASDAQ","US common","US","Micro (<$1bn)","Deramiocel (CAP-1002)","Cardiosphere-derived cells","DMD cardiomyopathy","Rare disease","NDA/BLA under review (CRL history)","Orphan, RMAT","CRL Jul 2025; HOPE-3 Ph3 topline late 2025; resubmission","1","",50,""),
("Replimune","REPL","NASDAQ","US common","US","Micro (<$1bn)","RP1 (vusolimogene oderparepvec)","Oncolytic HSV-1","Anti-PD-1-failed melanoma","Oncology","NDA/BLA under review (CRL history)","Breakthrough","CRL Jul 2025; resubmitted; PDUFA Apr 10 2026","1","",45,""),
("Stoke Therapeutics","STOK","NASDAQ","US common","US","Small ($1-10bn)","Zorevunersen (w/ Biogen)","SCN1A antisense (TANGO)","Dravet syndrome","Neurology","Phase 3","Orphan, Breakthrough","EMPEROR Ph3 readout 2027","2","",None,""),
("Cytokinetics dup end","","","","","","","","","","","","","","",None,""),
("Verona Pharma (acq. by Merck 2025) - see MRK","","","","","","","","","","","","","","",None,""),
("Legend Biotech","LEGN","NASDAQ","ADR","US/China","Small ($1-10bn)","Carvykti (cilta-cel) expansions (w/ J&J)","BCMA CAR-T","Multiple myeloma (earlier lines)","Hematology","Approved (recent)","Orphan, Breakthrough","CARTITUDE-5/6 readouts 2026-27","5","Carvykti $5bn+ peak",None,""),
("BeOne Medicines (BeiGene)","ONC","NASDAQ","ADR","Switzerland/China","Mid ($10-100bn)","Sonrotoclax","BCL2 inhibitor","R/R MCL, CLL","Hematology","NDA/BLA under review","Breakthrough, Orphan","MCL NDA accepted 2025 (priority); decision 2026","3","BCL2 class (venetoclax $2.5bn)",None,""),
("BeOne Medicines (BeiGene)","ONC","NASDAQ","ADR","Switzerland/China","Mid ($10-100bn)","BGB-16673","BTK degrader","R/R CLL","Hematology","Phase 3","Fast Track","CaDAnCe-302 Ph3 readout 2026-27","3","",None,""),
("BeOne Medicines (BeiGene)","ONC","NASDAQ","ADR","Switzerland/China","Mid ($10-100bn)","Tislelizumab (Tevimbra) expansions","PD-1","ESCC/gastric (approved), NSCLC","Oncology","Approved (recent)","—","","2","",None,""),
("Zai Lab","ZLAB","NASDAQ","ADR","China","Small ($1-10bn)","ZL-1310","DLL3 ADC","ES-SCLC","Oncology","Phase 2","Breakthrough, Orphan","Pivotal start 2025-26","2","",None,""),
("HUTCHMED","HCM","NASDAQ","ADR","Hong Kong/China","Small ($1-10bn)","Fruquintinib (Fruzaqla) expansions (w/ Takeda)","VEGFR TKI","mCRC (approved), gastric, RCC","Oncology","Approved (recent)","—","","1","",None,""),
("HUTCHMED","HCM","NASDAQ","ADR","Hong Kong/China","Small ($1-10bn)","Savolitinib (w/ AstraZeneca)","MET TKI","MET-amplified EGFRm NSCLC (SAFFRON), MET ex14","Oncology","Phase 3","Breakthrough, Fast Track","SAFFRON readout 2026; US NDA","1","",None,""),
("Akeso (via Summit) / Kelun (via Merck) - see partners","","","","","","","","","","","","","","",None,""),
("Teva Pharmaceutical","TEVA","NYSE","ADR","Israel","Mid ($10-100bn)","Duvakitug (TEV-'574, w/ Sanofi)","TL1A antibody","UC, Crohn's","Immunology","Phase 3","—","Ph3 started 2025; readouts 2027","15","TL1A class",None,""),
("Teva Pharmaceutical","TEVA","NYSE","ADR","Israel","Mid ($10-100bn)","Olanzapine LAI (TEV-749, Uzedy franchise)","Long-acting injectable","Schizophrenia","CNS/Psychiatry","NDA/BLA under review","—","SOLARIS Ph3 positive (no PDSS); NDA filed 2025; decision 2026","1.5","",None,""),
("Teva Pharmaceutical","TEVA","NYSE","ADR","Israel","Mid ($10-100bn)","Emrusolmin (TEV-56286)","Alpha-synuclein aggregation inhibitor","Multiple system atrophy","Neurology","Phase 2","Orphan","Ph2 readout 2026","1","",None,""),
("Viatris","VTRS","NASDAQ","US common","US","Small ($1-10bn)","MR-141 (phentolamine ophthalmic)","Alpha-adrenergic antagonist","Presbyopia / dim light disturbances","Ophthalmology","NDA/BLA under review","—","VEGA-3 Ph3 positive 2025; NDA 2026","1","",None,"Partner Opus Genetics"),
("Viatris","VTRS","NASDAQ","US common","US","Small ($1-10bn)","Selatogrel","P2Y12 antagonist (self-injected)","Suspected acute MI","Cardiovascular","Phase 3","—","SOS-AMI readout 2026","2","",None,"From Idorsia"),
("Viatris","VTRS","NASDAQ","US common","US","Small ($1-10bn)","Cenerimod","S1P1 modulator","Systemic lupus erythematosus","Immunology","Phase 3","—","OPUS Ph3 readouts 2026","3","",None,""),
("Organon","OGN","NYSE","US common","US","Small ($1-10bn)","Vtama (tapinarof) AD expansion","AhR agonist","Atopic dermatitis (approved Dec 2024)","Dermatology","Approved (recent)","—","","1","",None,""),
("Harmony Biosciences","HRMY","NASDAQ","US common","US","Small ($1-10bn)","Pitolisant HD / ZYN002","H3 antagonist; cannabidiol gel","Narcolepsy, IH; Fragile X","Neurology","Phase 3","Orphan","ZYN002 RECONNECT Ph3 missed (Sep 2025); pitolisant HD readouts 2026","2","",None,""),
("ACADIA Pharmaceuticals","ACAD","NASDAQ","US common","US","Small ($1-10bn)","ACP-101 (carbetocin nasal)","Oxytocin analog","Prader-Willi hyperphagia","Rare disease","Phase 3","Orphan","COMPASS PWS Ph3 readout late 2025/2026","1","",None,""),
("ACADIA Pharmaceuticals","ACAD","NASDAQ","US common","US","Small ($1-10bn)","ACP-204","5-HT2A inverse agonist","Alzheimer's disease psychosis","CNS/Psychiatry","Phase 2","—","Ph2 readout 2026","3","",None,""),
("Supernus Pharmaceuticals","SUPN","NASDAQ","US common","US","Small ($1-10bn)","Onapgo (apomorphine infusion)","Dopamine agonist SC infusion","Parkinson's motor fluctuations","Neurology","Approved (recent)","—","Approved Feb 2025","1","",None,""),
("Supernus Pharmaceuticals","SUPN","NASDAQ","US common","US","Small ($1-10bn)","SPN-820","mTORC1 activator","Treatment-resistant depression","CNS/Psychiatry","Phase 2","—","Ph2b missed (2024)","3","",10,""),
("Tonix Pharmaceuticals","TNXP","NASDAQ","US common","US","Micro (<$1bn)","Tonmya (TNX-102 SL)","Sublingual cyclobenzaprine","Fibromyalgia","Neurology","Approved (recent)","—","Approved Aug 2025","2","",None,""),
("Ardelyx","ARDX","NASDAQ","US common","US","Small ($1-10bn)","Xphozah / Ibsrela expansions","NHE3 inhibitor","Hyperphosphatemia; IBS-C","Nephrology","Approved (recent)","—","","1","",None,""),
("Cabaletta Bio","CABA","NASDAQ","US common","US","Micro (<$1bn)","Rese-cel (CABA-201)","CD19 CAR-T (autoimmune)","Myositis, lupus, SSc","Immunology","Phase 2","Fast Track, RMAT","Registrational cohort 2026","5","",None,""),
("Kiniksa Pharmaceuticals","KNSA","NASDAQ","US common","Bermuda/US","Small ($1-10bn)","KPL-387","IL-1R monthly antibody","Recurrent pericarditis","Cardiovascular","Phase 2/3","Orphan","Ph2/3 2026","1","",None,""),
("Ascendis dup end","","","","","","","","","","","","","","",None,""),
("Insmed dup end","","","","","","","","","","","","","","",None,""),
("Intellia Therapeutics","NTLA","NASDAQ","US common","US","Micro (<$1bn)","Lonvoguran ziclumeran (lonvo-z, NTLA-2002)","In vivo CRISPR KLKB1","Hereditary angioedema","Rare disease","Phase 3","Orphan, Breakthrough, RMAT","HAELO Ph3 readout 2026; BLA 2026-27","3","",None,""),
("Intellia Therapeutics","NTLA","NASDAQ","US common","US","Micro (<$1bn)","Nexiguran ziclumeran (nex-z, w/ Regeneron)","In vivo CRISPR TTR","ATTR-CM / PN","Cardiovascular","Phase 3","Orphan, RMAT","MAGNITUDE paused (Oct 2025) after liver toxicity; clinical hold","10","",25,"Safety event Oct 2025"),
("CRISPR Therapeutics","CRSP","NASDAQ","US common","Switzerland","Small ($1-10bn)","CTX310","In vivo CRISPR ANGPTL3","Hypertriglyceridemia / ASCVD","Cardiovascular","Phase 1","—","Data 2025-26","5","",None,""),
("CRISPR Therapeutics","CRSP","NASDAQ","US common","Switzerland","Small ($1-10bn)","Casgevy (w/ Vertex)","Ex vivo CRISPR","SCD / TDT","Hematology","Approved (recent)","Orphan","Ramp; pediatric 5-11 filing","3","",None,""),
("Beam Therapeutics","BEAM","NASDAQ","US common","US","Small ($1-10bn)","BEAM-101","Base-edited HSC","Sickle cell disease","Hematology","Phase 1/2","Orphan, RMAT","BLA planned 2026-27","3","",None,""),
("Beam Therapeutics","BEAM","NASDAQ","US common","US","Small ($1-10bn)","BEAM-302","In vivo base editing SERPINA1","AATD","Rare disease","Phase 1/2","Orphan","Ph1/2 positive (Mar 2025); pivotal 2026","2","",None,""),
("Verve Therapeutics (acq. by Lilly Jun 2025) - see LLY","","","","","","","","","","","","","","",None,""),
("uniQure","QURE","NASDAQ","US common","Netherlands","Small ($1-10bn)","AMT-130","AAV5 miHTT gene therapy","Huntington's disease","Neurology","NDA/BLA under review","Breakthrough, Orphan, RMAT","36-mo data positive (Sep 2025); FDA disputed external control (Nov 2025); BLA path uncertain","3","HD no disease-modifying therapy",40,"Regulatory uncertainty on accelerated approval"),
("PTC Therapeutics","PTCT","NASDAQ","US common","US","Small ($1-10bn)","Vatiquinone","15-LO inhibitor","Friedreich ataxia","Rare disease","NDA/BLA under review (CRL history)","Orphan","CRL Aug 2025","0.5","",15,""),
("PTC Therapeutics","PTCT","NASDAQ","US common","US","Small ($1-10bn)","Sepiapterin (Sephience)","BH4 precursor","Phenylketonuria","Rare disease","Approved (recent)","Orphan","Approved Jul 2025","1","",None,""),
("PTC Therapeutics","PTCT","NASDAQ","US common","US","Small ($1-10bn)","Votoplam (PTC518, w/ Novartis)","HTT splicing modifier","Huntington's disease","Neurology","Phase 3","Orphan","PIVOT-HD Ph2 positive (May 2025); Ph3 2026","3","",None,""),
("Sage Therapeutics (acq. by Supernus 2025) - see SUPN","","","","","","","","","","","","","","",None,""),
("Xenon Pharmaceuticals","XENE","NASDAQ","US common","Canada","Small ($1-10bn)","Azetukalner (XEN1101)","Kv7 potassium channel opener","Focal onset seizures, PGTCS, MDD","Neurology","Phase 3","—","X-TOLE2 Ph3 readout early 2026; NDA 2026","3","Epilepsy $8bn; Kv7 class",None,""),
("Marinus / Longboard (acq.) - skip","","","","","","","","","","","","","","",None,""),
("Cytokinetics end","","","","","","","","","","","","","","",None,""),
("Mineralys Therapeutics","MLYS","NASDAQ","US common","US","Small ($1-10bn)","Lorundrostat","Aldosterone synthase inhibitor","Uncontrolled hypertension","Cardiovascular","NDA/BLA under review","—","Launch-HTN / Advance-HTN Ph3 positive (Mar 2025); NDA filed 2025; decision 2026","5","Competes with AZ baxdrostat",None,""),
("Tarsus Pharmaceuticals","TARS","NASDAQ","US common","US","Small ($1-10bn)","TP-04 / TP-05","Lotilaner","Ocular rosacea; Lyme prevention","Ophthalmology","Phase 2","—","","1","",None,"Xdemvy approved 2023"),
("Ocular Therapeutix","OCUL","NASDAQ","US common","US","Small ($1-10bn)","Axpaxli (OTX-TKI)","Axitinib intravitreal hydrogel","Wet AMD, DR","Ophthalmology","Phase 3","—","SOL-1 topline early 2026; SOL-R 2026","10","Wet AMD $10bn+ (Eylea/Vabysmo)",None,""),
("Outlook Therapeutics","OTLK","NASDAQ","US common","US","Micro (<$1bn)","ONS-5010 (Lytenava)","Ophthalmic bevacizumab","Wet AMD","Ophthalmology","NDA/BLA under review (CRL history)","—","Third CRL Aug 2025; resubmitted; PDUFA Dec 31 2025 - verify","1","",40,""),
("EyePoint Pharmaceuticals","EYPT","NASDAQ","US common","US","Small ($1-10bn)","Duravyu (vorolanib insert)","TKI intravitreal insert","Wet AMD, DME","Ophthalmology","Phase 3","—","LUGANO/LUCIA topline mid-2026","10","",None,""),
("Amylyx Pharmaceuticals","AMLX","NASDAQ","US common","US","Micro (<$1bn)","Avexitide","GLP-1 receptor antagonist","Post-bariatric hypoglycemia","Endocrinology","Phase 3","Breakthrough, Orphan","LUCIDITY Ph3 readout H1 2026","1.5","",None,""),
("Crinetics Pharmaceuticals","CRNX","NASDAQ","US common","US","Small ($1-10bn)","Paltusotine (Palsonify)","Oral SST2 agonist","Acromegaly (approved Sep 2025); carcinoid syndrome Ph3","Endocrinology","Approved (recent)","Orphan","Carcinoid CAREFNDR Ph3 readout 2026","2","",None,""),
("Crinetics Pharmaceuticals","CRNX","NASDAQ","US common","US","Small ($1-10bn)","Atumelnant","ACTH antagonist","Congenital adrenal hyperplasia, Cushing's","Endocrinology","Phase 3","Orphan","CAH Ph3 CALM-CAH 2026","2","",None,""),
("Spyre Therapeutics","SYRE","NASDAQ","US common","US","Small ($1-10bn)","SPY001/002/003 combos","Long-acting a4b7 / TL1A / IL-23","UC, Crohn's","Immunology","Phase 2","—","SKYLINE-UC Ph2 data 2026","15","",None,""),
("Abivax","ABVX","NASDAQ","ADR","France","Small ($1-10bn)","Obefazimod","miR-124 enhancer (oral)","Ulcerative colitis, Crohn's","Immunology","Phase 3","—","ABTECT induction positive (Jul 2025); maintenance data Q2 2026; NDA H2 2026","10","Oral UC $10bn segment",None,""),
("Galderma (not US-listed) skip","","","","","","","","","","","","","","",None,""),
("Ionis end","","","","","","","","","","","","","","",None,""),
("Zealand Pharma","ZLDPF","OTC","ADR","Denmark","Small ($1-10bn)","Petrelintide (w/ Roche) / dapiglutide / survodutide (BI)","Amylin analog; GLP-1/GLP-2; GLP-1/glucagon","Obesity; MASH","Metabolic/Obesity","Phase 3","—","Survodutide SYNCHRONIZE Ph3 readouts 2026 (BI partnered)","150","",None,"Boehringer not US-listed; Zealand exposure via royalties"),
("Zealand Pharma","ZLDPF","OTC","ADR","Denmark","Small ($1-10bn)","Glepaglutide","GLP-2 analog","Short bowel syndrome","Gastroenterology","NDA/BLA under review (CRL history)","Orphan","CRL Dec 2024; additional Ph3 EASE-SBS 4 2026","0.5","",40,""),
("Genmab","GMAB","NASDAQ","ADR","Denmark","Mid ($10-100bn)","Rina-S (rinatabart sesutecan)","FRa ADC","Ovarian cancer, endometrial","Oncology","Phase 3","Breakthrough","RAINFOL-02 Ph3 readout 2026-27","3","",None,"From ProfoundBio"),
("Genmab","GMAB","NASDAQ","ADR","Denmark","Mid ($10-100bn)","Epcoritamab (Epkinly) expansions (w/ AbbVie)","CD20 x CD3 bispecific","2L FL (approved Nov 2025 EPCORE FL-1), DLBCL 1L/2L","Hematology","Approved (recent)","Breakthrough","EPCORE DLBCL-1 OS not stat-sig (2025); further readouts 2026","4","",None,""),
("Genmab","GMAB","NASDAQ","ADR","Denmark","Mid ($10-100bn)","Acasunlimab (w/ BioNTech)","PD-L1 x 4-1BB bispecific","2L NSCLC","Oncology","Phase 3","—","ABBIL1TY NSCLC-06 readout 2026-27","3","",None,""),
("Genmab","GMAB","NASDAQ","ADR","Denmark","Mid ($10-100bn)","Merus (acq. Sep 2025) petosemtamab","EGFR x LGR5 bispecific","1L/2L HNSCC, mCRC","Oncology","Phase 3","Breakthrough","LiGeR-HN1/HN2 interim 2026","3","",None,"Merus acquisition $8bn"),
("Ipsen","IPSEY","OTC","ADR","France","Mid ($10-100bn)","Tovorafenib / Iqirvo / elafibranor expansions","—","PBC (Iqirvo approved 2024); PSC Ph3","Hepatology","Phase 3","Orphan","ELMWOOD PSC Ph3","1","",None,""),
("Grifols","GRFS","NASDAQ","ADR","Spain","Small ($1-10bn)","Fibrinogen concentrate / GIGA2339","Plasma-derived; HBV mAb","Congenital fibrinogen deficiency","Hematology","NDA/BLA under review","Orphan","BLA decision 2025-26","0.5","",None,""),
("Precigen","PGEN","NASDAQ","US common","US","Micro (<$1bn)","Papzimeos (zopapogene imadenovec)","Adenoviral immunotherapy","Recurrent respiratory papillomatosis","Rare disease","Approved (recent)","Breakthrough, Orphan","Approved Aug 2025","0.5","",None,"Precigen"),
("Regenxbio","RGNX","NASDAQ","US common","US","Micro (<$1bn)","RGX-121 (clemidsogene lanparvovec)","AAV IDS gene therapy","MPS II (Hunter)","Rare disease","NDA/BLA under review","Orphan, RMAT, Fast Track","PDUFA extended to Feb 8 2026 - verify","1","",None,"Partnered w/ Nippon Shinyaku"),
("Regenxbio","RGNX","NASDAQ","US common","US","Micro (<$1bn)","RGX-202","Microdystrophin gene therapy","DMD","Rare disease","Phase 3","Orphan, Fast Track","Pivotal AFFINITY DUCHENNE data 2026; BLA 2026","3","",None,""),
("Regenxbio","RGNX","NASDAQ","US common","US","Micro (<$1bn)","ABBV-RGX-314 (w/ AbbVie)","Subretinal AAV anti-VEGF","Wet AMD, DR","Ophthalmology","Phase 3","—","ATMOSPHERE/ASCENT topline 2026","10","",None,""),
("Adaptimmune / others skip","","","","","","","","","","","","","","",None,""),
("Merus (acq. by Genmab) - see GMAB","","","","","","","","","","","","","","",None,""),
("Celcuity","CELC","NASDAQ","US common","US","Small ($1-10bn)","Gedatolisib","PI3K/mTOR inhibitor","HR+/HER2- advanced BC (PIK3CA wild-type & mutant)","Oncology","NDA/BLA under review","Breakthrough, Fast Track","VIKTORIA-1 WT positive (Jul 2025); NDA filed; decision 2026","2","",None,""),
("Olema Pharmaceuticals","OLMA","NASDAQ","US common","US","Micro (<$1bn)","Palazestrant","Complete ER antagonist","ER+/HER2- BC","Oncology","Phase 3","Fast Track","OPERA-01 topline 2026","3","",None,""),
("Cullinan Therapeutics","CGEM","NASDAQ","US common","US","Micro (<$1bn)","Zipalertinib (w/ Taiho)","EGFR ex20ins TKI","EGFR ex20ins NSCLC","Oncology","NDA/BLA under review","Breakthrough, Orphan","REZILIENT1 pivotal positive; NDA (Taiho) 2025-26","1","",None,""),
("Verastem Oncology","VSTM","NASDAQ","US common","US","Micro (<$1bn)","Avmapki Fakzynja Co-pack (avutometinib+defactinib)","RAF/MEK + FAK","KRASm LGSOC (approved May 2025); pancreatic","Oncology","Approved (recent)","Breakthrough, Orphan","RAMP 301 confirmatory; RAMP 205 PDAC","0.5","",None,""),
("Immunocore","IMCR","NASDAQ","ADR","UK","Small ($1-10bn)","Brenetafusp (IMC-F106C)","PRAME x CD3 ImmTAC","1L advanced cutaneous melanoma (w/ nivolumab)","Oncology","Phase 3","—","PRISM-MEL-301 readout 2026-27","3","",None,"Kimmtrak approved 2022"),
("Compass Pathways","CMPS","NASDAQ","ADR","UK","Micro (<$1bn)","COMP360 (psilocybin)","Psychedelic 5-HT2A agonist","Treatment-resistant depression","CNS/Psychiatry","Phase 3","Breakthrough","COMP005 positive (Jun 2025); COMP006 26-wk data 2026; rolling NDA","5","TRD $5bn",None,""),
("MindMed","MNMD","NASDAQ","US common","US","Small ($1-10bn)","MM120 (LSD tartrate ODT)","5-HT2A agonist","Generalized anxiety disorder, MDD","CNS/Psychiatry","Phase 3","Breakthrough","Voyage Ph3 topline H1 2026; Panorama H2 2026","5","GAD $5bn+",None,""),
("atai Beckley","ATAI","NASDAQ","US common","Germany/US","Micro (<$1bn)","BPL-003 (mebufotenin)","5-HT2A agonist (intranasal)","Treatment-resistant depression","CNS/Psychiatry","Phase 3","Breakthrough","Ph2b positive (Jul 2025); Ph3 2026","5","",None,""),
("Cybin","CYBN","NYSE American","US common","Canada","Micro (<$1bn)","CYB003 (deuterated psilocin)","5-HT2A agonist","MDD (adjunct)","CNS/Psychiatry","Phase 3","Breakthrough","APPROACH Ph3 readout 2026","5","",None,""),
("Lexicon Pharmaceuticals","LXRX","NASDAQ","US common","US","Micro (<$1bn)","Pilavapadin (LX9211)","AAK1 inhibitor","Diabetic peripheral neuropathic pain","Neurology","Phase 3","—","PROGRESS Ph2b mixed; Ph3 planning (partner sought)","3","",None,"Zynquista CRL Dec 2024"),
("Lexicon Pharmaceuticals","LXRX","NASDAQ","US common","US","Micro (<$1bn)","Sotagliflozin (Inpefa) HCM","SGLT1/2","Hypertrophic cardiomyopathy","Cardiovascular","Phase 3","—","SONATA-HCM readout 2026","2","",None,""),
("89bio (acq. by Roche Sep 2025) - see Roche pegozafermin","","","","","","","","","","","","","","",None,""),
("Sionna / Others skip","","","","","","","","","","","","","","",None,""),
("Savara","SVRA","NASDAQ","US common","US","Micro (<$1bn)","Molbreevi (molgramostim)","Inhaled GM-CSF","Autoimmune pulmonary alveolar proteinosis","Rare disease","NDA/BLA under review (CRL history)","Orphan, Breakthrough","RTF Aug 2025; resubmitted; decision 2026","0.5","",None,""),
("Zevra Therapeutics","ZVRA","NASDAQ","US common","US","Micro (<$1bn)","Miplyffa (arimoclomol) / celiprolol","HSP amplifier; beta blocker","NPC (approved Sep 2024); vascular EDS","Rare disease","Phase 3","Orphan","DiSCOVER vEDS Ph3 2026","0.5","",None,""),
("Dyne Therapeutics","DYN","NASDAQ","US common","US","Small ($1-10bn)","DYNE-251 (z-rostudirsen)","FORCE exon 51 skipping","DMD exon 51","Rare disease","NDA/BLA under review","Orphan, Breakthrough, Fast Track","Accelerated approval BLA early 2026","1","",None,""),
("Dyne Therapeutics","DYN","NASDAQ","US common","US","Small ($1-10bn)","DYNE-101 (z-rostudirsen for DM1)","FORCE DMPK antisense","Myotonic dystrophy type 1","Rare disease","Phase 3","Orphan, Breakthrough","Accelerated approval BLA 2026","3","DM1 no approved therapy; $3bn",None,""),
("Avidity Biosciences (acq. by Novartis Oct 2025) - see NVS","","","","","","","","","","","","","","",None,""),
("Wave Life Sciences","WVE","NASDAQ","US common","Singapore/US","Small ($1-10bn)","WVE-N531","Exon 53 skipping","DMD exon 53","Rare disease","Phase 2","Orphan","Accelerated approval NDA 2026","1","",None,""),
("Wave Life Sciences","WVE","NASDAQ","US common","Singapore/US","Small ($1-10bn)","WVE-007 (INHBE siRNA)","GalNAc siRNA","Obesity","Metabolic/Obesity","Phase 1","—","INLIGHT data 2025-26","20","",None,""),
("Cytokinetics end2","","","","","","","","","","","","","","",None,""),
("Tenax / Others skip","","","","","","","","","","","","","","",None,""),
("Cidara Therapeutics (acq. by Merck Nov 2025)","","","","","","","","","","","","","","",None,""),
("Vir Biotechnology","VIR","NASDAQ","US common","US","Small ($1-10bn)","Tobevibart + elebsiran","HDV antibody + siRNA","Chronic hepatitis delta","Hepatology","Phase 3","Breakthrough, Orphan","ECLIPSE 1 Ph3 readout 2026","1","",None,""),
("Assembly Biosciences","ASMB","NASDAQ","US common","US","Micro (<$1bn)","ABI-5366 / ABI-1179","Long-acting helicase-primase inhibitors","Recurrent genital herpes","Infectious disease/Vaccine","Phase 2","—","Ph1b/2a 2025-26","2","",None,"Gilead partnered"),
("Innoviva","INVA","NASDAQ","US common","US","Small ($1-10bn)","Zoliflodacin (Nuzolvence)","First-in-class oral antibiotic","Uncomplicated gonorrhea","Infectious disease/Vaccine","Approved (recent)","QIDP, Fast Track","Approved Dec 2025 - verify","0.5","",None,""),
("Iterum Therapeutics","ITRM","NASDAQ","US common","Ireland","Micro (<$1bn)","Orlynvah (sulopenem)","Oral penem","uUTI","Infectious disease/Vaccine","Approved (recent)","QIDP","Approved Oct 2024","0.3","",None,""),
("Ovid / Marinus skip","","","","","","","","","","","","","","",None,""),
("Atara Biotherapeutics","ATRA","NASDAQ","US common","US","Micro (<$1bn)","Tab-cel (Ebvallo)","Allogeneic EBV T-cells","EBV+ PTLD","Hematology","NDA/BLA under review (CRL history)","Breakthrough, Orphan","CRL Jan 2025 (3rd-party mfg); resubmitted; 2nd CRL Jan 2026 - verify","0.3","",35,""),
("Fulcrum Therapeutics","FULC","NASDAQ","US common","US","Micro (<$1bn)","Pociredir","EED inhibitor (HbF inducer)","Sickle cell disease","Hematology","Phase 1/2","Orphan, Fast Track","PIONEER data 2025-26","2","",None,""),
("Agios Pharmaceuticals","AGIO","NASDAQ","US common","US","Small ($1-10bn)","Mitapivat (Aqvesme) thalassemia","PK activator","Alpha/beta thalassemia","Hematology","Approved (recent)","Orphan","Approved Dec 2025 (ENERGIZE) - verify; SCD RISE UP Ph3 readout 2025-26","2","",None,""),
("Agios Pharmaceuticals","AGIO","NASDAQ","US common","US","Small ($1-10bn)","Tebapivat","PK activator","Lower-risk MDS anemia","Hematology","Phase 2/3","Orphan","Ph2b data 2025; Ph3 2026","2","",None,""),
("Keros Therapeutics","KROS","NASDAQ","US common","US","Micro (<$1bn)","Elritercept (w/ Takeda)","Activin ligand trap","MDS anemia, MF","Hematology","Phase 3","Orphan","RENEW Ph3 readout 2027","2","",None,"Cibinetide PAH halted"),
("Merus/others end","","","","","","","","","","","","","","",None,""),
("Ultragenyx end","","","","","","","","","","","","","","",None,""),
("Ocugen","OCGN","NASDAQ","US common","US","Micro (<$1bn)","OCU400","Modifier gene therapy","Retinitis pigmentosa (gene-agnostic)","Ophthalmology","Phase 3","Orphan, RMAT","liMeliGhT Ph3 readout 2026; BLA 2026","1","",None,""),
("Annexon Biosciences","ANNX","NASDAQ","US common","US","Micro (<$1bn)","Tanruprubart (ANX005)","C1q antibody","Guillain-Barre syndrome","Neurology","NDA/BLA under review","Orphan, Fast Track","BLA filed 2025 (real-world comparator); decision 2026","1","GBS no US-approved drug",60,"Single Ph3 in Bangladesh; RWE comparator risk"),
("Achieve Life Sciences","ACHV","NASDAQ","US common","US","Micro (<$1bn)","Cytisinicline","Nicotinic partial agonist","Smoking cessation, vaping cessation","CNS/Psychiatry","NDA/BLA under review","Breakthrough (vaping)","NDA submitted Jun 2025; PDUFA Jun 20 2026","2","Smoking cessation $2bn",None,""),
("Cytokinetics end3","","","","","","","","","","","","","","",None,""),
("Sionna Therapeutics","SION","NASDAQ","US common","US","Micro (<$1bn)","SION-719 / SION-451","NBD1 stabilizers","Cystic fibrosis","Rare disease","Phase 2","—","Ph2a data 2026","10","",None,""),
("Inozyme (acq. by BioMarin 2025) - see BMRN","","","","","","","","","","","","","","",None,""),
("BioMarin Pharmaceutical","BMRN","NASDAQ","US common","US","Mid ($10-100bn)","Voxzogo (vosoritide) hypochondroplasia & others","CNP analog","Hypochondroplasia, Turner, SHOX","Rare disease","Phase 3","Orphan","CANOPY Ph3 readouts 2026-27","3","",None,""),
("BioMarin Pharmaceutical","BMRN","NASDAQ","US common","US","Mid ($10-100bn)","BMN 333","Long-acting CNP","Achondroplasia","Rare disease","Phase 2/3","Orphan","Ph2/3 start 2025","2","",None,""),
("BioMarin Pharmaceutical","BMRN","NASDAQ","US common","US","Mid ($10-100bn)","BMN 401 (ENPP1 ERT, ex-Inozyme)","Enzyme replacement","ENPP1 deficiency","Rare disease","Phase 3","Orphan, Breakthrough","ENERGY 3 Ph3 readout 2026","0.5","",None,""),
("BioMarin Pharmaceutical","BMRN","NASDAQ","US common","US","Mid ($10-100bn)","Palynziq adolescents","PAL enzyme","PKU 12-17y","Rare disease","NDA/BLA under review","Orphan","sBLA decision 2026","1","",None,""),
("Halozyme (royalties) skip","","","","","","","","","","","","","","",None,""),
("Ligand skip","","","","","","","","","","","","","","",None,""),
("Ironwood Pharmaceuticals","IRWD","NASDAQ","US common","US","Micro (<$1bn)","Apraglutide","GLP-2 analog","Short bowel syndrome","Gastroenterology","Phase 3","Orphan","STARS Ph3 flawed; confirmatory Ph3 STARS 2 2026","1","",35,""),
("Phathom Pharmaceuticals","PHAT","NASDAQ","US common","US","Micro (<$1bn)","Voquezna (vonoprazan) expansions","P-CAB","Erosive esophagitis, NERD (approved); EoE Ph2","Gastroenterology","Approved (recent)","—","","2","",None,""),
("Ardelyx end","","","","","","","","","","","","","","",None,""),
("Tourmaline Bio (acq. by Novartis Sep 2025) - pacibekitug see NVS","","","","","","","","","","","","","","",None,""),
("Anaptys Bio","ANAB","NASDAQ","US common","US","Small ($1-10bn)","Rosnilimab","PD-1 agonist antibody","Rheumatoid arthritis, UC","Immunology","Phase 2","—","RA Ph2b positive (Feb 2025); UC Ph2 2026","10","",None,""),
("Ventyx Biosciences","VTYX","NASDAQ","US common","US","Micro (<$1bn)","VTX3232 / VTX2735","Oral NLRP3 inhibitors","Cardiovascular (obesity/ASCVD), recurrent pericarditis","Cardiovascular","Phase 2","—","Ph2 data 2025-26","5","",None,""),
("Corbus Pharmaceuticals","CRBP","NASDAQ","US common","US","Micro (<$1bn)","CRB-701 (Nectin-4 ADC)","Nectin-4 ADC","Urothelial, cervical, HNSCC","Oncology","Phase 1/2","—","Data 2026","3","",None,""),
("Tyra Biosciences","TYRA","NASDAQ","US common","US","Micro (<$1bn)","TYRA-300","FGFR3-selective inhibitor","Achondroplasia; NMIBC","Rare disease","Phase 2","Orphan","BEACH301 data 2026","2","",None,""),
("Cogent Biosciences","COGT","NASDAQ","US common","US","Small ($1-10bn)","Bezuclastinib","KIT D816V inhibitor","Non-advanced SM (SUMMIT positive Jul 2025); AdvSM; GIST","Oncology","NDA/BLA under review","Orphan, Breakthrough","NDA filed late 2025; decision 2026","2","Competes with Ayvakit",None,""),
("Blueprint - acquired","","","","","","","","","","","","","","",None,""),
("Deciphera (acq. by Ono) skip","","","","","","","","","","","","","","",None,""),
("IDEAYA Biosciences","IDYA","NASDAQ","US common","US","Small ($1-10bn)","Darovasertib + crizotinib","PKC inhibitor + MET","Metastatic uveal melanoma (HLA-A2-)","Oncology","Phase 2/3","Breakthrough","Registrational data 2026; potential accelerated approval","1","",None,""),
("Janux Therapeutics","JANX","NASDAQ","US common","US","Small ($1-10bn)","JANX007","PSMA x CD3 TRACTr","mCRPC","Oncology","Phase 1","—","Ph1b data 2026; pivotal 2026","5","",None,""),
("Bicycle Therapeutics","BCYC","NASDAQ","ADR","UK","Micro (<$1bn)","Zelenectide pevedotin","Nectin-4 Bicycle toxin conjugate","Urothelial cancer","Oncology","Phase 2/3","Fast Track","Duravelo-2 registrational data 2026","2","",None,""),
("Mural Oncology / Others skip","","","","","","","","","","","","","","",None,""),
("Alector","ALEC","NASDAQ","US common","US","Micro (<$1bn)","Latozinemab (w/ GSK)","Progranulin-raising antibody","FTD-GRN","Neurology","Phase 3","Orphan, Breakthrough","INFRONT-3 missed primary (Oct 2025)","1","",10,""),
("Prothena","PRTA","NASDAQ","US common","Ireland/US","Micro (<$1bn)","Birtamimab / PRX012 / coramitug","Amyloid antibodies","AL amyloidosis; AD; ATTR","Hematology","Phase 3","Orphan","AFFIRM-AL failed (May 2025); PRX012 Ph1; coramitug (Novo) Ph2","2","",15,""),
("Cassava Sciences","SAVA","NASDAQ","US common","US","Micro (<$1bn)","Simufilam","Filamin A binder","Alzheimer's (failed); TSC epilepsy","Neurology","Phase 2","—","AD Ph3 failed Nov 2024; TSC Ph2 2026","1","",10,""),
("Anavex Life Sciences","AVXL","NASDAQ","US common","US","Micro (<$1bn)","Blarcamesine","Sigma-1 agonist","Alzheimer's disease","Neurology","Phase 3","—","EMA CHMP negative (2025); no US NDA","15","",10,""),
("Cassava end","","","","","","","","","","","","","","",None,""),
("Cel-Sci / others skip","","","","","","","","","","","","","","",None,""),
("Longboard (acq. by Lundbeck) skip","","","","","","","","","","","","","","",None,""),
("H. Lundbeck","HLUYY","OTC","ADR","Denmark","Small ($1-10bn)","Bexicaserin","5-HT2C superagonist","Developmental and epileptic encephalopathies","Neurology","Phase 3","Orphan, Breakthrough","DEEp SEA Ph3 readout 2026","2","",None,"From Longboard acquisition"),
("H. Lundbeck","HLUYY","OTC","ADR","Denmark","Small ($1-10bn)","Amlenetug","Alpha-synuclein antibody","Multiple system atrophy","Neurology","Phase 3","Orphan","MASCOT Ph3 readout 2027","1","",None,""),
("Eisai","ESALY","OTC","ADR","Japan","Mid ($10-100bn)","Leqembi (lecanemab) SC / preclinical AD","Anti-amyloid","Early AD; preclinical AD (AHEAD 3-45)","Neurology","Approved (recent)","—","AHEAD 3-45 readout 2028","10","",None,"Partner Biogen"),
("Otsuka end","","","","","","","","","","","","","","",None,""),
("Chugai Pharmaceutical","CHGCY","OTC","ADR","Japan","Mid ($10-100bn)","Orforglipron (Lilly-licensed) / NXT007 / nemolizumab","—","Obesity (royalty); hemophilia; PN/AD","Metabolic/Obesity","Phase 3","—","","150","",None,"Orforglipron originated at Chugai"),
("Ono Pharmaceutical","OPHLY","OTC","ADR","Japan","Mid ($10-100bn)","Romvimza (vimseltinib, ex-Deciphera)","CSF1R inhibitor","Tenosynovial giant cell tumor","Oncology","Approved (recent)","Orphan, Breakthrough","Approved Feb 2025","0.5","",None,""),
("Shionogi","SGIOY","OTC","ADR","Japan","Mid ($10-100bn)","Zuranolone / ensitrelvir (Xocova)","GABA-A PAM; 3CL protease inhibitor","PPD (Zurzuvae, w/ Biogen); COVID-19 post-exposure prophylaxis","Infectious disease/Vaccine","NDA/BLA under review","Fast Track","Ensitrelvir SCORPIO-PEP positive; NDA filed 2025","1","",None,""),
("Sumitomo Pharma (ADR)","","","","","","","","","","","","","","",None,""),
("Kyowa Kirin","KYKOF","OTC","ADR","Japan","Mid ($10-100bn)","Ziftomenib (w/ Kura) / rocatinlimab (w/ Amgen) / KHK4083","—","AML; AD","Hematology","Approved (recent)","—","","2","",None,""),
("Mesoblast","MESO","NASDAQ","ADR","Australia","Small ($1-10bn)","Ryoncil (remestemcel-L) adult SR-aGVHD; Revascor","MSC therapy","Adult SR-aGVHD; chronic low back pain; HF","Immunology","Phase 3","Orphan, RMAT","Ryoncil pediatric approved Dec 2024; adult BLA path 2026; Revascor accelerated BLA","2","",None,""),
("Telix Pharmaceuticals","TLX","NASDAQ","ADR","Australia","Small ($1-10bn)","Zircaix (TLX250-CDx) / Pixclara (TLX101-CDx)","PET imaging agents","ccRCC imaging; glioma imaging","Oncology","NDA/BLA under review (CRL history)","Breakthrough","Zircaix CRL Aug 2025; Pixclara CRL Apr 2025; resubmissions 2026","0.5","",50,"Illuccix approved 2022"),
("Clarity Pharmaceuticals (not US-listed) skip","","","","","","","","","","","","","","",None,""),
("Opthea","OPTHF","OTC","ADR","Australia","Micro (<$1bn)","Sozinibercept","VEGF-C/D trap","Wet AMD","Ophthalmology","Phase 3","—","COAST/ShORe failed Mar 2025","10","",2,"Program discontinued"),
("Neuren Pharmaceuticals","NURPF","OTC","ADR","Australia","Small ($1-10bn)","NNZ-2591","IGF-1 analog","Phelan-McDermid, Angelman, Pitt Hopkins","Rare disease","Phase 3","Orphan","PMS Ph3 start 2025; readout 2027","1","",None,"Daybue (trofinetide) via Acadia"),
("Immutep","IMMP","NASDAQ","ADR","Australia","Micro (<$1bn)","Eftilagimod alfa","LAG-3 soluble protein","1L NSCLC (low PD-L1), HNSCC","Oncology","Phase 3","Fast Track","TACTI-004 Ph3 readout 2027","3","",None,""),
("Kazia Therapeutics","KZIA","NASDAQ","ADR","Australia","Micro (<$1bn)","Paxalisib","PI3K/mTOR brain-penetrant","Glioblastoma","Oncology","Phase 2","Orphan, Fast Track","GBM AGILE mixed; pivotal planning","1","",15,""),
("Neuphoria Therapeutics","NEUP","NASDAQ","US common","US/Australia","Micro (<$1bn)","BNC210","a7 nAChR NAM","Social anxiety disorder","CNS/Psychiatry","Phase 3","Fast Track","AFFIRM-1 Ph3 readout 2026","3","",None,""),
("Alterity Therapeutics","ATHE","NASDAQ","ADR","Australia","Micro (<$1bn)","ATH434","Iron chaperone / a-syn aggregation inhibitor","Multiple system atrophy","Neurology","Phase 2","Orphan, Fast Track","Ph2 positive (Jan 2025); Ph3 design w/ FDA 2026","1","",None,""),
("Incannex / others skip","","","","","","","","","","","","","","",None,""),
("Sanofi end","","","","","","","","","","","","","","",None,""),
("Ipsen end","","","","","","","","","","","","","","",None,""),
("Merck KGaA","MKKGY","OTC","ADR","Germany","Mid ($10-100bn)","Pimicotinib","CSF-1R inhibitor","Tenosynovial giant cell tumor","Oncology","NDA/BLA under review","Breakthrough, Orphan","MANEUVER Ph3 positive; NDA 2025-26","0.5","",None,"Licensed from Abbisko"),
("Merck KGaA","MKKGY","OTC","ADR","Germany","Mid ($10-100bn)","Precemtabart tocentecan (M9140)","CEACAM5 ADC","mCRC","Oncology","Phase 2","—","Ph2 data 2026","3","",None,""),
("Merck KGaA","MKKGY","OTC","ADR","Germany","Mid ($10-100bn)","Ogsiveo (nirogacestat, ex-SpringWorks)","Gamma secretase inhibitor","Desmoid tumors (approved); ovarian granulosa cell","Oncology","Approved (recent)","Orphan","Mirdametinib (Gomekli) NF1-PN approved Feb 2025","1","",None,"SpringWorks acquisition Jul 2025"),
("Boehringer (private) skip","","","","","","","","","","","","","","",None,""),
("Almirall (not US-listed) skip","","","","","","","","","","","","","","",None,""),
("Grifols end","","","","","","","","","","","","","","",None,""),
("Indivior","INDV","NASDAQ","US common","UK/US","Small ($1-10bn)","INDV-2000 (C4X_3256)","Orexin-1 antagonist","Opioid use disorder","CNS/Psychiatry","Phase 2","Fast Track","Ph2 data 2026","2","",None,""),
("Esperion Therapeutics","ESPR","NASDAQ","US common","US","Micro (<$1bn)","Nexletol/Nexlizet pediatric; ESP-1336","Bempedoic acid; next-gen","HeFH pediatric; hypertriglyceridemia","Cardiovascular","Phase 3","—","","2","",None,""),
("NewAmsterdam Pharma","NAMS","NASDAQ","US common","Netherlands","Small ($1-10bn)","Obicetrapib (+ ezetimibe FDC)","CETP inhibitor","Hypercholesterolemia / ASCVD","Cardiovascular","NDA/BLA under review","—","BROADWAY/BROOKLYN/TANDEM positive; NDA filed 2025 (Menarini ex-US); PREVAIL CVOT 2026","10","Oral LDL-lowering adjunct $10bn",None,""),
("Verve - acquired","","","","","","","","","","","","","","",None,""),
("Tenaya Therapeutics","TNYA","NASDAQ","US common","US","Micro (<$1bn)","TN-201","AAV9 MYBPC3 gene therapy","MYBPC3-associated HCM","Cardiovascular","Phase 1/2","Orphan, Fast Track","Data 2026","2","",None,""),
("Rocket Pharmaceuticals","RCKT","NASDAQ","US common","US","Micro (<$1bn)","Kresladi (marnetegragene autotemcel)","Lentiviral gene therapy","LAD-I","Rare disease","NDA/BLA under review (CRL history)","Orphan, RMAT","CRL Jun 2024 (CMC); resubmitted; PDUFA Mar 28 2026","0.2","",None,""),
("Rocket Pharmaceuticals","RCKT","NASDAQ","US common","US","Micro (<$1bn)","RP-A501","AAV gene therapy","Danon disease","Rare disease","Phase 2","Orphan, RMAT","Clinical hold (May 2025) after death; lifted Aug 2025; pivotal resumes","1","",40,""),
("Solid Biosciences","SLDB","NASDAQ","US common","US","Micro (<$1bn)","SGT-003","Next-gen microdystrophin","DMD","Rare disease","Phase 1/2","Orphan, Fast Track","Accelerated approval discussion 2026","3","",None,""),
("Abeona Therapeutics","ABEO","NASDAQ","US common","US","Micro (<$1bn)","Zevaskyn (pz-cel)","Autologous gene-corrected skin","RDEB","Rare disease","Approved (recent)","Orphan, RMAT","Approved Apr 2025","0.5","",None,""),
("Ionis final","","","","","","","","","","","","","","",None,""),
("Altimmune","ALT","NASDAQ","US common","US","Micro (<$1bn)","Pemvidutide","GLP-1/glucagon dual agonist","MASH, alcohol use disorder, obesity","Hepatology","Phase 2","Fast Track","IMPACT Ph2b MASH positive on resolution (Jun 2025), fibrosis missed","10","",None,""),
("Terns Pharmaceuticals","TERN","NASDAQ","US common","US","Micro (<$1bn)","TERN-701","Allosteric BCR-ABL inhibitor","CML","Oncology","Phase 1","—","CARDINAL data 2025-26","2","",None,""),
("Sagimet Biosciences","SGMT","NASDAQ","US common","US","Micro (<$1bn)","Denifanstat","FASN inhibitor","MASH F2-F3","Hepatology","Phase 3","Breakthrough, Fast Track","FASCINATE-3 Ph3 readout 2027","10","",None,""),
("GSK end","","","","","","","","","","","","","","",None,""),
("Cytokinetics final","","","","","","","","","","","","","","",None,""),
]

# drop placeholder rows (empty ticker)
ROWS = [r for r in ROWS if r[1]]

def pos_for(stage, ta, override):
    if override is not None:
        return override
    base = BASE_POS.get(stage, 25)
    if stage in ("Approved (recent)",):
        return 100
    adj = TA_ADJ.get(ta, 1.0)
    return round(min(base * adj, 95))

thin = Side(style="thin", color="BFBFBF")
border = Border(left=thin, right=thin, top=thin, bottom=thin)
hdr_fill = PatternFill("solid", fgColor="1F4E78")
hdr_font = Font(bold=True, color="FFFFFF")
wrap = Alignment(wrap_text=True, vertical="top")

wb = Workbook()

# ---------- Sheet 1: Pipeline ----------
ws = wb.active
ws.title = "Pipeline"
headers = ["#","公司 Company","代號 Ticker","交易所 Exchange","上巿類型 Listing","總部 HQ","巿值級別 Cap tier",
           "藥物/候選藥 Drug","作用機制 MoA","適應症 Indication","治療領域 TA","FDA階段 Stage",
           "FDA特殊資格 Designations","關鍵催化劑/時間 Catalyst","TAM (US$ bn, 峯值/巿場規模)","TAM 說明",
           "成功機會 PoS (%)","PoS 依據","備註 Notes"]
ws.append(headers)
for i, r in enumerate(ROWS, 1):
    (co,tk,ex,lst,hq,cap,drug,moa,ind,ta,stage,desig,cat,tam,tamn,ovr,notes) = r
    pos = pos_for(stage, ta, ovr)
    basis = ("Analyst override (event-specific)" if ovr is not None else
             ("Approved" if stage.startswith("Approved") else
              f"Industry base rate {BASE_POS.get(stage,25)}% x TA adj {TA_ADJ.get(ta,1.0)}"))
    tam_v = float(tam) if tam not in ("", None) else None
    ws.append([i,co,tk,ex,lst,hq,cap,drug,moa,ind,ta,stage,desig,cat,tam_v,tamn,pos,basis,notes])

widths = [5,26,8,10,11,12,16,34,30,34,18,26,22,44,12,40,10,34,36]
for c, w in enumerate(widths, 1):
    ws.column_dimensions[get_column_letter(c)].width = w
for cell in ws[1]:
    cell.fill = hdr_fill; cell.font = hdr_font; cell.alignment = Alignment(wrap_text=True, vertical="center"); cell.border = border
for row in ws.iter_rows(min_row=2):
    for cell in row:
        cell.alignment = wrap; cell.border = border
    row[14].number_format = '0.0'
    row[16].number_format = '0'
ws.freeze_panes = "C2"
ws.auto_filter.ref = ws.dimensions
ws.row_dimensions[1].height = 32

# ---------- Sheet 2: Company summary ----------
ws2 = wb.create_sheet("Company Summary")
ws2.append(["公司 Company","代號 Ticker","交易所","上巿類型","總部","巿值級別","候選藥數目 (# candidates)",
            "審批中 NDA/BLA (#)","Phase 3 (#)","近期獲批 (#)","加總 TAM (US$ bn, 未去重)","平均 PoS (%)","治療領域 TAs"])
from collections import OrderedDict
agg = OrderedDict()
for r in ROWS:
    k = (r[0], r[1])
    a = agg.setdefault(k, {"ex":r[2],"lst":r[3],"hq":r[4],"cap":r[5],"n":0,"nda":0,"p3":0,"appr":0,"tam":0.0,"pos":[],"tas":set()})
    a["n"] += 1
    if r[10].startswith("NDA/BLA"): a["nda"] += 1
    if r[10].startswith("Phase 3"): a["p3"] += 1
    if r[10].startswith("Approved"): a["appr"] += 1
    if r[13]: a["tam"] += float(r[13])
    a["pos"].append(pos_for(r[10], r[9], r[15]))
    a["tas"].add(r[9])
for (co,tk), a in agg.items():
    ws2.append([co,tk,a["ex"],a["lst"],a["hq"],a["cap"],a["n"],a["nda"],a["p3"],a["appr"],round(a["tam"],1),
                round(sum(a["pos"])/len(a["pos"])), ", ".join(sorted(a["tas"]))])
for c, w in enumerate([28,9,10,11,14,16,12,12,10,10,14,10,50], 1):
    ws2.column_dimensions[get_column_letter(c)].width = w
for cell in ws2[1]:
    cell.fill = hdr_fill; cell.font = hdr_font; cell.alignment = Alignment(wrap_text=True); cell.border = border
for row in ws2.iter_rows(min_row=2):
    for cell in row: cell.border = border; cell.alignment = wrap
ws2.freeze_panes = "B2"; ws2.auto_filter.ref = ws2.dimensions; ws2.row_dimensions[1].height = 32

# ---------- Sheet 3: FDA Decisions Pending ----------
from split_catalyst import split_catalyst, TODAY as SPLIT_TODAY

ws3 = wb.create_sheet("FDA Decisions Pending")
ws3.append(["公司 Company", "代號 Ticker", "成功機會 PoS (%)", "TAM (US$ bn)", "巿值級別 Cap tier",
            "藥物 Drug", "適應症 Indication", "FDA階段 Stage",
            f"已發生催化劑/PDUFA (截至 {SPLIT_TODAY:%Y-%m-%d})", "待發生催化劑/PDUFA (未來)",
            "備註 Notes"])
for r in ROWS:
    if not r[10].startswith("NDA/BLA"):
        continue
    past, fut = split_catalyst(r[12])
    ws3.append([r[0], r[1], pos_for(r[10], r[9], r[15]), float(r[13]) if r[13] else None, r[5],
                r[6], r[8], r[10], past or "—", fut or "—", r[16]])
for c, w in enumerate([26, 9, 11, 12, 16, 34, 34, 26, 52, 44, 36], 1):
    ws3.column_dimensions[get_column_letter(c)].width = w
for cell in ws3[1]:
    cell.fill = hdr_fill; cell.font = hdr_font
    cell.alignment = Alignment(wrap_text=True, vertical="center"); cell.border = border
for row in ws3.iter_rows(min_row=2):
    for cell in row: cell.border = border; cell.alignment = wrap
    row[2].number_format = '0'
    row[3].number_format = '0.0'
ws3.freeze_panes = "C2"; ws3.auto_filter.ref = ws3.dimensions; ws3.row_dimensions[1].height = 40

# colour-scale the PoS column so the risk gradient reads at a glance
from openpyxl.formatting.rule import ColorScaleRule
ws3.conditional_formatting.add(
    f"C2:C{ws3.max_row}",
    ColorScaleRule(start_type="num", start_value=0, start_color="F8CBAD",
                   mid_type="num", mid_value=60, mid_color="FFE699",
                   end_type="num", end_value=95, end_color="C6E0B4"))

# ---------- Sheet 4: Methodology ----------
ws4 = wb.create_sheet("Methodology & Notes")
notes = [
 ["FDA 藥物申請 Pipeline — 美國上巿 / ADR 可交易公司 (Curated snapshot)"],
 [""],
 ["資料截點 Data as-of", "知識截點約 2026 年中 (mid-2026)。標註『verify』的項目 = 該 PDUFA/決定日期在截點附近或之後，請以 FDA / 公司公告核實最新狀態。"],
 ["覆蓋範圍 Coverage", "本表為『重點策展』(curated) 而非窮盡式 (exhaustive) 名單。美國上巿/ADR 生物製藥公司逾 700 家，本表收錄約 " + str(len(agg)) + " 家、" + str(len(ROWS)) + " 個候選藥，聚焦：(a) NDA/BLA 審批中、(b) Phase 3、(c) 具巿場意義的 Phase 2 及 2024-25 新獲批藥。"],
 ["資料來源 Sources", "公司新聞稿/10-K/年報、FDA 新聞稿及 Drugs@FDA、ClinicalTrials.gov、BIO/Informa/QLS《Clinical Development Success Rates》、賣方研究對 TAM/峯值銷售的共識估計。本環境無法即時連接 openFDA / ClinicalTrials.gov API (網絡政策封鎖)，故未能自動核對。"],
 [""],
 ["FDA 階段定義 Stage definitions", ""],
 ["Approved (recent)", "2024 年中至 2026 年中獲 FDA 批准 (含加速批准)，列出以便追蹤標籤擴充/確認性試驗。"],
 ["NDA/BLA under review", "已向 FDA 提交 NDA/BLA 或 sNDA/sBLA，等待 PDUFA 決定。"],
 ["NDA/BLA under review (CRL history)", "曾收 Complete Response Letter (CRL) 或 Refuse-to-File，現重新提交。"],
 ["Phase 3 (positive readout, filing pending)", "Ph3 達主要終點，尚未提交。"],
 ["Phase 3 / Phase 2/3 / Phase 2 / Phase 1/2", "按 ClinicalTrials.gov 登記之最高階段。"],
 [""],
 ["成功機會 PoS 方法 Probability-of-success method", ""],
 ["基準率 Base rate (到最終獲批 LOA)", "; ".join(f"{k}: {v}%" for k,v in BASE_POS.items())],
 ["治療領域調整 TA adjustment (乘數)", "; ".join(f"{k}: x{v}" for k,v in TA_ADJ.items())],
 ["分析師覆寫 Analyst override", "當有具體事件 (Ph3 失敗、CRL、安全事故、FDA 對數據集提出質疑) 時，以事件特定機率取代基準率，並於『PoS 依據』欄註明。"],
 ["PoS 上限", "非已獲批項目上限 95%。"],
 [""],
 ["TAM 定義", "以 US$ 十億計，代表該適應症/藥物類別之全球可及巿場 (峯值銷售或類別巿場規模)，多來自公司指引或賣方共識；同一公司內多個候選藥可能共享同一 TAM (例如肥胖 ~US$150bn)，故 Company Summary 內加總 TAM 為『未去重』僅供參考。"],
 [""],
 ["催化劑切分 Catalyst split", "『FDA Decisions Pending』分頁將催化劑按 2026-09-04 切為『已發生』與『待發生』兩欄。判斷準則：clause 陳述已完成動作 (positive / filed / accepted / CRL / RTF / approved / withdrawn / missed) 歸『已發生』；陳述預定動作 (decision / PDUFA / readout / filing) 而日期仍在未來則歸『待發生』；預定動作但日期或整個年度已過，亦歸『已發生』。"],
 ["[日期已過，結果待核實]", "該 PDUFA 日期已過，但落在本資料集知識截點 (約 2026 年中) 之後，故 FDA 的實際決定結果本表無從得知，必須自行核實。"],
 ["免責聲明 Disclaimer", "僅供研究參考，不構成投資建議。生物科技股價對 FDA 決定高度敏感，請以最新公告核實。"],
]
for n in notes: ws4.append(n)
ws4.column_dimensions["A"].width = 42; ws4.column_dimensions["B"].width = 140
ws4["A1"].font = Font(bold=True, size=14)
for row in ws4.iter_rows(min_row=2):
    for cell in row: cell.alignment = wrap
    if row[0].value and not row[1].value and row[0].value != "": row[0].font = Font(bold=True)

# ---------- Sheet 5: Ticker Watchlist (unique tickers) ----------
TV_CHART = "https://www.tradingview.com/chart/Q1c5VWwD/?symbol="

ws5 = wb.create_sheet("Ticker Watchlist")
ws5.append(["代號 Ticker (按此開圖 click to chart)","公司 Company","交易所 Exchange","上巿類型 Listing",
            "總部 HQ","巿值級別 Cap tier","候選藥數目 #","審批中 NDA/BLA #","Phase 3 #","近期獲批 #",
            "平均 PoS (%)","主要治療領域 TAs","TradingView URL"])
seen = {}
for (co, tk), a in agg.items():
    if tk in seen:
        e = seen[tk]
        e["n"] += a["n"]; e["nda"] += a["nda"]; e["p3"] += a["p3"]; e["appr"] += a["appr"]
        e["pos"] += a["pos"]; e["tas"] |= a["tas"]
    else:
        seen[tk] = {"co": co, "ex": a["ex"], "lst": a["lst"], "hq": a["hq"], "cap": a["cap"],
                    "n": a["n"], "nda": a["nda"], "p3": a["p3"], "appr": a["appr"],
                    "pos": list(a["pos"]), "tas": set(a["tas"])}
for tk in sorted(seen):
    e = seen[tk]
    ws5.append([tk, e["co"], e["ex"], e["lst"], e["hq"], e["cap"], e["n"], e["nda"], e["p3"], e["appr"],
                round(sum(e["pos"]) / len(e["pos"])), ", ".join(sorted(e["tas"])),
                TV_CHART + tk.lower()])
for c, w in enumerate([28, 30, 12, 12, 16, 16, 10, 12, 10, 10, 11, 46, 62], 1):
    ws5.column_dimensions[get_column_letter(c)].width = w
for cell in ws5[1]:
    cell.fill = hdr_fill; cell.font = hdr_font; cell.alignment = Alignment(wrap_text=True, vertical="center"); cell.border = border
for row in ws5.iter_rows(min_row=2):
    for cell in row: cell.border = border; cell.alignment = wrap
ws5.freeze_panes = "B2"; ws5.auto_filter.ref = ws5.dimensions; ws5.row_dimensions[1].height = 32

# ---------- Apply TradingView hyperlinks to every ticker cell ----------
link_font = Font(color="0563C1", underline="single")
# (sheet, 1-based ticker column)
for sheet, col in ((ws, 3), (ws2, 2), (ws3, 2), (ws5, 1)):
    for row in sheet.iter_rows(min_row=2, min_col=col, max_col=col):
        cell = row[0]
        t = cell.value
        if not t:
            continue
        cell.hyperlink = TV_CHART + str(t).strip().lower()
        cell.font = link_font
# URL column on watchlist sheet also clickable
for row in ws5.iter_rows(min_row=2, min_col=13, max_col=13):
    cell = row[0]
    if cell.value:
        cell.hyperlink = cell.value
        cell.font = link_font

# ---------- Note the linking convention in Methodology ----------
ws4.append([""])
ws4.append(["TradingView 連結 TradingView links",
            "所有『代號 Ticker』欄位均已加上超連結，格式為 " + TV_CHART + "<ticker(小寫)>，"
            "例如 ticker = NE -> " + TV_CHART + "ne 。ADR/OTC 代號在 TradingView 上可能需要加交易所前綴 "
            "(例如 OTC:RHHBY) 方能正確開圖，若連結未能載入請於 TradingView 內手動搜尋該代號。"])

out = "FDA_Pipeline_US_Listed.xlsx"
wb.save(out)
print(f"Wrote {out}: {len(ROWS)} candidates across {len(agg)} companies, {len(seen)} unique tickers")

# Optional second copy under a caller-supplied name (kept out of git on purpose).
import sys
if len(sys.argv) > 1:
    wb.save(sys.argv[1])
    print("Also wrote", sys.argv[1])
