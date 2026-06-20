from datetime import datetime

import pytest


def _insert_project_and_session(db_session, project_slug="my-project", session_id="sess-001", model="claude-sonnet-4-6"):
    from devlens.db.models.analytics import Session as SessionModel
    from devlens.db.models.project import Project

    project = Project(name=project_slug, slug=project_slug, path=f"/home/user/{project_slug}")
    db_session.add(project)
    db_session.flush()

    session = SessionModel(
        session_id=session_id,
        provider="claude",
        project_id=project.id,
        model=model,
        started_at=datetime(2026, 6, 20, 9, 0, 0),
        ended_at=datetime(2026, 6, 20, 9, 30, 0),
        message_count=10,
        tool_call_count=4,
        total_input_tokens=9000,
        total_output_tokens=400,
    )
    db_session.add(session)
    db_session.commit()
    return project, session


def test_sessions_list_empty(client):
    response = client.get("/api/sessions")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["pages"] == 0


def test_sessions_list_returns_sessions(client, db_session):
    _insert_project_and_session(db_session)

    response = client.get("/api/sessions")
    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 1
    assert len(data["items"]) == 1
    item = data["items"][0]
    assert item["session_id"] == "sess-001"
    assert item["project_name"] == "my-project"
    assert item["model"] == "claude-sonnet-4-6"


def test_sessions_pagination(client, db_session):
    from devlens.db.models.analytics import Session as SessionModel
    from devlens.db.models.project import Project

    project = Project(name="proj", slug="proj", path="/home/user/proj")
    db_session.add(project)
    db_session.flush()

    for i in range(25):
        s = SessionModel(
            session_id=f"session-{i:03d}",
            provider="claude",
            project_id=project.id,
            started_at=datetime(2026, 6, 20, i % 24, 0, 0),
        )
        db_session.add(s)
    db_session.commit()

    response = client.get("/api/sessions?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 25
    assert data["pages"] == 3
    assert len(data["items"]) == 10

    response2 = client.get("/api/sessions?page=3&page_size=10")
    data2 = response2.json()
    assert len(data2["items"]) == 5


def test_sessions_filter_by_project(client, db_session):
    project1, _ = _insert_project_and_session(db_session, "proj-a", "sess-a")
    _insert_project_and_session(db_session, "proj-b", "sess-b")

    response = client.get(f"/api/sessions?project_id={project1.id}")
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["session_id"] == "sess-a"


def test_sessions_search(client, db_session):
    _insert_project_and_session(db_session, "alpha-project", "sess-alpha")
    _insert_project_and_session(db_session, "beta-project", "sess-beta")

    response = client.get("/api/sessions?search=alpha")
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["project_name"] == "alpha-project"


def test_session_detail(client, db_session):
    from devlens.db.models.analytics import Message, ToolUsage
    from devlens.db.models.analytics import Session as SessionModel
    from devlens.db.models.project import Project

    project = Project(name="detail-proj", slug="detail-proj", path="/home/user/detail-proj")
    db_session.add(project)
    db_session.flush()

    session = SessionModel(
        session_id="detail-session",
        provider="claude",
        project_id=project.id,
        model="claude-sonnet-4-6",
        started_at=datetime(2026, 6, 20, 9, 0, 0),
        ended_at=datetime(2026, 6, 20, 9, 30, 0),
        message_count=2,
        tool_call_count=1,
        total_input_tokens=1000,
        total_output_tokens=200,
    )
    db_session.add(session)
    db_session.flush()

    db_session.add(Message(
        session_id=session.id,
        role="user",
        content_summary="Hello",
        input_tokens=0,
        output_tokens=0,
        timestamp=datetime(2026, 6, 20, 9, 0, 0),
    ))
    db_session.add(Message(
        session_id=session.id,
        role="assistant",
        content_summary="I'll help you.",
        input_tokens=1000,
        output_tokens=200,
        model="claude-sonnet-4-6",
        timestamp=datetime(2026, 6, 20, 9, 0, 5),
    ))
    db_session.add(ToolUsage(
        session_id=session.id,
        tool_name="Read",
        execution_count=1,
        is_error_count=0,
    ))
    db_session.commit()

    response = client.get(f"/api/sessions/{session.id}")
    assert response.status_code == 200
    data = response.json()

    assert data["session_id"] == "detail-session"
    assert data["project_name"] == "detail-proj"
    assert len(data["messages"]) == 2
    assert len(data["tool_usages"]) == 1
    assert data["tool_usages"][0]["tool_name"] == "Read"


def test_session_detail_not_found(client):
    response = client.get("/api/sessions/99999")
    assert response.status_code == 404


def test_sessions_duration_computed(client, db_session):
    _insert_project_and_session(db_session)

    response = client.get("/api/sessions")
    data = response.json()
    item = data["items"][0]
    # 30 minutes between 09:00 and 09:30
    assert item["duration_minutes"] == 30.0


def test_sessions_has_compaction_false_by_default(client, db_session):
    _insert_project_and_session(db_session)

    response = client.get("/api/sessions")
    data = response.json()
    assert data["items"][0]["has_compaction"] is False
