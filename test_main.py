import sys
sys.path.append('.')
from fastapi.testclient import TestClient
from main import app
from dateutil import parser
import datetime
import time
client = TestClient(app)


def test_endpoint():
    response = client.get("/v1/tasks")
    assert response.status_code == 200

def test_add_fetch_task():
    data ={"schedule_time":"2021-06-05T17:00:00", "lines":"victoria,central"}
    response = client.post("/v1/tasks", json=data)
    assert response.status_code == 200
    task_id = response.json()['task_id']
    response = client.get(f"/v1/tasks/{task_id}")
    assert response.status_code == 200

def test_add_fetch_update_task():
    data ={"schedule_time":"2021-06-05T05:00:00", "lines":"victoria,central"}
    response = client.post("/v1/tasks", json=data)
    assert response.status_code == 200
    task_id = response.json()['task_id']
    response = client.get(f"/v1/tasks/{task_id}")
    assert response.status_code == 200
    res = response.json()
    assert parser.parse(res['schedule_time']) == parser.parse(data['schedule_time'])
    assert res['lines'] == data['lines'].split(',')

    # update
    data2 ={"schedule_time":"2022-06-05T05:00:00", "lines":"central"}
    response = client.post(f"/v1/tasks/{task_id}", json=data2)
    assert response.status_code == 200
    response = client.get(f"/v1/tasks/{task_id}")
    assert response.status_code == 200
    res = response.json()
    assert parser.parse(res['schedule_time']) == parser.parse(data2['schedule_time'])
    assert res['lines'] == data2['lines'].split(',')

def test_add_delete_task():
    data ={"schedule_time":"2021-06-05T05:00:00", "lines":"victoria,central"}
    response = client.post("/v1/tasks", json=data)
    assert response.status_code == 200
    task_id = response.json()['task_id']
    response = client.get(f"/v1/tasks/{task_id}")
    assert response.status_code == 200
    response = client.delete(f"/v1/tasks/{task_id}")
    assert response.status_code == 200
    response = client.get(f"/v1/tasks/{task_id}")
    assert response.status_code == 404


# def test_schedule():
#     data ={"schedule_time":str(datetime.datetime.now()+datetime.timedelta(seconds=3)),
#     "lines":"victoria,central"}
#     response = client.post("/v1/tasks", json=data)
#     assert response.status_code == 200
#     task_id = response.json()['task_id']
#     response = client.get(f"/v1/tasks/{task_id}")
#     assert response.status_code == 200
#     task = response.json()
#     assert task['has_run'] == False
#     time.sleep(5)
#     response = client.get(f"/v1/tasks/{task_id}")
#     assert response.status_code == 200
#     task = response.json()
#     assert task['has_run'] == True