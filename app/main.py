from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = FastAPI()

while True:
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="socialmedia",
            user="postgres",
            password="1234$",
            cursor_factory=RealDictCursor
        )

        cursor = conn.cursor()
        print("Database connection successful")
        break
    except Exception as error:
        print("Database connection failed")
        print("Error:", error)
        

class Post(BaseModel):
    title: str
    content: str
    published: bool = True

my_posts = [
    {"title": "Post 1", "content": "Content of post 1", "id": 1, "published": True, "rating": 5.0},
    {"title": "Post 2", "content": "Content of post 2", "id": 2, "unpublished": False, "rating": 4.5}
]

def find_post(id):
    for p in my_posts:
        if p['id'] == id:
            return p

@app.get("/")
def root():
    return {"message": "Hello World This is Social Media"}

@app.get("/posts")
def get_posts():
    posts = cursor.execute("""
        SELECT * FROM posts
    """)
    posts = cursor.fetchall()

    return {"data": posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    cursor.execute("""
        INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *
        """, (post.title, post.content, post.published))
    new_post = cursor.fetchone()

    conn.commit()

    return {"data": new_post}

@app.get("/posts/{id}")
def get_post(id: int):
    cursor.execute("""
        SELECT * FROM posts WHERE id = %s
        """, (str(id),))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} was not found!")

    return {"data": post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute("""
        DELETE FROM posts WHERE id = %s RETURNING *
    """, (str(id),))
    deleted_post = cursor.fetchone()
    conn.commit()

    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} was not found!")
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute("""
        UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *
    """, (post.title, post.content, post.published, str(id),))
    updated_post = cursor.fetchone()
    conn.commit()

    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} was not found!")
    
    return {"data": updated_post}