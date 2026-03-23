
import joblib

class ModelClient:
    def __init__(self):
        self.loaded_model = joblib.load("/root/code/hackathon/virtual-bank-agentic-consultant/backend/app/checkpoints/stock_clustering_model.pkl")
        self.loaded_scaler = joblib.load("/root/code/hackathon/virtual-bank-agentic-consultant/backend/app/checkpoints/scaler.pkl")
    
    def load(self):
        pass
        