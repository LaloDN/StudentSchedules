from pydantic import BaseModel, Field
from datetime import date

class Student(BaseModel):
    id: int = Field(default=...,title='Id of the student in DB')
    firstName: str = Field(default=...,title='Fist name of the student',max_length=50)
    secondName: str = Field(default=...,title='Second name of the student',max_length=50)
    studentId: int = Field(default=...,title='Id of the student in the shcool',ge=10000)
    birthday: date = Field(default=...,title='Birthday of the student in DD-MM-YYYY format')
    semester: str = Field(default=...,title='Current grade of the student',ge=1,le=10)
    gpa: float = Field(default=...,title='Grade point average of the student',ge=0,le=100)
    carrerId: int = Field(default=...,title='Database ID of the student carrer')

class Asignature(BaseModel):
    id: int = Field(default=...,title='Id of the asignature in the DB')
    name: str = Field(default=...,title='Name of the asignature',max_length=80)
    semester: str = Field(default=...,title='Grade to which it belongs the asignature',ge=1,le=10)
    carrerId: int = Field(default=...,title='Database ID of the asignature carrer to which it belongs')

class Teacher(BaseModel):
    id: int = Field(default=...,title='Id of the teacher in the DB')
    employeeId: int = Field(default=...,title='Personal employee number of the teacher in the school',ge=1000)
    firstName: str = Field(default=...,title='First name of the teacher',max_length=50)
    secondName: str = Field(default=...,title='Second name of the teacher',max_length=50)

class Carrer(BaseModel):
    id: int = Field(default=...,title='Id of the carrer in the DB')
    name: str = Field(default=...,title='Name of the carrer',max_length=40)
    
class StudentAsignature(BaseModel):
    id: int = Field(default=...,title='Id of the relationship student-asignature')
    idStudent: int = Field(default=...,title='Database ID of the student')
    idAsignature: int = Field(default=...,title='Database ID of the asignature')

class TeacherAsignature(BaseModel):
    id: int = Field(default=...,title='Id of the relationship teacher-asignature')
    hour: string = Field(default=...,title='Schedule of the class',max_length=30)
    groupNo: int = Field(default=...,title='Number of the group class',ge=100,le=999)
    idTeacher: int = Field(default=...,title='Database ID of the teacher')
    idAsignature: int = Field(default=...,title='Database ID of the asignature')
