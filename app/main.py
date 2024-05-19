from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # Import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
import models, database

app = FastAPI()

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

@app.post("/receive_data")
async def receive_data(sensor_data: SensorDataCreate, db: Session = Depends(database.get_db)):
    if not validate_sensor_data(sensor_data):
        raise HTTPException(status_code=400, detail="Received corrupted data")
    

    new_data = models.SensorData(
        voltage=sensor_data.Voltage,
        current=sensor_data.Current,
        power=sensor_data.Power,
        energy=sensor_data.Energy,
        frequency=sensor_data.Frequency,
        pf=sensor_data.PF
    )
    print(sensor_data)
    db.add(new_data)
    db.commit()
    db.refresh(new_data)
    
    return {"message": "Data received successfully"}


@app.get("/readings")
async def readings(db:Session = Depends(database.get_db)):
    readings = db.query(models.SensorData).all()
    return readings
    