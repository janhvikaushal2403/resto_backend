from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from typing import List
import base64

from .. import schemas, models, utils
from ..database import get_db

router = APIRouter(prefix='/orders', tags=["Orders"])


@router.post('/')
def all_orders(
        rest_data: schemas.RestID,
        db: Session = Depends(get_db)):

    ord_query = db.query(models.Orders).filter(
        models.Orders.r_id == rest_data.r_id).all()

    if not ord_query:
        return {
            'status': "400",
            'msg': "no orders for this restaurant",
        }

    return {
        'status': "200",
        'msg': "successfully fetched orders",
        'data': [{
            'order_id': orders.o_id,
            'rest_id': orders.r_id,
            'book_time': orders.booktime,
            'remarks': orders.remarks,
            'dine_in': orders.dine_in,
            'amount': orders.amt,

            'user_details': {
                "id": orders.users.id,
                "name": orders.users.name,
                "email": orders.users.email,
                "phone": orders.users.phone,
            },

            # 'pay_details': {
            #     "id": orders.payment.id,
            #     "mode": orders.payment.mode,
            #     "trans_id": orders.payment.payno,
            # },

            'items': [
                {
                    'orditem_id': item_data.id,
                    'item': item_data.items.name,
                    'size': item_data.item_prices.quantity if item_data.items.has_quantity else None,
                    # 'price': item_data.item_size.price if item_data.items.has_quantity else item_data.items.price,
                    'price': item_data.price,
                    'qty': item_data.qty,
                    'extras': item_data.extras if item_data.extras else []
                } for item_data in orders.orderitems
            ]
        } for orders in ord_query
        ]
    }


@router.post("/create",
             #  response_model=tSchemas.RequisitionOut,
             status_code=status.HTTP_200_OK)
def make_order(order: schemas.PlaceOrder,
               db: Session = Depends(get_db)):

    user_query = db.query(models.Users).filter(
        models.Users.email == order.order_by.email).first()

    if not user_query:
        user = order.order_by.model_dump()
        new_user = models.Users(**user)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

    else:
        new_user = user_query

    order_exist = False

    old_order = db.query(models.Orders).filter(models.Orders.u_id == new_user.id,
                                               models.Orders.pay_id.is_(None)).order_by(desc(models.Orders.booktime)).first()
    if old_order is not None:
        order_exist = True
        new_order = old_order
        new_order.amt += order.amt

    else:
        new_order = models.Orders(
            amt=order.amt,
            dine_in=order.dine_in,
            remarks=order.remarks,
            r_id=order.rest_id,
            u_id=new_user.id)
        db.add(new_order)

    db.commit()
    db.refresh(new_order)

    for item in order.items:
        new_item = models.OrderItems(
            item_id=item.id,
            size_id=item.size if item.size != 0 else None,
            price=item.price,
            qty=item.qty,
            ord_id=new_order.o_id)

        db.add(new_item)
        db.commit()
        db.refresh(new_item)

        for ext in item.extras:
            item_ext = models.orderitem_extras_association.insert().values(
                orderitem_id=new_item.id, extras_id=ext)
            db.execute(item_ext)

        db.commit()
        db.refresh(new_item)

    order_data = db.query(models.Orders).filter(
        models.Orders.o_id == new_order.o_id).first()

    return {
        'status': "200",
        'msg': "successfully place order request",
        'data': {
            'order_id': order_data.o_id,
            'rest_id': order.rest_id,
            'book_time': order_data.booktime,
            'remarks': order_data.remarks,
            'dine_in': order_data.dine_in,
            'amount': order_data.amt,

            'items': [
                {
                    'orditem_id': item_data.id,
                    'item': item_data.items.name,
                    'size': item_data.item_prices.quantity if item_data.items.has_quantity else None,
                    'price': item_data.price,
                    'qty': item_data.qty,
                    'extras': item_data.extras if item_data.extras else []
                } for item_data in order_data.orderitems
            ],

            'user_details': {
                "id": order_data.users.id,
                "name": order_data.users.name,
                "email": order_data.users.email,
                "phone": order_data.users.phone,
            },

            # 'pay_details': {
            #     "id": orders.payment.id,
            #     "mode": orders.payment.mode,
            #     "trans_id": orders.payment.payno,
            # },
        }
    }


@router.post("/complete",
             #  response_model=tSchemas.RequisitionOut,
             status_code=status.HTTP_200_OK)
def complete_order(order: schemas.OrderID,
                   db: Session = Depends(get_db)):

    order_qry = db.query(models.Orders).filter(
        models.Orders.o_id == order.o_id).first()

    if not order_qry:
        return {
            'status': "400",
            'msg': "order not found"
        }

    comp_ord = models.CompetedOrders(
        amt=order_qry.amt,
        dine_in=order_qry.dine_in,
        remarks=order_qry.remarks,
        r_id=order_qry.r_id,
        u_id=order_qry.u_id)

    db.add(comp_ord)
    db.commit()
    db.refresh(comp_ord)

    # shift orderitems
    for item in order_qry.orderitems:
        comp_item = models.CompletedOrderItems(
            item_id=item.id,
            size_id=item.size_id,
            price=item.price,
            qty=item.qty,
            ord_id=comp_ord.o_id)

        db.add(comp_item)
        db.commit()

        delete_stmt = models.orderitem_extras_association.delete().where(
            models.orderitem_extras_association.c.orderitem_id == item.id)
        db.execute(delete_stmt)
        db.commit()

        db.refresh(comp_item)


    db.delete(order_qry)
    db.commit()

    return {
        'status': "400",
        'msg': "order marked completed successfully"
    }


@router.delete("/delete",
               #  response_model=tSchemas.RequisitionOut,
               status_code=status.HTTP_200_OK)
def cancel_order(order: schemas.OrderID,
                 db: Session = Depends(get_db)):

    order_data = db.query(models.Orders).filter(
        models.Orders.o_id == order.o_id).first()
    if not order_data:
        return {
            'status': "400",
            'msg': "order not found"
        }

    db.delete(order_data)
    db.commit()

    return {
        'status': "200",
        'msg': "successfully cancel order request"
    }
