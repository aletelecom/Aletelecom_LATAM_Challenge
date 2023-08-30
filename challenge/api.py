import fastapi
from fastapi import HTTPException
import pandas as pd
from pydantic import BaseModel
from typing import List, Dict, Any
from pathlib import Path


from challenge.model import DelayModel

app = fastapi.FastAPI()

top_10_features = [
    "OPERA_Latin American Wings", 
    "MES_7",
    "MES_10",
    "OPERA_Grupo LATAM",
    "MES_12",
    "TIPOVUELO_I",
    "MES_4",
    "MES_11",
    "OPERA_Sky Airline",
    "OPERA_Copa Air"
]

delay_model = DelayModel()
BASE_DIR = Path(__file__).resolve(strict=True).parent
model_name = 'LR_Feat_Imp_Balanced_2023-08-26.pkl'
model_folder = 'ml_models'
model_path = BASE_DIR.joinpath('..',model_folder, model_name)

delay_model.load_model(model_path)

class InputData(BaseModel):
    flights: List[Dict[str, Any]]


@app.get("/", status_code=200)
def read_root():
    return {'LATAM Challenge':'Aletelecom'}

@app.get("/health", status_code=200)
async def get_health() -> dict:
    return {
        "status": "OK"
    }

@app.post("/predict", status_code=200)
async def post_predict(input_data: InputData) -> dict:

    if not input_data.flights:
        raise HTTPException(status_code=400, detail='No flight data provided')

    flight_data = pd.DataFrame(input_data.flights)

    try:

        flight_features = delay_model.preprocess(flight_data)
        predictions = delay_model.predict(flight_features)
    
    except ValueError as ve:
        error_message = str(ve)
        if "Unknown column passed" in error_message:
            raise HTTPException(status_code=400, detail="Unknown column")
        else:
            raise HTTPException(status_code=400, detail=error_message)
    
    return {'predict': predictions}