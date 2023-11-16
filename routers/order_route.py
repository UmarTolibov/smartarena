from fastapi import APIRouter, Depends, status, encoders, exceptions
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import exists, select, delete, update, or_, and_
from database import OrderModel, Order, User, Stadium
from utils import get_db

order_router = APIRouter(prefix="/order", tags=['Ordering'])


@order_router.post('')
async def order_stadium(order: OrderModel, authorize: AuthJWT = Depends(),
                        db: AsyncSession = Depends(get_db)):
    """
        ## Add an order
        This route is for creating orders.
        ### Required:

        ```- JWT  in header
        stadium_id: int
        start_time: datetime.datetime
        hour: float
        ```
        ### Others
        ` status:str ` default:` PENDING `
    """
    try:
        authorize.jwt_required()
        subject = authorize.get_jwt_subject()
    except Exception:
        raise exceptions.HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please provide a valid token")
    user_query = select(User.id).where(or_(User.email == subject, User.username == subject))
    stadium_e_query = select(exists().where(or_(Stadium.id == order.stadium_id)))
    stadium_exist = (await db.execute(stadium_e_query)).scalar()
    if stadium_exist is False:
        raise exceptions.HTTPException(status_code=400,
                                       detail="Stadium with this id doesn't exists or has been deleted")
    else:
        user_id = (await db.execute(user_query)).scalar()
        stadium_query = select(Stadium.number_of_orders).where(Stadium.id == order.stadium_id)
        stadium_order_num = (await db.execute(stadium_query)).scalar() + 1
        add_number_q = update(Stadium).where(Stadium.id == order.stadium_id).values(number_of_orders=stadium_order_num)

        new_order = Order(status=order.status, user_id=user_id, stadium_id=order.stadium_id,
                          start_time=order.start_time, hour=order.hour)

        await db.execute(add_number_q)
        db.add(new_order)
        await db.commit()
        await db.refresh(new_order)
        return encoders.jsonable_encoder({"order": order})


@order_router.patch('/edit/{order_id}')
async def edit_order(order: OrderModel, order_id: int, authorize: AuthJWT = Depends(),
                     db: AsyncSession = Depends(get_db)):
    """
            ## Edit Order
            This route is for updating a specific orders.
            ### Required:

            - `  JWT  in header ` jwt_subject must be the one who created this order or an Admin
            - ` order_id: int ` query param -> id of an order

            ### Optional:

            ```
            stadium_id: int
            start_time: datetime.datetime
            hour: float
            status:str -> default: PENDING
            ```
    """

    try:
        authorize.jwt_required()
        subject = authorize.get_jwt_subject()
    except Exception:
        raise exceptions.HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please provide a valid token")
    user_query = select(User).where(or_(User.email == subject, User.username == subject))
    user = (await db.execute(user_query)).scalar()
    query = select(Order).where(Order.id == order_id)

    order_exist = (await db.execute(query)).scalar()
    if order_exist is None:
        raise exceptions.HTTPException(status_code=status.HTTP_204_NO_CONTENT)
    elif order_exist.user_id == user.id or user.is_staff:
        await db.execute(
            update(Order).where(Order.id == order_id).values(status=order.status, stadium_id=order.stadium_id,
                                                             start_time=order.start_time, hour=order.hour))
        await db.commit()
        return encoders.jsonable_encoder({"message": "Updated", "stadium": order})


@order_router.delete('/delete')
async def delete_order(order_id: int, authorize: AuthJWT = Depends(),
                       db: AsyncSession = Depends(get_db)):
    """
            ## Delete Order
            This route is for deleting a specific orders.
            ### Required:
            - `  JWT  in header ` jwt_subject must be the one who created this order or an Admin
            - ` order_id: int ` query param -> id of an order
    """

    try:
        authorize.jwt_required()
        subject = authorize.get_jwt_subject()
    except Exception:
        raise exceptions.HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please provide a valid token")
    user_query = select(User).where(or_(User.email == subject, User.username == subject))
    user = (await db.execute(user_query)).scalar()
    query = select(Order).where(and_(Order.id == order_id))
    order_exist = (await db.execute(query)).scalar()
    if order_exist is None:
        raise exceptions.HTTPException(status_code=status.HTTP_204_NO_CONTENT)
    elif order_exist.user_id == user.id or user.is_staff:
        delete_query = delete(Order).where(Order.id == order_id)
        await db.execute(delete_query)
        await db.commit()


@order_router.get('/my')
async def list_all_my_orders(authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    """
            ## Get my Orders
            This route is for fetching all orders of user.
            ### Required:
            - `  JWT  in header `
    """

    try:
        authorize.jwt_required()
        subject = authorize.get_jwt_subject()
    except Exception:
        raise exceptions.HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please provide a valid token")
    user_query = select(User).where(or_(User.email == subject, User.username == subject))
    user = (await db.execute(user_query)).scalar()
    user_id: int = user.id
    query = select(Order).where(Order.user_id == user_id)
    stadiums = (await db.execute(query)).scalars()
    response = encoders.jsonable_encoder({"stadiums": [i for i in stadiums.all()]})
    return response


@order_router.get('')
async def retrieve_or_get_all_orders(order_id: int = 0, get_all: bool = False, db: AsyncSession = Depends(get_db),
                                     authorize: AuthJWT = Depends()):
    """
            ## Get a specific order or List all orders (` admins ` only)
            This route is for retrieving/listing orders.
            ### Required:
            - `  JWT  in header ` jwt_subject must be an Admin
            - ` order_id: int ` query param -> id of an order if you want to get a single order
            - ` get_all: bool ` query param -> set it to 1/true/yes if you want to get all orders

    """

    try:
        authorize.jwt_required()
        subject = authorize.get_jwt_subject()
    except Exception:
        raise exceptions.HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please provide a valid token")
    user_query = select(User).where(or_(User.email == subject, User.username == subject))
    user = (await db.execute(user_query)).scalar()
    if user.is_staff is False:
        raise exceptions.HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="This action is forbidden")

    if get_all:
        query = select(Order)
        order = (await db.execute(query)).scalars().all()
    else:
        query = select(Order).where(Order.id == order_id)
        order = (await db.execute(query)).scalar()
    return encoders.jsonable_encoder(order)
