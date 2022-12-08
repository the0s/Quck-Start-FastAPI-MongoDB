from pydantic import BaseModel, Field
from mongo_helpers import PyObjectId
import datetime
from bson import ObjectId
from typing import Union

class Task(BaseModel):
    task_id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    has_run: bool
    lines: list
    schedule_time: Union[datetime.datetime,None] = None
    result: Union[list,None] = None
    run_time: Union[datetime.datetime,None] = None

    def to_mongo(self):
        to_dict = vars(self)
        return to_dict

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime.datetime: str}


class AddTaskBody(BaseModel):
    schedule_time: Union[str,None] = None
    lines: Union[str,None] = None
