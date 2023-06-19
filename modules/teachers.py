from fastapi import APIRouter, Body, HTTPException, Query, Depends
from typing import Annotated, List, Union
from sqlalchemy.exc import SQLAlchemyError
from sql.connection import db_connection
from schemes import Teacher_DB, Teacher_Scheme
from sql.definition import Teacher
from utils import model_to_dict, Error400, Error404

router = APIRouter(prefix='/teachers',tags=['Teacher'])

@router.post('/create/',status_code=201)
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
            return {'status_code':400,'message':'There was an error registering the teacher'}

    except Error400 as e:
        raise HTTPException(status_code=400, detail = {'message': str(e)})
    except Exception as e:
        raise HTTPException(status_code=500, detail = {'message': 'Function error','error':str(e)})
    except SQLAlchemyError as e:
        raise HTTPException(status_code=560, detail = {'message': 'SQLAlchemy error','error':str(e)})
