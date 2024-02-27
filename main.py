from fastapi import FastAPI
from pydantic import BaseModel
import sqlalchemy
from databases import Database
from datetime import datetime


# Создание экземпляра FastAPI
app = FastAPI(docs_url='/')

# Конфигурация базы данных
DATABASE_URL = "sqlite:///./test.db"
database = Database(DATABASE_URL)

# Определение модели задачи
class Task(BaseModel):
    description: str
    deadline: datetime
    status: bool

# Создание таблицы задач в базе данных
metadata = sqlalchemy.MetaData()

tasks = sqlalchemy.Table(
    "tasks",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("description", sqlalchemy.String),
    sqlalchemy.Column("deadline", sqlalchemy.DateTime),
    sqlalchemy.Column("status", sqlalchemy.Boolean)
)

# Создание таблицы в базе данных
engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)


# Маршрут для создания новой задачи
@app.post("/tasks/")
async def create_task(task: Task):
    query = tasks.insert().values(
        description=task.description,
        deadline=task.deadline,
        status=task.status
    )
    await database.execute(query)
    return {"message": "Task created successfully"}

# Маршрут для просмотра списка всех задач
@app.get("/tasks/")
async def get_tasks():
    query = tasks.select()
    return await database.fetch_all(query)


# Маршрут для обновления задачи
@app.put("/tasks/{task_id}/")
async def update_task(task_id: int, task: Task):
    query = tasks.update().where(tasks.c.id == task_id).values(
        description=task.description,
        deadline=task.deadline,
        status=task.status
    )
    await database.execute(query)
    return {"message": "Task updated successfully"}

# Маршрут для удаления задачи
@app.delete("/tasks/{task_id}/")
async def delete_task(task_id: int):
    query = tasks.delete().where(tasks.c.id == task_id)
    await database.execute(query)
    return {"message": "Task deleted successfully"}

# Маршрут для просмотра отдельной задачи
@app.get("/tasks/{task_id}/")
async def get_task(task_id: int):
    query = tasks.select().where(tasks.c.id == task_id)
    return await database.fetch_one(query)

from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("username", sqlalchemy.String),
    sqlalchemy.Column("hashed_password", sqlalchemy.String),
)


SECRET_KEY = 'yoursecretcey'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30
# Создание модели пользователя
class User(BaseModel):
    username: str
    password: str

# Хэширование пароля
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Генерация токена
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Маршрут для создания пользователя
@app.post("/users/")
async def create_user(user: User):
    hashed_password = pwd_context.hash(user.password)
    query = user.insert().values(username=user.username, hashed_password=hashed_password)
    await database.execute(query)
    return {"message": "User created successfully"}

# Аутентификация пользователя
def authenticate_user(username: str, password: str):
    user = database.execute(username.select().where(username.c.username == username)).fetchone()
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user

# Создание токена при успешной аутентификации
@app.post("/token/")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# ... (existing code)

from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
import sqlalchemy
from databases import Database
from datetime import datetime, timedelta
# ... (other imports)

# Route for creating a new user
@app.post("/users/")
async def create_user(user: User):
    hashed_password = pwd_context.hash(user.password)
    query = users.insert().values(
        username=user.username,
        hashed_password=hashed_password
    )
    await database.execute(query)
    return {"message": "User created successfully"}

# Route for updating a user
@app.put("/users/{user_id}/")
async def update_user(user_id: int, updated_user: User):
    hashed_password = pwd_context.hash(updated_user.password)
    query = users.update().where(users.c.id == user_id).values(
        username=updated_user.username,
        hashed_password=hashed_password
    )
    await database.execute(query)
    return {"message": "User updated successfully"}

# Route for deleting a user
@app.delete("/users/{user_id}/")
async def delete_user(user_id: int):
    query = users.delete().where(users.c.id == user_id)
    await database.execute(query)
    return {"message": "User deleted successfully"}


# ... (existing code)

# Определение модели банковской карты
class BankCard(BaseModel):
    card_number: str
    card_holder: str
    expiration_date: datetime
    cvv: str

# Создание таблицы банковских карт в базе данных
bank_cards = sqlalchemy.Table(
    "bank_cards",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("card_number", sqlalchemy.String),
    sqlalchemy.Column("card_holder", sqlalchemy.String),
    sqlalchemy.Column("expiration_date", sqlalchemy.DateTime),
    sqlalchemy.Column("cvv", sqlalchemy.String),
)

# Маршрут для создания новой банковской карты
@app.post("/bank-cards/")
async def create_bank_card(card: BankCard):
    query = bank_cards.insert().values(
        card_number=card.card_number,
        card_holder=card.card_holder,
        expiration_date=card.expiration_date,
        cvv=card.cvv,
    )
    await database.execute(query)
    return {"message": "Bank card created successfully"}

# Маршрут для просмотра списка всех банковских карт
@app.get("/bank-cards/")
async def get_bank_cards():
    query = bank_cards.select()






