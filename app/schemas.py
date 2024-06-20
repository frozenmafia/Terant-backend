from pydantic import BaseModel
from typing import List
from datetime import datetime


class MeasurementSchema(BaseModel):
    id: int
    module_id: int
    timestamp: datetime
    voltage: float
    current: float
    power: float
    energy: float
    frequency: float
    power_factor: float

    class Config:
        orm_mode = True

class ModuleSchema(BaseModel):
    id: int
    device_id: int
    module_number: int
    on:int
    measurements: List[MeasurementSchema]

    class Config:
        orm_mode = True

class DeviceSchema(BaseModel):
    id: int
    number_of_modules: int
    modules: List[ModuleSchema]

    class Config:
        orm_mode = True

class ModuleStatusSchema:
    id: int
    device_id: int
    module_number: int
    on:int
class DevicesStatusSchema:
    id: int
    number_of_modules: int
    modules: List[ModuleStatusSchema]

    # class Config:
    #     orm_mode = True



class ModuleStatusToggle:
    status:int