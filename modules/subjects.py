from fastapi import APIRouter, Body, HTTPException, Query, Depends
from sqlalchemy import exc,or_
from typing import Annotated, List, Union
from sqlalchemy.exc import SQLAlchemyError
from sql.connection import db_connection
from schemes import Teacher_DB, Teacher_Scheme, Teacher_Auxiliar
from sql.definition import Teacher
from utils import model_to_dict, Error400, Error404

router = APIRouter(prefix='/subjects',tags=['Subject'])

