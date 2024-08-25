from pydantic import BaseModel


class SchemaMealInfo(BaseModel):
    school_name: str
    date: str | int | None = None


class SchemaClassTimeInfo(BaseModel):
    school_name: str
    class_name: str
    class_time: str


class FolderMake(BaseModel):
    folder_name: str = "New Folder"
    folder_password: str | None = None
    folder_admin_password: str


class Encryption(BaseModel):
    data: str


class Decryption(BaseModel):
    data: str
