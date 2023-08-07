from fastapi import APIRouter, Body, HTTPException, Query, Depends
from sqlalchemy import exc,or_
from typing import Annotated, List, Union
from sqlalchemy.exc import SQLAlchemyError
from sql.connection import db_connection
from schemes import Teacher_DB, Teacher_Scheme, Teacher_Auxiliar
from sql.definition import Teacher
from utils import model_to_dict, Error400, Error404

router = APIRouter(prefix='/teachers',tags=['Teacher'])

@router.post('/create/',status_code=201, responses={
    201:{
            "description": "Teacher item created",
            "content": {
                "application/json": {
                    "example": {'status_code':201,'message':'Teacher registered successfully!', 'id':204}
                }
            }},
    400:{
        "description": "Teacher already exists or employee ID has already taken",
                    "content": {
                        "application/json": {
                            "example": {'detail':{'message':'A teacher with the same name is already registered'}}
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
async def new_teacher(teacher : Annotated[Teacher_Scheme,Body], session = Depends(db_connection)):
    """Create a new teacher"""
    try:
        #Check if teacher already exists by their names and check if employee ID is unique
        result = session.query(Teacher).filter(Teacher.firstName == teacher.firstName,
        Teacher.secondName == teacher.secondName).first()
        if result:
            raise Error400("A teacher with the same name is already registered")
        result = session.query(Teacher).filter_by(employeeId = teacher.employeeId).first()
        if result:
            raise Error400("The given employee ID it's already assigned")

        teacher_dict = teacher.dict()
        teacher_db = Teacher(**teacher_dict)
        session.add(teacher_db)
        result = session.query(Teacher.id).filter(Teacher.firstName == teacher.firstName,
        Teacher.secondName == teacher.secondName).first()

        if result:
            session.commit()
            return {'status_code':201,'message':'Teacher registered successfully!', 'id':result[0]}
        else:
            session.rollback()
            raise Exception("There was an error registering the teacher")

    except Error400 as e:
        raise HTTPException(status_code=400, detail = {'message': str(e)})
    except Exception as e:
        raise HTTPException(status_code=500, detail = {'message': 'Function error','error':str(e)})
    except SQLAlchemyError as e:
        raise HTTPException(status_code=560, detail = {'message': 'SQLAlchemy error','error':str(e)})

@router.get('/search/',status_code=200, response_model=Teacher_DB, responses={
    200:{
            "description": "Teacher item retrieved",
            "content": {
                "application/json": {
                    "example": {'employeeId':2030, 'firstName': 'Marco', 'secondName': 'D-Rossi', 'id':1}
                }
            }},
    400:{
            "description": "Bad request: no one of the required fields is present",
            "content": {
                "application/json": {
                    "example": {'detail':{'message': 'You must provide either name(s) or id for the teacher to be returned'}}
                }
            }},
    404:{
            "description": "Teacher item not found",
            "content": {
                "application/json": {
                    "example": {'detail':{'message': 'Record not found in the database'}} 
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
async def get_teacher(teacher : Annotated[Teacher_Auxiliar,Body],
                        sesion = Depends(db_connection)):
    """Get one teacher from the database based on the given search parameters"""
    try:
        if teacher.firstName and teacher.secondName:
            result = sesion.query(Teacher).filter(Teacher.firstName.ilike(f'%{teacher.firstName}%'),
                    Teacher.secondName.ilike(f'%{teacher.secondName}%')).first()
        elif teacher.firstName or teacher.secondName:
            result = sesion.query(Teacher).filter(or_(Teacher.firstName.ilike(f'%{teacher.firstName}%'),
                    Teacher.secondName.ilike(f'%{teacher.secondName}%'))).first()
        elif teacher.employeeId:
            result = sesion.query(Teacher).filter_by(employeeId = teacher.employeeId).first()
        elif teacher.id:
            result = sesion.query(Teacher).filter(Teacher.id == teacher.id).first()
        else:
            raise Error400
        
        if result is None:
            raise Error404

        teacher_db = Teacher_DB(**model_to_dict(result))
        return teacher_db

    except Error400:
        raise HTTPException(status_code=400,detail={'message': 'You must provide either name(s) or id for the teacher to be returned'})
    except Error404:
        raise HTTPException(status_code=404,detail={'message': 'Record not found in the database'})
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500,detail={'message': 'SQLAlchemy error','error':str(e)})
    except Exception as e:
        raise HTTPException(status_code=560,detail={'message': 'Function error', 'error':str(e)})
        
@router.get('/obtain/',status_code=200, response_model=List[Teacher_DB], responses={
    200:{
            "description": "Teacher items retrieved successfully",
            "content": {
                "application/json": {
                    "example":[
                                {
                                    "employeeId": 2390,
                                    "firstName": "Dillan",
                                    "secondName": "Smith",
                                    "id": 1
                                },
                                {
                                    "employeeId": 3511,
                                    "firstName": "Bob",
                                    "secondName": "Ishigami",
                                    "id": 30
                                },
                                {
                                    "employeeId": 1005,
                                    "firstName": "Roberto",
                                    "secondName": "Fuentes",
                                    "id": 4
                                }
                            ]
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
async def get_teachers(session = Depends(db_connection)):
    """Get the full list of all the teachers"""
    try:
        result = session.query(Teacher).all()
        teacher_dicts = [model_to_dict(row) for row in result]
        teachers = [Teacher_DB(**t) for t in teacher_dicts]
        return teachers
    except Exception as e:
        raise HTTPException(status_code=500,detail={'message': 'Function error', 'error':str(e)})
    except SQLAlchemyError as e:
        raise HTTPException(status_code=560,detail={'message': 'SQLAlchemy error','error':str(e)})

@router.put('/modify/',status_code=201,response_model=Teacher_DB, responses={
    201:{
            "description": "Teacher item modified successfully",
            "content": {
                "application/json": {
                    "example": {"employeeId": 2134,"firstName": "Jurgen", "secondName": "Crock", "id": 1}
                }
            }},
    400:{
            "description": "Bad request: missing required fields or the data updates more or less than one item at once",
            "content": {
                "application/json": {
                    "example": {'detail':{'message':'You most specify at least one field that will be modified'}}
                }
            }},
    404:{
            "description": "Teacher item not found in the database",
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
async def modify_teacher(teacher: Annotated[Teacher_Auxiliar,Body],session = Depends(db_connection)):
    """Modify a teacher's information"""
    try:
        if not(teacher.employeeId or teacher.firstName or teacher.secondName):
            raise Error400("You most specify at least one field that will be modified")
        
        #We use the id to serach the teacher, the other fields will be used to update the information
        old_record = session.query(Teacher).filter_by(id=teacher.id).first()
        if old_record is None:
            raise Error404

        result = session.query(Teacher).filter_by(id=teacher.id).update({
            Teacher.employeeId: teacher.employeeId if teacher.employeeId else old_record.employeeId,
            Teacher.firstName: teacher.firstName  if teacher.firstName else old_record.firstName,
            Teacher.secondName: teacher.secondName if teacher.secondName else old_record.secondName,
        })
        if result != 1:
            session.rollback()
            raise Error400("There was an error while updating the record")
        session.commit()
        new_record = session.query(Teacher).filter_by(id=teacher.id).first()
        new_teacher = Teacher_DB(**model_to_dict(new_record))
        return new_teacher
    except Error400 as e:
        raise HTTPException(status_code=400,detail={'message': str(e)})
    except Error404:
        raise HTTPException(status_code=404,detail={'message': 'Record not found in the database'})
    except Exception as e:
        raise HTTPException(status_code=500,detail={'message': 'Function error', 'error':str(e)})
    except SQLAlchemyError as e:
        raise HTTPException(status_code=560,detail={'message': 'SQLAlchemy error','error':str(e)})
    
@router.delete('/erase/',status_code=201, responses={
    201:{
            "description": "Teacher item removed successfully",
            "content": {
                "application/json": {
                    "example": {'status_code': 201,'message': f'Success! Teacher Jonathan Banner was deleted successfully'}
                }
            }},
    400:{
            "description": "The teacher cannot be removed",
            "content": {
                "application/json": {
                    "example": {'detail':{'message':'There was an error deleting the teacher'}}
                }
            }},
    404:{
            "description": "Teacher item not found in the database",
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
async def delete_teacher(teacher_id: Annotated[int,Query(ge=0,example=12,description='Id of the teacher to be deleted')],
                        session=Depends(db_connection)):
    """Delete a teacher from the database by their id"""
    try:
        teacher = session.query(Teacher.firstName,Teacher.secondName).filter_by(id=teacher_id).first()
        if teacher is None:
            raise Error404
        result = session.query(Teacher).filter_by(id=teacher_id).delete()
        if result != 1:
            session.rollback()
            raise Error400
        session.commit()
        return {'status_code': 201,'message': f'Success! Teacher {teacher[0]} {teacher[1]} was deleted successfully'}
    except Error400:
        raise HTTPException(status_code=400,detail={'message': 'There was an error deleting the teacher'})
    except Error404:
        raise HTTPException(status_code=404,detail={'message': f'The teacher with id {teacher_id} does not exist'})
    except Exception as e:
        raise HTTPException(status_code=500,detail={'message': 'Function error', 'error':str(e)})
    except SQLAlchemyError() as e:
        raise HTTPException(status_code=560,detail={'message': 'SQLAlchemy error','error':str(e)})