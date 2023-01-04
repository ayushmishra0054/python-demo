from fastapi import FastAPI,status,Security
from fastapi.middleware.cors import CORSMiddleware
import json,todomodel
from typing import Union
from pydantic import BaseModel, AnyHttpUrl, BaseSettings, Field
from fastapi_azure_auth import SingleTenantAzureAuthorizationCodeBearer

#AUTH

class Settings(BaseSettings):
    SECRET_KEY: str = Field('my super secret key', env='SECRET_KEY')
    BACKEND_CORS_ORIGINS: list[Union[str, AnyHttpUrl]] = ['http://localhost:8000']
    OPENAPI_CLIENT_ID: str = Field(default='', env='OPENAPI_CLIENT_ID')
    APP_CLIENT_ID: str = Field(default='', env='APP_CLIENT_ID')
    TENANT_ID: str = Field(default='', env='TENANT_ID')

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = True

settings = Settings()

#INIT

app = FastAPI()

with open('/home/ayush/Documents/Python-Demo/todos.json') as f:
    data=json.load(f)
data2=json.dumps(data,indent=2)

class Todo(BaseModel):
    userid: int
    todoid: int
    title:  str
    completed: bool

#more auth
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
azure_scheme = SingleTenantAzureAuthorizationCodeBearer(
    app_client_id=settings.APP_CLIENT_ID,
    tenant_id=settings.TENANT_ID,
    scopes={
        f'api://{settings.APP_CLIENT_ID}/user_impersonation': 'user_impersonation',
    }
)

#CRUD operations
@app.get("/", dependencies=[Security(azure_scheme)])
async def root():
    return data2

@app.get("/completed")
async def completed():
    return{"completed": true}

@app.get("/todos/{todoid}")
async def todos(todoid:int):
    ret={}
    for todo in data2:
        if todo.todoid==todoid:
            ret.append(todo)
    return ret
    
@app.get("/todos/user/{uid}")
def red_todos(uid: int):
    ret={}
    for todo in data2:
        if todo.userid==uid:
            ret.append(todo)
    return ret

@app.post("/todos/",status_code=status.HTTP_201_CREATED)
async def create_todo(todo: Todo):
        ins = {
            "userId": todo.userid,
            "id" : todo.itemid,
            "title" : todo.description,
            "completed" : todo.completed
        }
        data2.append(ins)
#write to file:
        with open("todos.json", "w") as f: 
            json.dump(data2, f) 

@app.put("/todos/{id}",status_code=status.HTTP_201_CREATED)
async def create_todo(id : int ,todo: Todo):
    # print(id)
        ins = (data2[id-1])
        data2.pop(id-1)
        ins = {
            "userId": todo.userid,
            "id" : todo.itemid,
            "title" : todo.description,
            "completed" : todo.completed
        }
        data2.append(ins)
        print(data2)
        with open("todos.json", "w") as f: 
            json.dump(data2, f) 

@app.delete("/todos/{id}",status_code=status.HTTP_200_OK)
async def del_todo(id : int):
        i = 0
        while i <len(data2):
            if data2[i]["id"] == id:
                data2.pop(id-1)
                break
            i+=1
        with open("todos.json", "w") as f: 
            json.dump(data2, f) 

@app.on_event('startup')
async def load_config() -> None:
    """
    Load OpenID config on startup.
    """
    await azure_scheme.openid_config.load_config()