const {Document,Packer,Paragraph,TextRun,HeadingLevel,Table,TableRow,TableCell,WidthType,ShadingType,AlignmentType,BorderStyle,PageOrientation,LevelFormat,convertInchesToTwip}=require('docx');
const fs=require('fs');
const F="Times New Roman", CJK="PMingLiU";
const W=15840-2*1080;             // landscape Letter content width (DXA)

const t=(s,o={})=>new TextRun({text:s,font:{name:F,eastAsia:CJK},size:o.sz||20,bold:o.b,italics:o.i,color:o.c});
const P=(s,o={})=>new Paragraph({children:Array.isArray(s)?s:[t(s,o)],spacing:{after:o.after??100,line:o.line??260},alignment:o.al,indent:o.ind,border:o.border,numbering:o.num});
const H=(s,l)=>new Paragraph({heading:l,spacing:{before:240,after:120},
  children:[new TextRun({text:s,font:{name:F,eastAsia:CJK},bold:true,size:l===HeadingLevel.HEADING_1?28:24,color:l===HeadingLevel.HEADING_1?"1F4E78":"2E75B6"})]});

function table(head,rows,widths,shades){
  const tot=widths.reduce((a,b)=>a+b,0);
  const cw=widths.map(w=>Math.round(w/tot*W));
  cw[cw.length-1]=W-cw.slice(0,-1).reduce((a,b)=>a+b,0);
  const cell=(txt,i,o={})=>new TableCell({width:{size:cw[i],type:WidthType.DXA},
    shading:o.fill?{type:ShadingType.CLEAR,fill:o.fill,color:"auto"}:undefined,
    margins:{top:60,bottom:60,left:90,right:90},
    children:String(txt).split("\n").map((ln,k)=>P(ln,{sz:o.sz||17,b:o.b,c:o.c,after:k===String(txt).split("\n").length-1?0:40,line:230}))});
  return new Table({columnWidths:cw,width:{size:W,type:WidthType.DXA},
    rows:[new TableRow({tableHeader:true,children:head.map((h,i)=>cell(h,i,{b:true,fill:"1F4E78",c:"FFFFFF",sz:17}))}),
      ...rows.map((r,ri)=>new TableRow({children:r.map((v,i)=>cell(v,i,{fill:(shades&&shades[ri])||(ri%2?"F2F6FA":undefined)}))}))]});
}
const bullets={config:[{reference:"b",levels:[{level:0,format:LevelFormat.BULLET,text:"•",alignment:AlignmentType.LEFT,
  style:{paragraph:{indent:{left:convertInchesToTwip(0.28),hanging:convertInchesToTwip(0.18)}}}}]}]};
const B=s=>P(s,{num:{reference:"b",level:0},after:60});

const doc=new Document({numbering:bullets,styles:{default:{document:{run:{font:{name:F,eastAsia:CJK},size:20}}}},
 sections:[{properties:{page:{size:{width:12240,height:15840,orientation:PageOrientation.LANDSCAPE},margin:{top:1080,bottom:1080,left:1080,right:1080}}},children:[

P([t("FDA Pipeline Watchlist R4 — 第三方評論裁決報告",{b:true,sz:34,c:"1F4E78"})],{after:60,al:AlignmentType.CENTER}),
P([t("評論來源：Gemini 與 Grok　│　裁決基準：檔案實際數據　│　報告日：2026-09-05",{sz:19,c:"595959"})],{after:40,al:AlignmentType.CENTER}),
P("",{border:{bottom:{style:BorderStyle.SINGLE,size:8,color:"1F4E78"}},after:200}),

H("一、執行摘要",HeadingLevel.HEADING_1),
P("兩份評論都指出同一件事：檔案已過時。這一點成立，而且我早已聲明——資料知識截點約在 2026 年中，今日已是 2026-09-05，中間有三個月的監管事件未覆蓋。但兩者的品質差距很大。"),
B("Grok 的評論實質上更有價值。它正確識別出多項 PDUFA 已經解決，並給出具體結果與日期，建議亦可直接執行。"),
B("Gemini 的評論有一個系統性錯誤：它把 13 個已經過去 5 至 9 個月的 PDUFA 日期，當成「即將發生的關鍵催化劑」。這不是小瑕疵，而是會直接導致錯誤交易時機的判斷。"),
B("Gemini 的核心結論「FDA 審查重心由療效轉向 CMC」不獲檔案數據支持，屬抽樣偏差。"),
B("兩者都遺漏了檔案中最需要即時處理的一批：21 行 PDUFA 已過但結果未知的個股。"),
P([t("重要限制：",{b:true}),t("本環境的網絡政策封鎖 api.fda.gov、clinicaltrials.gov 及 fda.gov，因此 Grok 提出的批文事實（藥名、批准日期）我無法核實。下文會明確區分「已核實」與「未能核實」。",{b:false})]),

H("二、Gemini 的時間框架錯誤（最嚴重問題）",HeadingLevel.HEADING_1),
P("Gemini 將以下事件列在「即將發生的關鍵 PDUFA 與催化劑時間點」標題之下。以 2026-09-05 計，14 個帶明確日期的事件中，13 個已經過去。"),
table(["PDUFA 日期","公司","藥物","Gemini 的定性","實際狀態（距今）"],[
 ["2025-12-16","GSK","Depemokimab","2025 Q4 最終決策","已過 8.7 個月"],
 ["2025-12-20","RYTM","Imcivree 下丘腦肥胖","2025 Q4 最終決策","已過 8.5 個月"],
 ["2025-12-28","SNY","Tolebrutinib","（列為安全性風險）","已過 8.3 個月，且再度延期"],
 ["2025-12-30","CORT","Relacorilant","2025 Q4 最終決策","已過 8.2 個月"],
 ["2025-12-31","OTLK","ONS-5010","2025 Q4 最終決策","已過 8.2 個月"],
 ["2026-01-05","DNLI","Tividenofusp alfa","2026 Q1 集中審批期","已過 8.0 個月"],
 ["2026-01-13","TVTX","Filspari sNDA","2026 Q1 集中審批期","已過 7.7 個月"],
 ["2026-02-08","RGNX","RGX-121","2026 Q1 集中審批期","已過 6.9 個月"],
 ["2026-03-28","RCKT","Kresladi","2026 Q1 集中審批期","已過 5.3 個月"],
 ["2026-04-10","REPL","RP1","2026 Q1 集中審批期","已過 4.9 個月"],
 ["2026-06-05","PFE / ARVN","Vepdegestrant","「2026 年中至年底」","已過 3.0 個月"],
 ["2026-06-20","ACHV","Cytisinicline","「2026 年中至年底」","已過 2.5 個月"],
 ["2026-09-18","NUVL","Zidesamtinib","「2026 年中至年底」","唯一真正未來：13 日後"],
],[13,9,16,17,20],[null,null,null,null,null,null,null,null,null,null,null,null,"C6E0B4"]),
P([t("自相矛盾之處：",{b:true}),t("Gemini 自己引用了檔案對 PFE/ARVN 與 ACHV 的註記「排程上日期已過，結果待核實」，卻仍把兩者放在「即將發生」的標題下。它讀到了警示，但沒有據此修正分類。",{})],{after:80}),
P([t("另一處把已發生講成未來風險：",{b:true}),t("Gemini 稱「Atara 面臨 2026 年初收到第二次 CRL 的高風險」。檔案已明確記載 2nd CRL Jan 2026 為已發生事實。同樣，它稱「Novo CagriSema 預計於 2026 年初提交」，而 2026 年初已過去八個月。",{})]),

H("三、Gemini 核心結論的抽樣偏差",HeadingLevel.HEADING_1),
P("Gemini 的總結是：「FDA 明顯將審查重心從單一的療效指標，轉向對生產製程（CMC）、真實世界證據對照的嚴謹度，以及長期總體生存期（OS）數據的完整性。」我對全部 82 行審批中項目做了阻力歸因，結果不支持這個推論。"),
table(["阻力類別","行數","佔比","涉及公司"],[
 ["無已知阻力","66","80.5%","絕大多數大型藥廠的乾淨 Ph3 遞交案"],
 ["其他 CRL / RTF","7","8.5%","CAPR、OTLK、PTCT、REPL、SVRA、TLX、ZLDPF"],
 ["CMC / 第三方生產","5","6.1%","ATRA、DSNKY、RARE、RCKT、SRRK"],
 ["對照組 / 單一試驗設計","2","2.4%","ANNX、QURE"],
 ["安全性","1","1.2%","SNY"],
 ["OS / 療效未達標","1","1.2%","SMMT"],
],[22,8,8,62]),
P("CMC 相關僅佔 6.1%，八成個案沒有任何已知監管阻力。更關鍵的是，這個檔案本身是策展樣本，我在編製時刻意收錄了具 CRL 歷史的個案作為風險示例，因此樣本對「有問題的個案」存在系統性過度代表。用這樣的樣本去推論 FDA 的政策方向，方法上不成立。"),
P("Gemini 亦漏數了 CMC 群組的成員。它只點名 SRRK、ATRA、RCKT 三家，實際應為五家——遺漏了 RARE（UX111 因 CMC 收 CRL）與 DSNKY（patritumab 因生產問題收 CRL）。"),

H("四、Gemini 準確的部分",HeadingLevel.HEADING_1),
P("以下歸因與檔案完全吻合，應予肯定："),
B("CMC／第三方代工為 CRL 主因而非療效不佳——SRRK（Catalent 灌裝廠）、ATRA（第三方生產）、RCKT（CMC）三例準確。"),
B("OS 數據不成熟的否決風險——SMMT ivonescimab（HARMONi OS 未達統計顯著）與 DSNKY patritumab（HERTHENA-Lung02 OS 不顯著）兩例準確。"),
B("外部對照組合規爭議——QURE AMT-130（FDA 質疑外部對照）與 ANNX tanruprubart（單一孟加拉試驗加真實世界對照）兩例準確。"),
B("SNY tolebrutinib 因肝安全性反覆延期——準確。"),
B("OTLK 第三次 CRL、SVRA 收 RTF 後重新提交——準確。"),
B("檔案只涵蓋 FDA，不含 EMA 或 NMPA——準確，這確為檔案的既有範圍限制。"),

H("五、Grok 的評論：品質較高，但含未能核實的事實",HeadingLevel.HEADING_1),
P("Grok 正確地把時間軸擺對了，並指出多項已解決的審批。它同時提出了具體的結論性事實，包括商品名與批准日期。這些我在本環境無法查證。"),
table(["Grok 的主張","類型","我的核實結果"],[
 ["LLY orforglipron 於 2026-04-01 以 Foundayo 獲批","批文事實","無法核實。此日期落在我的知識窗口內而我的資料缺載，代表兩種可能：我的策展資料有漏，或 Grok 有誤。須以 FDA 公告確認。"],
 ["PFE / ARVN vepdegestrant 於 2026-05-01 以 Veppanu 獲批","批文事實","無法核實。同上，落在我的知識窗口內而未載。"],
 ["TAK oveporexton 於 2026-08-05 以 Orzeyful 獲批","批文事實","無法核實。晚於我的知識截點。"],
 ["TAK / PTGX rusfertide 於 2026-08-28 以 Mimrylo 獲批","批文事實","無法核實。晚於我的知識截點。"],
 ["GSK depemokimab 於 2025-12-16 以 Exdensur 獲批（僅重度嗜酸性哮喘，CRSwNP 未批）","批文事實","無法核實。檔案僅記 PDUFA 日期，未記結果。"],
 ["SNY tolebrutinib 美國仍未決；歐盟 2026-06 以 Cenrifki 獲批","批文事實","無法核實。與檔案「再度延期」的記載方向一致。"],
 ["SRRK apitegromab PDUFA 2026-09-30 仍有效","前瞻日期","無法核實，但與檔案「重新提交、decision 2026」一致，屬合理。"],
 ["RARE UX111 PDUFA 2026-09-19","前瞻日期","無法核實，與檔案一致，屬合理。"],
 ["MRK Winrevair sNDA PDUFA 約 2026-09-21","前瞻日期","無法核實，與檔案 sNDA decisions 2026 一致，屬合理。"],
],[34,10,56]),
P([t("風險提示：",{b:true}),t("商品名（Foundayo、Veppanu、Orzeyful、Mimrylo、Exdensur、Cenrifki）屬於語言模型最容易虛構的細節類型。這些名稱若真確，可直接在 FDA 的 Drugs@FDA 或公司新聞稿查到；若查不到，整條主張即應作廢。在核實之前，不應據此調整持倉。",{})]),

H("六、Grok 的批評中我不完全同意的一點",HeadingLevel.HEADING_1),
P("Grok 稱排程格「稀疏、標籤不一致、用途不大」。稀疏是事實，但成因不是格線設計，而是源資料本身缺日期。我實測過："),
B("27 行的已發生事實在原文中根本沒有日期（例如「CREST Ph3 positive」、「ROCKET Ph3 done」），無論格線推多遠都無法定位到某個月。"),
B("25 行的事實早於 2025-09，超出一年回溯範圍，這批已在狀態欄以「早於格線」逐項列明事件類型與年份，並未丟失。"),
B("其餘 78 行在格線左側有已發生標記，55 行在右側有待發生標記。以現有源資料而言，覆蓋率已接近上限。"),
P("要真正填滿格線，需要逐隻藥回填試驗讀數的確切月份，這必須連接 ClinicalTrials.gov，而本環境被封鎖。Grok 的觀察正確，但歸因錯了。"),

H("七、兩者都遺漏的三項",HeadingLevel.HEADING_1),
P([t("1　21 行「PDUFA 已過但結果未知」——最高優先的核實佇列",{b:true})],{after:60}),
P("檔案中有 21 行沒有任何待發生項目，原因是它們的 PDUFA 日期已過而結果未載。這批正是資訊落差最大、最可能已經發生股價重估的個股，包括 SNY、GSK、RYTM、CORT、DNLI、TVTX、RGNX、REPL、OTLK、RCKT、ATRA、PFE、ARVN、ACHV。兩份評論都沒有把它們列為獨立的行動項。"),
P([t("2　風險分層的量化差距",{b:true})],{after:60}),
P("以檔案的 PoS 估算，無已知阻力的 66 行平均成功率 84.5%，有已知阻力的 16 行平均 53.6%，相差 30.9 個百分點。這是一個可直接用於倉位分層的數字，兩份評論都只作定性描述，沒有量化。"),
P([t("3　TAM 集中度",{b:true})],{after:60}),
P("在 61 行真正未發生的催化劑中，LLY orforglipron 與 NVO CagriSema 各自對應約 1,500 億美元的 TAM，單是這兩項就遠超其餘所有項目的總和。組合層面的催化劑風險高度集中於肥胖賽道，而非分散於各治療領域。若 Grok 所述 orforglipron 已於 4 月獲批屬實，這個集中度已經釋放了一半。"),

H("八、建議行動",HeadingLevel.HEADING_1),
table(["優先次序","行動","理由"],[
 ["1（即時）","核實 Grok 提出的六項批文事實，以 Drugs@FDA 與公司新聞稿為準","若屬實，檔案有六行需由「審批中」改為「已獲批」，PoS 一併改為 100%"],
 ["2（即時）","清查 21 行「PDUFA 已過但結果未知」","資訊落差最大，股價可能已完成重估"],
 ["3（本週）","為檔案加入 Grok 建議的四個欄位：曾收 CRL（是／否＋原因）、生產廠風險、加速批准對傳統批准、是否預期召開 AdCom","此四項是目前 PoS 模型未納入的真實閘門"],
 ["4（本週）","下調有未結 CMC 或檢查問題個案的 PoS","現行模型只按階段與治療領域調整，未對生產風險扣分"],
 ["5（需網絡）","以 openFDA 與 ClinicalTrials.gov 自動回填所有缺失日期","可一次過解決 27 行無日期與檔案整體時效問題"],
],[12,44,44]),
P([t("關於第 5 項：",{b:true}),t("本環境的出口政策封鎖了 api.fda.gov 與 clinicaltrials.gov。生成腳本已寫好，只要在有網絡的環境執行，即可把整份檔案由策展資料升級為 API 實時資料，並自動覆蓋全部美國上巿及 ADR 藥廠，而非現時的 178 家策展樣本。",{})]),

P("",{border:{bottom:{style:BorderStyle.SINGLE,size:6,color:"BFBFBF"}},after:120}),
P([t("免責聲明：本報告為研究參考，不構成投資建議。檔案數據為策展樣本，知識截點約 2026 年中；標示「無法核實」的內容必須經一手來源確認後方可使用。",{i:true,sz:17,c:"595959"})]),
]}]});
Packer.toBuffer(doc).then(b=>{fs.writeFileSync("FDA_R4_第三方評論裁決報告.docx",b);console.log("written",b.length)});
