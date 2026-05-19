"""Backend API tests for PosePerfect AI"""
import os
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://pose-wireframe.preview.emergentagent.com').rstrip('/')


@pytest.fixture
def api_client():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


# Root endpoint
def test_root_endpoint(api_client):
    r = api_client.get(f"{BASE_URL}/api/")
    assert r.status_code == 200
    data = r.json()
    assert "message" in data
    assert "PosePerfect" in data["message"]


# Poses list - no filter
def test_get_all_poses(api_client):
    r = api_client.get(f"{BASE_URL}/api/poses")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 7  # seeded 7 poses
    p = data[0]
    for key in ["id", "name", "mood_pack", "scene_type", "landmarks"]:
        assert key in p
    assert isinstance(p["landmarks"], list)
    assert len(p["landmarks"]) == 33


# Filter by mood
@pytest.mark.parametrize("mood,expected_min", [
    ("Y2K Aesthetic", 2),
    ("Vogue Editorial", 2),
    ("Candid Streetwear", 3),
])
def test_get_poses_by_mood(api_client, mood, expected_min):
    r = api_client.get(f"{BASE_URL}/api/poses", params={"mood": mood})
    assert r.status_code == 200
    data = r.json()
    assert len(data) >= expected_min
    for p in data:
        assert p["mood_pack"] == mood


# Filter by scene
@pytest.mark.parametrize("scene", ["urban_street", "beach", "indoor_cafe", "architectural"])
def test_get_poses_by_scene(api_client, scene):
    r = api_client.get(f"{BASE_URL}/api/poses", params={"scene": scene})
    assert r.status_code == 200
    data = r.json()
    for p in data:
        assert p["scene_type"] == scene


# Combined filter
def test_poses_mood_and_scene(api_client):
    r = api_client.get(f"{BASE_URL}/api/poses",
                       params={"mood": "Y2K Aesthetic", "scene": "urban_street"})
    assert r.status_code == 200
    data = r.json()
    assert len(data) >= 2
    for p in data:
        assert p["mood_pack"] == "Y2K Aesthetic"
        assert p["scene_type"] == "urban_street"


# No _id leaked
def test_no_mongo_id_leaked(api_client):
    r = api_client.get(f"{BASE_URL}/api/poses")
    for p in r.json():
        assert "_id" not in p


# Empty filter result
def test_filter_no_match(api_client):
    r = api_client.get(f"{BASE_URL}/api/poses", params={"mood": "NonExistent"})
    assert r.status_code == 200
    assert r.json() == []


# Get pose by id
def test_get_pose_by_id(api_client):
    all_r = api_client.get(f"{BASE_URL}/api/poses")
    pid = all_r.json()[0]["id"]
    r = api_client.get(f"{BASE_URL}/api/poses/{pid}")
    assert r.status_code == 200
    assert r.json()["id"] == pid


# Status create + read
def test_status_create_and_get(api_client):
    r = api_client.post(f"{BASE_URL}/api/status", json={"client_name": "TEST_pytest"})
    assert r.status_code == 200
    d = r.json()
    assert d["client_name"] == "TEST_pytest"
    assert "id" in d
    r2 = api_client.get(f"{BASE_URL}/api/status")
    assert r2.status_code == 200
    assert any(s["client_name"] == "TEST_pytest" for s in r2.json())
