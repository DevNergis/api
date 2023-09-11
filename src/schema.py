from pydantic import BaseModel

class cdt_(BaseModel):
    server_name: str
    invite_link: str
    random: bool

class mealServiceDietInfo_(BaseModel):
    SchoolName: str

class qloat_body_(BaseModel):
    password: str
