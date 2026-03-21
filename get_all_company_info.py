import requests
import json

stocks = [
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

base_url = "http://localhost:8080/api/v1/company/info/"
headers = {'accept': 'application/json'}
all_company_info = {}


for symbol in stocks:
    url = f"{base_url}{symbol}"
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            all_company_info[symbol] = response.json()
            print(f"Done: {symbol}")
        else:
            print(f"Error {response.status_code} at: {symbol}")
            
    except Exception as e:
        print(e)
        
