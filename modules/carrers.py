from fastapi import APIRouter, Body, HTTPException, Query, Depends
from typing import Annotated
from sqlalchemy.exc import SQLAlchemyError
from sql.connection import db_connection
from schemes import Carrer

router = APIRouter(prefix='/carrers')

@router.post('/create/',status_code=201,tags=['Carrer'])
async def new_carrer(carrer: Annotated[Carrer,Body], session = Depends(db_connection)):
    try:
        return {'it':'works'}
    except Exception as e:
        return {'msg':str(e)}
