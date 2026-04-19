# Task 5.5
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from pydantic import EmailStr   #insert at top of the file

class Token(SQLModel):
    access_token: str
    token_type: str

class UserCreate(SQLModel):
    username:str
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)

class UserResponse(SQLModel):
    id: Optional[int]
    username:str
    email: EmailStr

class User(SQLModel, table=False):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    password: str
    role:str = ""

class Admin(User, table=True):
    role:str = "admin"

class RegularUser(User, table=True):
    role:str = "regular_user"

    todos: list['Todo'] = Relationship(back_populates="user")

class TodoCategory(SQLModel, table=True):
    category_id: int = Field(foreign_key="category.id", primary_key=True)
    todo_id: int = Field(foreign_key="todo.id", primary_key=True)

class Category(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key="regularuser.id")
    text:str

    todos:list['Todo'] = Relationship(back_populates="categories", link_model=TodoCategory)

class CategoryResponse(SQLModel):
    id: Optional[int] = Field(primary_key=True, default=None)
    text:str
    # Exercise 1, Step 3 ,Part 2
    class Config:
        from_attributes = True

class CategoryCreate(SQLModel):
    text: str

class TodoCreate(SQLModel):
    text:str

class TodoResponse(SQLModel):
    id: Optional[int] = Field(primary_key=True, default=None)
    text:str
    done: bool = False
    categories: list[CategoryResponse] = [] # Exercise 1, Step 2
    # Exercise 1, Step 3 ,Part 1
    class Config:
        from_attributes = True

class TodoUpdate(SQLModel):
    text: Optional[str] = None
    done: Optional[bool] = None

class Todo(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key="regularuser.id")
    text:str
    done: bool = False

    user: RegularUser = Relationship(back_populates="todos")
    categories:list['Category'] = Relationship(back_populates="todos", link_model=TodoCategory)

    def toggle(self):
        self.done = not self.done
    
    def get_cat_list(self):
        return ', '.join([category.text for category in self.categories])
    
#====================================================================

# Exercises 

#--------------------------------------------------------------------

## Exercise 1
### Update the response datamodel for todos such that it also returns a list of category items. A single category item should show the ID of the category and the category's text

#### Step 1 - Create a Category Response Model
##### See line 46 to 51, the CategoryResponse model between the Category model, and the CategoryCreate model

#### Step 2 - Update the TodoResponse model to include a list of categories
##### See the updated TodoResponse model above on line 53

#### Step 3 - Enable ORM mode for the TodoResponse model
##### See the updated TodoResponse model above on line 55 for part 1, and the updated CategoryResponse model above on line 91 for part 2
#--------------------------------------------------------------------


#====================================================================


""" from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from pydantic import EmailStr   #insert at top of the file

class Token(SQLModel):
    access_token: str
    token_type: str

class UserResponse(SQLModel):
    id: Optional[int]
    username:str
    email: EmailStr

class User(SQLModel, table=False):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    password: str
    role:str = ""

class Admin(User, table=True):
    role:str = "admin"

class RegularUser(User, table=True):
    role:str = "regular_user"

    todos: list['Todo'] = Relationship(back_populates="user")

class TodoCategory(SQLModel, table=True):
    category_id: int = Field(foreign_key="category.id", primary_key=True)
    todo_id: int = Field(foreign_key="todo.id", primary_key=True)

class Category(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key="regularuser.id")
    text:str

    todos:list['Todo'] = Relationship(back_populates="categories", link_model=TodoCategory)

class Todo(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key="regularuser.id")
    text:str
    done: bool = False

    user: RegularUser = Relationship(back_populates="todos")
    categories:list['Category'] = Relationship(back_populates="todos", link_model=TodoCategory)

    def toggle(self):
        self.done = not self.done
    
    def get_cat_list(self):
        return ', '.join([category.text for category in self.categories])


# Task 4.1
class UserCreate(SQLModel):
    username:str
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)


# Task 5.1 
class TodoCreate(SQLModel):
    text:str

class TodoResponse(SQLModel):
    id: Optional[int] = Field(primary_key=True, default=None)
    text:str
    done: bool = False

class TodoUpdate(SQLModel):
    text: Optional[str] = None
    done: Optional[bool] = None
 """