import pytest
from app import create_app
from models import db
from seed import seed_database

@pytest.fixture(scope="module")
def test_client():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():
        db.create_all()
        # Seed test data
        seed_database()
        with app.test_client() as client:
            yield client
        db.drop_all()

def test_offset_pagination(test_client):
    """Test offset pagination strategy"""
    res = test_client.get("/books?strategy=offset&page=1&limit=3")
    assert res.status_code == 200
    data = res.get_json()
    assert data["strategy"] == "offset"
    assert len(data["data"]) == 3
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["total"] == 10
    assert data["pagination"]["has_next"] is True

def test_cursor_pagination(test_client):
    """Test cursor pagination strategy"""
    res1 = test_client.get("/books?strategy=cursor&limit=3")
    assert res1.status_code == 200
    data1 = res1.get_json()
    assert data1["strategy"] == "cursor"
    assert len(data1["data"]) == 3
    assert data1["pagination"]["has_more"] is True
    assert data1["pagination"]["next_cursor"] is not None

    # Fetch next page using cursor
    cursor = data1["pagination"]["next_cursor"]
    res2 = test_client.get(f"/books?strategy=cursor&limit=3&cursor={cursor}")
    assert res2.status_code == 200
    data2 = res2.get_json()
    assert len(data2["data"]) == 3
    # Check that records are different
    ids1 = [b["id"] for b in data1["data"]]
    ids2 = [b["id"] for b in data2["data"]]
    assert set(ids1).isdisjoint(set(ids2))

def test_filter_genre(test_client):
    """Test filter theo category slug (genre)"""
    res = test_client.get("/books?genre=tech")
    assert res.status_code == 200
    data = res.get_json()
    for book in data["data"]:
        assert book["category"]["slug"] == "tech"

def test_multi_key_sorting(test_client):
    """Test multi-key sorting (price_vnd ASC, title DESC)"""
    res = test_client.get("/books?sort=price_vnd,title&order=asc,desc&limit=10")
    assert res.status_code == 200
    data = res.get_json()
    prices = [b["price_vnd"] for b in data["data"]]
    assert prices == sorted(prices)
