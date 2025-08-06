from pydantic import BaseModel
from typing import Optional


'''
 Pydantic is the data-validation library for python that is supported in the FastApi too.
 kind of yup for python
'''
class TaskCreate(BaseModel):
    title: str
    description: str
    user_id: int

class TaskStatus(BaseModel):
    id: str
    status: str
    result: Optional[dict] = None