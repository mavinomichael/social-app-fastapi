# from typing import Optional
# from fastapi import FastAPI, Response, status, HTTPException
#
# from pydantic import BaseModel
# from random import randrange
# import psycopg2
# from psycopg2.extras import RealDictCursor
# import time
#
# app = FastAPI()
#
#
# class Post(BaseModel):
#     title: str
#     content: str
#     published: bool = True
#     rating: Optional[int] = None
#
#
# while True:
#     try:
#         conn = psycopg2.connect(host='localhost', database='social', user='postgres', password='6085',
#                                 cursor_factory=RealDictCursor)
#         cursor = conn.cursor()
#         print("database connection was successful")
#         break
#     except Exception as error:
#         print("connecting to database failed")
#         print("error", error)
#         time.sleep(2)
#
# my_posts = [
#     {
#         "id": 0,
#         "title": "first title",
#         "content": "first post content",
#         "published": False,
#         "rating": 5
#     },
#     {
#         "id": 1,
#         "title": "second title",
#         "content": "second post content",
#         "published": True,
#         "rating": 4
#     }
# ]
#
#
# def find_post(id):
#     for post in my_posts:
#         if post['id'] == id:
#             return post
#
#
# def find_post_index(id):
#     for i, post in enumerate(my_posts):
#         if post['id'] == id:
#             return i
#
#
# @app.get("/")
# def root():
#     return {"message": "Hello World"}
#
#
# @app.get("/posts")
# def get_post():
#     cursor.execute("""SELECT * FROM posts""")
#     posts = cursor.fetchall()
#     return {"data": posts}
#
#
# # included a comma next to str(id) in case of a bug that arises
# @app.get("/posts/{id}")
# def get_post(id: int):
#     cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id),))
#     post = cursor.fetchone()
#     if not post:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"post with id: {id} not found")
#     return {"post_detail": post}
#
#
# @app.post("/posts", status_code=status.HTTP_201_CREATED)
# def create_post(post: Post):
#     cursor.execute(
#         """INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""",
#         (post.title, post.content, post.published))
#     new_post = cursor.fetchone()
#     conn.commit()
#     return {"data": new_post}
#
#
# @app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_post(id: int):
#     cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id),))
#     deleted_post = cursor.fetchone()
#     conn.commit()
#
#     if deleted_post is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"post with id: {id} does not exist")
#
#     return Response(status_code=status.HTTP_204_NO_CONTENT)
#
#
# @app.put("/posts/{id}")
# def update_post(id: int, post: Post):
#     cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",
#                    (post.title, post.content, post.published, (str(id),)))
#     updated_post = cursor.fetchone()
#     conn.commit()
#
#     if updated_post is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"post with id: {id} does not exist")
#     return {"data": updated_post}
