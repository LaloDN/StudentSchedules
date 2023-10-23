from fastapi import APIRouter, Body, HTTPException, Query, Depends
from sqlalchemy import exc,or_
from typing import Annotated, List, Union
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sql.connection import db_connection
from schemes import  Subject_Scheme, Subject_DB, Subject_Auxiliar
from sql.definition import Subject, Career
from utils import model_to_dict, Error400, Error404

router = APIRouter(prefix='/subjects',tags=['Subject'])

@router.post('/create',status_code=201,responses={
    201:{
            "description": "Subject item created",
            "content": {
                "application/json": {
                    "example": {'status_code':201,'message':'Subject registered successfully!', 'id':1024}
                }
            }},
     400:{
        "description": "Subject already exists or the career ID dosent exist",
                    "content": {
                        "application/json": {
                            "example": {'detail':{'message':'The career with the id 12 does not exist in the database'}}
                        }
            }}
})
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

@router.get('/search/',status_code=200,response_model=Subject_DB,responses={
    400:{
            "description": "Bad request",
            "content": {
                "application/json": {
                    "example": {'detail':{'status_code':400,'message':'You must provide either name or id for the subject to be returned'}}
                }
            }},
    404:{
            "description": "Subject not found in database",
            "content": {
                "application/json": {
                    "example": {'detail':{'status_code':404,'message':'Record not found in the database' }}
                }
        }}
})
async def search_subject(subject: Annotated[Subject_Auxiliar,Body], session = Depends(db_connection)):
    """Search one subject by their name or id in the database"""
    try:
        subject: Subject_Auxiliar
        if subject.id:
            result = session.query(Subject).filter_by(id = subject.id).first()
        elif subject.name:
            result = session.query(Subject).filter(Subject.name.ilike(f'%{subject.name}%')).first()
        else:
            raise Error400()

        if result:
            return result
        raise Error404()
    except Error400:
        raise HTTPException(status_code=400,detail={'message': 'You must provide either name or id for the subject to be returned'})
    except Error404:
        raise HTTPException(status_code=404,detail={'message': 'Record not found in the database'})
    except SQLAlchemyError as e:
        raise HTTPException(status_code=560, detail = {'message': 'SQLAlchemy error','error':str(e)})
    except Exception as e:
        raise HTTPException(status_code=500, detail = {'message': 'Function error','error':str(e)})

@router.get('/obtain/',status_code=200,response_model=List[Subject_DB])
async def get_subjects(session = Depends(db_connection)):
    """Get a full list of subjects"""
    try:
        results = session.query(Subject).all()
        subjects_dict = [model_to_dict(row) for row in results]
        return subjects_dict
 
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500,detail={'message': 'SQLAlchemy error','error':str(e)})
    except Exception as e:
        raise HTTPException(status_code=560,detail={'message': 'Function error', 'error':str(e)})

@router.put('/modify/',status_code=201,response_model=Subject_Auxiliar)
async def modify_subject(subject: Annotated[Subject_Auxiliar,Body],session : Session= Depends(db_connection)):
    """Modify the fields of one subject"""
    try:
        subject: Subject_Auxiliar
        old_subject: Subject
        if not(subject.careerId or subject.name or subject.semester):
            raise Error400("You must specify at least one field that will be modified")
        #Validate that career exists
        if subject.careerId:
            result = session.query(Career.id).filter_by(id = subject.careerId).first()
            if result is None:
                raise Error400(f"The career with the ID {subject.careerId} does not exists in the database")
        
        old_subject = session.query(Subject).filter_by(id = subject.id).first()
        if old_subject is None:
            raise Error404

        result = session.query(Subject).filter_by(id = subject.id).update({
            Subject.careerId : subject.careerId if subject.careerId else old_subject.careerId,
            Subject.name : subject.name if subject.name else old_subject.name,
            Subject.semester : subject.semester if subject.semester else old_subject.semester
        })
        if result != 1:
            session.rollback()
            raise Error400("There was an error while updating the record")
     
        new_record = session.query(Subject).filter_by(id = subject.id).first()
        new_subject = Subject_DB(**model_to_dict(new_record))
        return new_subject    
    except Error400 as e:
        raise HTTPException(status_code=400,detail={'message': str(e)})
    except Error404:
        raise HTTPException(status_code=404,detail={'message': 'Record not found in the database'})
    except SQLAlchemyError as e:
        raise HTTPException(status_code=560,detail={'message': 'SQLAlchemy error','error':str(e)})
    except Exception as e:
        raise HTTPException(status_code=500,detail={'message': 'Function error', 'error':str(e)})

@router.delete('/erase/',status_code=201)
async def delete_subject(subject_id : Annotated[int,Query(default=...,ge=1,title='Subject ID',description='Id of the subject to be deleted',example=208)],
                        session = Depends(db_connection)):
    """Deletes one subject by their id"""
    try:
        session: Session
        subject = session.query(Subject.name).filter_by(id = subject_id).first()
        if subject is None:
            raise Error404
        result = session.query(Subject).filter_by(id = subject_id).delete()
        if result != 1:
            session.rollback()
            raise Error400 
        session.commit()
        return {'status_code':201,'message':f'Success! The subject {subject[0]} was deleted succesfully'}
    except Error400:
        raise HTTPException(status_code=400,detail={'message': 'There was an error deleting the subject'})
    except Error404:
        raise HTTPException(status_code=404,detail={'message': f'The subject with id {subject_id} does not exist'})
    except SQLAlchemyError as e:
        raise HTTPException(status_code=560,detail={'message': 'SQLAlchemy error','error':str(e)})
    except Exception as e:
        raise HTTPException(status_code=500,detail={'message': 'Function error', 'error':str(e)})