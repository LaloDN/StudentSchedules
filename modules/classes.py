from fastapi import APIRouter, Body, HTTPException, Query, Depends
from sqlalchemy.exc import SQLAlchemyError
from sql.connection import db_connection
from sqlalchemy.orm import Session
from typing import Annotated, List
from schemes import  Classes_Scheme, Classes_DB, Classes_Auxiliar
from sql.definition import Class, Teacher, Subject
from utils import model_to_dict, Error400, Error404
from datetime import datetime
import re

router = APIRouter(prefix='/classes',tags=["Class"])

@router.post('/create/',status_code=201)
async def new_class(class_item : Annotated[Classes_Scheme,Body], session = Depends(db_connection)):
    try:
        class_item : Classes_Scheme
        session : Session

        #Hour in format hh:mm AM/PM
        pattern = r'^\d{1,2}:\d{2} [APap][Mm]$'
        class_item.hour =class_item.hour.upper()
        if not re.match(pattern,class_item.hour):
            raise Error400("The hour isn't in format hh:mm AM/PM") 
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


@router.get('/search/',status_code=200, response_model=Classes_DB)
async def get_class(group_no: Annotated[int,Query(default=...,title='Group number',description='Number of the class group',gt=0)],
                        session = Depends(db_connection)):
    try:
        session : Session
        class_item = session.query(Class).filter_by(groupNo = group_no).first()
        if not class_item:
            raise Error404
        class_dict = model_to_dict(class_item)
        return class_dict
    except Error404 as e:
        raise HTTPException(status_code=404,detail={'message':f'The class with the group number #{group_no} does not exists'})
    except SQLAlchemyError as e:
        raise HTTPException(status_code=560, detail = {'message': 'SQLAlchemy error','error':str(e)})
    except Exception as e:
        raise HTTPException(status_code=500, detail = {'message': 'Function error','error':str(e)})


@router.get('/obtain/',status_code=200,response_model=List[Classes_DB])
async def get_classes(session = Depends(db_connection)):
    try:
        session : Session
        classes = session.query(Class).all()
        classes_dict = [model_to_dict(class_item) for class_item in classes]
        return classes_dict
    except SQLAlchemyError as e:
        raise HTTPException(status_code=560, detail = {'message': 'SQLAlchemy error','error':str(e)})
    except Exception as e:
        raise HTTPException(status_code=500, detail = {'message': 'Function error','error':str(e)})


@router.put('/modify/',status_code=201,response_model=Classes_DB)
async def modify_class( class_item: Annotated[Classes_Auxiliar,Body], session = Depends(db_connection)):
    try:
        session : Session
        old_record : Class

        if not(class_item.groupNo or class_item.hour or class_item.idSubject or class_item.idTeacher):
            raise Error400('You must specify at least one field that will be modified')
        
        old_record = session.query(Class).filter_by(id = class_item.id).first()
        if old_record is None:
            raise Error404
        
        #If the user wants to modify the subject or teacher, we make sure that the ids exists
        if class_item.idSubject:
            subject = session.query(Subject.id).filter_by(id = class_item.idSubject).first()
            if subject is None:
                raise Error400(f'The subject with the id {class_item.idSubject} does not exists in the database')
        if class_item.idTeacher:
            teacher = session.query(Teacher.id).filter_by( id = class_item.idTeacher).first()
            if teacher is None:
                raise Error400(f'The teacher with the id {class_item.idTeacher} does not exists in the database')

        #Check if the new group number has not been assigned yet
        if class_item.groupNo:
            group_class = session.query(Class.id).filter(Class.groupNo == class_item.groupNo, Class.id != class_item.id).first()
            if group_class:
                raise Error400(f'The group number #{class_item.groupNo} has already been assigned to another class')

        if class_item.hour:
            pattern = r'^\d{1,2}:\d{2} [APap][Mm]$'
            class_item.hour =class_item.hour.upper()
            if not re.match(pattern,class_item.hour):
                raise Error400("The hour isn't in format hh:mm AM/PM") 

        if class_item.idTeacher or class_item.hour:
            #If the user wants to modify some teacher or schedule of a class, we will use this dictionary 
            #with the original values, which will change according to user input, this dictionary will help us 
            #to check if the final teacher and the hour of the record do not collide with another record
            final_schedule = {'id':old_record.id,
                                'teacher_id':old_record.idTeacher,
                                'hour':old_record.hour}
            if class_item.idTeacher:
                final_schedule['teacher_id'] = class_item.idTeacher
            if class_item.hour:
                final_schedule['hour'] = class_item.hour
            teacher_class = session.query(Class.id).filter(Class.hour == final_schedule['hour'],\
                                Class.idTeacher == final_schedule['teacher_id'], Class.id != final_schedule['id']).first()
            if teacher_class:
                raise Error400(f'Cannot update the teacher/schedule of the class, the teacher with the id {final_schedule["teacher_id"]}\
                     is busy in another class at the same time')

        modified_class = session.query(Class).filter_by(id = class_item.id).update({
            Class.groupNo: class_item.groupNo if class_item.groupNo else old_record.groupNo,
            Class.hour: class_item.hour if class_item.hour else old_record.hour,
            Class.idSubject: class_item.idSubject if class_item.id else old_record.idSubject,
            Class.idTeacher: class_item.idTeacher if class_item.idTeacher else old_record.idTeacher
        })

        if modified_class != 1:
            session.rollback()
            raise Error400("There was an error while updating the record")
        session.commit()
          
        new_record = session.query(Class).filter_by(id = class_item.id).first()
        new_class = Classes_DB(**model_to_dict(new_record))
        return new_class
    except Error400 as e:
        raise HTTPException(status_code=400, detail = {'message': str(e)})
    except SQLAlchemyError as e:
        raise HTTPException(status_code=560, detail = {'message': 'SQLAlchemy error','error':str(e)})
    except Exception as e:
        raise HTTPException(status_code=500, detail = {'message': 'Function error','error':str(e)})

@router.delete('/erase/',status_code=201,responses={})
async def delete_class(class_id : Annotated[int,Query(title='Id class',description='Id of the class to be deleted',ge=1,example=1203)],
                        session = Depends(db_connection)):
    try:
        session : Session
        class_item = session.query(Class).filter_by(id = class_id).first()
        if class_item is None:
            raise Error400

        deleted_class = session.query(Class).filter_by(id = class_id).delete()
        if deleted_class != 1:
            session.rollback()
            raise Error400
        session.commit()
        return {'status_code':201,'message':f'Success! The class with the id {class_id} was deleted succesfully'}
    except Error400:
        raise HTTPException(status_code=400,detail={'message':'There was an error deleting the class'})
    except Error404:
        raise HTTPException(status_code=404,detail={'message': f'The class with id {class_id} does not exist'})
    except SQLAlchemyError as e:
        raise HTTPException(status_code=560, detail = {'message': 'SQLAlchemy error','error':str(e)})
    except Exception as e:
        raise HTTPException(status_code=500, detail = {'message': 'Function error','error':str(e)})

