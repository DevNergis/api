from pydantic import BaseModel


class SchemaMealInfo(BaseModel):
    school_name: str
    date: str | int | None = None


class SchemaClassTimeInfo(BaseModel):
    school_name: str
    class_name: str
    class_time: str
