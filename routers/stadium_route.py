from fastapi import APIRouter, Depends, status, encoders, exceptions, Response
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select, update, delete, or_, and_
from database import User, Stadium, StadiumModel
from utils import get_db

stadium_router = APIRouter(prefix="/stadium", tags=['Stadium'])


@stadium_router.post('/')
async def add_stadium(stadium: StadiumModel, authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        authorize.jwt_required()
        subject = authorize.get_jwt_subject()
    except Exception as e:
        raise exceptions.HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please provide a valid token")
    user_query = select(User.id).where(or_(User.email == subject, User.username == subject))
    owner_id = (await db.execute(user_query)).scalar()

    new_stadium = Stadium(
        name=stadium.name, description=stadium.description, image_url=stadium.image_url, price=stadium.price,
        opening_time=stadium.opening_time, closing_time=stadium.closing_time, is_active=stadium.is_active,
        region=stadium.region, district=stadium.district, location=stadium.location, user_id=owner_id
    )

    db.add(new_stadium)
    try:
        await db.commit()
        await db.refresh(new_stadium)
        return encoders.jsonable_encoder({"stadium": new_stadium})
    except Exception as e:
        raise exceptions.HTTPException(detail=f"name of the stadium is already taken{e}",
                                       status_code=status.HTTP_400_BAD_REQUEST)


@stadium_router.patch('/edit')
async def edit_stadium(stadium: StadiumModel, s: int, authorize: AuthJWT = Depends(),
                       db: AsyncSession = Depends(get_db)):
    try:
        authorize.jwt_required()
        subject = authorize.get_jwt_subject()
    except Exception as e:
        raise exceptions.HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please provide a valid token")
    user_query = select(User.id).where(or_(User.email == subject, User.username == subject))
    owner_id = (await db.execute(user_query)).scalar()
    stadium_query = select(Stadium).where(and_(Stadium.id == s, Stadium.user_id == owner_id))
    stadium_exist = (await db.execute(stadium_query)).scalar()
    if stadium_exist is None:
        raise exceptions.HTTPException(status_code=401,
                                       detail="This actions are permitted to stadiums' owner only")
    else:
        await db.execute(
            update(Stadium).where(Stadium.id == s).values(name=stadium.name, description=stadium.description,
                                                          image_url=stadium.image_url, price=stadium.price,
                                                          opening_time=stadium.opening_time,
                                                          closing_time=stadium.closing_time,
                                                          is_active=stadium.is_active,
                                                          region=stadium.region, district=stadium.district,
                                                          location=stadium.location))
        await db.commit()
        return encoders.jsonable_encoder({"message": "Updated", "stadium": stadium})


@stadium_router.get('/my')
async def list_all_my_stadiums(authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        authorize.jwt_required()
        subject = authorize.get_jwt_subject()
    except Exception as e:
        raise exceptions.HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please provide a valid token")
    user_query = select(User).where(or_(User.email == subject, User.username == subject))
    user = (await db.execute(user_query)).scalar()
    stadiums = (await db.execute(select(Stadium).where(Stadium.user_id == user.id))).scalars()
    response = encoders.jsonable_encoder({"stadiums": [i for i in stadiums.all()]})
    return response


@stadium_router.get('/')
async def retrieve_or_get_all_stadium(s_id: int = 0, get_all: bool = False, authorize: AuthJWT = Depends(),
                                      db: AsyncSession = Depends(get_db)):
    try:
        authorize.jwt_required()
    except Exception as e:
        raise exceptions.HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please provide a valid token")
    if get_all is True and s_id == 0:
        query = select(Stadium).where(Stadium.is_active)
        stadiums = (await db.execute(query)).scalars().all()
        return encoders.jsonable_encoder(stadiums)
    elif s_id != 0 and get_all is False:
        query = select(Stadium).where(Stadium.id == s_id)
        stadium = (await db.execute(query)).scalar()
        return encoders.jsonable_encoder(stadium)
    else:
        raise exceptions.HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please use one query only")


@stadium_router.delete('/delete')
async def remove_stadium(s_id: int, authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        authorize.jwt_required()
        subject = authorize.get_jwt_subject()
    except Exception as e:
        raise exceptions.HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please provide a valid token")
    user_query = select(User.id).where(or_(User.email == subject, User.username == subject))
    owner_id = (await db.execute(user_query)).scalar()
    stadium_query = select(Stadium).where(and_(Stadium.id == s_id, Stadium.user_id == owner_id))
    stadium = (await db.execute(stadium_query)).scalar()
    if stadium is None:
        raise exceptions.HTTPException(status_code=401,
                                       detail="You're unauthorized or the stadium with this id no longer exists")
    else:
        await db.execute(delete(Stadium).where(Stadium.id == s_id))
        await db.commit()
        return Response(content=f"Stadium{stadium.name} deleted", status_code=status.HTTP_200_OK)
