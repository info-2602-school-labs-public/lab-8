# Task 5.4
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from app.database import SessionDep
from app.models import *
from app.auth import encrypt_password, verify_password, create_access_token, AuthDep
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from fastapi import status

todo_router = APIRouter(tags=["Todo Management"])


@todo_router.get('/todos', response_model=list[TodoResponse])
def get_todos(db:SessionDep, user:AuthDep):
    return user.todos

@todo_router.get('/todo/{id}', response_model=TodoResponse)
def get_todo_by_id(id:int, db:SessionDep, user:AuthDep):
    todo = db.exec(select(Todo).where(Todo.id==id, Todo.user_id==user.id)).one_or_none()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return todo

@todo_router.post('/todos', response_model=TodoResponse)
def create_todo(db:SessionDep, user:AuthDep, todo_data:TodoCreate):
    todo = Todo(text=todo_data.text, user_id=user.id)
    try:
        db.add(todo)
        db.commit()
        db.refresh(todo)
        return todo
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="An error occurred while creating an item",
        )

@todo_router.put('/todo/{id}', response_model=TodoResponse)
def update_todo(id:int, db:SessionDep, user:AuthDep, todo_data:TodoUpdate):
    todo = db.exec(select(Todo).where(Todo.id==id, Todo.user_id==user.id)).one_or_none()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
    if todo_data.text:
        todo.text = todo_data.text
    if todo_data.done is not None:
        todo.done = todo_data.done
    #if todo_data.done:
        #todo.done = todo_data.done
    try:
        db.add(todo)
        db.commit()
        return todo
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="An error occurred while updating an item",
        )

@todo_router.delete('/todo/{id}', status_code=status.HTTP_200_OK)
def delete_todo(id:int, db:SessionDep, user:AuthDep):

    todo = db.exec(select(Todo).where(Todo.id==id, Todo.user_id==user.id)).one_or_none()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
    try:
        db.delete(todo)
        db.commit()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="An error occurred while deleting an item",
        )
    
#====================================================================

# Exercises 

#--------------------------------------------------------------------

## Exercise 2
### Build out the following endpoints for category management

# +-----------------------------------+---------------------+-------------+-----------------------------------------------------------------------------------------------------------------------------------------------------+
# | Route Name (AuthorizedUser Class) | Route                             | HTTP Method | Description                                                                                                                           |
# +-----------------------------------+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------------------+
# | Create Category                   | /category                         | POST        | Create a new category for the **CURRENT LOGGED IN** user                                                                              |
# +-----------------------------------+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------------------+
# | Add Category to Todo              | /todo/{todo_id}/category/{cat_id} | POST        | Assigns the category cat_id to the todo todo_id if the user is authorized to access it                                                |  
# +-----------------------------------+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------------------+
# | Remove Category from Todo         | /todo/{todo_id}/category/{cat_id} | DELETE      | Removes the category cat_id from the todo todo_id if the user is authorized to access it and if the category was assigned to the todo |
# +-----------------------------------+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------------------+
# | Get todos for category            | /category/{cat_id}/todos          | GET         | Retrieves ALL todos for the category cat_id for the CURRENT LOGGED IN user if the user is authorized to access it                     |
# +-----------------------------------+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------------------+

##--------------------------------------------------------------------
### Part 1 - Create Category

@todo_router.post("/category", response_model=CategoryResponse)
def create_category(db: SessionDep, user: AuthDep, category_data: CategoryCreate):
    category = Category(
        text=category_data.text, 
        user_id=user.id
    )
    try:
        db.add(category)
        db.commit()
        db.refresh(category)
        return category
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not create category",
        )
    
##--------------------------------------------------------------------
### Part 1 - Add Category to Todo

@todo_router.post("/todo/{todo_id}/category/{cat_id}")
def add_category_to_todo(todo_id:int, cat_id:int, db: SessionDep, user: AuthDep):

    todo = db.exec(
        select(Todo).where(Todo.id==todo_id, Todo.user_id==user.id)
        ).one_or_none()
    
    category = db.exec(
        select(Category).where(Category.id==cat_id, Category.user_id==user.id)
        ).one_or_none()
    
    if not todo or not category:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
    
    if category in todo.categories:
        return {"detail": "Category already added to todo"}
    try:
        todo.categories.append(category)
        db.commit()
        return {"detail": "Category added to todo"}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not add category to todo",
        )
    
##--------------------------------------------------------------------
### Part 3 - Remove Category from Todo

@todo_router.delete("/todo/{todo_id}/category/{cat_id}")
def remove_category_from_todo(todo_id:int, cat_id:int, db: SessionDep, user: AuthDep):

    todo = db.exec(
        select(Todo).where(Todo.id==todo_id, Todo.user_id==user.id)
    ).one_or_none()
    
    category = db.exec(
        select(Category).where(Category.id==cat_id, Category.user_id==user.id)
    ).one_or_none()
    
    if not todo or not category:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
    
    if category not in todo.categories:
        return {"detail": "Category not assigned to todo"}
    try:
        todo.categories.remove(category)
        db.commit()
        return {"detail": "Category removed from todo"}
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not remove category from todo",
        )
    
##--------------------------------------------------------------------
### Part 4 - Get todos for category

@todo_router.get("/category/{cat_id}/todos", response_model=list[TodoResponse])
def get_todos_for_category(cat_id:int, db: SessionDep, user: AuthDep):

    category = db.exec(
        select(Category).where(Category.id==cat_id, Category.user_id==user.id)
    ).one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
    
    return category.todos

##--------------------------------------------------------------------
#====================================================================