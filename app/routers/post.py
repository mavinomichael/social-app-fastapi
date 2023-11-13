from typing import List, Optional
from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session, joinedload, subqueryload
from sqlalchemy import func, and_
from .. import models, schemas, oauth2
from ..database import get_db

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)


@router.get("/", response_model=List[schemas.PostResponse])
def get_posts(db: Session = Depends(get_db),
              limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    posts = db.query(
        models.Post,
        func.count(models.Vote.post_id).label("votes")) \
        .outerjoin(models.Vote, and_(models.Post.id == models.Vote.post_id)) \
        .options(subqueryload(models.Post.owner)) \
        .group_by(models.Post.id) \
        .filter(models.Post.title.contains(search)) \
        .limit(limit) \
        .offset(skip) \
        .all()

    posts = [dict(post._mapping) for post in posts]
    return posts


# included a comma next to str(id) in case of a bug that arises, response_model=schemas.PostResponse
@router.get("/{id}", response_model=schemas.PostResponse)
def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(
        models.Post,
        func.count(models.Vote.post_id).label("votes")
    ) \
        .outerjoin(models.Vote, and_(models.Post.id == models.Vote.post_id)) \
        .options(subqueryload(models.Post.owner)) \
        .filter(models.Post.id == id) \
        .group_by(models.Post.id) \
        .first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {id} not found")

    post = dict(post._mapping)

    return post


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db),
                current_user: models.User = Depends(oauth2.get_current_user)):
    new_post = models.Post(owner_id=current_user.id, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db),
                current_user: models.User = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorised to perform requested action")

    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.Post)
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db),
                current_user: models.User = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post_found = post_query.first()

    if post_found is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorised to perform requested action")

    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()

    return post_query.first()
