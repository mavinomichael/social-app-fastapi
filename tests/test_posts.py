import pytest
from app import schemas


def test_get_all_posts(authorized_client, test_posts):
    response = authorized_client.get("/posts/")

    def validate(post):
        return schemas.PostResponse(**post)

    posts_map = map(validate, response.json())
    posts_list = list(posts_map)

    assert len(response.json()) == len(test_posts)
    assert response.status_code == 200


# this test will be useful if unauthenticated users can't fetch post
# by checking for a 401, in this case check for a 200.
def test_unauthorised_user_get_all_posts(client, test_posts):
    response = client.get("/posts/")
    assert response.status_code == 200


def test_unauthorised_user_get_one_post(client, test_posts):
    response = client.get(f"/posts/{test_posts[0].id}")
    assert response.status_code == 200


def test_get_one_post_not_exist(authorized_client, test_posts):
    response = authorized_client.get("/posts/88888")
    assert response.status_code == 404


def test_get_one_post(authorized_client, test_posts):
    response = authorized_client.get(f"/posts/{test_posts[1].id}")
    post = schemas.PostResponse(**response.json())
    assert response.status_code == 200
    assert post.Post.id == test_posts[1].id
    assert post.Post.title == test_posts[1].title
    assert post.Post.content == test_posts[1].content


@pytest.mark.parametrize("title, content, published", [
    ("awesome new title", "awesome new content", True),
    ("favourite swallow", "i love amala", True),
    ("buildings", "microsoft", True)
])
def test_create_post(authorized_client, test_user, test_posts, title, content, published):
    response = authorized_client.post("/posts/",
                                      json={"title": title, "content": content, "published": published})

    created_post = schemas.Post(**response.json())

    assert response.status_code == 201
    assert created_post.title == title
    assert created_post.content == content
    assert created_post.published == published
    assert created_post.owner_id == test_user['id']


def test_create_post_published_true(authorized_client, test_user, test_posts):
    response = authorized_client.post("/posts/",
                                      json={"title": "arbitrary title", "content": "arbitrary content"})

    created_post = schemas.Post(**response.json())

    assert response.status_code == 201
    assert created_post.title == "arbitrary title"
    assert created_post.content == "arbitrary content"
    assert created_post.published == True
    assert created_post.owner_id == test_user['id']


def test_unauthorized_user_create_post(client, test_user, test_posts):
    response = client.post("/posts/",
                           json={"title": "arbitrary title", "content": "arbitrary content"})
    assert response.status_code == 401


def test_unauthorized_user_delete_post(client, test_user, test_posts):
    response = client.delete(f"/posts/{test_posts[0].id}")
    assert response.status_code == 401


def test_delete_post_success(authorized_client, test_user, test_posts):
    response = authorized_client.delete(f"/posts/{test_posts[0].id}")
    # fetch all post to verify post was deleted
    assert response.status_code == 204


def test_delete_post_non_exist(authorized_client, test_user, test_posts):
    response = authorized_client.delete("/posts/80000000")
    assert response.status_code == 404


def test_delete_other_user_post(authorized_client, test_user, test_posts):
    response = authorized_client.delete(f"/posts/{test_posts[3].id}")
    assert response.status_code == 403


def test_update_post(authorized_client, test_user, test_posts):
    data = {
        "title": "updated title",
        "content": "updated title",
        "id": test_posts[0].id
    }

    response = authorized_client.put(f"/posts/{test_posts[0].id}", json=data)
    updated_post = schemas.Post(**response.json())
    assert response.status_code == 200
    assert updated_post.title == data['title']
    assert updated_post.content == data['content']


def test_update_other_user_post(authorized_client, test_user, test_posts):
    data = {
        "title": "updated title",
        "content": "updated title",
        "id": test_posts[3].id
    }

    response = authorized_client.put(f"/posts/{test_posts[3].id}", json=data)
    assert response.status_code == 403


def test_unauthorized_user_update_post(client, test_posts):
    data = {
        "title": "updated title",
        "content": "updated title",
        "id": test_posts[0].id
    }

    response = client.put(f"/posts/{test_posts[0].id}", json=data)
    assert response.status_code == 401


def test_update_post_non_exist(authorized_client, test_user, test_posts):
    data = {
        "title": "updated title",
        "content": "updated title",
        "id": test_posts[0].id
    }
    response = authorized_client.put(f"/posts/80000000", json=data)
    assert response.status_code == 404
