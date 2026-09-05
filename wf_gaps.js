export const meta = {
  name: 'fda-pending-gaps',
  description: 'Close the 13 open unknowns on the FDA pending tab: undisclosed PDUFA dates, unresolved outcomes and un-filed applications',
  phases: [
    { title: '查核', detail: '每個空白一個 agent，只採信一手來源' },
    { title: '複核', detail: '對任何具體日期/結論作對抗性複核' },
  ],
}

const AS_OF = '2026-09-05'

const S = {
  type: 'object',
  properties: {
    ticker: { type: 'string' },
    answer: { type: 'string', enum: ['已查得','未公開','無此事'] },
    status: { type: 'string', description: '截至今日的美國監管狀態，一句中文' },
    date: { type: 'string', description: 'PDUFA 或行動日 YYYY-MM-DD，或窗口如 2026 Q4；未公開則寫「未公開」' },
    ex_us: { type: 'string', description: 'EMA/CHMP/EC/MHRA/PMDA/NMPA 狀態含日期；查無則「未查得公開紀錄」' },
    next_catalyst: { type: 'string', description: '下一個尚未發生的催化劑' },
    confidence: { type: 'string', enum: ['高','中','低'] },
    sources: { type: 'string', description: '來源網域+日期，分號分隔' },
  },
  required: ['ticker','answer','status','date','ex_us','next_catalyst','confidence','sources'],
}

const V = {
  type: 'object',
  properties: {
    holds: { type: 'boolean', description: '原結論是否經得起推翻嘗試' },
    corrected_status: { type: 'string' },
    corrected_date: { type: 'string' },
    reason: { type: 'string' },
  },
  required: ['holds','corrected_status','corrected_date','reason'],
}

const GAPS = [
  { t: 'ABBV', d: 'Tavapadon', q: 'NDA 於 2025-09-26 遞交，AbbVie 指引 2026 上半年決定，但截至今日查不到批准或 CRL 公告。FDA 是否已行動？有無延期、CRL、批准？查 AbbVie 新聞稿、SEC 10-Q/8-K、FDA 2026 novel approvals 名單。' },
  { t: 'NVS', d: 'Ianalumab (Sjögren)', q: 'BLA 已受理並獲優先審查，PDUFA 目標日是否公開？查 Novartis 新聞稿與 6-K。' },
  { t: 'NVO', d: 'Denecimig / Mim8', q: 'BLA 於 2025-09-29 遞交，PDUFA 目標日是否公開？FDA 是否已行動？查 Novo Nordisk 6-K 與新聞稿。' },
  { t: 'NVO', d: 'CagriSema', q: 'NDA 於 2025-12-18 遞交，PDUFA 目標日是否公開？公司指引 2026 年底決定，有無更精確日期？' },
  { t: 'TEVA', d: "TEV-'749 olanzapine LAI", q: 'NDA 於 2026-02-20 受理，PDUFA 目標日是否公開？EMA MAA 進度？' },
  { t: 'MKKGY', d: 'Pimicotinib', q: 'NDA 於 2026-01-12 受理，PDUFA 目標日是否公開？FDA 是否已行動？中國/加拿大以外還有哪些地區已批？' },
  { t: 'LLY', d: 'Orforglipron 第二型糖尿病適應症', q: '肥胖適應症已於 2026-04-01 獲批。T2D 適應症的 NDA 是否已遞交/受理？有無 PDUFA？查 Lilly IR。' },
  { t: 'REGN', d: 'Dupixent CPUO (不明原因慢性搔癢)', q: 'CPUO 適應症的 sBLA 是否已向 FDA 遞交？LIBERTY-CPUO-CHIC Ph3 結果如何？公司指引申報時程為何？' },
  { t: 'AMGN', d: 'Rocatinlimab', q: 'Kyowa Kirin 於 2026-03 因惡性腫瘤安全訊號暫停全部試驗。截至今日計劃是否恢復、終止或有新決定？' },
  { t: 'QURE', d: 'AMT-130', q: '公司指引 2026 Q3 向 FDA 遞交 BLA。截至今日是否已遞交？FDA 是否已受理？MHRA 申請進度？' },
  { t: 'ANNX', d: 'Tanruprubart', q: '公司指引 2026 Q4 遞交美國 BLA。截至今日是否已遞交？EMA MAA (2026-01-08 遞交) 的 CHMP 進度如何？' },
  { t: 'NAMS', d: 'Obicetrapib', q: '美國 NDA 是否已向 FDA 遞交？EC 是否已就 CHMP 2026-07 正面意見作出決定？PREVAIL 期中分析時程？' },
  { t: 'TLX', d: 'Zircaix / TLX250-CDx', q: 'CRL 後的 BLA 重交是否已完成並獲 FDA 受理？有無新 PDUFA？' },
]

log(`查核 ${GAPS.length} 個未決空白（截至 ${AS_OF}）`)

const out = await pipeline(
  GAPS,
  (g) => agent(
`你是監管事務分析師。今日 ${AS_OF}。用 WebSearch 查明以下問題，只採信一手或高可信來源（FDA.gov、公司 IR/新聞稿、SEC 8-K/10-Q/6-K、EMA/EC/MHRA/PMDA/NMPA 官方、主要醫藥媒體）。

標的：${g.t} — ${g.d}
問題：${g.q}

規則：
- 若 PDUFA 或決定日確實未公開，answer 填「未公開」，不要用審查時鐘推算後當作事實。
- 若查得，answer 填「已查得」並給出日期與來源。
- 若該事件根本不存在（例如申請從未遞交），answer 填「無此事」。
- 寧可標未公開也不要編造。`,
    { label: `查核:${g.t}:${g.d.slice(0, 16)}`, phase: '查核', schema: S }
  ),
  (r, g) => {
    if (!r) return null
    if (r.answer !== '已查得') return { g, r, checked: false }
    return agent(
`你是對抗性複核員。今日 ${AS_OF}。有人宣稱：

${g.t} — ${g.d}
狀態：${r.status}
日期：${r.date}
來源：${r.sources}

用 WebSearch 嘗試推翻它。若一手來源明確支持，holds=true；若找不到佐證或找到相反證據，holds=false 並在 corrected_* 給出你認為正確的內容。不確定時傾向 holds=false。`,
      { label: `複核:${g.t}`, phase: '複核', schema: V }
    ).then(v => ({ g, r, v, checked: true }))
  }
)

const ok = out.filter(Boolean)
log(`完成 ${ok.length}/${GAPS.length}`)
return ok
