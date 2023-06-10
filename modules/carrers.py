from fastapi import APIRouter, Body, HTTPException, Query, Depends
from typing import Annotated, List, Union
from sqlalchemy.exc import SQLAlchemyError
from sql.connection import db_connection
from schemes import Carrer_Scheme
from sql.definition import Carrer
from utils import model_to_dict

router = APIRouter(prefix='/carrers',tags=['Carrer'])

@router.post('/create/',status_code=201, responses = {
    201 :{'status_code':201,'message':'Carrer created successfully!', 'id':435}})
async def new_carrer(carrer: Annotated[Carrer_Scheme,Body], session = Depends(db_connection)):
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
        raise HTTPException(status_code=501,detail={'message': 'SQLAlchemy error', 'error':str(e)})

@router.get('/search/',status_code=200, response_model = Carrer_Scheme)
async def get_carrers(name : Annotated[str | None,Query(max_length=40)] = None,
                    id : Annotated[int | None,Query(ge=1)] = None,
                    session = Depends(db_connection)) :
    try:
        if name:
            result = session.query(Carrer).filter(Carrer.name.ilike(f'%{name}%')).first()
        elif id:
            result = session.query(Carrer).filter_by(id=id).first()
        else:
            return {'status_code':400, 'message': 'You must provide either name or id for the carrer to be returned'}
        
        if result is None:
            return{'status_code':404,'message':'Record not found in the database'}

        carrer = Carrer_Scheme(**model_to_dict(result))
        return carrer
    except Exception as e:
        raise HTTPException(status_code=500,detail={'message': 'Function error', 'error':str(e)})
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500,detail={'message': 'SQLAlchemy error','error':str(e)})

@router.get('/obtain/',status_code=200, response_model = List[Carrer_Scheme])
async def get_carrers(session = Depends(db_connection)) :
    try:
        result = session.query(Carrer).all()
        carrer_dicts = [model_to_dict(row) for row in result]
        carrers = [Carrer_Scheme(**c) for c in carrer_dicts]
        return carrers
    except Exception as e:
        raise HTTPException(status_code=500,detail={'message': 'Function error', 'error':str(e)})
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500,detail={'message': 'SQLAlchemy error','error':str(e)})
