from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
import base64

from .. import schemas, models, utils
from ..database import get_db

router = APIRouter(prefix='/restaurant', tags=["Restaurant"])


@router.get("/",
            # response_model=tSchemas.MaterialListOut,
            status_code=status.HTTP_200_OK)
def get_restraurents(db: Session = Depends(get_db)):

    rests = db.query(models.Restaurants).all()

    return {
        "status": "200",
        'msg': "successfully fetched data",
        "data":  [{
            'id': rest_create.id,
            'name': rest_create.name,
            'email': rest_create.email,
            'email2': rest_create.email,
            'phone': rest_create.phone,
            'address': rest_create.address,
            'oname': rest_create.oname,
            'ophone': rest_create.ophone,
            'banner': rest_create.banner,
            'menuimage': rest_create.menuimage,
        }for rest_create in rests
        ]
    }


@router.get("/{r_id}",
            # response_model=tSchemas.MaterialListOut,
            status_code=status.HTTP_200_OK)
def get_restraurent(r_id: int,
                    db: Session = Depends(get_db)):

    rest_create = db.query(models.Restaurants).filter(
        models.Restaurants.id == r_id).first()

    if not rest_create:
        return {
            "status": "400",
            'msg': "rest not available",
        }

    return {
        "status": "200",
        'msg': "successfully fetched rest",
        "data":  {
            'id': rest_create.id,
            'name': rest_create.name,
            'email': rest_create.email,
            'email2': rest_create.email,
            'phone': rest_create.phone,
            'address': rest_create.address,
            'oname': rest_create.oname,
            'ophone': rest_create.ophone,
            'banner': rest_create.banner,
            'menuimage': rest_create.menuimage,
        }

    }


@router.post('/create')
def create_restraurents(
        rest: schemas.CreateRest,
        db: Session = Depends(get_db)):

    new_rest = rest.model_dump(exclude={"password"})

    hashed_pass = utils.hash(rest.password)

    rest_create = models.Restaurants(**new_rest, password=hashed_pass)

    db.add(rest_create)
    db.commit()
    db.refresh(rest_create)

    return {
        'status': '200',
        'msg': 'restraurent added successfully!',
        'data': {
            'id': rest_create.id,
            'name': rest_create.name,
            'email': rest_create.email,
            'email2': rest_create.email,
            'phone': rest_create.phone,
            'address': rest_create.address,
            'oname': rest_create.oname,
            'ophone': rest_create.ophone,
            'banner': rest_create.banner,
            'menuimage': rest_create.menuimage,
        }
    }
