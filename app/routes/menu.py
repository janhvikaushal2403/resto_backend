import os
from fastapi import APIRouter, status, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse

from sqlalchemy.orm import Session, joinedload
from typing import List

from .. import schemas, models, utils
from ..database import get_db

router = APIRouter(prefix='/menu', tags=["Restaurant"])


@router.post("/",
             # response_model=tSchemas.MaterialListOut,
             status_code=status.HTTP_200_OK)
def get_menu(rest_data: schemas.RestID,
             db: Session = Depends(get_db)):

    menu_query = db.query(models.Items, models.Groups).filter(
        models.Items.r_id == rest_data.r_id).join(
        models.Groups, models.Items.g_id == models.Groups.g_id).all()

    # for menu in menu_query:
    #     print(menu)

    response_data = {
        'rest_id': rest_data.r_id,
        'groups': []
    }

    for item, group in menu_query:
        # Check if the group is already in the response
        group_data = next(
            (g for g in response_data['groups'] if g['g_id'] == group.g_id), None)

        if group_data is None:
            # If the group is not in the response, add it
            group_data = {
                'g_id': group.g_id,
                'gname': group.gname,
                'items': []
            }
            response_data['groups'].append(group_data)

        # Add the item information to the group
        group_data['items'].append({
            'item_id': item.id,
            'name': item.name,
            'desc': item.desc,
            'ordertype': item.ordertype,
            'has_quantity': item.has_quantity,
            'item_prices': item.item_prices,
            'def_prices': item.def_price,
            'image': item.image,
            'is_avail': item.is_avail,
            'labels': item.labels,
        })

    return {
        'status': '200',
        'msg': 'menu fetched successfully!',
        'data': response_data
    }


@router.post("/item",
             # response_model=tSchemas.MaterialListOut,
             status_code=status.HTTP_200_OK)
def get_item(item: schemas.ItemId,
             db: Session = Depends(get_db)):

    item_create = db.query(models.Items).filter(
        models.Items.id == item.id).first()

    if not item_create:
        return {
            'status': '400',
            'msg': 'item does not exist!'
        }

    return {'status': '200',
            'msg': 'item added successfully!',
            'data': {
                'rest_id': item_create.r_id,
                'group_id': item_create.g_id,
                'item': {
                    'item_id': item_create.id,
                    'name': item_create.name,
                    'image': item_create.image,
                    'desc': item_create.desc,
                    'has_quantity': item_create.has_quantity,
                    'ordertype': item_create.ordertype,
                    'item_prices': item_create.item_prices,
                    'def_prices': item_create.def_price,
                    'is_active': item_create.is_avail,
                    'labels': item_create.labels

                }
            }
            }

# @router.post('/image')
# def upload(
#         image: UploadFile,
#         db: Session = Depends(get_db)):
#     return {
#         "path": image.filename
#     }


@router.post('/create/default')
def create_default_item(item: schemas.CreateDefaultItem,
                        db: Session = Depends(get_db)):

    new_item = item.model_dump(exclude={"labels"})
    item_create = models.Items(**new_item)

    db.add(item_create)
    db.commit()
    db.refresh(item_create)

    for label in item.labels:
        item_label = models.items_labels.insert().values(
            item_id=item_create.id, label_id=label)
        db.execute(item_label)
    db.commit()

    # item_query = db.query(models.items_labels, models.Labels).filter(models.items_labels.c.item_id == item_create.id).join(
    #     models.Labels, models.Labels.id == models.items_labels.c.label_id).all()
    # item_query = db.query(models.Items).filter(models.Items.id == item_create.id).first()

    # image_url =  static_url + static_images_path + item_create.image

    return {
        'status': '200',
        'msg': 'item added successfully!',
        'data': {
            'rest_id': item_create.r_id,
            'group_id': item_create.g_id,
            'item': {
                'item_id': item_create.id,
                'name': item_create.name,
                'image': item_create.image,
                'desc': item_create.desc,
                'has_quantity': item_create.has_quantity,
                'ordertype': item_create.ordertype,
                'item_prices': item_create.item_prices,
                'def_prices': item_create.def_price,
                'is_active': item_create.is_avail,
                'labels': item_create.labels
                # 'labels': [{
                #     'id': label[2].id,
                #     'name': label[2].name
                # } for label in item_query],
            }
        }
    }


@router.post('/create/variety')
def create_variety_item(item: schemas.CreateVarietyItem,
                        db: Session = Depends(get_db)):

    new_item = item.model_dump(exclude={"labels", "item_prices"})
    item_create = models.Items(**new_item)

    item_create.has_quantity = True  # to make the item variable

    db.add(item_create)
    db.commit()
    db.refresh(item_create)

    for label in item.labels:
        item_label = models.items_labels.insert().values(
            item_id=item_create.id, label_id=label)
        db.execute(item_label)
    db.commit()

    for i_price in item.item_prices:
        item_price = models.ItemPrices(
            quantity=i_price.qty, price=i_price.price, item_id=item_create.id)
        db.add(item_price)
    db.commit()

    return {
        'status': '200',
        'msg': 'item added successfully!',
        'data': {
            'rest_id': item_create.r_id,
            'group_id': item_create.g_id,
            'item': {
                'item_id': item_create.id,
                'name': item_create.name,
                'image': item_create.image,
                'desc': item_create.desc,
                'has_quantity': item_create.has_quantity,
                'ordertype': item.ordertype,
                'item_prices': item_create.item_prices,
                'def_prices': item_create.def_price,
                'is_active': item_create.is_avail,
                'labels': item_create.labels
                # 'labels': [{
                #     'id': label[2].id,
                #     'name': label[2].name
                # } for label in item_query],
            }
        }
    }

# @router.get("/images/{image_id}")
# def get_image(image_id: int):
#     image_path = f"images/{image_id}.jpg"  # Adjust the path to your image storage
#     if os.path.exists(image_path):
#         return FileResponse(image_path, media_type="image/jpeg")
#     else:
#         return {"detail": "Image not found"}
