export const meta = {
  name: 'fda-pending-refresh',
  description: 'Verify US + ex-US regulatory status and next catalyst for 82 FDA pending-decision assets as of 2026-09-05',
  phases: [
    { title: '核實', detail: '每個標的一個 agent，搜尋 FDA/公司/EMA 一手來源' },
    { title: '複核', detail: '對與基準線衝突或低信心的結果作對抗性複核' },
  ],
}

const AS_OF = '2026-09-05'

const S = {
  type: 'object',
  properties: {
    ticker: { type: 'string' },
    us_status: { type: 'string', enum: ['已獲批','審批中(有PDUFA)','審批中(無PDUFA)','CRL','撤回或終止','未遞交','不明'] },
    us_status_date: { type: 'string', description: 'FDA 行動日 YYYY-MM-DD；無則空字串' },
    us_detail: { type: 'string', description: '一句中文說明美國最新監管狀態，含關鍵日期' },
    ex_us: { type: 'string', description: 'EMA/CHMP/MHRA/PMDA/NMPA/EC 狀態，含日期；查無則寫「未查得公開紀錄」' },
    next_catalyst: { type: 'string', description: '下一個尚未發生的催化劑，中文；若無則寫「無」' },
    next_date: { type: 'string', description: '預計日期或窗口，如 2026-11-30 / 2026 Q4 / 不明' },
    confidence: { type: 'string', enum: ['高','中','低'] },
    conflicts_baseline: { type: 'boolean', description: '是否與提供的基準線陳述實質衝突' },
    conflict_note: { type: 'string', description: '若衝突，說明何處不同；否則空字串' },
    sources: { type: 'string', description: '主要來源網域+日期，分號分隔' },
  },
  required: ['ticker','us_status','us_status_date','us_detail','ex_us','next_catalyst','next_date','confidence','conflicts_baseline','conflict_note','sources'],
}

const V = {
  type: 'object',
  properties: {
    refuted: { type: 'boolean', description: '基準線是否被推翻 (true = 新結論成立，基準線錯)' },
    corrected_status: { type: 'string' },
    corrected_date: { type: 'string' },
    reason: { type: 'string' },
  },
  required: ['refuted','corrected_status','corrected_date','reason'],
}

const ITEMS = [
 {
  "ticker": "LLY",
  "company": "Eli Lilly",
  "drug": "Orforglipron (Foundayo)",
  "ind": "肥胖 / 超重合併共病",
  "baseline_status": "已獲批 — 2026-04-01 (肥胖)",
  "baseline_next": "T2D 適應症 FDA 決定；LillyDirect 銷量數據",
  "baseline_date": "2026 H2 – 2027 (T2D 未公布 PDUFA)",
  "baseline_other": "歐盟/日本：本次未核實",
  "baseline_fda": "NDA (肥胖) 2025 年底遞交，使用國家優先審查券；2026-04-01 獲批 Foundayo，審查僅約 50 日；T2D 適應症另行申報"
 },
 {
  "ticker": "PFE",
  "company": "Pfizer",
  "drug": "Sasanlimab (SC PD-1, Zumrad)",
  "ind": "BCG-naive 高風險 NMIBC (合併 BCG)【附件誤寫 BCG-unresponsive】",
  "baseline_status": "撤回或終止 — 美國 2025-12 撤回；歐盟 2026-02 撤回",
  "baseline_next": "Pfizer 補充數據後重新申報 (若有)",
  "baseline_date": "不明",
  "baseline_other": "EMA：MAA (Zumrad) 2026-02-13 撤回；CHMP 臨時意見為不可批准",
  "baseline_fda": "美國申請於 2025-12 撤回 (Pfizer FY2025 10-K)，以收集額外數據及分析；無 PDUFA"
 },
 {
  "ticker": "PFE",
  "company": "Pfizer",
  "drug": "Vepdegestrant (Veppanu, 與 Arvinas)",
  "ind": "ESR1m ER+/HER2- 晚期乳癌 (二線後)",
  "baseline_status": "已獲批 — 2026-05-01",
  "baseline_next": "Arvinas 尋找商業化夥伴；上市進度",
  "baseline_date": "2026 H2",
  "baseline_other": "本次未核實",
  "baseline_fda": "NDA 受理 2025；PDUFA 2026-06-05；提前於 2026-05-01 獲批 Veppanu (首個 PROTAC)，同時批准 Guardant360 CDx"
 },
 {
  "ticker": "MRK",
  "company": "Merck & Co.",
  "drug": "Enlicitide (Lipfendra)",
  "ind": "高膽固醇血症 (含 HeFH)",
  "baseline_status": "已獲批 — 2026-07-15",
  "baseline_next": "CORALreef Outcomes CVOT 讀數；上市放量",
  "baseline_date": "CVOT 2027-28",
  "baseline_other": "本次未核實",
  "baseline_fda": "NDA 2025 遞交；2026-07-15 獲批 Lipfendra 20mg (公司公告 07-16)，首個口服 PCSK9"
 },
 {
  "ticker": "MRK",
  "company": "Merck & Co.",
  "drug": "Winrevair (sotatercept) HYPERION 標籤擴充",
  "ind": "新確診 PAH (中/高風險)",
  "baseline_status": "審批中(有PDUFA) — 2026-09-21",
  "baseline_next": "PDUFA 決定",
  "baseline_date": "2026-09-21 (16 日後)",
  "baseline_other": "本次未核實",
  "baseline_fda": "sBLA 2026-02 受理；PDUFA 2026-09-21"
 },
 {
  "ticker": "JNJ",
  "company": "Johnson & Johnson",
  "drug": "Icotrokinra (Icotyde)",
  "ind": "中重度斑塊型銀屑病 (成人及 ≥12 歲青少年)",
  "baseline_status": "已獲批 — 2026-03-17",
  "baseline_next": "UC/Crohn's Ph3 ICONIC-UC 讀數；PsA 申報",
  "baseline_date": "2026 H2 – 2027",
  "baseline_other": "本次未核實",
  "baseline_fda": "NDA 2025 遞交；2026-03-17 獲批 Icotyde (公司公告 03-18)，首個口服 IL-23R 拮抗劑"
 },
 {
  "ticker": "JNJ",
  "company": "Johnson & Johnson",
  "drug": "Rybrevant Faspro (SC amivantamab)",
  "ind": "EGFRm NSCLC (所有 Rybrevant 適應症)",
  "baseline_status": "已獲批 — 2025-12-17",
  "baseline_next": "MARIPOSA OS 更新；SC 滲透率；每月方案採用",
  "baseline_date": "持續",
  "baseline_other": "本次未核實",
  "baseline_fda": "BLA；2025-12-17 獲批 Rybrevant Faspro (SC)；2026-02-17 每月給藥方案獲批；公司報告歐洲/日本/中國亦有 SC 核准"
 },
 {
  "ticker": "ABBV",
  "company": "AbbVie",
  "drug": "Tavapadon",
  "ind": "帕金森病 (單藥早期 + levodopa 輔助)",
  "baseline_status": "審批中(無PDUFA) — 指引窗口已過，結果未公開",
  "baseline_next": "FDA 決定 (逾期)",
  "baseline_date": "不明 — 建議即時核查",
  "baseline_other": "任何監管機構均未批准",
  "baseline_fda": "NDA 2025-09-26 遞交；標準審查；AbbVie 指引 2026 H1 決定；截至 2026-09-05 無公開批准或 CRL 紀錄 (最新消息 2026-08-04 仍為審查中)"
 },
 {
  "ticker": "ABBV",
  "company": "AbbVie",
  "drug": "Pivekimab sunirine (Decnupaz)",
  "ind": "BPDCN (成人)",
  "baseline_status": "已獲批 — 2026-05-27",
  "baseline_next": "上市；聯合療法研究",
  "baseline_date": "持續",
  "baseline_other": "本次未核實",
  "baseline_fda": "BLA；2026-05-27 獲批 Decnupaz，首個 BPDCN ADC、可門診起始"
 },
 {
  "ticker": "AMGN",
  "company": "Amgen",
  "drug": "Rocatinlimab (OX40)",
  "ind": "中重度異位性皮膚炎",
  "baseline_status": "撤回或終止 — 計劃已暫停 (Kyowa Kirin)",
  "baseline_next": "Kyowa Kirin 對計劃前途的決定",
  "baseline_date": "不明",
  "baseline_other": "無",
  "baseline_fda": "未遞交 BLA。Amgen 於 2026-01-30 終止合作、把全球權利交還 Kyowa Kirin；Kyowa Kirin 於 2026-03 因惡性腫瘤訊號 (含 Kaposi 肉瘤) 全面暫停所有臨床試驗"
 },
 {
  "ticker": "GILD",
  "company": "Gilead Sciences",
  "drug": "Anito-cel (anitocabtagene autoleucel, 與 Arcellx)",
  "ind": "R/R 多發性骨髓瘤 (四線後)",
  "baseline_status": "審批中(有PDUFA) — 2026-12-23",
  "baseline_next": "PDUFA 決定",
  "baseline_date": "2026-12-23",
  "baseline_other": "本次未核實",
  "baseline_fda": "BLA 受理；PDUFA 2026-12-23。Gilead 以約 78 億美元收購 Arcellx ($115 現金 + $5 CVR，CVR 繫於 2029 年前累計銷售 ≥$60 億)"
 },
 {
  "ticker": "GILD",
  "company": "Gilead Sciences",
  "drug": "Trodelvy 一線 mTNBC",
  "ind": "一線轉移性 TNBC (單藥 PD-L1 不適用者；合併 Keytruda CPS≥10)",
  "baseline_status": "已獲批 — 2026-06-24",
  "baseline_next": "ASCENT-05 輔助治療讀數；OS 更新",
  "baseline_date": "2027",
  "baseline_other": "歐盟：EC 批准一線 (PD-L1 不適用者) 2026",
  "baseline_fda": "sBLA；2026-06-24 同時獲批兩項一線適應症"
 },
 {
  "ticker": "REGN",
  "company": "Regeneron",
  "drug": "Odronextamab (CD20xCD3)",
  "ind": "R/R 濾泡性淋巴瘤 (FL) 及 DLBCL",
  "baseline_status": "CRL — 2025-08 (第三方生產廠)",
  "baseline_next": "Catalent 廠問題解決後重交；OLYMPIA-1 數據",
  "baseline_date": "2026 H2 – 2027",
  "baseline_other": "歐盟：EMA 2024-08-22 有條件批准 (Ordspono) FL 及 DLBCL 三線後",
  "baseline_fda": "2024-03 首次 CRL (確認性試驗入組)；2025-02 重交 FL BLA，PDUFA 2025-07-30；2025-08 第二次 CRL (Catalent Indiana 廠檢查問題，無療效/安全疑慮)；DLBCL 加速批准路徑放棄，改走 Ph3。美國至今未批"
 },
 {
  "ticker": "REGN",
  "company": "Regeneron",
  "drug": "Dupixent — CPUO (不明原因慢性搔癢)",
  "ind": "CPUO",
  "baseline_status": "未遞交 — 仍屬 Phase 3",
  "baseline_next": "CPUO Ph3 讀數 / sBLA",
  "baseline_date": "2027 申報窗口 (公司 2025-12 管線指引)",
  "baseline_other": "無",
  "baseline_fda": "CPUO 未見公開 sBLA 遞交紀錄"
 },
 {
  "ticker": "NVO",
  "company": "Novo Nordisk",
  "drug": "CagriSema (cagrilintide + semaglutide)",
  "ind": "肥胖 / 超重",
  "baseline_status": "審批中(無PDUFA) — 預期 2026 Q4",
  "baseline_next": "FDA 決定",
  "baseline_date": "2026 Q4 (估算 12 月)",
  "baseline_other": "歐盟：本次未核實",
  "baseline_fda": "NDA 2025-12-18 遞交；標準審查；預期 2026 Q4 決定；PDUFA 未公開"
 },
 {
  "ticker": "NVO",
  "company": "Novo Nordisk",
  "drug": "Mim8 / denecimig",
  "ind": "血友病 A 預防 (含/不含抑制物)",
  "baseline_status": "審批中(無PDUFA) — 推算 2026 Q4",
  "baseline_next": "FDA 決定",
  "baseline_date": "約 2026-09 至 2026-12 (估算)",
  "baseline_other": "本次未核實",
  "baseline_fda": "BLA 2025-09-29 遞交；截至 2026-07 仍審查中；PDUFA 未公開 (標準 12 個月推算約 2026-09/10)"
 },
 {
  "ticker": "AZN",
  "company": "AstraZeneca",
  "drug": "Baxdrostat (Baxfendy)",
  "ind": "未受控高血壓 (合併其他降壓藥)",
  "baseline_status": "已獲批 — 2026-05-15",
  "baseline_next": "CKD / 原發性醛固酮增多症擴充；MLYS lorundrostat 競爭 (PDUFA 12/22)",
  "baseline_date": "2026 Q4 – 2027",
  "baseline_other": "本次未核實",
  "baseline_fda": "NDA 2025 優先審查受理；2026-05-15 獲批 Baxfendy (公告 05-18)，首個醛固酮合成酶抑制劑"
 },
 {
  "ticker": "AZN",
  "company": "AstraZeneca",
  "drug": "Camizestrant (Etcamah)",
  "ind": "HR+/HER2- 晚期乳癌，一線 AI+CDK4/6 期間出現 ESR1 突變 (ctDNA 導向換藥)",
  "baseline_status": "已獲批 — 2026-09-04 (加速批准)",
  "baseline_next": "SERENA-4 一線讀數；確認性數據；付費方對 ctDNA 監測的接受度",
  "baseline_date": "2027",
  "baseline_other": "歐盟：EC 已批准 (Etcamah)；CHMP 正面；沙特/阿聯酋已批",
  "baseline_fda": "NDA 2025-07 受理 (BTD 2025-05)；ODAC 2026-04-30 召開；PDUFA 延期以審查 ctDNA 清除數據 (ASCO 2026)；2026-09-04 獲加速批准 Etcamah — FDA 首個基於 ctDNA 抗藥突變 (影像進展前) 的批准"
 },
 {
  "ticker": "NVS",
  "company": "Novartis",
  "drug": "Ianalumab (BAFF-R)",
  "ind": "Sjögren 症 (另 ITP、SLE)",
  "baseline_status": "審批中(無PDUFA) — 推算 2026 Q4",
  "baseline_next": "FDA 決定",
  "baseline_date": "約 2026 Q4 (估算)",
  "baseline_other": "全球申報自 2026 初起；歐盟本次未核實",
  "baseline_fda": "BTD 2026-01-16；BLA 已受理並獲優先審查 (Patsnap 2026-04)；PDUFA 未公開 (優先審查推算約 2026 Q4)"
 },
 {
  "ticker": "NVS",
  "company": "Novartis",
  "drug": "Pluvicto — PSMAddition",
  "ind": "PSMA+ 轉移性激素敏感前列腺癌 (mHSPC，合併 ARPI)",
  "baseline_status": "已獲批 — 2026-07-31",
  "baseline_next": "OS 成熟數據；供應鏈",
  "baseline_date": "2027",
  "baseline_other": "本次未核實",
  "baseline_fda": "sNDA 2025 遞交；2026-07-31 獲批 mHSPC，合資格患者數近倍增"
 },
 {
  "ticker": "NVS",
  "company": "Novartis",
  "drug": "OAV101 IT (Itvisma, 鞘內 onasemnogene)",
  "ind": "SMA ≥2 歲 (兒童/青少年/成人)",
  "baseline_status": "已獲批 — 2025-11-24",
  "baseline_next": "上市放量；歐盟",
  "baseline_date": "持續",
  "baseline_other": "本次未核實",
  "baseline_fda": "BLA；2025-11-24 獲批 Itvisma；2025-12 美國供應；日本 2026 Q1、歐盟 2026 Q2 亦批 (公司 Q2 披露)"
 },
 {
  "ticker": "RHHBY",
  "company": "Roche",
  "drug": "Giredestrant (口服 SERD)",
  "ind": "(1) ESR1m ER+ 晚期乳癌合併 everolimus (evERA)；(2) ER+ 早期乳癌輔助 (lidERA)",
  "baseline_status": "審批中(有PDUFA) — 2026-11-30 (早期) / 2026-12-18 (晚期)",
  "baseline_next": "PDUFA (早期 lidERA) 11/30；PDUFA (晚期 evERA) 12/18",
  "baseline_date": "2026-11-30",
  "baseline_other": "本次未核實",
  "baseline_fda": "NDA (evERA，晚期 ESR1m + everolimus) 2026-02-20 受理 → PDUFA 2026-12-18；NDA (lidERA，早期輔助；iDFS -30%) 2026-06-02 受理並獲優先審查 → PDUFA 2026-11-30"
 },
 {
  "ticker": "SNY",
  "company": "Sanofi",
  "drug": "Tolebrutinib",
  "ind": "nrSPMS (無復發次發進展型 MS)",
  "baseline_status": "CRL — 2025-12-24 (肝毒性)",
  "baseline_next": "Sanofi 回應 CRL 路徑 / 新證據；PERSEUS PPMS",
  "baseline_date": "2027+",
  "baseline_other": "歐盟：CHMP 2026-04-23 正面；EC 2026-06-19 批准 Cenrifki (無復發 SPMS，公司公告 06-23)——與 FDA 結論相反",
  "baseline_fda": "BTD；PDUFA 2025-09-28 → 延至 2025-12-28 → 2025-12-24 收 CRL：因嚴重藥物性肝損傷 (DILI) 風險，FDA 認為任何亞群均無法確立有利 benefit-risk，REMS 不足"
 },
 {
  "ticker": "GSK",
  "company": "GSK",
  "drug": "Depemokimab (Exdensur)",
  "ind": "(1) 重度嗜酸性哮喘；(2) CRSwNP",
  "baseline_status": "已獲批 (哮喘) — 2025-12-16；CRL (CRSwNP) — 2025-12",
  "baseline_next": "CRSwNP 重交；上市",
  "baseline_date": "2026 H2 – 2027",
  "baseline_other": "MHRA 2025-12-15 批准兩項適應症；EC 批准兩項；日本批准兩項；中國批准 CRSwNP",
  "baseline_fda": "兩項 BLA 受理，PDUFA 2025-12-16 → 哮喘於 2025-12-16 獲批 Exdensur (首個半年一次生物製劑)；CRSwNP 同期被 FDA 拒絕 (CRL)"
 },
 {
  "ticker": "GSK",
  "company": "GSK",
  "drug": "Tebipenem pivoxil HBr (Utebzi, 與 Spero)",
  "ind": "複雜性尿路感染 (cUTI) 含腎盂腎炎",
  "baseline_status": "已獲批 — 2026-06-17",
  "baseline_next": "上市；抗藥性管理",
  "baseline_date": "持續",
  "baseline_other": "本次未核實",
  "baseline_fda": "2022 首次 CRL (Spero)；NDA 2025-12 重交；PDUFA 2026-06-18；2026-06-17 獲批 Utebzi，首個口服碳青黴烯"
 },
 {
  "ticker": "TAK",
  "company": "Takeda",
  "drug": "Oveporexton / TAK-861 (Orzeyful)",
  "ind": "第一型猝睡症 (NT1)",
  "baseline_status": "已獲批 — 2026-08-05",
  "baseline_next": "DEA 分級 → 正式上市；NT2/IH 擴充",
  "baseline_date": "2026 Q4",
  "baseline_other": "本次未核實",
  "baseline_fda": "NDA 2026-02-10 受理 (優先審查)；2026-08-05 獲批 Orzeyful，首個 OX2R 激動劑；DEA 管制分級待定"
 },
 {
  "ticker": "TAK",
  "company": "Takeda",
  "drug": "Rusfertide (Mimrylo, 與 Protagonist)",
  "ind": "真性紅血球增多症 (PV)",
  "baseline_status": "已獲批 — 2026-08-28",
  "baseline_next": "上市；PTGX 權利金",
  "baseline_date": "持續",
  "baseline_other": "本次未核實",
  "baseline_fda": "NDA 2026-01 遞交 (優先審查、BTD、孤兒藥、Fast Track)；2026-08-28 獲批 Mimrylo，首個 hepcidin 模擬肽"
 },
 {
  "ticker": "DSNKY",
  "company": "Daiichi Sankyo",
  "drug": "Ifinatamab deruxtecan / I-DXd (與 Merck)",
  "ind": "鉑類後 ES-SCLC",
  "baseline_status": "審批中(有PDUFA) — 2026-10-10",
  "baseline_next": "PDUFA 決定",
  "baseline_date": "2026-10-10",
  "baseline_other": "Project Orbis 同步申報 (澳/加等)",
  "baseline_fda": "BLA 2026-04 受理 (優先審查、RTOR、Project Orbis)；PDUFA 2026-10-10"
 },
 {
  "ticker": "DSNKY",
  "company": "Daiichi Sankyo",
  "drug": "Patritumab deruxtecan / HER3-DXd",
  "ind": "EGFRm NSCLC (二線後)",
  "baseline_status": "撤回或終止 — BLA 已撤回 2025-05-29",
  "baseline_next": "合併 T-DXd 乳癌研究 (2026-08 啟動)",
  "baseline_date": "無 NSCLC 申報",
  "baseline_other": "無",
  "baseline_fda": "BLA 2023-12 優先審查 → 2024-06 CRL (第三方廠) → 2025-05-29 自願撤回 BLA (因 OS 不顯著)"
 },
 {
  "ticker": "DSNKY",
  "company": "Daiichi Sankyo",
  "drug": "Enhertu — DESTINY-Breast09 (合併 pertuzumab)",
  "ind": "一線 HER2+ 轉移性乳癌",
  "baseline_status": "已獲批 — 2025-12-15 (一線 MBC)；2026-05-15 (早期 ×2)",
  "baseline_next": "DB-05；早期乳癌上市",
  "baseline_date": "2026 H2 – 2027",
  "baseline_other": "歐盟：EC 批准 2026",
  "baseline_fda": "sBLA 優先審查；2025-12-15 獲批一線 HER2+ MBC；2026-05-15 再獲批兩項早期乳癌適應症 (新輔助 DB-11：pCR 67.3% vs 56.3%；輔助)"
 },
 {
  "ticker": "SMMT",
  "company": "Summit Therapeutics",
  "drug": "Ivonescimab (PD-1×VEGF, 與 Akeso)",
  "ind": "EGFRm 非鱗狀 NSCLC，三代 TKI 後 (合併化療)",
  "baseline_status": "審批中(有PDUFA) — 2026-11-14",
  "baseline_next": "PDUFA 決定；HARMONi-3 PFS 更新",
  "baseline_date": "2026-11-14",
  "baseline_other": "中國：Akeso 已獲批多項適應症 (NMPA)",
  "baseline_fda": "BLA 2025 年底遞交，已受理；PDUFA 2026-11-14；FDA 要求 OS 統計顯著"
 },
 {
  "ticker": "IONS",
  "company": "Ionis",
  "drug": "Olezarsen (Tryngolza) — sHTG",
  "ind": "重度高三酸甘油酯血症 (降 TG 及急性胰臟炎風險)",
  "baseline_status": "已獲批 — 2026-06-24",
  "baseline_next": "上市 (2026-07 供應)；ARWR plozasiran sHTG 競爭",
  "baseline_date": "持續",
  "baseline_other": "FCS 已於美國及歐盟獲批",
  "baseline_fda": "sNDA 2026-02 受理 (優先審查 + BTD)；PDUFA 2026-06-30；2026-06-24 獲批，首個降低 sHTG 胰臟炎風險藥物"
 },
 {
  "ticker": "BBIO",
  "company": "BridgeBio",
  "drug": "Encaleret",
  "ind": "ADH1 (自體顯性低血鈣症第 1 型)",
  "baseline_status": "審批中(有PDUFA) — 2027-05-08",
  "baseline_next": "PDUFA 決定",
  "baseline_date": "2027-05-08",
  "baseline_other": "EMA MAA 計劃 2026 H2 遞交；歐盟/日本孤兒藥資格",
  "baseline_fda": "NDA 約 2026-05 遞交；2026-07-22 受理；PDUFA 2027-05-08；Fast Track、孤兒藥"
 },
 {
  "ticker": "AXSM",
  "company": "Axsome",
  "drug": "AXS-05 / Auvelity — 阿茲海默症躁動",
  "ind": "阿茲海默症失智相關躁動",
  "baseline_status": "已獲批 — 2026-04-30",
  "baseline_next": "上市；Rexulti 競爭",
  "baseline_date": "持續",
  "baseline_other": "本次未核實",
  "baseline_fda": "sNDA 2025-12-31 受理 (優先審查、BTD)；PDUFA 2026-04-30；2026-04-30 獲批，首個非抗精神病藥物"
 },
 {
  "ticker": "AXSM",
  "company": "Axsome",
  "drug": "AXS-12 (reboxetine)",
  "ind": "猝睡症猝倒",
  "baseline_status": "審批中(有PDUFA) — 2027-05-01",
  "baseline_next": "PDUFA 決定",
  "baseline_date": "2027-05-01",
  "baseline_other": "本次未核實",
  "baseline_fda": "NDA 2026-07-15 受理；PDUFA 2027-05-01；不召開 AdCom"
 },
 {
  "ticker": "AXSM",
  "company": "Axsome",
  "drug": "AXS-14 (esreboxetine)",
  "ind": "纖維肌痛",
  "baseline_status": "撤回或終止 — RTF 後退回 Phase 3",
  "baseline_next": "FORWARD Ph3 讀數",
  "baseline_date": "2027",
  "baseline_other": "無",
  "baseline_fda": "2025-06 收 Refuse-to-File (RTF)；需 FORWARD 補足第二項合格試驗"
 },
 {
  "ticker": "JAZZ",
  "company": "Jazz",
  "drug": "Zanidatamab (Ziihera) — 一線 GEA",
  "ind": "一線 HER2+ 胃/GEJ/食道腺癌 (合併化療 + tislelizumab)",
  "baseline_status": "已獲批 — 2026-08-25",
  "baseline_next": "上市；歐盟申報",
  "baseline_date": "持續",
  "baseline_other": "本次未核實",
  "baseline_fda": "sBLA 優先審查；PDUFA 2026-08-25；2026-08-25 獲批 (合併化療 + Tevimbra)"
 },
 {
  "ticker": "EXEL",
  "company": "Exelixis",
  "drug": "Zanzalintinib (合併 atezolizumab)",
  "ind": "三線後轉移性大腸癌",
  "baseline_status": "審批中(有PDUFA) — 2026-12-03",
  "baseline_next": "PDUFA 決定",
  "baseline_date": "2026-12-03",
  "baseline_other": "本次未核實",
  "baseline_fda": "NDA 2025-12 遞交；2026-02 受理 (標準審查)；PDUFA 2026-12-03"
 },
 {
  "ticker": "UTHR",
  "company": "United Therapeutics",
  "drug": "Tyvaso (霧化 treprostinil) — IPF",
  "ind": "特發性肺纖維化",
  "baseline_status": "審批中(有PDUFA) — 約 2027-04",
  "baseline_next": "FDA 決定；TETON-PPF (進展性肺纖維化) 讀數",
  "baseline_date": "2027-04 (月底)",
  "baseline_other": "本次未核實",
  "baseline_fda": "sNDA 2026-06 遞交；已受理 (2026-09)；公司尋求優先審查但決定預期 2027-04 底 (即標準審查)"
 },
 {
  "ticker": "RARE",
  "company": "Ultragenyx",
  "drug": "UX111 (rebisufligene etisparvovec)",
  "ind": "Sanfilippo A 型 (MPS IIIA)",
  "baseline_status": "審批中(有PDUFA) — 2026-09-19",
  "baseline_next": "PDUFA 決定",
  "baseline_date": "2026-09-19",
  "baseline_other": "本次未核實",
  "baseline_fda": "BLA 優先審查 → 2025-07 CRL (CMC 補件 + 廠檢查)；重交；2026-04-02 受理；PDUFA 2026-09-19 (加速批准)"
 },
 {
  "ticker": "RARE",
  "company": "Ultragenyx",
  "drug": "DTX401 / pariglasgene (Genglycos)",
  "ind": "糖原儲積症 Ia 型 (GSDIa) ≥8 歲",
  "baseline_status": "已獲批 — 2026-08-19 (加速批准)",
  "baseline_next": "上市；確認性研究",
  "baseline_date": "持續",
  "baseline_other": "EMA 孤兒藥 + PRIME",
  "baseline_fda": "BLA 2026-02-23 受理 (優先審查、RMAT)；PDUFA 2026-08-23；2026-08-19 加速批准 Genglycos，公司首個基因療法"
 },
 {
  "ticker": "MRNA",
  "company": "Moderna",
  "drug": "mRNA-1010 (mFlusiva) 流感疫苗",
  "ind": "季節性流感 ≥50 歲",
  "baseline_status": "已獲批 — 2026-08-05",
  "baseline_next": "2026-27 流感季採用；ACIP 建議；mRNA-1083 組合疫苗",
  "baseline_date": "2026 Q4",
  "baseline_other": "本次未核實",
  "baseline_fda": "BLA → 2026-02 中 FDA 拒絕受理 (RTF) → 修訂策略受理 → 2026-06-18 VRBPAC AdCom → 2026-08-05 獲批 mFlusiva ≥50 歲 (50-64 完全批准；≥65 加速批准 + 上市後研究)；mRNA-1083 流感+COVID 組合疫苗美國申請於 2025 撤回"
 },
 {
  "ticker": "RYTM",
  "company": "Rhythm",
  "drug": "Imcivree (setmelanotide) — 後天性下丘腦肥胖",
  "ind": "後天性下丘腦肥胖 (成人及兒童)",
  "baseline_status": "已獲批 — 2026-03-19",
  "baseline_next": "上市；口服 bivamelagon Ph3",
  "baseline_date": "持續",
  "baseline_other": "歐盟：CHMP 2026-03-26 正面意見",
  "baseline_fda": "sNDA 優先審查；PDUFA 2025-12-20 → 2025-11 延至 2026-03-20 → 2026-03-19 獲批 (≥4 歲)，首個且唯一療法"
 },
 {
  "ticker": "ARVN",
  "company": "Arvinas",
  "drug": "Vepdegestrant (Veppanu, 與 Pfizer)",
  "ind": "ESR1m ER+/HER2- 晚期乳癌",
  "baseline_status": "已獲批 — 2026-05-01",
  "baseline_next": "商業化夥伴公告；上市",
  "baseline_date": "2026 H2",
  "baseline_other": "本次未核實",
  "baseline_fda": "2026-05-01 獲批 (PDUFA 6/5 前)；首個 PROTAC；Arvinas 尋求商業化夥伴"
 },
 {
  "ticker": "ACLX",
  "company": "Arcellx",
  "drug": "Anito-cel (與 Gilead/Kite)",
  "ind": "R/R 多發性骨髓瘤",
  "baseline_status": "審批中(有PDUFA) — 2026-12-23 (公司被收購中)",
  "baseline_next": "收購交割；PDUFA",
  "baseline_date": "2026-12-23",
  "baseline_other": "本次未核實",
  "baseline_fda": "PDUFA 2026-12-23；Gilead 以 $115 現金 + $5 CVR 收購 Arcellx (約 $78 億)"
 },
 {
  "ticker": "PTGX",
  "company": "Protagonist",
  "drug": "Rusfertide (與 Takeda)",
  "ind": "真性紅血球增多症",
  "baseline_status": "已獲批 — 2026-08-28",
  "baseline_next": "里程碑金 + 權利金",
  "baseline_date": "持續",
  "baseline_other": "本次未核實",
  "baseline_fda": "2026-08-28 獲批 Mimrylo"
 },
 {
  "ticker": "PTGX",
  "company": "Protagonist",
  "drug": "Icotrokinra (與 J&J) — 權利金",
  "ind": "銀屑病 (權利金/里程碑)",
  "baseline_status": "已獲批 — 2026-03-18 (權利金啟動)",
  "baseline_next": "UC/Crohn's 擴充里程碑",
  "baseline_date": "2027",
  "baseline_other": "本次未核實",
  "baseline_fda": "2026-03-18 獲批 Icotyde"
 },
 {
  "ticker": "DNLI",
  "company": "Denali",
  "drug": "Tividenofusp alfa / DNL310 (Avlayah)",
  "ind": "Hunter 症候群 (MPS II) 含神經表現",
  "baseline_status": "已獲批 — 2026-03-24 (加速批准)",
  "baseline_next": "上市；COMPASS 確認；DNL126 (MPS IIIA)",
  "baseline_date": "2026 H2 – 2027",
  "baseline_other": "本次未核實",
  "baseline_fda": "BLA 2025-07 受理 (優先審查、BTD)；PDUFA 2026-01-05 → 延至 2026-04-05 (臨床藥理補件)；2026-03-24 加速批准 Avlayah (公司公告 03-25)，首個處理神經症狀的 MPS II 療法"
 },
 {
  "ticker": "PRAX",
  "company": "Praxis",
  "drug": "Ulixacaltamide HCl",
  "ind": "原發性顫抖 (成人)",
  "baseline_status": "審批中(有PDUFA) — 2027-01-29",
  "baseline_next": "PDUFA 決定",
  "baseline_date": "2027-01-29",
  "baseline_other": "本次未核實",
  "baseline_fda": "BTD 2025-12；NDA 2026 初遞交；2026-04-14 受理；PDUFA 2027-01-29；不召開 AdCom"
 },
 {
  "ticker": "CORT",
  "company": "Corcept",
  "drug": "Relacorilant",
  "ind": "(1) 皮質醇增多症/庫欣 (高血壓)；(2) 鉑類抗藥卵巢癌 (Lifyorli，合併 nab-paclitaxel)",
  "baseline_status": "已獲批 (卵巢癌) — 2026-03-25；審批中(有PDUFA) (庫欣) — 2026-12-17",
  "baseline_next": "庫欣 PDUFA 12/17；Lifyorli 上市；EU 卵巢癌決定",
  "baseline_date": "2026-12-17",
  "baseline_other": "歐盟：卵巢癌 MAA 審查中 (公司 2026 Q2 披露)",
  "baseline_fda": "庫欣：PDUFA 2025-12-30 → 2025-12-30 CRL (需額外療效證據) → 2026-06-17 重交 (僅補充分析，6 個月審查) → PDUFA 2026-12-17。卵巢癌：NDA 受理，PDUFA 2026-07-11 → 提前於 2026-03-25 獲批 Lifyorli，首個 SGRA"
 },
 {
  "ticker": "TVTX",
  "company": "Travere",
  "drug": "Filspari (sparsentan) — FSGS",
  "ind": "局灶節段性腎小球硬化 (≥8 歲，非腎病症候群)",
  "baseline_status": "已獲批 — 2026-04",
  "baseline_next": "FSGS 上市；pegtibatinase HARMONY Ph3",
  "baseline_date": "持續",
  "baseline_other": "本次未核實",
  "baseline_fda": "sNDA 2025-05 受理 (傳統批准)；原計劃 AdCom 於 2025-09-10 取消；PDUFA 2026-01-13 → 延後 → 2026-04 獲完全批准，首個且唯一 FSGS 藥物"
 },
 {
  "ticker": "VERA",
  "company": "Vera Therapeutics",
  "drug": "Atacicept (Trutakna)",
  "ind": "原發性 IgA 腎病 (加速批准，降蛋白尿)",
  "baseline_status": "已獲批 — 2026-07-07 (加速批准)",
  "baseline_next": "sBLA 完全批准 (2026 Q4 遞交)；eGFR 數據",
  "baseline_date": "2026 Q4 遞交；2027 決定",
  "baseline_other": "本次未核實",
  "baseline_fda": "BLA 優先審查；2026-07-07 加速批准 Trutakna；與 FDA 對齊提前 eGFR 分析，計劃 2026 Q4 遞交 sBLA 轉完全批准"
 },
 {
  "ticker": "NUVL",
  "company": "Nuvalent (已被 GSK 收購)",
  "drug": "Zidesamtinib (Jideytro)",
  "ind": "TKI 前治療 ROS1+ 晚期 NSCLC",
  "baseline_status": "已獲批 — 2026-07-22 (公司已被 GSK 收購)",
  "baseline_next": "GSK 商業化；neladalkib (ALK) NDA",
  "baseline_date": "2026 H2 – 2027 (neladalkib)",
  "baseline_other": "本次未核實",
  "baseline_fda": "NDA 2025-11-19 受理；PDUFA 2026-09-18；提前於 2026-07-22 獲批 Jideytro。GSK 於 2026-06-09 宣布、2026-07-15 完成以 $124/股 (約 $106 億) 收購 Nuvalent；NUVL 已除牌"
 },
 {
  "ticker": "ROIV",
  "company": "Roivant / Priovant",
  "drug": "Brepocitinib (Lisraya, TYK2/JAK1)",
  "ind": "皮肌炎 (成人)",
  "baseline_status": "已獲批 — 2026-08-27",
  "baseline_next": "上市；NIU (非感染性葡萄膜炎) 開發",
  "baseline_date": "持續",
  "baseline_other": "本次未核實",
  "baseline_fda": "NDA 受理並獲優先審查 (2026 Q1)；PDUFA 2026 Q3；2026-08-27 獲批 Lisraya 30mg，首個且唯一口服皮肌炎標靶藥；即日供應"
 },
 {
  "ticker": "IRON",
  "company": "Disc Medicine",
  "drug": "Bitopertin",
  "ind": "紅血球生成性原紫質症 (EPP)",
  "baseline_status": "CRL — 2026-02-13",
  "baseline_next": "APOLLO Ph3 數據 → CRL 回應 → FDA 決定",
  "baseline_date": "2026 Q4 (數據)；2027 年中 (決定)",
  "baseline_other": "本次未核實",
  "baseline_fda": "NDA (加速批准，PPIX 替代終點) → 2026-02-13 CRL：FDA 認可 PPIX 下降但認為未證明 PPIX 變化與日光暴露終點相關；已與 FDA 對齊 APOLLO 可支持傳統批准；決定預期 2027 年中"
 },
 {
  "ticker": "SRRK",
  "company": "Scholar Rock",
  "drug": "Apitegromab",
  "ind": "脊髓性肌萎縮症 (SMA，兒童及成人)",
  "baseline_status": "審批中(有PDUFA) — 2026-09-30 (歐盟 MAA 已撤回待重交)",
  "baseline_next": "PDUFA 決定 (25 日後)；EU MAA 重交；JNDA",
  "baseline_date": "2026-09-30",
  "baseline_other": "歐盟：因 Catalent OAI 於 2026-08-20 撤回 MAA，將以替代廠重交；日本：PMDA 同意無需額外日本臨床試驗，JNDA 目標 2026 年底",
  "baseline_fda": "BLA 優先審查 → 2025-09 CRL (Catalent Indiana 灌裝廠) → 重交 (新增第二個美國灌裝廠) → 受理；PDUFA 2026-09-30。Catalent Indiana 於 2026-04 檢查後被 FDA 列為 OAI；公司 2026-08-21 確認已自美國 BLA 移除該廠、改用替代廠"
 },
 {
  "ticker": "CAPR",
  "company": "Capricor",
  "drug": "Deramiocel (CAP-1002)",
  "ind": "DMD 心肌病變 / 上肢功能",
  "baseline_status": "審批中(有PDUFA) — 2026-11-22 (AdCom 3:9 反對)",
  "baseline_next": "PDUFA 決定",
  "baseline_date": "2026-11-22",
  "baseline_other": "本次未核實",
  "baseline_fda": "2025-07 CRL → 2026-03 FDA 撤回 CRL 恢復審查 (Class 2 重交)，PDUFA 2026-08-22 → 重大修訂 (24 個月 OLE + 收窄適應症至上肢功能) → 延至 2026-11-22；CTGTAC 2026-07-29 就心肌病變療效投票 3 贊成 / 9 反對"
 },
 {
  "ticker": "REPL",
  "company": "Replimune",
  "drug": "RP1 / vusolimogene oderparepvec (Tudriqev, 合併 nivolumab)",
  "ind": "抗 PD-1 後進展的不可切除晚期皮膚黑色素瘤",
  "baseline_status": "已獲批 — 2026-08-06 (加速批准)",
  "baseline_next": "上市；IGNYTE-3 確認性試驗",
  "baseline_date": "持續",
  "baseline_other": "本次未核實",
  "baseline_fda": "BLA → 2025-07 CRL → 重交 → 2026-04-10 第二次 CRL (證據不足) → Class 1 重交 2026-06-26 受理 (目標 8/2) → ODAC 2026-07-30 投票 10:3 支持 → 2026-08-06 加速批准 Tudriqev"
 },
 {
  "ticker": "ONC",
  "company": "BeOne Medicines",
  "drug": "Sonrotoclax (Beqalzi)",
  "ind": "R/R 套細胞淋巴瘤 (BTKi 後，≥2 線)",
  "baseline_status": "已獲批 — 2026-05-13 (加速批准)",
  "baseline_next": "CLL sNDA (CELESTIAL-TNCLL)；上市",
  "baseline_date": "2027",
  "baseline_other": "中國：本次未核實",
  "baseline_fda": "NDA 優先審查；2026-05-13 加速批准 Beqalzi，十年來首個新 BCL2 抑制劑"
 },
 {
  "ticker": "TEVA",
  "company": "Teva",
  "drug": "TEV-'749 (olanzapine LAI, 每月 SC)",
  "ind": "精神分裂症 (成人)",
  "baseline_status": "審批中(無PDUFA) — 推算 2026 Q4",
  "baseline_next": "FDA 決定；EMA 意見",
  "baseline_date": "約 2026-10 至 12 (估算)",
  "baseline_other": "EMA MAA 2026-05-21 受理",
  "baseline_fda": "NDA 2025-12-09 遞交；2026-02-20 受理 (標準審查，推算約 2026-10)；PDUFA 未公開"
 },
 {
  "ticker": "VTRS",
  "company": "Viatris",
  "drug": "MR-141 (phentolamine 眼藥水 0.75%)",
  "ind": "老花眼",
  "baseline_status": "審批中(有PDUFA) — 2026-10-17",
  "baseline_next": "PDUFA 決定",
  "baseline_date": "2026-10-17",
  "baseline_other": "本次未核實",
  "baseline_fda": "sNDA 2026-02-25 受理；PDUFA 2026-10-17"
 },
 {
  "ticker": "QURE",
  "company": "uniQure",
  "drug": "AMT-130 (AAV5 miHTT)",
  "ind": "亨廷頓病",
  "baseline_status": "未遞交 — BLA 計劃 2026 Q3 (即將)",
  "baseline_next": "BLA 遞交 (美國) 及 MHRA 申請，均目標 2026 Q3；FDA 受理及 PDUFA",
  "baseline_date": "2026 Q3/Q4 遞交；約 2027 年中決定",
  "baseline_other": "本次未核實",
  "baseline_fda": "2025-11 FDA 質疑外部對照 → Type B 會議後 FDA 轉向：接受 3 年數據作加速批准主要依據、cUHDRS 為中期臨床終點；BLA 計劃 2026 Q3 遞交 (滾動)；確認性研究採同期標準治療對照"
 },
 {
  "ticker": "PTCT",
  "company": "PTC Therapeutics",
  "drug": "Vatiquinone",
  "ind": "Friedreich 共濟失調 (兒童)",
  "baseline_status": "CRL — 2025-08-19 (需新研究)",
  "baseline_next": "PROVE-FA 啟動 (2026 Q3)；24 個月追蹤",
  "baseline_date": "2028+",
  "baseline_other": "本次未核實",
  "baseline_fda": "2025-08-19 CRL (療效證據不足)；2025-12 Type C 會議：FDA 要求額外研究；2026-04 與 FDA 溝通新研究路徑；PROVE-FA 新研究目標 2026 Q3 啟動 (24 個月追蹤)"
 },
 {
  "ticker": "MLYS",
  "company": "Mineralys",
  "drug": "Lorundrostat",
  "ind": "高血壓 (合併其他降壓藥；聚焦抗藥性高血壓)",
  "baseline_status": "審批中(有PDUFA) — 2026-12-22",
  "baseline_next": "PDUFA 決定",
  "baseline_date": "2026-12-22",
  "baseline_other": "本次未核實",
  "baseline_fda": "NDA 2026-03 受理；PDUFA 2026-12-22"
 },
 {
  "ticker": "OTLK",
  "company": "Outlook Therapeutics",
  "drug": "ONS-5010 / Lytenava (bevacizumab-vikg)",
  "ind": "濕性 AMD",
  "baseline_status": "已獲批 — 2026-07-24",
  "baseline_next": "上市與供應；BPCIA 獨佔",
  "baseline_date": "持續",
  "baseline_other": "歐盟/英國：Lytenava 已獲批 (2024)",
  "baseline_fda": "2023-08 CRL (CMC) → 2025-08-27 第二次 CRL (療效證據) → 2025-12-30/31 第三次 CRL (OND 認定療效成立，餘標籤問題) → 2026-03 Type A / 2026-04 正式爭議解決 → 2026-06 重交 (Class 1) 受理，PDUFA 2026-07-29 → 2026-07-24 獲批 Lytenava，首個且唯一眼科專用 bevacizumab；預期 12 年 BPCIA 參考產品獨佔期"
 },
 {
  "ticker": "ZLDPF",
  "company": "Zealand Pharma",
  "drug": "Glepaglutide (GLP-2)",
  "ind": "短腸症候群",
  "baseline_status": "CRL — 2024-12-19 (需新 Ph3)",
  "baseline_next": "新 Ph3 讀數",
  "baseline_date": "2027-28",
  "baseline_other": "EMA MAA 曾遞交；本次未核實現況",
  "baseline_fda": "2024-12-19 CRL (擬上市劑量療效/安全證據不足；要求額外 Ph3)"
 },
 {
  "ticker": "GRFS",
  "company": "Grifols",
  "drug": "Fibrinogen human-chmt (Fesilty, BT524)",
  "ind": "先天性纖維蛋白原缺乏症急性出血 (成人及兒童)",
  "baseline_status": "已獲批 — 2025-12-16",
  "baseline_next": "上市放量",
  "baseline_date": "持續",
  "baseline_other": "歐盟：Biotest 生產 (德國)；本次未核實 EU 狀態",
  "baseline_fda": "BLA；2025-12-16 獲批 Fesilty (公司公告 12-19)；2026-06-15 美國上市"
 },
 {
  "ticker": "RGNX",
  "company": "Regenxbio",
  "drug": "RGX-121 / clemidsogene lanparvovec",
  "ind": "Hunter 症候群 (MPS II)",
  "baseline_status": "CRL — 2026-02-07；Clinical hold — 2026-08-24",
  "baseline_next": "解除 hold / 安全調查；BLA 重交路徑 (短期無)",
  "baseline_date": "2027+ (無近期事件)",
  "baseline_other": "本次未核實",
  "baseline_fda": "BLA 加速批准；PDUFA 2025-11 → 延至 2026-02-08 → 2026-02-07 CRL (02-09 公告)：神經型族群定義、外部對照可比性、替代終點適當性；2026-01 因 RGX-111 SAE 部分臨床暫停；2026-08-24 FDA 再度 clinical hold：CAMPSIITE 5 名受試者 (給藥後 3-6 年) 脊椎 MRI 發現無症狀小結節/囊性腫塊 (判定非嚴重、可能良性)；公司稱短期內不會重交 BLA"
 },
 {
  "ticker": "CELC",
  "company": "Celcuity",
  "drug": "Gedatolisib (Revtorpyk)",
  "ind": "HR+/HER2- PIK3CA 野生型晚期乳癌 (合併 fulvestrant ± palbociclib)",
  "baseline_status": "已獲批 — 2026-07-14",
  "baseline_next": "PIK3CA-mut sNDA；上市",
  "baseline_date": "2027",
  "baseline_other": "本次未核實",
  "baseline_fda": "NDA 優先審查；PDUFA 2026-07-17；2026-07-14 獲批 Revtorpyk，首個 pan-PI3K/mTOR 抑制劑"
 },
 {
  "ticker": "CGEM",
  "company": "Cullinan / Taiho",
  "drug": "Zipalertinib",
  "ind": "EGFR exon 20 插入突變 NSCLC (鉑類後，± amivantamab)",
  "baseline_status": "審批中(有PDUFA) — 2027-02-27",
  "baseline_next": "PDUFA 決定",
  "baseline_date": "2027-02-27",
  "baseline_other": "本次未核實",
  "baseline_fda": "滾動 NDA 2025-11 啟動 → 2026-02 完成 → 2026-04-28 受理；PDUFA 2027-02-27；BTD (2021)"
 },
 {
  "ticker": "SVRA",
  "company": "Savara",
  "drug": "Molgramostim 吸入液 (Molbreevi)",
  "ind": "自體免疫性肺泡蛋白沉積症 (aPAP)",
  "baseline_status": "審批中(有PDUFA) — 2026-11-22",
  "baseline_next": "PDUFA 決定",
  "baseline_date": "2026-11-22",
  "baseline_other": "EMA：MAA 審查中，公司窗口 2027 Q1；MHRA 2026 Q4；Molbreevi 為 FDA/EMA 有條件接受商品名",
  "baseline_fda": "2025-08 RTF → 重交 → 受理 (優先審查)；PDUFA 2026-08-22 → 回應資訊要求構成重大修訂 → 延至 2026-11-22；FDA 未提出安全/療效/生產疑慮"
 },
 {
  "ticker": "DYN",
  "company": "Dyne Therapeutics",
  "drug": "Z-rostudirsen / DYNE-251",
  "ind": "DMD exon 51 跳讀",
  "baseline_status": "審批中(有PDUFA) — 2027-01-21",
  "baseline_next": "PDUFA 決定",
  "baseline_date": "2027-01-21",
  "baseline_other": "本次未核實",
  "baseline_fda": "BLA 2026-05-26 遞交 (加速批准，dystrophin 替代終點)；2026-07-20 受理 (優先審查)；PDUFA 2027-01-21"
 },
 {
  "ticker": "ATRA",
  "company": "Atara Biotherapeutics",
  "drug": "Tabelecleucel / tab-cel (Ebvallo)",
  "ind": "EBV+ 移植後淋巴增生疾病 (≥2 歲，一線後)",
  "baseline_status": "CRL — 2026-01 (需新研究)",
  "baseline_next": "新隨機研究或計劃收縮",
  "baseline_date": "2027+",
  "baseline_other": "歐盟：Ebvallo 已獲批 (2022)",
  "baseline_fda": "2025-01 CRL (第三方廠) → 2025-07 重交受理 → 2026-01-09 第二次 CRL：GMP 問題已解決、無安全疑慮，但 FDA 不再接受單臂 ALLELE 支持加速批准，要求新研究；2026-05-07 Type A 討論預先指定歷史對照方案"
 },
 {
  "ticker": "ANNX",
  "company": "Annexon",
  "drug": "Tanruprubart (ANX005, C1q)",
  "ind": "Guillain-Barré 症候群",
  "baseline_status": "未遞交 — BLA 計劃 2026 Q4",
  "baseline_next": "BLA 遞交 (Q4 2026)；CHMP 意見",
  "baseline_date": "2026 Q4 (遞交)；2027 H2 (決定)",
  "baseline_other": "EMA：MAA 2026-01-08 遞交",
  "baseline_fda": "美國 BLA 尚未遞交——計劃 2026 Q4 (納入 FORWARD 數據)"
 },
 {
  "ticker": "ACHV",
  "company": "Achieve Life Sciences",
  "drug": "Cytisinicline",
  "ind": "尼古丁依賴 (戒煙；另戒電子煙)",
  "baseline_status": "CRL — 2026-06-20 (生產/標籤)",
  "baseline_next": "NDA 重交 (Q4 2026) → FDA 決定",
  "baseline_date": "2026 Q4 (重交)；2027 H1 (決定)",
  "baseline_other": "本次未核實",
  "baseline_fda": "NDA 2025-06 遞交；PDUFA 2026-06-20；2026-06-20 CRL (公司公告 06-22)：第三方生產廠 cGMP 檢查觀察未結 + 最終標籤未完成，無療效/安全缺陷；計劃 2026 Q4 以 Adare 為主要生產商重交，潛在 2027 H1 獲批"
 },
 {
  "ticker": "BMRN",
  "company": "BioMarin",
  "drug": "Palynziq (pegvaliase) — 青少年",
  "ind": "PKU 12-17 歲",
  "baseline_status": "已獲批 — 2026-02-27",
  "baseline_next": "青少年滲透",
  "baseline_date": "持續",
  "baseline_other": "本次未核實",
  "baseline_fda": "sBLA 2025-10 受理 (優先審查)；PDUFA 2026-02-28；2026-02-27 獲批"
 },
 {
  "ticker": "COGT",
  "company": "Cogent Biosciences",
  "drug": "Bezuclastinib",
  "ind": "(1) 非晚期系統性肥大細胞增多症 (NonAdvSM)；(2) AdvSM；(3) GIST 二線 (合併 sunitinib)",
  "baseline_status": "審批中(有PDUFA) — 2026-11-30 (GIST) / 2026-12-30 (NonAdvSM)",
  "baseline_next": "GIST PDUFA 11/30；NonAdvSM PDUFA 12/30；AdvSM 受理",
  "baseline_date": "2026-11-30",
  "baseline_other": "本次未核實",
  "baseline_fda": "NonAdvSM NDA 受理，PDUFA 2026-12-30 (不召開 AdCom、無潛在審查問題)；GIST NDA 2026-05-28 受理 (優先審查)，PDUFA 2026-11-30；AdvSM NDA 2026-06-30 遞交，受理/日期待核 —— 三項平行審查"
 },
 {
  "ticker": "SGIOY",
  "company": "Shionogi",
  "drug": "Ensitrelvir (Xocova) — 暴露後預防【附件將 zuranolone 併入此行有誤：Zurzuvae 為 Biogen/Sage 產品，美國 2023 已獲批】",
  "ind": "COVID-19 暴露後預防 (≥12 歲)",
  "baseline_status": "已獲批 — 2026-05-29",
  "baseline_next": "美國採用；治療適應症申報",
  "baseline_date": "持續",
  "baseline_other": "日本：PEP 補充適應症 2026-03-23 獲批",
  "baseline_fda": "NDA 2025-09 受理；PDUFA 2026-06-16；提前於 2026-05-29 獲批 (公司公告 06-01)，首個且唯一口服 PEP；2026-07-29 美國供應"
 },
 {
  "ticker": "TLX",
  "company": "Telix",
  "drug": "(1) Pixclara / TLX101-CDx；(2) Zircaix / TLX250-CDx",
  "ind": "(1) 復發/進展神經膠質瘤 PET 顯影；(2) 透明細胞腎細胞癌 PET 顯影",
  "baseline_status": "審批中(有PDUFA) — Pixclara 2026-09-11；Zircaix 未重交",
  "baseline_next": "Pixclara PDUFA；Zircaix 重交",
  "baseline_date": "2026-09-11",
  "baseline_other": "本次未核實",
  "baseline_fda": "Pixclara：2025-04 CRL → Type A → 2026-03 重交 → 2026-04-10 受理；PDUFA 2026-09-11。Zircaix：2025-08 CRL (兩家第三方廠 CMC 缺陷) → Type A 正面 → 重交包正在定稿，尚未重交"
 },
 {
  "ticker": "MKKGY",
  "company": "Merck KGaA / EMD Serono",
  "drug": "Pimicotinib (CSF-1R, 授權自 Abbisko)",
  "ind": "腱鞘巨細胞瘤 (TGCT)",
  "baseline_status": "審批中(無PDUFA) — 推算 2026 Q4",
  "baseline_next": "FDA 決定",
  "baseline_date": "約 2026-11 (估算)",
  "baseline_other": "中國 NMPA 2025-12-21 批准；加拿大 2026-06-12 批准；EMA PRIME",
  "baseline_fda": "NDA 2026-01-12 受理 (標準審查，推算約 2026-11)；PDUFA 未公開；BTD"
 },
 {
  "ticker": "NAMS",
  "company": "NewAmsterdam Pharma",
  "drug": "Obicetrapib (± ezetimibe FDC)",
  "ind": "原發性高膽固醇血症 / ASCVD",
  "baseline_status": "未遞交 (美國) — 歐盟 CHMP 正面",
  "baseline_next": "PREVAIL 期中 (Q4 2026)；EC 批准；美國 NDA 時程",
  "baseline_date": "2026 Q4",
  "baseline_other": "EMA：MAA 2025 受理；CHMP 2026-07-24 正面意見 (Ubeslo 單方 / Evlarco FDC)；EC 決定 2026 H2；MHRA、Swissmedic 2026 H2",
  "baseline_fda": "美國 NDA 未遞交——公司等待 PREVAIL"
 },
 {
  "ticker": "RCKT",
  "company": "Rocket Pharmaceuticals",
  "drug": "Kresladi / marnetegragene autotemcel",
  "ind": "重度白血球黏附缺陷症 I 型 (LAD-I，兒童)",
  "baseline_status": "已獲批 — 2026-03-26 (加速批准)",
  "baseline_next": "PRV 出售；RP-A501 Danon 關鍵試驗",
  "baseline_date": "2026 H2",
  "baseline_other": "本次未核實",
  "baseline_fda": "2024-06 CRL (CMC) → 重交 → PDUFA 2026-03-28 → 2026-03-26 加速批准 (公司公告 03-27)，首個 LAD-I 基因療法；獲罕見兒科疾病優先審查券"
 }
]

log(`核實 ${ITEMS.length} 個標的的美國與海外監管狀態 (截至 ${AS_OF})`)

const results = await pipeline(
  ITEMS,
  (item) => agent(
`你是監管事務分析師。今日為 ${AS_OF}。用 WebSearch 核實以下標的的最新監管狀態，只採信一手或高可信來源 (FDA.gov、公司新聞稿/IR、SEC 8-K/10-Q、EMA/EC/MHRA/PMDA/NMPA 官方、主要醫藥媒體)。

標的：${item.company} (${item.ticker}) — ${item.drug}
適應症：${item.ind}

已有基準線 (可能過時或有誤，請獨立核實，不要照抄)：
- 美國狀態：${item.baseline_status}
- 監管歷史：${item.baseline_fda}
- 海外：${item.baseline_other}
- 下一催化劑：${item.baseline_next} / ${item.baseline_date}

必須查明：
1. 截至 ${AS_OF} 美國最新狀態：已獲批 (給 FDA 行動日，注意公司新聞稿常晚一日)／有 PDUFA 的審批中 (給日期)／已遞交但 PDUFA 未公開／CRL 或 RTF／撤回或終止／尚未遞交。
2. 海外監管：EMA/CHMP 意見或 EC 決定、MHRA、PMDA(日本)、NMPA(中國)。查不到就寫「未查得公開紀錄」，不要臆測。
3. 下一個「尚未發生」的催化劑及其日期或窗口。已發生的不算。
4. 若你的結論與基準線實質衝突 (例如基準線說審批中但實際已獲批/已收 CRL)，把 conflicts_baseline 設為 true 並說明。

寧可標「不明」也不要編造日期。`,
    { label: `核實:${item.ticker}:${item.drug.slice(0, 18)}`, phase: '核實', schema: S }
  ),
  (res, item) => {
    if (!res) return null
    if (!res.conflicts_baseline && res.confidence === '高') return { item, res, verified: true }
    return agent(
`你是對抗性複核員。今日 ${AS_OF}。有人宣稱：

${item.company} (${item.ticker}) — ${item.drug}
新結論：${res.us_status}${res.us_status_date ? ' @ ' + res.us_status_date : ''} — ${res.us_detail}
與之衝突的舊基準線：${item.baseline_status}
其引用來源：${res.sources}

用 WebSearch 嘗試「推翻」這個新結論。若找到一手來源明確支持新結論，refuted=true (代表基準線確實錯、新結論成立)；若新結論站不住或找不到佐證，refuted=false 並在 corrected_* 給出你認為正確的狀態與日期。不確定時傾向 refuted=false。`,
      { label: `複核:${item.ticker}`, phase: '複核', schema: V }
    ).then(v => ({ item, res, verify: v, verified: false }))
  }
)

const ok = results.filter(Boolean)
log(`完成 ${ok.length}/${ITEMS.length}；其中 ${ok.filter(r => !r.verified).length} 項經對抗性複核`)
return ok
