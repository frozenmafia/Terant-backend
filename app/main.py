from fastapi import FastAPI, Depends, HTTPException, Header, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timedelta
import json
from typing import List, Optional
from pydantic import BaseModel
from prometheus_client import generate_latest, REGISTRY
from prometheus_client.exposition import choose_encoder
import logging
import paho.mqtt.client as mqtt
from . import models, database, schemas  # Adjust import path as needed

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

broker = 'v74ef674.ala.asia-southeast1.emqxsl.com'
port = 8883
client_id = 'python-mqtt-publisher'
username = 'anchalshivank'
password = '123qwe123qwe'

# Initialize MQTT client
client = mqtt.Client(client_id=client_id)

# Set username and password
client.username_pw_set(username, password)

# Callback function for on_publish event
def on_publish(client, userdata, mid):
    print(f"Message {mid} published")

# Set callback function
client.on_publish = on_publish

# Configure TLS/SSL
client.tls_set()

# Connect to broker
client.connect(broker, port)

# Start the MQTT client loop
client.loop_start()


# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_request(request: Request, call_next):
    # logger.info(f"Incoming request: {request.method} {request.url}")
    # logger.info(f"Request headers: {request.headers}")
    # logger.info(f"Request body: {await request.body()}")

    response = await call_next(request)

    return response

# Example model for sensor data
class SensorDataCreate(BaseModel):
    Voltage: str
    Current: str
    Power: str
    Energy: str
    Frequency: str
    PF: str

# Example model for sensor readings
class Reading(BaseModel):
    module: int
    voltage: Optional[float]
    current: Optional[float]
    power: Optional[float]
    energy: Optional[float]
    frequency: Optional[float]
    powerFactor: Optional[float]

# Example model for sensor data with timestamps
class ReadingData(BaseModel):
    timestamp: int
    readings: List[Reading]

# Example model for sensor device data
class SensorData(BaseModel):
    deviceId: str
    data: List[ReadingData]

# Endpoint to retrieve all readings
@app.get("/readings")
async def readings(db: Session = Depends(database.get_db)):
    readings = db.query(models.SensorData).all()
    return readings

# Endpoint to handle Prometheus metrics
@app.get("/metrics")
async def metrics(accept: str = Header(None)):
    # Default accept header if not provided
    if accept is None:
        accept_header = "*/*"
    else:
        accept_header = str(accept)
    
    # Split accept header into list of accepted types with their q values
    accepted_types = [item.strip() for item in accept_header.split(',')]

    # Pass the accept_header to choose_encoder
    encoder, content_type = choose_encoder(accepted_types)
    
    # Collect metrics from Prometheus registry
    metrics_data = REGISTRY.collect()

    # Return response with encoded metrics and appropriate content type
    return Response(content=encoder(metrics_data), media_type=content_type)

# Example endpoint to add a device
@app.post("/add-device/{nom}")
async def add_device(nom: int, db: Session = Depends(database.get_db)):
    try:
        device = models.Device(number_of_modules=nom)
        db.add(device)
        db.commit()
        db.refresh(device)

        modules = [models.Module(device_id=device.id, module_number=i+1) for i in range(nom)]
        db.add_all(modules)
        db.commit()

        return device
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding device: {e}")

# Example endpoint to receive sensor data
@app.post("/receive_data")
async def receive_data(request: Request, db: Session = Depends(database.get_db)):
    try:
        body_bytes = await request.body()
        body_str = body_bytes.decode("utf-8")
        json_body = json.loads(body_str)
        sensor_data = SensorData(**json_body)

        current_time = datetime.now()
        data = sensor_data.data
        last_timestamp = data[-1].timestamp

        measurements = []
        for d in data:
            timestamp = d.timestamp
            timestamp_diff = last_timestamp - timestamp
            actual_time = current_time - timedelta(milliseconds=timestamp_diff)

            for reading in d.readings:
                module = db.query(models.Module).filter_by(device_id=sensor_data.deviceId, module_number=reading.module).first()
                if not module:
                    raise HTTPException(status_code=404, detail=f"Module not found for device {sensor_data.deviceId} and module number {reading.module}")

                measurement = models.Measurement(
                    module_id=module.id,
                    timestamp=actual_time,
                    voltage=reading.voltage,
                    current=reading.current,
                    power=reading.power,
                    energy=reading.energy,
                    frequency=reading.frequency,
                    power_factor=reading.powerFactor
                )
                measurements.append(measurement)

        db.add_all(measurements)
        db.commit()

        return {"message": "Data received successfully"}
    except Exception as e:
        logger.error(f"Error receiving data: {e}")
        raise HTTPException(status_code=422, detail=f"Validation error: {e}")

# Example endpoint to retrieve all devices
@app.get("/all", response_model=List[schemas.DeviceSchema])
async def get_all(db: Session = Depends(database.get_db)):
    devices = db.query(models.Device).all()
    logger.info(f"Retrieved all devices: {devices}")
    return devices

# Example endpoint to retrieve a specific device
@app.get("/device/{device_id}", response_model=schemas.DeviceSchema)
async def get_device(device_id: int, db: Session = Depends(database.get_db)):
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

# Example endpoint to retrieve a specific module
@app.get("/module/{module_id}", response_model=schemas.ModuleSchema)
async def get_module(module_id: int, db: Session = Depends(database.get_db)):
    module = db.query(models.Module).filter(models.Module.id == module_id).first()
    if module is None:
        raise HTTPException(status_code=404, detail="Module not found")
    return module

@app.get("/device_status/{device_id}")
async def get_device_status(device_id: int, db: Session = Depends(database.get_db)):
    device_with_modules = (
        db.query(models.Device)
        .filter(models.Device.id == device_id)
        .options(joinedload(models.Device.modules))
        .first()
    )

    if not device_with_modules:
        raise HTTPException(status_code=404, detail="Device not found")

    # Constructing the desired data structure
    modules_data = []
    for module in device_with_modules.modules:
        module_data = {
            "module_number": module.module_number,
            "status": module.on
            # Add more fields as needed
        }
        modules_data.append(module_data)

    # Return a dictionary representation of the device with modules
    return {
        "id": device_with_modules.id,
        "number_of_modules": device_with_modules.number_of_modules,
        "modules": modules_data
    }


@app.put("/device/{device_id}/module/{module_number}/toggle-status")
async def toggle_module_status(device_id: int, module_number: int, db: Session = Depends(database.get_db)):
    # Fetch the module from the database based on device_id and module_number
    module = db.query(models.Module).filter(
        models.Module.device_id == device_id,
        models.Module.module_number == module_number
    ).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    # Toggle module status (assuming 'on' is represented as 0 or 1)
    module.on = 1 if module.on == 0 else 0

    # Commit changes to the database
    db.commit()

    # Publish MQTT message
    topic = f"devices/{device_id}/module/{module_number}"
    message = {
        'device_id': device_id,
        'module_number': module_number,
        'status': module.on  # Publish the updated status (0 or 1)
    }
    client.publish(topic, json.dumps(message),retain=True,qos=2)

    return module