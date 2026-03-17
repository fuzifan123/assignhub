import requests
from datetime import datetime, timedelta
import json
import time

BASE_URL = "http://localhost:3000/api"

def test():
    try:
        print('--- Testing Registration ---')
        reg_payload = {
            "email": f"student_{int(time.time())}@example.com",
            "password": "securePassword123"
        }
        reg_res = requests.post(f"{BASE_URL}/register", json=reg_payload)
        reg_res.raise_for_status()
        reg_data = reg_res.json()
        print('Registration Success')
        token = reg_data["token"]
        headers = {"Authorization": f"Bearer {token}"}

        print('\n--- Testing Login ---')
        login_res = requests.post(f"{BASE_URL}/login", json=reg_payload)
        login_res.raise_for_status()
        print('Login Success')

        print('\n--- Testing Create Course ---')
        course_payload = {"name": "Database Systems"}
        course_res = requests.post(f"{BASE_URL}/courses", json=course_payload, headers=headers)
        course_res.raise_for_status()
        course_id = course_res.json()["id"]
        print(f'Create Course Success, ID: {course_id}')

        print('\n--- Testing Create Task (3.3.1) ---')
        deadline = (datetime.utcnow() + timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
        task_payload = {
            "title": "Complete Assignment 1",
            "deadline": deadline,
            "status": "todo",
            "course_id": course_id
        }
        task_res = requests.post(f"{BASE_URL}/tasks", json=task_payload, headers=headers)
        task_res.raise_for_status()
        task_data = task_res.json()
        task_id = task_data["id"]
        print(f'Create Task Success, ID: {task_id}, Title: {task_data["title"]}, Deadline: {task_data["deadline"]}')

        print('\n--- Testing Get Task List (3.3.2) ---')
        tasks_res = requests.get(f"{BASE_URL}/tasks", headers=headers, params={"course_id": course_id})
        tasks_res.raise_for_status()
        print(f'Get Tasks (Filtered by course_id) Success, count: {len(tasks_res.json())}')

        print('\n--- Testing Get Single Task (3.3.3) ---')
        task_detail_res = requests.get(f"{BASE_URL}/tasks/{task_id}", headers=headers)
        task_detail_res.raise_for_status()
        print(f'Get Single Task Success: {task_detail_res.json()["title"]} (Course: {task_detail_res.json()["course_name"]})')

        print('\n--- Testing Update Task (3.3.4) ---')
        update_payload = task_payload.copy()
        update_payload["title"] = "Complete Assignment 1 (Updated)"
        update_res = requests.put(f"{BASE_URL}/tasks/{task_id}", json=update_payload, headers=headers)
        update_res.raise_for_status()
        print(f'Update Task Success, New Title: {update_res.json()["title"]}')

        print('\n--- Testing Patch Task Status (3.3.5) ---')
        patch_res = requests.patch(f"{BASE_URL}/tasks/{task_id}/status", json={"status": "doing"}, headers=headers)
        patch_res.raise_for_status()
        print(f'Patch Status Success, New Status: {patch_res.json()["status"]}')

        print('\n--- Testing Dashboard (3.4) ---')
        # Create an upcoming task (within 24h for reminder check)
        imminent_deadline = (datetime.utcnow() + timedelta(hours=12)).strftime("%Y-%m-%dT%H:%M:%SZ")
        requests.post(f"{BASE_URL}/tasks", json={
            "title": "Urgent Task",
            "deadline": imminent_deadline,
            "status": "todo",
            "course_id": course_id
        }, headers=headers)
        
        dash_res = requests.get(f"{BASE_URL}/dashboard", headers=headers)
        dash_res.raise_for_status()
        dash_data = dash_res.json()
        print(f'Dashboard Success: {len(dash_data["courses"])} courses, {len(dash_data["upcoming_tasks"])} upcoming tasks')
        for t in dash_data["upcoming_tasks"]:
            print(f'  - {t["title"]} due at {t["deadline"]} ({t["course_name"]})')

        print('\n--- Testing Delete Task (3.3.6) ---')
        del_res = requests.delete(f"{BASE_URL}/tasks/{task_id}", headers=headers)
        del_res.raise_for_status()
        print('Delete Task Success')

        print('\n--- All tests completed successfully! ---')
    except requests.exceptions.HTTPError as e:
        print('Test failed:', e.response.json())
    except Exception as e:
        print('Test failed:', str(e))

if __name__ == "__main__":
    test()
