from fastapi import APIRouter, Body, HTTPException, Query, Depends
from typing import Annotated, List, Union
from sqlalchemy.exc import SQLAlchemyError
from sql.connection import db_connection
from schemes import Carrer_Scheme, Carrer_DB
from sql.definition import Carrer
from utils import model_to_dict, Error400, Error404

router = APIRouter(prefix='/carrers',tags=['Carrer'])

@router.post('/create/',status_code=201, responses = {
    201:{
            "description": "Item created",
            "content": {
                "application/json": {
                    "example": {'status_code':201,'message':'Carrer created successfully!', 'id':435}
                }
            }},
    500:{
            "description": "Function internal error",
            "content": {
                "application/json": {
                    "example": {'message':'Function error','error':'Some Python error message...'}
                }
            }},
    560:{
            "description": "SQLAlchemy error",
            "content": {
                "application/json": {
                    "example": {'message':'SQLAlchemy error','error':'Some SQLALchemy error message...'}
                }
            }}
})
async def new_carrer(carrer: Annotated[Carrer_Scheme,Body], session = Depends(db_connection)):
    """Creates a new carrer"""
    try:
        carrer_dict = carrer.dict()
        carrer_db = Carrer(**carrer_dict)
        #Comprobe if the carrer name already exists
        result = session.query(Carrer.name).filter_by(name=carrer_dict['name']).first()
        if result is not None:
            return {'status_code':400, 'message':'Carrer already exists'}
        session.add(carrer_db)
        result = session.query(Carrer.id).filter_by(name=carrer_dict['name']).first()[0] #Bring back the id from the database
        if result:
            session.commit()
            return {'status_code':201,'message':'Carrer created successfully!', 'id':result}
        else:
            session.rollback()
            return {'status_code':400,'message':'There was an error creating the carrer'}
    except Exception as e:
        raise HTTPException(status_code=500,detail={'message': 'Function error', 'error':str(e)})
    except SQLAlchemyError as e:
        raise HTTPException(status_code=560,detail={'message': 'SQLAlchemy error', 'error':str(e)})

@router.get('/search/',status_code=200, response_model = Carrer_DB, responses={
    200:{
        "description": "Carrer item retrieved successfully",
        "content": {
            "application/json": {
                "example": {"id": 20, "name": "Elementary education"}
            }
        }},
    400:{
        "description": "Empty id and name in the request",
        "content": {
            "application/json": {
                "example": {'detail':{'message': 'You must provide either name or id for the carrer to be returned'}}
            }
        }},
    404:{
        "description": "Carrer item not found",
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
async def get_carrers(name : Annotated[str | None,Query(max_length=40)] = None,
                    id : Annotated[int | None,Query(ge=1)] = None,
                    session = Depends(db_connection)) :
    try:
        if name:
            result = session.query(Carrer).filter(Carrer.name.ilike(f'%{name}%')).first()
        elif id:
            result = session.query(Carrer).filter_by(id=id).first()
        else:
            raise Error400
        
        if result is None:
            raise Error404

        carrer = Carrer_DB(**model_to_dict(result))
        return carrer
    except Error400:
        raise HTTPException(status_code=400,detail={'message': 'You must provide either name or id for the carrer to be returned'})
    except Error404:
        raise HTTPException(status_code=404,detail={'message': 'Record not found in the database'})
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500,detail={'message': 'SQLAlchemy error','error':str(e)})
    except Exception as e:
        raise HTTPException(status_code=500,detail={'message': 'Function error', 'error':str(e)})

@router.get('/obtain/',status_code=200, response_model = List[Carrer_DB])
async def get_carrers(session = Depends(db_connection)) :
    try:
        result = session.query(Carrer).all()
        carrer_dicts = [model_to_dict(row) for row in result]
        carrers = [Carrer_DB(**c) for c in carrer_dicts]
        return carrers
    except Exception as e:
        raise HTTPException(status_code=500,detail={'message': 'Function error', 'error':str(e)})
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500,detail={'message': 'SQLAlchemy error','error':str(e)})
