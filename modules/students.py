
from fastapi import APIRouter, Depends, Query, Body, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sql.connection import db_connection

router = APIRouter(prefix="/students")

@router.post('/create/',status_code=204,tags=['Student'])
async def new_student(session = Depends(db_connection)):
    return {'message':'funcoina!'}