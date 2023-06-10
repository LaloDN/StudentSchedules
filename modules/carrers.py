from fastapi import APIRouter, Body, HTTPException, Query, Depends
from typing import Annotated
from sqlalchemy.exc import SQLAlchemyError
from sql.connection import db_connection
from schemes import Carrer_Scheme
from sql.definition import Carrer

router = APIRouter(prefix='/carrers')

@router.post('/create/',status_code=201,tags=['Carrer'])
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
        raise HTTPException(status_code=501,detail=str(e))
