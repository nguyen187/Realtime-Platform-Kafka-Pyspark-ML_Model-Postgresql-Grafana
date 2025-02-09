from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import joblib
from keras.models import load_model
import os
# from keras.src.legacy.saving import legacy_h5_format
from contextlib import asynccontextmanager

# FastAPI app instance

# Paths to your model and scaler
model_path = "./model/network_2.h5"
scale_path = "./model/scale_2.pkl"
print(model_path)
# Load the model and scaler


# Define input and output schemas
class InputData(BaseModel):
    data: list[list[float]]

class PredictionResponse(BaseModel):
    Sugar_feed_rate: float
    Water_for_injection: float
    Substrate_concentration: float
    Temperature: float
    Dissolved_oxygen_concentration: float
    Vessel_Volume: float
    pH: float
    Predict: float

ml_models = {}
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    ml_models["predict"] = load_model(model_path)
    ml_models["scale"] = joblib.load(scale_path)
    
    yield
    # Clean up the ML models and release the resources
    ml_models.clear()

app = FastAPI(lifespan=lifespan)

# Prediction endpoint
@app.post("/predict", response_model=list[PredictionResponse])
async def predict(input_data: InputData):
    data = np.array(input_data.data)
    
    # Data preprocessing
    data.T[0] = data.T[0] * data.T[2]  # Example transformation
    data = np.delete(data, 2, axis=1)
    data = np.insert(data, 6, data.T[2], axis=1)
    
    # Scaling the data
    data_trans = ml_models["scale"].transform(data)
    
    # Making predictions
    y_hat = ml_models["predict"].predict(data_trans)
    
    # Form the output in the specified format
    result = []
    for i in range(len(y_hat)):
        row = {
            "Sugar_feed_rate": float(input_data.data[i][0]),
            "Water_for_injection": float(input_data.data[i][1]),
            "Substrate_concentration": float(input_data.data[i][2]),
            "Temperature": float(input_data.data[i][3]),
            "Dissolved_oxygen_concentration": float(input_data.data[i][4]),
            "Vessel_Volume": float(input_data.data[i][5]),
            "pH": float(input_data.data[i][6]),
            "Predict": float(y_hat[i][0])
        }
        result.append(row)

    return result

