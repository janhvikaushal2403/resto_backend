from sqlalchemy import Column, LargeBinary, Table, Boolean, Integer, String, Float, ForeignKey, TIMESTAMP, text
from sqlalchemy.orm import relationship

from .database import Base


# Define the association table for the Many-to-Many relationship
items_labels = Table(
    'items_labels',
    Base.metadata,
    Column('item_id', Integer, ForeignKey('items.id')),
    Column('label_id', Integer, ForeignKey('labels.id'))
)

restaurant_groups = Table(
    'restaurant_groups',
    Base.metadata,
    Column('restaurant_id', Integer, ForeignKey('restaurants.id')),
    Column('group_id', Integer, ForeignKey('groups.g_id'))
)

orderitem_extras_association = Table(
    'orderitem_extras_association',
    Base.metadata,
    Column('orderitem_id', Integer, ForeignKey('orderitems.id')),
    Column('extras_id', Integer, ForeignKey('extras.id'))
)


# class Images(Base):
#     __tablename__ = 'images'

#     id = Column(Integer, primary_key=True,autoincrement=True, index=True)
#     filename = Column(String, index=True)
#     data = Column(LargeBinary)

#     rest_id = Column(Integer, ForeignKey('restaurants.id'), nullable=True)
#     item_id = Column(Integer, ForeignKey('items.id'), nullable=True)

#     items = relationship('Items', back_populates='images')
#     restaurants = relationship('Restaurants', back_populates='images')


class Restaurants(Base):
    __tablename__ = 'restaurants'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String(255), nullable=False)
    address = Column(String(500), nullable=False)

    oname = Column(String(255), nullable=False)
    ophone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=False, index=True, unique=True)
    email2 = Column(String(255), nullable=True, index=True, unique=False)
    password = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True, unique=True, index=True)

    banner = Column(String(255), nullable=True)
    menuimage = Column(String(255), nullable=True)

    # is_active = Column(Boolean, nullable=False, default=False)
    # created_at = Column(TIMESTAMP(timezone=True),
    #                     nullable=False, server_default=text('now()'))
    extras = relationship('Extras', back_populates='restaurants')

    __allow_unmapped__ = True


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String(200), nullable=False)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=False, index=True, unique=True)

    orders = relationship('Orders', back_populates='users')
    completed_orders = relationship('CompetedOrders', back_populates='users')

    __allow_unmapped__ = True


class Groups(Base):
    __tablename__ = 'groups'
    g_id = Column(Integer, primary_key=True,
                  nullable=False, autoincrement=True)
    gname = Column(String(200), nullable=False)

    __allow_unmapped__ = True


class Labels(Base):
    __tablename__ = 'labels'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String(50), nullable=False)

    items = relationship('Items', secondary=items_labels,
                         back_populates='labels')

    __allow_unmapped__ = True


class Items(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String(255), nullable=False)
    desc = Column(String(500), nullable=True)
    has_quantity = Column(Boolean, nullable=False, default=False)
    def_price = Column(Float, nullable=True)
    image = Column(String(255), nullable=True)
    is_avail = Column(Boolean, nullable=False, default=True)
    # 0 both, 1:dine in, 2: take away
    ordertype = Column(Integer, nullable=False, default=0)

    g_id = Column(Integer, ForeignKey(
        "groups.g_id"), nullable=False)
    r_id = Column(Integer, ForeignKey(
        "restaurants.id"), nullable=False)

    labels = relationship('Labels', secondary=items_labels,
                          back_populates='items')
    orderitems = relationship('OrderItems', back_populates='items')
    completed_orderitems = relationship(
        'CompletedOrderItems', back_populates='items')
    item_prices = relationship('ItemPrices', back_populates='items')
    __allow_unmapped__ = True


class ItemPrices(Base):
    __tablename__ = 'item_prices'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    # Nullable for items without quantity
    quantity = Column(String(50), nullable=True)
    price = Column(Float, nullable=False)

    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)

    items = relationship('Items', back_populates='item_prices')
    orderitems = relationship('OrderItems', back_populates='item_prices')
    completed_orderitems = relationship(
        'CompletedOrderItems', back_populates='item_prices')


class Extras(Base):
    __tablename__ = 'extras'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    r_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    name = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)

    restaurants = relationship('Restaurants', back_populates='extras')
    orderitems = relationship(
        'OrderItems', secondary=orderitem_extras_association, back_populates='extras')


class Orders(Base):
    __tablename__ = 'orders'
    o_id = Column(Integer, primary_key=True,
                  nullable=False, autoincrement=True)
    amt = Column(Integer, nullable=False)
    dine_in = Column(Boolean, nullable=False, default=True)
    remarks = Column(String(500), nullable=True)
    booktime = Column(TIMESTAMP(timezone=True),
                      nullable=False, server_default=text('now()'))

    u_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    r_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    pay_id = Column(Integer, ForeignKey("payments.id"), nullable=True)

    orderitems = relationship(
        "OrderItems", back_populates="orders", cascade='all, delete-orphan')
    users = relationship("Users", back_populates="orders")
    # payments = relationship("Payments", back_populates="orders")

    __allow_unmapped__ = True


class OrderItems(Base):
    __tablename__ = 'orderitems'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    ord_id = Column(Integer, ForeignKey(
        "orders.o_id", ondelete='CASCADE'), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"))
    size_id = Column(Integer, ForeignKey("item_prices.id"), nullable=True)
    price = Column(Float, nullable=False)
    qty = Column(Integer, nullable=False)

    items = relationship("Items", back_populates="orderitems")
    item_prices = relationship('ItemPrices', back_populates='orderitems')
    orders = relationship("Orders", back_populates="orderitems")
    extras = relationship(
        'Extras', secondary=orderitem_extras_association, back_populates='orderitems')


class CompetedOrders(Base):
    __tablename__ = 'completed_orders'
    o_id = Column(Integer, primary_key=True,
                  nullable=False, autoincrement=True)
    amt = Column(Integer, nullable=False)
    dine_in = Column(Boolean, nullable=False, default=True)
    remarks = Column(String(500), nullable=True)
    booktime = Column(TIMESTAMP(timezone=True),
                      nullable=False, server_default=text('now()'))

    u_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    r_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    pay_id = Column(Integer, ForeignKey("payments.id"), nullable=True)

    completed_orderitems = relationship(
        "CompletedOrderItems", back_populates="completed_orders", cascade='all, delete-orphan')
    users = relationship("Users", back_populates="completed_orders")
    # payments = relationship("Payments", back_populates="orders")

    __allow_unmapped__ = True


class CompletedOrderItems(Base):
    __tablename__ = 'completed_orderitems'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    ord_id = Column(Integer, ForeignKey(
        "completed_orders.o_id", ondelete='CASCADE'), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"))
    size_id = Column(Integer, ForeignKey("item_prices.id"))
    price = Column(Float, nullable=False)
    qty = Column(Integer, nullable=False)

    items = relationship("Items", back_populates="completed_orderitems")
    item_prices = relationship(
        'ItemPrices', back_populates='completed_orderitems')
    completed_orders = relationship(
        "CompetedOrders", back_populates="completed_orderitems")


class Payments(Base):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    ord_id = Column(Integer, ForeignKey("orders.o_id"), nullable=False)
    mode = Column(Integer, nullable=False)  # 0:online, 1:counter
    payno = Column(Integer, nullable=False)

    # order = relationship("Orders", back_populates="orderitems")

# class Requests(Base):
#     __tablename__ = 'requests'
#     id = Column(Integer, primary_key=True, nullable=False, au toincrement=True)
#     o_id = Column(Integer, ForeignKey(
#         "orders.o_id"), nullable=False)
#     r_id = Column(Integer, ForeignKey(
#         "restaurants.id"), nullable=False)
