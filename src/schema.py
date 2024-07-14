from pydantic import BaseModel

__folder_json__ = {
    "folder_uuid": "hex(uuid)",
    "folder_name": "hex(base85(input(folder_name))",
    "folder_password": "hex(password_hash)",
    "folder_contents": [
        {
            "file_uuid": "hex(uuid)",
            "file_name": "hex(base85(input(file_name))"
        },
        {
            "file_uuid": "hex(uuid)",
            "file_name": "hex(base85(input(file_name))"
        }
    ]
}

folder_json = {
    "folder_uuid": "hex(uuid)",
    "folder_name": "hex(base85(input(folder_name))",
    "folder_password": "hex(password_hash)",
    "folder_contents": [
        {
            "file_uuid": "hex(uuid)",
            "file_name": "hex(base85(input(file_name))"
        },
        {
            "file_uuid": "hex(uuid)",
            "file_name": "hex(base85(input(file_name))"
        }
    ]
}


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
