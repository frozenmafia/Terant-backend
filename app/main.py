from fastapi import FastAPI, Request
from pydantic import BaseModel
import json

app = FastAPI()


class SensorData(BaseModel):
    Voltage: str
    Current: str
    Power: str
    Energy: str
    Frequency: str
    PF: str


@app.get("/")
def get_home():
    return {"message": "Welcome to the homepage!"}

@app.post("/receive_data")
async def receive_data(request: Request, sensor_data: SensorData):
    # Handle received data, you can perform any processing or saving here
    print("Received data:", sensor_data.dict())
    print(sensor_data.Voltage)

    # You can also send a response back if needed
    return {"message": "Data received successfully"}
