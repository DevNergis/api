from pydantic import BaseModel


# noinspection PyPep8Naming
class cdt_(BaseModel):
    server_name: str
    invite_link: str
    random: bool

class mealservicedietinfo_(BaseModel):
    SchoolName: str
