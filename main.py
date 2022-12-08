from typing import Union
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer
from pymongo import MongoClient
from dateutil import parser
import datetime
from database import get_collection
from models import Task, AddTaskBody
from functions import get_tfl_data
from fastapi_utils.tasks import repeat_every

# get database
tasks_db = get_collection()

app = FastAPI()

@app.get("/v1/scheduler")
@app.on_event("startup")
@repeat_every(seconds=1)
def run_scheduler() -> None:
    try:
        tasks = tasks_db.find({"has_run": False})
        now = datetime.datetime.now().replace(microsecond=0,second=0)
        for t in tasks:
            t = Task(**t)
            timedelta = t.schedule_time - now
            if timedelta.seconds < 5:
                lines = ','.join(t.lines)
                result = get_tfl_data(lines)
                query = {"_id": str(t.task_id)}
                newvalues = {"$set": {"result": result,
                                    "has_run": True,
                                    "run_time":datetime.datetime.now()}}
                res = tasks_db.update_one(query, newvalues)
    except Exception as e:
        print(e)


@app.get("/v1/tfl/{lines}")
def test_tfl(lines: str):
    if lines and isinstance(lines, str):
        return get_tfl_data(lines)
    raise HTTPException(status_code=404, detail="Provide a prober string")


@app.get("/v1/tasks")
@app.get("/v1/tasks/{task_id}")
def get_tasks(task_id: str = None):
    if task_id is None:
        result = []
        for i in tasks_db.find():
            t = Task(**i)
            result.append(t)
        return result
    else:
        task = tasks_db.find_one({"_id": task_id})
        if task:
            return Task(**task)
        else:
            raise HTTPException(status_code=404, detail="Task not found")


@app.post("/v1/tasks")
def add_task(data: AddTaskBody):
    schedule_time = parser.parse(
        data.schedule_time) if data.schedule_time else None
    lines = data.lines.split(',') if data.lines else None
    if schedule_time is None: # run now!
        result = get_tfl_data(data.lines)
        t = Task(schedule_time=schedule_time, lines=lines,
                 has_run=True, result=result, run_time=datetime.datetime.now())
        tasks_db.insert_one(jsonable_encoder(t))
    else:
        t = Task(schedule_time=schedule_time, lines=lines,
                 has_run=False, result=None)
        tasks_db.insert_one(jsonable_encoder(t))
    return {"detail": f"Task added with id {t.task_id}",
            "task_id":str(t.task_id)}


@app.delete("/v1/tasks/{task_id}")
def delete_task(task_id: str):
    query = {"_id": task_id}
    task = tasks_db.find_one(query)
    if task:
        tasks_db.delete_one(query)
        return {"detail": "Task Deleted"}
    else:
        raise HTTPException(status_code=404, detail="Task not found")


@app.post("/v1/tasks/{task_id}")
def update_task(task_id: str, data: AddTaskBody):
    query = {"_id": task_id}
    task = tasks_db.find_one(query)
    if task:
        task = Task(**task)
        if not task.has_run:
            schedule_time = parser.parse(data.schedule_time) \
                if data.schedule_time else None
            lines = data.lines.split(',') if data.lines else None
            newvalues = {
                "$set": {"schedule_time": schedule_time, "lines": lines}}
            res = tasks_db.update_one(query, newvalues)
            return {"detail": "Task updated"}
        else:
            raise HTTPException(status_code=404, detail="Task has already run")
    else:
        raise HTTPException(status_code=404, detail="Task not found")
