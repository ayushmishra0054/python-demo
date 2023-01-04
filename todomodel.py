from pydantic import BaseModel
class todo(BaseModel):
    userid: int
    todoid: int
    title:  str
    completed: bool