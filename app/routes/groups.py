from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
import base64

from .. import schemas, models, utils
from ..database import get_db

router = APIRouter(prefix='/groups', tags=["Restaurant"])

@router.post("/",
            # response_model=tSchemas.MaterialListOut,
            status_code=status.HTTP_200_OK)
def get_groups(rest_data : schemas.RestID,
                     db: Session = Depends(get_db)):

    grp_query = db.query(models.restaurant_groups, models.Groups).join(models.Groups, models.Groups.g_id == models.restaurant_groups.c.group_id).all()

    return {
        'status': '200',
        'msg': 'groups fetched successfully!',
        'data': {
            'rest_id' : rest_data.r_id,
            'groups':[{
                'g_id': grp[2].g_id,
                'gname': grp[2].gname
                } for grp in grp_query
            ]
        }
    }


@router.post('/create')
def create_group(
    grp : schemas.CreateGroup,
    db: Session = Depends(get_db)):

    grp_create = models.Groups(gname=grp.name)

    db.add(grp_create)
    db.commit()
    db.refresh(grp_create)

    group_rest_association = models.restaurant_groups.insert().values(restaurant_id=grp.r_id, group_id=grp_create.g_id)
    db.execute(group_rest_association)
    db.commit()

    return {
        'status': '200',
        'msg': 'group added successfully!',
        'data': {
            'rest_id' : grp.r_id,
            'group': {
            'g_id': grp_create.g_id,
            'gname': grp_create.gname
        }
        }     
    }



router2 = APIRouter(prefix='/labels', tags=["Restaurant"])

@router2.post('/create')
def create_label(
    label : schemas.CreateLabel,
    db: Session = Depends(get_db)):

    label_create = models.Labels(name=label.name)

    db.add(label_create)
    db.commit()
    db.refresh(label_create)

    return {
        'status': '200',
        'msg': 'label added successfully!',
        'data': label_create    
    }

@router2.get('/')
def get_labels(db: Session = Depends(get_db)):

    labels = db.query(models.Labels).all()

    return {
        'status': '200',
        'msg': 'label fetched successfully!',
        'data': labels    
    }


router3 = APIRouter(prefix='/extras', tags=["Restaurant"])

@router3.post('/create')
def create_label(
    ext : schemas.CreateExtra,
    db: Session = Depends(get_db)):

    ext_crt = models.Extras(name=ext.name, price=ext.price, r_id=ext.r_id)

    db.add(ext_crt)
    db.commit()
    db.refresh(ext_crt)

    return {
        'status': '200',
        'msg': 'extra added successfully!',
        'data': ext_crt    
    }

@router3.post('/')
def get_labels(rest: schemas.RestID,
    db: Session = Depends(get_db)):

    extras = db.query(models.Extras).filter(models.Extras.r_id == rest.r_id).all()

    return {
        'status': '200',
        'msg': 'extras fetched successfully!',
        'data': extras  
    }