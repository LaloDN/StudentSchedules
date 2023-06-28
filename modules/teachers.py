from fastapi import APIRouter, Body, HTTPException, Query, Depends
from sqlalchemy import exc,or_
from typing import Annotated, List, Union
from sqlalchemy.exc import SQLAlchemyError
from sql.connection import db_connection
from schemes import Teacher_DB, Teacher_Scheme
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
    try:
        #Check if teacher already exists by their names and check if employee ID is unique
        result = session.query(Teacher).filter(Teacher.firstName == teacher.firstName,
        Teacher.secondName == teacher.secondName).first()
        if result:
            raise Error400("A teacher with the same name is already registered")
        result = session.query(Teacher).filter_by(employeeId = teacher.employeeId).first()
        if result:
            raise Error404("The given employee ID it's already assigned")

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

@router.get('/search/',status_code=200, response_model=Teacher_DB, responses={})
async def get_teachers(first_name : Annotated[str | None,Query(max_length=40,example="Elian")] = None,
                        second_name : Annotated[str | None,Query(max_length=40,example="Davis")] = None,
                        id: Annotated[int | None, Query(ge=1,example=201)] = None,
                        sesion = Depends(db_connection)):
    try:
        if first_name and second_name:
            result = sesion.query(Teacher).filter(Teacher.firstName.ilike(f'%{first_name}%'),
                    Teacher.secondName.ilike(f'%{second_name}%')).first()
        elif first_name or second_name:
            result = sesion.query(Teacher).filter(or_(Teacher.firstName.ilike(f'%{first_name}%'),
                    Teacher.secondName.ilike(f'%{second_name}%'))).first()
        elif id:
            result = sesion.query(Teacher).filter(Teacher.id == id).first()
        else:
            raise Error400
        
        if result is None:
            raise Error404

        teacher = Teacher_DB(**model_to_dict(result))
        return teacher

    except Error400:
        raise HTTPException(status_code=400,detail={'message': 'You must provide either name(s) or id for the teacher to be returned'})
    except Error404:
        raise HTTPException(status_code=404,detail={'message': 'Record not found in the database'})
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500,detail={'message': 'SQLAlchemy error','error':str(e)})
    except Exception as e:
        raise HTTPException(status_code=560,detail={'message': 'Function error', 'error':str(e)})
        
@router.get('/obtain/',status_code=200, response_model=List[Teacher_DB])
async def get_teacher(session = Depends(db_connection)):
    try:
        result = session.query(Teacher).all()
        teacher_dicts = [model_to_dict(row) for row in result]
        teachers = [Teacher_DB(**t) for t in teacher_dicts]
        return teachers
    except Exception as e:
        raise HTTPException(status_code=500,detail={'message': 'Function error', 'error':str(e)})
    except SQLAlchemyError as e:
        raise HTTPException(status_code=560,detail={'message': 'SQLAlchemy error','error':str(e)})