
from fastapi import APIRouter, Depends, Query, Body, HTTPException
from typing import Annotated, List
from utils import model_to_dict
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from sql.connection import db_connection
from schemes import Student_Auxiliar, Student_DB, Student_Scheme
from sql.definition import Student
from utils import Error400, Error404
from datetime import datetime

router = APIRouter(prefix="/students",tags=["Student"])

@router.post('/create/',status_code=201,responses={
    201:{
            "description": "Teacher item created",
            "content": {
                "application/json": {
                    "example": {'status_code':201,'message':'Student registered successfully!', 'id':88}
                }
            }},
    400:{
        "description": "Teacher already exists or employee ID has already taken",
                    "content": {
                        "application/json": {
                            "example": {'detail':{'message':'A student with the same name is already registered'}}
                        }
            }
        },
    500:{
            "description": "Function internal error",
            "content": {
                "application/json": {
                    "example": {'detail':{'message':'Function error','error':'Some Python error message...'}}
                }
            }},
    560:{
            "description": "SQLAlchemy error",
            "content": {
                "application/json": {
                    "example": {'detail':{'message':'SQLAlchemy error','error':'Some SQLALchemy error message...'}}
                }
            }}
})
async def new_student(student :Annotated[Student_Scheme,Body],session = Depends(db_connection)):
    """Create a new student"""
    try:
        student : Student_Scheme
        
        #Check if student exists
        result = session.query(Student).filter_by(firstName = student.firstName, secondName = student.secondName).first()
        if result:
            raise Error400('A student with the same name is already registered')
        result = session.query(Student).filter_by(studentId = student.studentId).first()
        if result:
            raise Error400('A student with the same student id is already registered')
        #Parse the date string from request to date
        birthday = datetime.strptime(student.birthday,'%Y-%m-%d')
        student.birthday = birthday.date()
        student_dict = student.dict()
        student_db = Student(**student_dict)
        session.add(student_db) 
        result = session.query(Student.id).filter_by(firstName = student.firstName, secondName = student.secondName).first()

        if result:
            session.commit()
            return {'status_code':201,'message':'Student registered successfully!', 'id':result[0]}
        else:
            session.rollback()
            raise Exception("There was an error registering the student")       
    except Error400 as e:
        raise HTTPException(status_code=400, detail = {'message': str(e)})
    except Exception as e:
        raise HTTPException(status_code=500, detail = {'message': 'Function error','error':str(e)})
    except SQLAlchemyError as e:
        raise HTTPException(status_code=560, detail = {'message': 'SQLAlchemy error','error':str(e)})

@router.get('/search/',status_code=200,response_model=Student_DB)
async def get_student(student : Annotated[Student_Auxiliar,Body], session = Depends(db_connection)):
    """Search one student in the database"""
    try:
        student : Student_Auxiliar
        if student.firstName and student.secondName:
            result = session.query(Student).filter(Student.firstName.ilike(f'%{student.firstName}%'),
                                            Student.secondName.ilike(f'%{student.secondName}')).first()
        elif student.firstName or student.secondName:
            result = session.query(Student).filter(or_(Student.firstName.ilike(f'%{student.firstName}%'),
                                            Student.secondName.ilike(f'%{student.secondName}'))).first()
        elif student.studentId:
            result = session.query(Student).filter_by(studentId = student.studentId).first()
        elif student.id:
            result = session.query(Student).filter_by(id = student.id).first()
        else:
            raise Error400
        
        if result is None:
            raise Error404

        student_db = Student_DB(**model_to_dict(result))
        return student_db
    except Error400:
        raise HTTPException(status_code=400,detail={'message': 'You must provide either name(s) or id for the student to be returned'})
    except Error404:
        raise HTTPException(status_code=404,detail={'message': 'Record not found in the database'})
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500,detail={'message': 'SQLAlchemy error','error':str(e)})
    except Exception as e:
        raise HTTPException(status_code=560,detail={'message': 'Function error', 'error':str(e)})

@router.get('/obtain/',status_code=200, response_model=List[Student_DB])
async def get_students(session=Depends(db_connection)):
    """Get a full list of students"""
    try:
        results = session.query(Student).all()
        students_dict = [model_to_dict(row) for row in results]
        students = [Student_DB(**students_dict)]
        return students
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500,detail={'message': 'SQLAlchemy error','error':str(e)})
    except Exception as e:
        raise HTTPException(status_code=560,detail={'message': 'Function error', 'error':str(e)})
    
@router.put('/modify/',status_code=201, response_model=Student_DB,responses={
    400:{
            "description": "Bad request: missing required fields or the data updates more or less than one item at once",
            "content": {
                "application/json": {
                    "example": {'detail':{'message':'You most specify at least one field that will be modified'}}
                }
            }},
    404:{
            "description": "Student item not found in the database",
            "content": {
                "application/json": {
                    "example": {'detail':{'message':'Record not found in the database'}}
                }
            }},
    500:{
            "description": "Function internal error",
            "content": {
                "application/json": {
                    "example": {'detail':{'message':'Function error','error':'Some Python error message...'}}
                }
            }},
    560:{
            "description": "SQLAlchemy error",
            "content": {
                "application/json": {
                    "example": {'detail':{'message':'SQLAlchemy error','error':'Some SQLALchemy error message...'}}
                }
            }}
})
async def modify_student(student : Annotated[Student_Auxiliar,Body], session = Depends(db_connection)):
    """Modify the fields of one student"""
    try:
        student: Student_Auxiliar
        old_record : Student
        if not(student.birthday or student.careerId or student.firstName or student.secondName or student.gpa or student.semester or student.studentId):
            raise Error400("You must specify at least one field that will be modified")

        old_record = session.query(Student).filter_by(id = student.id).first()
        if old_record is None:
            raise Error404

        result = session.query(Student).filter_by(id = student.id).update({
            Student.birthday: student.birthday if student.birthday else old_record.birthday,
            Student.careerId: student.careerId if student.careerId else old_record.careerId,
            Student.firstName: student.firstName if student.firstName else old_record.firstName,
            Student.secondName: student.secondName if student.secondName else old_record.secondName,
            Student.gpa: student.gpa if student.gpa else old_record.gpa,
            Student.semester: student.semester if student.semester else old_record.semester,
            Student.studentId: student.studentId if student.studentId else old_record.studentId
        })
        if result != 1:
            session.rollback()
            raise Error400("There was an error while updating the record")
        session.commit()
        new_record = session.query(Student).filter_by(id = student.id).first()
        new_student = Student_DB(**model_to_dict(new_record))
        return new_student
    except Error400 as e:
        raise HTTPException(status_code=400,detail={'message': str(e)})
    except Error404:
        raise HTTPException(status_code=404,detail={'message': 'Record not found in the database'})
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500,detail={'message': 'SQLAlchemy error','error':str(e)})
    except Exception as e:
        raise HTTPException(status_code=560,detail={'message': 'Function error', 'error':str(e)})   

@router.delete('/erase/',status_code=201,responses={
     201:{
            "description": "Student item removed successfully",
            "content": {
                "application/json": {
                    "example": {'status_code': 201,'message': f'Success! Student John Winston was deleted successfully'}
                }
            }},
    400:{
            "description": "The student cannot be removed",
            "content": {
                "application/json": {
                    "example": {'detail':{'message':'There was an error deleting the student'}}
                }
            }},
    404:{
            "description": "Student item not found in the database",
            "content": {
                "application/json": {
                    "example": {'detail':{'message':'Record not found in the database'}}
                }
            }},
    500:{
            "description": "Function internal error",
            "content": {
                "application/json": {
                    "example": {'detail':{'message':'Function error','error':'Some Python error message...'}}
                }
            }},
    560:{
            "description": "SQLAlchemy error",
            "content": {
                "application/json": {
                    "example": {'detail':{'message':'SQLAlchemy error','error':'Some SQLALchemy error message...'}}
                }
            }}
})
async def delete_student(student_id: Annotated[int,Query(ge=0,example=204,description="Id of the student to be deleted")],
                            session = Depends(db_connection)):
    """Deletes one student from the database by their id"""
    try:
        student = session.query(Student.firstName,Student.secondName).filter_by(id = student_id).first()
        if student is None:
            raise Error404 
        result = session.query(Student).filter_by(id = student_id).delete()
        if result != 1:
            session.rollback()
            raise Error400 
        session.commit()
        return {'status_code':201,'message':f'Success! The student {student[0]} {student[1]} was deleted succesfully'}
    except Error400:
        raise HTTPException(status_code=400,detail={'message': 'There was an error deleting the student'})
    except Error404:
        raise HTTPException(status_code=404,detail={'message': f'The student with id {student_id} does not exist'})
    except Exception as e:
        raise HTTPException(status_code=500,detail={'message': 'Function error', 'error':str(e)})
    except SQLAlchemyError() as e:
        raise HTTPException(status_code=560,detail={'message': 'SQLAlchemy error','error':str(e)})