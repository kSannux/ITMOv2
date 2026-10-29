import re

import pytest

import app as web


@pytest.fixture
def client():
    app = web.create_app()
    app.config["TESTING"] = True
    return app.test_client()


def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    assert 'Экспорт в JSON' in response.get_data(as_text=True)
    assert client.get('/static/app.js').status_code == 200


def test_export_page_snapshot(client):
    rows = [{"name": "Иван"}, {"name": "Анна"}]
    response = client.post('/export', json={"data": rows, "filters_applied": {"search": "а"}})
    assert response.status_code == 200
    document = response.get_json()
    assert document['data'] == rows
    assert document['total_items'] == 2
    assert document['filters_applied'] == {"search": "а"}
    assert re.fullmatch(r'attachment; filename="export-\d{8}-\d{6}\.json"', response.headers['Content-Disposition'])


def test_empty_and_invalid(client):
    assert client.post('/export', json={"data": []}).get_json() == {"error": "empty_dataset"}
    assert client.post('/export', json={"data": None}).status_code == 422
    assert client.post('/export', json=[]).status_code == 400


def test_serializer_failure(client, monkeypatch):
    def fail(*args):
        raise RuntimeError('test failure')
    monkeypatch.setattr(web, 'export_visible_to_json', fail)
    response = client.post('/export', json={"data": [{}]})
    assert response.status_code == 500
    assert response.get_json() == {"error": "export_failed"}
