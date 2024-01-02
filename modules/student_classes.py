from fastapi import APIRouter, Body, HTTPException, Query, Depends
from sqlalchemy.exc import SQLAlchemyError
from typing import Annotated, List
from sql.connection import db_connection
from sql.definition import Class,StudentClass,Student
from sqlalchemy.orm.session import Session
from utils import Error400,Error404

router = APIRouter(prefix='/student_classes',tags=['Student Classes'])

@router.post('/create/',status_code=200,responses={})
async def new_student_class(student_id : Annotated[int,Query(default=...,title='Student ID',description='Database id of the student to be enrrolled',ge=1,example=102)],
                            class_id : Annotated[int,Query(default=...,title='Class ID',description='Database id of the class',ge=1,example=947)],
                            session : Session = Depends(db_connection)):
    pass

def check_disponibility(student_id : int, class_id : int, session : Session) ->bool:
    class_schedule : str = session.query(Class.hour).filter(Class.id == class_id).first() 
    class_at_same_hour = session.query(Class.id).\
                        filter(Class.hour == class_schedule, Class.id != class_id,
                                     StudentClass.idStudent == student_id).\
                        join(StudentClass, Class.id == StudentClass.idStudent).first()
    return true if class_at_same_hour is not None else false 