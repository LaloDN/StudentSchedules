from fastapi import APIRouter, Body, HTTPException, Query, Depends
from sqlalchemy import exc,or_
from typing import Annotated, List, Union
from sqlalchemy.exc import SQLAlchemyError
from sql.connection import db_connection
from schemes import  Subject_Scheme, Subject_DB, Subject_Auxiliar
from sql.definition import Subject, Career
from utils import model_to_dict, Error400, Error404

router = APIRouter(prefix='/subjects',tags=['Subject'])

@router.post('/create',status_code=201)
async def new_subject(subject: Annotated[Subject_Scheme,Body],session = Depends(db_connection)):
    """Crates a new subject"""
    try:
        #Check if carrer with the id exists and the subject name is unique
        result= session.query(Career.id).filter_by(id = subject.careerId).first()
        if not result:
            raise Error400(f'The career with the id {subject.careerId} does not exist in the database')
        result = session.query(Subject.id).filter_by( name = subject.name).first()
        if result:
            raise Error400('A subject with the same name is already registered')
        subject_dict = subject.dict()
        subject_db = Subject(**subject_dict)
        session.add(subject_db)

        result = session.query(Subject.id).filter_by(name = subject.name).first()
        if result:
            session.commit()
            return {'status_code':201,'message':'Subject registered successfully!', 'id':result[0]}
        session.rollback()
        raise Exception("There was an error registering the subject")    

    except Error400 as e:
        raise HTTPException(status_code=400, detail = {'message': str(e)})
    except SQLAlchemyError as e:
        raise HTTPException(status_code=560, detail = {'message': 'SQLAlchemy error','error':str(e)})
    except Exception as e:
        raise HTTPException(status_code=500, detail = {'message': 'Function error','error':str(e)})

