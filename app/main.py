from fastapi import FastAPI, Depends, HTTPException, File, Body, Request
import json
from typing import Annotated, List, Optional
from fastapi.middleware.cors import CORSMiddleware  # Import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from . import models, database
import logging
import re
app = FastAPI()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from all origins, you can restrict it to specific origins if needed
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Allow various HTTP methods
    allow_headers=["*"],  # Allow all headers
)

class SensorDataCreate(BaseModel):
    Voltage: str
    Current: str
    Power: str
    Energy: str
    Frequency: str
    PF: str
    
    def __str__(self):
        return (
            f"SensorDataCreate(Voltage={self.Voltage}, "
            f"Current={self.Current}, Power={self.Power}, "
            f"Energy={self.Energy}, Frequency={self.Frequency}, "
            f"PF={self.PF})"
        )


@app.middleware("http")
async def log_request(request, call_next):
    # logger.info(f"Incoming request: {request.method} {request.url}")
    # logger.info(f"Request headers: {request.headers}")
    # logger.info(f"Request body: {await request.body()}")
    # logger.info(f"Request :{request}")

    response = await call_next(request)

    return response

@app.get("/")
def get_home():
    return {"message": "Welcome to the homepage!"}

def validate_sensor_data(sensor_data: SensorDataCreate) -> bool:
    # Check for 'nan' values in the data
    return not any(
        value.lower() == 'nan' 
        for value in [
            sensor_data.Voltage, sensor_data.Current, sensor_data.Power,
            sensor_data.Energy, sensor_data.Frequency, sensor_data.PF
        ]
    )

# @app.post("/receive_data")
# async def receive_data(data):
#   """
#   This endpoint receives data containing timestamps from an ESP32 device.
#   """
#   # Split the data into lines and strip any leading/trailing whitespaces
#   lines = data.decode().strip().splitlines()
#   measurements = []
#   for line in lines:
#     # Extract the time value from each line
#     time_value = int(line.split(":")[1].strip())
#     # Create a Measurement object and append it to the list
#     measurements.append(Measurement(time=time_value))
  
#   # Process the list of measurements (logic depends on your specific needs)
#   # You can store them in a database, send them for further processing, etc.
#   # ... (your processing logic) ...
  
#   return {"message": "Data received successfully!"}

# @app.post("/receive_data")
# async def receive_data(sensor_data:Annotated[bytes, File()], db: Session = Depends(database.get_db)):
#     if not validate_sensor_data(sensor_data):
#         raise HTTPException(status_code=400, detail="Received corrupted data")
    

#     # new_data = models.SensorData(
#     #     voltage=sensor_data.Voltage,
#     #     current=sensor_data.Current,
#     #     power=sensor_data.Power,
#     #     energy=sensor_data.Energy,
#     #     frequency=sensor_data.Frequency,
#     #     pf=sensor_data.PF
#     # )
#     # print(sensor_data)
#     # db.add(new_data)
#     # db.commit()
#     # db.refresh(new_data)
#     print(sensor_data)
    
#     return {"message": "Data received successfully"}

class Reading(BaseModel):
    module: int
    voltage: Optional[float]
    current: Optional[float]
    power: Optional[float]
    energy: Optional[float]
    frequency: Optional[float]
    powerFactor: Optional[float]

    def to_json(self) -> str:
        return json.dumps(self.dict())

class ReadingData(BaseModel):
    timestamp: int
    readings: List[Reading]

    def to_json(self) -> str:
        return json.dumps(self.dict())

class SensorData(BaseModel):
    deviceId: str
    data: List[ReadingData]

    def to_json(self) -> str:
        return json.dumps(self.dict())
@app.post("/receive_data")
async def receive_data(request: Request):
    try:
        # Read the request body as bytes
        body_bytes = await request.body()
        
        # Decode bytes to string
        body_str = body_bytes.decode("utf-8")
        # print(body_str)
        json_body = json.loads(body_str)
        # print(json_body)
        sensor_data = SensorData(**json_body)
        print(sensor_data.to_json())


    except json.JSONDecodeError:
        print("Invalid JSON")
        raise HTTPException(status_code=422, detail="Invalid JSON")
    except Exception as e:
        print("Validation error")
        raise HTTPException(status_code=422, detail=f"Validation error: {e}")

    return {"message": "Data received successfully"}

@app.get("/readings")
async def readings(db:Session = Depends(database.get_db)):
    readings = db.query(models.SensorData).all()
    return readings
    