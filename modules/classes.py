from fastapi import APIRouter, Body, HTTPException, Query, Depends
from sqlalchemy.exc import SQLAlchemyError
from sql.connection import db_connection
from sqlalchemy.orm import Session
from typing import Annotated, List
from schemes import  Classes_Scheme, Classes_DB, Classes_Auxiliar
from sql.definition import Class, Teacher, Subject
from utils import model_to_dict, Error400, Error404
from datetime import datetime

router = APIRouter(prefix='/classes',tags=["Class"])

@router.post('/create',status_code=201)
async def new_class(class_item : Annotated[Classes_Scheme,Body], session = Depends(db_connection)):
    try:
        class_item : Classes_Scheme
        session : Session

        #Hour in format hh:mm AM/PM
        try:
            datetime.today().strftime("%H:%M %p")
        except:
            return -1
        #Check if teacher and subject exists
        teacher = session.query(Teacher.id).filter_by(id = class_item.idTeacher).first()
        if teacher is None:
            raise Error400(f'The teacher with the ID {class_item.idTeacher} does not exist in the database')
        subject = session.query(Subject.id).filter_by(id = class_item.idSubject).first()
        if subject is None:
            raise Error400(f'The subject with the ID {class_item.idSubject} does not exist in the database')

        #Check if class group is unique
        class_group = session.query(Class.groupNo).filter_by(groupNo = class_item.groupNo).first()
        if class_group:
            raise Error400('A class with the same group number already exists')

        #Check if the teacher is free in the indicated hour
        teacher_class = session.query(Teacher.firstName,Teacher.secondName,Class.groupNo).\
            filter(Class.hour == class_item.hour, Class.idTeacher == class_item.idTeacher).\
                join(Class, Teacher.id == Class.idTeacher).first()
        if teacher_class is not None:
            raise Error400(f"""The teacher {teacher_class[0]} {teacher_class[1]} has already assigned to the class
            number {teacher_class[2]} at the same hour """)
            
        class_dict = class_item.dict()
        class_db = Class(**class_dict)
        session.add(class_db)
        record = session.query(Class.id).filter_by(groupNo = class_item.groupNo).first()
        if record:
            session.commit()
            return {'status_code':201,'message':'Class registered successfully!', 'id':record[0]}
        session.rollback()
        raise SQLAlchemyError("There was an error registering the class")    

    except Error400 as e:
        raise HTTPException(status_code=400, detail = {'message': str(e)})
    except SQLAlchemyError as e:
        raise HTTPException(status_code=560, detail = {'message': 'SQLAlchemy error','error':str(e)})
    except Exception as e:
        raise HTTPException(status_code=500, detail = {'message': 'Function error','error':str(e)})
