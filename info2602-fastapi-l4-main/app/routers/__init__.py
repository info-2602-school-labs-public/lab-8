from fastapi import APIRouter
main_router = APIRouter()

# Task 3.1 addition
from .auth import auth_router
main_router.include_router(auth_router)

# Task 5.2 
from .todo import todo_router
main_router.include_router(todo_router)

