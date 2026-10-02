import pytest

# сущность: (данные для создания, данные для обновления)
CASES = {
    "groups": (
        {"name": "ИВТ-21"},
        {"name": "ИВТ-22"},
    ),
    "teachers": (
        {"full_name": "Петров Пётр", "department": "ИТ"},
        {"full_name": "Петров Пётр", "department": "Математика"},
    ),
    "students": (
        {"full_name": "Иванов Иван", "email": "ivanov@mail.ru", "group_id": None},
        {"full_name": "Иванов Иван", "email": "ivanov2@mail.ru", "group_id": None},
    ),
    "courses": (
        {"title": "DevOps", "hours": 72, "teacher_id": None},
        {"title": "DevOps", "hours": 108, "teacher_id": None},
    ),
}

ENTITIES = list(CASES)


def create(client, entity):
    response = client.post(f"/{entity}", json=CASES[entity][0])
    assert response.status_code == 201
    return response.json()


@pytest.mark.parametrize("entity", ENTITIES)
def test_create(client, entity):
    body = create(client, entity)
    assert body["id"] > 0
    for key, value in CASES[entity][0].items():
        assert body[key] == value


@pytest.mark.parametrize("entity", ENTITIES)
def test_list(client, entity):
    create(client, entity)
    response = client.get(f"/{entity}")
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.parametrize("entity", ENTITIES)
def test_get_by_id(client, entity):
    created = create(client, entity)
    response = client.get(f"/{entity}/{created['id']}")
    assert response.status_code == 200
    assert response.json() == created


@pytest.mark.parametrize("entity", ENTITIES)
def test_update(client, entity):
    created = create(client, entity)
    new_data = CASES[entity][1]
    response = client.put(f"/{entity}/{created['id']}", json=new_data)
    assert response.status_code == 200
    for key, value in new_data.items():
        assert response.json()[key] == value


@pytest.mark.parametrize("entity", ENTITIES)
def test_delete(client, entity):
    created = create(client, entity)
    assert client.delete(f"/{entity}/{created['id']}").status_code == 204
    assert client.get(f"/{entity}/{created['id']}").status_code == 404


@pytest.mark.parametrize("entity", ENTITIES + ["grades"])
def test_not_found(client, entity):
    assert client.get(f"/{entity}/999").status_code == 404


def test_grade_full_cycle(client):
    student = create(client, "students")
    course = create(client, "courses")
    payload = {"student_id": student["id"], "course_id": course["id"], "value": 5}

    response = client.post("/grades", json=payload)
    assert response.status_code == 201
    grade_id = response.json()["id"]

    assert client.get(f"/grades/{grade_id}").json()["value"] == 5
    assert len(client.get("/grades").json()) == 1

    payload["value"] = 4
    assert client.put(f"/grades/{grade_id}", json=payload).json()["value"] == 4

    assert client.delete(f"/grades/{grade_id}").status_code == 204
    assert client.get(f"/grades/{grade_id}").status_code == 404


def test_grade_validation(client):
    response = client.post("/grades", json={"student_id": 1, "course_id": 1, "value": 7})
    assert response.status_code == 422


def test_duplicate_email_conflict(client):
    create(client, "students")
    response = client.post("/students", json=CASES["students"][0])
    assert response.status_code == 409


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
