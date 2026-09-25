import pytest

from infrastructure.seed import (
    BLD_SEVER_1,
    CAT_DOOR,
    CAT_NO_POWER,
    CAT_PROTECHKA,
    OPT_CAN_SHUT,
    OPT_CLOSER,
    OPT_FLOOR,
    OPT_NIGHT_NO,
    OPT_NIGHT_YES,
    OPT_ROOM,
    OPT_THREAT_NO,
    OPT_TRIPPED,
    Q_BREAKER,
    Q_DOOR_NIGHT,
    Q_DOOR_WHAT,
    Q_LEAK_WHERE,
    Q_POWER_SCOPE,
    Q_SHUT_OFF,
    Q_THREAT,
    SPEC_SEVER_PLUMBER,
)


def _login(client, username="dispatcher_sever", password="sever123"):
    r = client.post("/api/auth/login", json={"username": username, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_happy_path_submit_accept_assign_complete(client):
    # Submit water ticket with floor + can shut → recommendation match
    submit = client.post(
        "/api/tickets",
        headers={"X-Max-User-Id": "resident-100"},
        json={
            "buildingId": BLD_SEVER_1,
            "categoryId": CAT_PROTECHKA,
            "answers": {
                Q_LEAK_WHERE: OPT_FLOOR,
                Q_SHUT_OFF: OPT_CAN_SHUT,
                Q_THREAT: OPT_THREAT_NO,
            },
        },
    )
    assert submit.status_code == 200, submit.text
    ticket = submit.json()
    assert ticket["status"] == "NEW"
    assert "корневой вентиль" in ticket["recommendationTextSnapshot"].lower() or "корневой" in ticket["recommendationTextSnapshot"]
    ticket_id = ticket["id"]

    token = _login(client)
    headers = {"Authorization": f"Bearer {token}"}

    accept = client.post(f"/api/tickets/{ticket_id}/accept", headers=headers)
    assert accept.status_code == 200, accept.text
    assert accept.json()["status"] == "ACCEPTED"

    assign = client.post(
        f"/api/tickets/{ticket_id}/assign",
        headers=headers,
        json={"specialistId": SPEC_SEVER_PLUMBER},
    )
    assert assign.status_code == 200, assign.text
    assert assign.json()["status"] == "IN_PROGRESS"
    assert assign.json()["assigneeSpecialistId"] == SPEC_SEVER_PLUMBER

    complete = client.post(f"/api/tickets/{ticket_id}/complete", headers=headers)
    assert complete.status_code == 200, complete.text
    assert complete.json()["status"] == "DONE"


def test_cancel_by_resident(client):
    submit = client.post(
        "/api/tickets",
        headers={"X-Max-User-Id": "resident-200"},
        json={
            "buildingId": BLD_SEVER_1,
            "categoryId": CAT_NO_POWER,
            "answers": {
                Q_POWER_SCOPE: OPT_ROOM,
                Q_BREAKER: OPT_TRIPPED,
            },
        },
    )
    assert submit.status_code == 200, submit.text
    ticket_id = submit.json()["id"]
    assert "автомат" in submit.json()["recommendationTextSnapshot"].lower()

    cancel = client.post(
        f"/api/tickets/{ticket_id}/cancel",
        headers={"X-Max-User-Id": "resident-200"},
        json={"reason": "Проблема решилась"},
    )
    assert cancel.status_code == 200, cancel.text
    assert cancel.json()["status"] == "CANCELLED_BY_RESIDENT"
    assert cancel.json()["cancelReason"] == "Проблема решилась"

def test_list_org_high_first(client):
    # LOW-ish door without night open
    client.post(
        "/api/tickets",
        headers={"X-Max-User-Id": "r1"},
        json={
            "buildingId": BLD_SEVER_1,
            "categoryId": CAT_DOOR,
            "answers": {
                Q_DOOR_WHAT: OPT_CLOSER,
                Q_DOOR_NIGHT: OPT_NIGHT_NO,
            },
        },
    )
    # HIGH door open night
    high = client.post(
        "/api/tickets",
        headers={"X-Max-User-Id": "r2"},
        json={
            "buildingId": BLD_SEVER_1,
            "categoryId": CAT_DOOR,
            "answers": {
                Q_DOOR_WHAT: OPT_CLOSER,
                Q_DOOR_NIGHT: OPT_NIGHT_YES,
            },
        },
    )
    assert high.status_code == 200
    assert high.json()["urgencyLevel"] == "HIGH"

    token = _login(client)
    lst = client.get(
        "/api/tickets",
        params={"role": "org"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert lst.status_code == 200, lst.text
    items = lst.json()
    assert len(items) >= 2
    # HIGH must come before non-HIGH
    urgencies = [i["urgencyLevel"] for i in items]
    seen_non_high = False
    for u in urgencies:
        if u != "HIGH":
            seen_non_high = True
        elif seen_non_high:
            pytest.fail("HIGH ticket appeared after non-HIGH")


def test_resolve_building_by_address(client):
    r = client.post(
        "/api/buildings/resolve",
        json={"addressQuery": "Ленина 10"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["id"] == BLD_SEVER_1


def test_dispatcher_cannot_accept_other_org_ticket(client):
    # Ticket for Sever org
    submit = client.post(
        "/api/tickets",
        headers={"X-Max-User-Id": "r-cross"},
        json={
            "buildingId": BLD_SEVER_1,
            "categoryId": CAT_PROTECHKA,
            "answers": {
                Q_LEAK_WHERE: OPT_FLOOR,
                Q_SHUT_OFF: OPT_CAN_SHUT,
                Q_THREAT: OPT_THREAT_NO,
            },
        },
    )
    assert submit.status_code == 200
    ticket_id = submit.json()["id"]

    # Login as Yug dispatcher
    token = _login(client, username="dispatcher_yug", password="yug123")
    accept = client.post(
        f"/api/tickets/{ticket_id}/accept",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert accept.status_code == 400
    assert "УК" in accept.json()["detail"]
