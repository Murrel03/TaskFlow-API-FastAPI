"""Task + project CRUD tests: create, read, filter, paginate, update, delete, 404s."""


def _make_task(client, headers, project_id, **overrides):
    payload = {"title": "Write tests", "project_id": project_id}
    payload.update(overrides)
    return client.post("/tasks", json=payload, headers=headers)


def test_create_project(client, auth_headers):
    resp = client.post("/projects", json={"name": "Portfolio"}, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.json()["name"] == "Portfolio"


def test_create_task(client, auth_headers, project_id):
    resp = _make_task(client, auth_headers, project_id, priority="high")
    assert resp.status_code == 201
    body = resp.json()
    assert body["title"] == "Write tests"
    assert body["status"] == "todo"
    assert body["priority"] == "high"
    assert body["project_id"] == project_id


def test_create_task_in_missing_project_404(client, auth_headers):
    resp = _make_task(client, auth_headers, 9999)
    assert resp.status_code == 404


def test_list_tasks_and_filter_by_status(client, auth_headers, project_id):
    _make_task(client, auth_headers, project_id, title="One")
    _make_task(client, auth_headers, project_id, title="Two", status="done")
    _make_task(client, auth_headers, project_id, title="Three")

    resp = client.get("/tasks", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["total"] == 3

    resp = client.get("/tasks?status=done", headers=auth_headers)
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "Two"


def test_list_tasks_pagination(client, auth_headers, project_id):
    for i in range(5):
        _make_task(client, auth_headers, project_id, title=f"Task {i}")
    page1 = client.get("/tasks?skip=0&limit=2", headers=auth_headers).json()
    page2 = client.get("/tasks?skip=2&limit=2", headers=auth_headers).json()
    assert page1["total"] == 5
    assert len(page1["items"]) == 2
    assert len(page2["items"]) == 2
    assert page1["items"][0]["id"] != page2["items"][0]["id"]


def test_get_task(client, auth_headers, project_id):
    task_id = _make_task(client, auth_headers, project_id).json()["id"]
    resp = client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == task_id


def test_get_missing_task_404(client, auth_headers):
    resp = client.get("/tasks/424242", headers=auth_headers)
    assert resp.status_code == 404


def test_update_task_status(client, auth_headers, project_id):
    task_id = _make_task(client, auth_headers, project_id).json()["id"]
    resp = client.put(
        f"/tasks/{task_id}", json={"status": "in_progress"}, headers=auth_headers
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "in_progress"


def test_delete_task(client, auth_headers, project_id):
    task_id = _make_task(client, auth_headers, project_id).json()["id"]
    resp = client.delete(f"/tasks/{task_id}", headers=auth_headers)
    assert resp.status_code == 204
    assert client.get(f"/tasks/{task_id}", headers=auth_headers).status_code == 404


def test_delete_project(client, auth_headers, project_id):
    resp = client.delete(f"/projects/{project_id}", headers=auth_headers)
    assert resp.status_code == 204
    assert client.get(f"/projects/{project_id}", headers=auth_headers).status_code == 404


def test_task_validation_error(client, auth_headers, project_id):
    resp = client.post("/tasks", json={"project_id": project_id}, headers=auth_headers)
    assert resp.status_code == 422
