from fastapi import APIRouter, Depends, status, encoders, exceptions, Response
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select, update, delete, or_, and_

from database import User, Stadium, StadiumModel
from utils import get_db

stadium_router = APIRouter(prefix="/stadium", tags=['Stadium'])


@stadium_router.post('')
async def add_stadium(stadium: StadiumModel, authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    """
            ## Add a stadium
            This route is for adding stadiums.
            ### Required:

            ```- JWT  in header
            "name": str,
            "description": str,
            "image": url,
            "price": int,
            "opening_time": str -"00:00:00",
            "closing_time": str -"00:00:00",
            "is_active": bool,
            "region": str,
            "district": str,
            "location": str
            ```
        """
    try:
        authorize.jwt_required()
        subject = authorize.get_jwt_subject()
    except Exception as e:
        raise exceptions.HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                       detail=f"Please provide a valid token\n{e}")
    user_query = select(User).where(or_(User.email == subject, User.username == subject, User.number == subject))
    owner = (await db.execute(user_query)).scalar()
    if owner.is_active:
        owner_id = owner.id
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
    else:
        raise exceptions.HTTPException(detail=f"Please activate your account",
                                       status_code=status.HTTP_401_UNAUTHORIZED)


@stadium_router.put('/edit')
async def edit_stadium(stadium: StadiumModel, s: int, authorize: AuthJWT = Depends(),
                       db: AsyncSession = Depends(get_db)):
    """
                ## Update a stadium info `Owner|admin only`
                This route is for editing stadium.
                ### Required:

                ```- JWT  in header
                "name": str,
                "description": str,
                "image": url,
                "price": int,
                "opening_time": str -"00:00:00",
                "closing_time": str -"00:00:00",
                "is_active": bool,
                "region": str,
                "district": str,
                "location": str
                ```
    """
    try:
        authorize.jwt_required()
        subject = authorize.get_jwt_subject()
    except Exception as e:
        raise exceptions.HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                       detail=f"Please provide a valid token\n{e}")
    user_query = select(User.id).where(or_(User.email == subject, User.username == subject, User.number == subject))
    owner_id = (await db.execute(user_query)).scalar()
    admin = (
        await db.execute(select(User.is_staff).where(or_(User.email == subject, User.username == subject)))).scalar()
    stadium_query = select(Stadium).where(and_(Stadium.id == s, Stadium.user_id == owner_id))
    stadium_exist = (await db.execute(stadium_query)).scalar()
    if stadium_exist is None or not admin:
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
    """
                    ## Lists all stadium info of `Owner`
                    This route is for retrieving stadiums.
                    ### Required:

                    ```- JWT  in header
                    ```
        """
    try:
        authorize.jwt_required()
        subject = authorize.get_jwt_subject()
    except Exception as e:
        raise exceptions.HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                       detail=f"Please provide a valid token\n{e}")
    user_query = select(User).where(or_(User.email == subject, User.username == subject, User.number == subject))
    user = (await db.execute(user_query)).scalar()
    if user.is_active:
        stadiums = (await db.execute(select(Stadium).where(Stadium.user_id == user.id))).scalars()
        response = encoders.jsonable_encoder({"stadiums": [i for i in stadiums.all()]})
        return response
    else:
        raise exceptions.HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please activate your account")


@stadium_router.get('')
async def retrieve_or_get_all_stadium(s_id: int = 0, get_all: bool = False, authorize: AuthJWT = Depends(),
                                      db: AsyncSession = Depends(get_db)):
    """
                ## Get all or specific stadium info
                This route is for `get`ting stadium(s)
                ### Required:

                ```- JWT  in header
                "s_id": int = 0
                ### or
                "get_all": bool = False|0
                ```
    """

    try:
        authorize.jwt_required()
        subject = authorize.get_jwt_subject()
    except Exception as e:
        raise exceptions.HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                       detail=f"Please provide a valid token\n{e}")
    user_query = select(User.is_staff).where(
        or_(User.email == subject, User.username == subject, User.number == subject))
    user = (await db.execute(user_query)).scalar()
    if user:
        if get_all is True and s_id == 0:
            query = select(Stadium).where(Stadium.is_active)
            stadiums = (await db.execute(query)).scalars().all()
            return encoders.jsonable_encoder(stadiums)
        elif s_id != 0 and get_all is False:
            query = select(Stadium).where(Stadium.id == s_id)
            stadium = (await db.execute(query)).scalar()
            return encoders.jsonable_encoder(stadium)
        else:
            raise exceptions.HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                           detail="Please use at least one query")
    else:
        raise exceptions.HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                       detail="Please activate your account")


@stadium_router.delete('/delete')
async def remove_stadium(s_id: int, authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    """
    ## Delete stadium `owner` only
    This route is for removing stadium from database
    ### Required
    - `s_id : int`
    """
    try:
        authorize.jwt_required()
        subject = authorize.get_jwt_subject()
    except Exception as e:
        raise exceptions.HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                       detail=f"Please provide a valid token\n{e}")
    user_query = select(User.id).where(or_(User.email == subject, User.username == subject, User.number == subject))
    owner_id = (await db.execute(user_query)).scalar()
    stadium_query = select(Stadium).where(and_(Stadium.id == s_id, Stadium.user_id == owner_id))
    stadium = (await db.execute(stadium_query)).scalar()
    if stadium is None:
        raise exceptions.HTTPException(status_code=401,
                                       detail="You're unauthorized or the stadium with this id no longer exists")
    else:
        await db.execute(delete(Stadium).where(Stadium.id == s_id))
        await db.commit()
        return Response(content=f"Stadium {stadium.name} deleted", status_code=status.HTTP_200_OK)
