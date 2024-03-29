from pydantic import BaseModel, Field
from datetime import date
from typing import Union

#region student
class Student_Scheme(BaseModel):
    """Student input model"""
    firstName: str = Field(default=...,title='Fist name of the student',max_length=50)
    secondName: str = Field(default=...,title='Second name of the student',max_length=50)
    studentId: int = Field(default=...,title='Id of the student in the shcool',ge=10000)
    birthday: Union[str,date] = Field(default=...,title='Birthday of the student in YYYY-MM-DD format',regex=r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])$")
    semester: int = Field(default=...,title='Current grade of the student',ge=1,le=10)
    gpa: float = Field(default=...,title='Grade point average of the student',ge=0,le=100)
    careerId: int = Field(default=...,title='Database ID of the student career')

    class Config:
        schema_extra ={
            "example": {
                "firstName": "Horacio",
                "secondName": "Gomez",
                "studentId": 19930,
                "birthday": "2002-04-11",
                "semester": 2,
                "gpa": 77.8,
                "careerId": 2
            }
        }

class Student_DB(Student_Scheme):
    """Student model with id field"""
    id : int = Field(title="Student ID",description="Id of the student in the database")

class Student_Auxiliar(BaseModel):
    """An auxiliar model which is used to search a student or modify the information of a student"""
    id : int = Field(default=0,title="Student ID",description="Id of the student in the database")
    firstName: Union[str,None] = Field(default=None,title='Fist name of the student',max_length=50)
    secondName: Union[str,None] = Field(default=None,title='Second name of the student',max_length=50)
    studentId: Union[int,None] = Field(default=None,title='Id of the student in the shcool',ge=10000)
    birthday: Union[date,None] = Field(default=None,title='Birthday of the student in DD-MM-YYYY format')
    semester: Union[int,None] = Field(default=None,title='Current grade of the student',ge=1,le=10)
    gpa: Union[float,None] = Field(default=None,title='Grade point average of the student',ge=0,le=100)
    careerId: Union[int,None] = Field(default=None,title='Database ID of the student career')
#endregion

#region subject
class Subject_Scheme(BaseModel):
    """Subject input model"""
    name: str = Field(default=...,title='Name of the subject',max_length=80)
    semester: int = Field(default=...,title='Grade to which it belongs the subject',ge=1,le=10)
    careerId: int = Field(default=...,title='Database ID of the subject career to which it belongs')

    class Config:
        schema_extra ={
            "example": {
                "name": "Phisical Education IV",
                "semster": 5,
                "careerId": 3
            }
        }

class Subject_DB(Subject_Scheme):
    """Subject model with id field"""
    id : int = Field(title="Subject ID",description="Id of the subject in the database")

class Subject_Auxiliar(BaseModel):
    """An auxiliar model which is used to search a student or modify the information of a student"""
    id : int = Field(default=0,title="Student ID",description="Id of the subject in the database")
    name: Union[str,None] = Field(default=None,title='Name of the subject',max_length=80)
    semester: Union[int,None] = Field(default=0,title='Grade to which it belongs the subject',ge=1,le=10)
    careerId: Union[int,None] = Field(default=0,title='Database ID of the subject career to which it belongs')

    class Config:
        schema_extra ={
            "example": {
                "id": 23,
                "name": "Phisical Education IV",
                "semster": 5,
                "careerId": 3
            }
        }
#endregion

#region teacher
class Teacher_Scheme(BaseModel):
    """Teacher input model"""
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

class Teacher_DB(Teacher_Scheme):
    """Career database model with id field"""
    id : int = Field(title="Teacher ID", description="Id of the teacher in the database")

class Teacher_Auxiliar(BaseModel):
    """An axuliar model which is used to search a teacher or modify the information of a teacher"""
    id : int = Field(default=0,title="Teacher ID", description="Id of the teacher in the database")
    employeeId: Union[int,None] = Field(default=None,title='Personal employee number of the teacher in the school',ge=1000)
    firstName: Union[str,None] = Field(default=None,title='First name of the teacher',max_length=50)
    secondName: Union[str,None] = Field(default=None,title='Second name of the teacher',max_length=50)

    class Config:
        schema_extra ={
            "example": {
                "employeeId": 2004,
                "firstName": "George",
                "secondName": "Mendel",
                "id": 96
            }
        }
#endregion

#region career
class Career_Scheme(BaseModel):
    """Career input model"""
    name: str = Field(default=...,title='Career name',description='Name of the career',max_length=40,example="Aviation")

class Career_DB(Career_Scheme):
    """Career database model with id field"""
    id : int = Field(title="Career ID",description='Id of the career in the database')
#endregion

#region class
class Classes_Scheme(BaseModel):
    """Classes input model"""
    hour: str = Field(default=...,title='Schedule of the class',max_length=30)
    groupNo: int = Field(default=...,title='Number of the group class',ge=100,le=999)
    idTeacher: int = Field(default=...,title='Database ID of the teacher')
    idSubject: int = Field(default=...,title='Database ID of the subject')

    class Config:
        schema_extra ={
            "example": {
                "hour": "14:00:00",
                "groupNo": 340,
                "idTeacher": 2003,
                "idSubject": 13
            }
        }

class Classes_DB(Classes_Scheme):
    """Classes database model with an ID"""
    id : int = Field(title='Classes ID',description='ID of the class inside the database')

class Classes_Auxiliar(BaseModel):
    """An axuliar model which is used to search a class or modify the information of a class"""
    id : int = Field(default=0,title="Class ID", description="Id of the class in the database") 
    hour: str = Field(default=None,title='Schedule of the class',max_length=30)
    groupNo: Union[int,None] = Field(default=None,title='Number of the group class',ge=100,le=999)
    idTeacher: Union[int,None] = Field(default=None,title='Database ID of the teacher',gt=0)
    idSubject: Union[int,None] = Field(default=None,title='Database ID of the subject',gt=0)

    class Config:
        schema_extra ={
            "example": {
                "hour": "14:00:00",
                "groupNo": 340,
                "idTeacher": 2003,
                "idSubject": 13
            }
        }
#endregion

class StudentClasses_Scheme(BaseModel):
    """Student-Classes input model"""
    idStudent: int = Field(default=...,title='Student ID',description='Database ID of the student')
    idClass: int = Field(default=...,title='Class ID',description='Database ID of the class')

    class Config:
        schema_extra ={
            "example": {
                "idStudent": 23003,
                "idClass": 4,
            }
        }

class StudentClasses_DB(StudentClasses_Scheme):
    """Student Class database model with ID field"""
    id: int = Field(title='StudentClasses ID',description='Database ID of the student-class')

