import json
class DataClient:
    def __init__(self):
        self.company_summaries = None
        self.company_analysis = None
        self.stocks = [
            "ACB","BCM","BID","BVH","CTG","FPT","GAS","GVR","HDB","HPG",
            "MBB","MSN","MWG","PLX","POW","SAB","SSI","STB","TCB","TPB",
            "VCB","VHM","VIB","VIC","VJC","VNM","VPB","VRE",
            "AAA","ANV","ASM","BCG","BSI","BMP","CII","CMG","CSM",
            "CSV","DBC","DCM","DGC","DIG","DPM","DXG","EVF","FRT","GEX",
            "GMD","HAH","HSG","IDC","IJC","KBC","KDH","LPB","MBS","MSB",
            "NKG","NLG","NT2","OCB","PAN","PC1","PDR","PET","PHR","PVD",
            "PVS","PVT","REE","SBT","SHB","SJS","SZC","TCH","TCM","TNG",
            "VCG","VGC","VHC","VIX","VND","VOS","YEG"
        ]

    def load_all_company_info(self):

        company_summaries = [
            json.load(open(f"/root/code/hackathon/virtual-bank-agentic-consultant/backend/app/data/company/{key}/summary.json", "r", encoding="utf-8")) for key in self.stocks
        ]

        
        self.company_summaries = dict(zip(
            self.stocks,
            company_summaries
        ))

    def load_all_company_analysis(self):
        company_analysis = [
            json.load(open(f"/root/code/hackathon/virtual-bank-agentic-consultant/backend/app/data/stock/{key}/ohlcv_analysis_data.json", "r", encoding="utf-8")) for key in self.stocks
        ]

        self.company_analysis = dict(zip(
            self.stocks,
            company_analysis
        ))
        