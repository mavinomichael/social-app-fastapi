from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base
from app.config import settings
from contextlib import contextmanager
from app.oauth2 import create_access_token
from app import models

SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:' \
                          f'{settings.database_password}@{settings.database_hostname}:' \
                          f'{settings.database_port}/{settings.database_name}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Session = sessionmaker(bind=engine)


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = TestingSessionLocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


@pytest.fixture
def session():
    clear_tables()
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture
def test_user(client):
    user_data = {"email": "michael@gmail.com",
                 "password": "password123"}
    response = client.post("/users/", json=user_data)

    assert response.status_code == 201
    print(response.json())
    new_user = response.json()
    new_user['password'] = user_data['password']
    return new_user


@pytest.fixture
def test_user_2(client):
    user_data = {"email": "mavino@gmail.com",
                 "password": "password123"}
    response = client.post("/users/", json=user_data)

    assert response.status_code == 201
    print(response.json())
    new_user = response.json()
    new_user['password'] = user_data['password']
    return new_user


@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user['id']})


@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }

    return client


@pytest.fixture
def test_posts(test_user, session, test_user_2):
    posts_data = [{
        "title": "first title",
        "content": "first content",
        "owner_id": test_user['id']
    }, {
        "title": "second title",
        "content": "second content",
        "owner_id": test_user['id']
    }, {
        "title": "third title",
        "content": "third content",
        "owner_id": test_user['id']
    }, {
        "title": "third title",
        "content": "third content",
        "owner_id": test_user_2['id']
    }]

    def create_post_model(post):
        return models.Post(**post)

    post_map = map(create_post_model, posts_data)
    posts = list(post_map)

    session.add_all(posts)

    session.commit()

    fetched_posts = session.query(models.Post).all()
    session.commit()
    list(fetched_posts)

    return fetched_posts


@pytest.fixture
def test_vote(test_posts, test_user, session):
    new_vote = models.Vote(post_id=test_posts[3].id, user_id=test_user['id'])
    session.add(new_vote)
    session.commit()


def clear_tables():
    with session_scope() as conn:
        for table in Base.metadata.sorted_tables:
            conn.execute(
                text(f"TRUNCATE {table.name} RESTART IDENTITY CASCADE;")
            )
        conn.commit()
