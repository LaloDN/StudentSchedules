from pydantic import BaseModel, Field
from datetime import date
from typing import Union


class Student(BaseModel):
    firstName: str = Field(default=...,title='Fist name of the student',max_length=50)
    secondName: str = Field(default=...,title='Second name of the student',max_length=50)
    studentId: int = Field(default=...,title='Id of the student in the shcool',ge=10000)
    birthday: date = Field(default=...,title='Birthday of the student in DD-MM-YYYY format')
    semester: int = Field(default=...,title='Current grade of the student',ge=1,le=10)
    gpa: float = Field(default=...,title='Grade point average of the student',ge=0,le=100)
    carrerId: int = Field(default=...,title='Database ID of the student carrer')

    class Config:
        schema_extra ={
            "example": {
                "firstName": "Horacio",
                "secondName": "Gomez",
                "studentId": 19930,
                "birthday": "22-04-2011",
                "semester": 2,
                "gpa": 77.8,
                "carrerId": 2
            }
        }

class Asignature(BaseModel):
    name: str = Field(default=...,title='Name of the asignature',max_length=80)
    semester: int = Field(default=...,title='Grade to which it belongs the asignature',ge=1,le=10)
    carrerId: int = Field(default=...,title='Database ID of the asignature carrer to which it belongs')

    class Config:
        schema_extra ={
            "example": {
                "name": "Phisical Education IV",
                "semster": 5,
                "carrerId": 3
            }
        }

class Teacher(BaseModel):
    employeeId: int = Field(default=...,title='Personal employee number of the teacher in the school',ge=1000)
    firstName: str = Field(default=...,title='First name of the teacher',max_length=50)
    secondName: str = Field(default=...,title='Second name of the teacher',max_length=50)

    class Config:
        schema_extra ={
            "example": {
                "employeeId": 2004,
                "firstName": "George",
                "secondName": "Mendel"
            }
        }

class Carrer_Scheme(BaseModel):
    """Carrer input model"""
    name: str = Field(default=...,title='Carrer name',description='Name of the carrer',max_length=40,example="Aviation")

class Carrer_DB(Carrer_Scheme):
    """Carrer database model with id field"""
    id : int = Field(title="Carrer ID",description='Id of the carrer in the database')
    
    class Config:
        schema_extra ={
            "single_example": {
                "id": 20,
                "name": "Elementary education"
            },
            "list_example":[
                {
                    "id": 4,
                    "name": "Robotics"
                },
                {
                    "id": 37,
                    "name": "Electronic engineering"
                },
                {
                    "id": 122,
                    "name": "Aviation"
                }
            ]
        }

class StudentAsignature(BaseModel):
    idStudent: int = Field(default=...,title='Database ID of the student')
    idAsignature: int = Field(default=...,title='Database ID of the asignature')

    class Config:
        schema_extra ={
            "example": {
                "idStudent": 23003,
                "idAsignature": 4,
            }
        }

class TeacherAsignature(BaseModel):
    hour: str = Field(default=...,title='Schedule of the class',max_length=30)
    groupNo: int = Field(default=...,title='Number of the group class',ge=100,le=999)
    idTeacher: int = Field(default=...,title='Database ID of the teacher')
    idAsignature: int = Field(default=...,title='Database ID of the asignature')

    class Config:
        schema_extra ={
            "example": {
                "hour": "14:00:00",
                "groupNo": 340,
                "idTeacher": 2003,
                "idAsignature": 13
            }
        }
