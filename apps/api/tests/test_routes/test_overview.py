from datetime import date, datetime


def test_overview_empty_db(client):
    response = client.get("/api/overview")
    assert response.status_code == 200
    data = response.json()

    assert data["total_sessions"] == 0
    assert data["total_projects"] == 0
    assert data["total_tokens"] == 0
    assert data["cost_all_time"] == 0.0
    assert data["cost_30d"] == 0.0
    assert data["token_trend"] == []
    assert data["cost_trend"] == []
    assert data["most_active_project"] is None
    assert data["most_used_model"] is None


def test_overview_response_shape(client):
    response = client.get("/api/overview")
    assert response.status_code == 200
    data = response.json()

    required_keys = [
        "total_sessions",
        "total_projects",
        "total_input_tokens",
        "total_output_tokens",
        "total_tokens",
        "cost_all_time",
        "cost_30d",
        "active_projects_30d",
        "token_trend",
        "cost_trend",
        "most_active_project",
        "most_used_model",
    ]
    for key in required_keys:
        assert key in data, f"Missing key: {key}"


def test_overview_with_data(client, db_session):
    from devlens.db.models.analytics import DailyAggregate, Session as SessionModel
    from devlens.db.models.project import Project

    project = Project(name="test-proj", slug="test-proj", path="/home/user/test-proj")
    db_session.add(project)
    db_session.flush()

    session = SessionModel(
        session_id="session-abc",
        provider="claude",
        project_id=project.id,
        model="claude-sonnet-4-6",
        started_at=datetime(2026, 6, 20, 9, 0, 0),
        ended_at=datetime(2026, 6, 20, 9, 30, 0),
        message_count=10,
        tool_call_count=5,
        total_input_tokens=9000,
        total_output_tokens=400,
    )
    db_session.add(session)

    agg = DailyAggregate(
        date=date(2026, 6, 20),
        provider="claude",
        project_id=project.id,
        input_tokens=9000,
        output_tokens=400,
        cache_creation_tokens=800,
        cache_read_tokens=5300,
        session_count=1,
        message_count=10,
        estimated_cost=0.05,
    )
    db_session.add(agg)
    db_session.commit()

    response = client.get("/api/overview")
    assert response.status_code == 200
    data = response.json()

    assert data["total_sessions"] == 1
    assert data["total_projects"] == 1
    assert data["most_active_project"] == "test-proj"
    assert data["most_used_model"] == "claude-sonnet-4-6"
    assert data["cost_all_time"] > 0
    assert len(data["token_trend"]) == 1
