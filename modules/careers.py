from fastapi import APIRouter, Body, HTTPException, Query, Depends
from typing import Annotated, List, Union
from sqlalchemy.exc import SQLAlchemyError
from sql.connection import db_connection
from schemes import Career_Scheme, Career_DB
from sql.definition import Career
from utils import model_to_dict, Error400, Error404

router = APIRouter(prefix='/careers',tags=['Career'])

@router.post('/create/',status_code=201, responses = {
    201:{
            "description": "Item created",
            "content": {
                "application/json": {
                    "example": {'status_code':201,'message':'Career created successfully!', 'id':435}
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
async def new_career(career: Annotated[Career_Scheme,Body], session = Depends(db_connection)):
    """Creates a new career"""
    try:
        career_dict = career.dict()
        career_db = Career(**career_dict)
        #Comprobe if the career name already exists
        result = session.query(Career.name).filter_by(name=career_dict['name']).first()
        if result is not None:
            return {'status_code':400, 'message':'Career already exists'}
        session.add(career_db)
        result = session.query(Career.id).filter_by(name=career_dict['name']).first()[0] #Bring back the id from the database
        if result:
            session.commit()
            return {'status_code':201,'message':'Career created successfully!', 'id':result}
        else:
            session.rollback()
            return {'status_code':400,'message':'There was an error creating the career'}
    except Exception as e:
        raise HTTPException(status_code=500,detail={'message': 'Function error', 'error':str(e)})
    except SQLAlchemyError as e:
        raise HTTPException(status_code=560,detail={'message': 'SQLAlchemy error', 'error':str(e)})

@router.get('/search/',status_code=200, response_model = Career_DB, responses={
    200:{
        "description": "Career item retrieved successfully",
        "content": {
            "application/json": {
                "example": {"id": 20, "name": "Elementary education"}
            }
        }},
    400:{
        "description": "Empty id and name in the request",
        "content": {
            "application/json": {
                "example": {'detail':{'message': 'You must provide either name or id for the career to be returned'}}
            }
        }},
    404:{
        "description": "Career item not found",
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
async def get_careers(name : Annotated[str | None,Query(max_length=40,example="Aviation")] = None,
                    id : Annotated[int | None,Query(ge=1,example=6)] = None,
                    session = Depends(db_connection)) :
    """Search a signle career by name or id"""
    try:
        if name:
            result = session.query(Career).filter(Career.name.ilike(f'%{name}%')).first()
        elif id:
            result = session.query(Career).filter_by(id=id).first()
        else:
            raise Error400
        
        if result is None:
            raise Error404

        career = Career_DB(**model_to_dict(result))
        return career
    except Error400:
        raise HTTPException(status_code=400,detail={'message': 'You must provide either name or id for the career to be returned'})
    except Error404:
        raise HTTPException(status_code=404,detail={'message': 'Record not found in the database'})
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500,detail={'message': 'SQLAlchemy error','error':str(e)})
    except Exception as e:
        raise HTTPException(status_code=500,detail={'message': 'Function error', 'error':str(e)})

@router.get('/obtain/',status_code=200, response_model = List[Career_DB], responses={
     200:{
        "description": "Career items retrieved successfully",
        "content": {
            "application/json": {
                "example": [
                    {
                        "id": 4,
                        "name": "Robotics"
                    },
                    {
                        "id": 37,
                        "name": "Electronic engineering"
                    },
                    {
                        "id": 122,
                        "name": "Aviation"
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
async def get_careers(session = Depends(db_connection)) :
    """Get list of all careers in existence"""
    try:
        result = session.query(Career).all()
        career_dicts = [model_to_dict(row) for row in result]
        careers = [Career_DB(**c) for c in career_dicts]
        return careers
    except Exception as e:
        raise HTTPException(status_code=500,detail={'message': 'Function error', 'error':str(e)})
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500,detail={'message': 'SQLAlchemy error','error':str(e)})

@router.put('/modify/',status_code = 201)
async def modify_career(id : Annotated[int,Query(ge=0,example=14,description="Id of the career to be modified")],session = Depends(db_connection)):
    return {'hi':'hi'}