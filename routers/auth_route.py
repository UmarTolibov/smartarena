from fastapi import APIRouter, Depends, status, encoders, exceptions, Query
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import exists, select, update, or_
from werkzeug.security import generate_password_hash, check_password_hash

from database import SignUpModel, LogInModel, Settings, ChangePassword, Email, User
from utils import get_db, send_email

auth_router = APIRouter(tags=['Authentication'], prefix='/auth')


@AuthJWT.load_config
def get_config():
    return Settings()


@auth_router.post('/signup', response_model=SignUpModel, status_code=status.HTTP_201_CREATED)
async def signup(user_data: SignUpModel, db: AsyncSession = Depends(get_db)):
    """
        ## Sing up
        This route registers the user.
        ### Required fields:
        ```
            username: str,
            email : str,
            number : str,
            password : str,
            is_staff : bool,
            is_active : bool

        ```
    """
    check_email_query = select(exists().where(User.email == user_data.email))
    check_username_query = select(exists().where(User.username == user_data.username))
    check_number_query = select(exists().where(User.number == user_data.number))

    check_email = await db.execute(check_email_query)
    check_username = await db.execute(check_username_query)
    check_number = await db.execute(check_number_query)

    if check_email.scalar() or check_username.scalar() or check_number.scalar():
        raise exceptions.HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                       detail="User with this email/username already exists")

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        number=user_data.number,
        password=generate_password_hash(user_data.password),
        is_active=user_data.is_active,
        is_staff=user_data.is_staff
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@auth_router.post('/login', status_code=status.HTTP_200_OK, response_description="logged in")
async def login(user: LogInModel, db: AsyncSession = Depends(get_db), authorize: AuthJWT = Depends()):
    """
        ## Login a user
        This route logs users in.
        ### Required fields:
        - `email` : str optional
        - `number` : str optional
        - `username` : str optional
        - `password` : str

        Returns a pair of jwt tokens : `access` and `refresh`
    """
    check_email_query = select(User).where(User.email == user.email)
    check_username_query = select(User).where(User.username == user.username)
    check_number_query = select(User).where(User.number == user.number)
    if user.email:
        check_user = await db.execute(check_email_query)
        check_user = check_user.scalar()
    elif user.username:
        check_user = await db.execute(check_username_query)
        check_user = check_user.scalar()
    elif user.number:
        check_user = await db.execute(check_number_query)
        check_user = check_user.scalar()
    else:
        raise exceptions.HTTPException(status_code=400, detail="email/username/number must be provided")
    if check_user and check_password_hash(check_user.password, user.password):
        subject = check_user.username if user.username is not None else user.email
        access_token = authorize.create_access_token(subject=subject)
        refresh_token = authorize.create_refresh_token(subject=subject)
        response = {
            "access": access_token,
            "refresh": refresh_token
        }
        return encoders.jsonable_encoder(response)
    raise exceptions.HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid username or password")


@auth_router.get('/refresh', status_code=status.HTTP_200_OK)
async def token_refresh(authorize: AuthJWT = Depends()):
    """
        ## Refreshing a Token
        This route is for refreshing expired/invalid tokens.
        ### Required:
        -` Bearer refresh_token ` in header
    """
    try:
        authorize.jwt_refresh_token_required()
    except Exception:
        raise exceptions.HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Provide a valid refresh token")
    current_user = authorize.get_jwt_subject()
    access_token = authorize.create_access_token(current_user)

    return encoders.jsonable_encoder({"access": access_token})


@auth_router.get("/verify")
async def verify_email(e: str = Query(..., max_length=50), code: int = None, db: AsyncSession = Depends(get_db)):
    """
        ## verify user's email
        this route verifies email of user and adds user to active users group
        ### query parameters:
        - `e` : str max-len = 50 (email)
        - `code` : digit - verification code (not required)
    """
    query = select(User).where(User.email == e)
    user = await db.execute(query)
    user = user.scalar()
    if code is None:
        s_code = await send_email(user)
        try:
            await db.execute(update(User).where(User.email == e).values(email_var=s_code))
            await db.commit()
            await db.refresh(user)
        except ExceptionGroup as e:
            raise exceptions.HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)
    else:
        if user.email_var == code:
            await db.execute(update(User).where(User.email == e).values(is_active=True, email_var=0))
            await db.commit()
            await db.refresh(user)
            return encoders.jsonable_encoder({"message": "Email verified"})
    return encoders.jsonable_encoder({"message": "verify your email by clicking the link we've sent"})


@auth_router.patch('/change-password')
async def change_password(password_data: ChangePassword, c: int = None, user: int = None,
                          db: AsyncSession = Depends(get_db),
                          authorize: AuthJWT = Depends()):
    """
            ## change-password
            This route updates the password of user in database.
            if `c` and `user` queries are not provided the user must be authorized by jwt
            ### Required fields:
            - `old_password` : str
            - `new_password` : str
            - `r_new_password` : str
            query parameters:
            - `c` : int = user.email_var
            - `user` : int = user_id
            Returns a success message on success
    """
    if c and user:
        query = select(User).where(User.id == user)
        verify = (await db.execute(query)).scalar().email_var == c
        if not verify:
            raise exceptions.HTTPException(status_code=401)
    else:
        try:
            authorize.jwt_required()
        except Exception as e:
            raise exceptions.HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                           detail=f"Provide a valid refresh token{e}")
        subject = authorize.get_jwt_subject()
        query = select(User).where(or_(User.email == subject, User.username == subject))
    user = (await db.execute(query)).scalar()
    password_match = check_password_hash(user.password, password_data.old_password)
    if password_match:
        if password_data.new_password != password_data.r_new_password:
            raise exceptions.HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                           detail="Please recheck your new_password!")
        await db.execute(update(User).where(User.username == user.username).values(
            password=generate_password_hash(password_data.new_password)))
        await db.commit()
        return encoders.jsonable_encoder({"message": "Your password has been changed successfully"})
    raise exceptions.HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please recheck your old password")


@auth_router.post("/reset-password")
async def reset_password(email: Email, db: AsyncSession = Depends(get_db)):
    """
        ## reset-password
        This route sends email verification to given email.
        ### Required fields:
        - `email` : str
        Returns a success message on success
    """
    user = (await db.execute(select(User).where(User.email == email.email))).scalar()
    if user is None:
        raise exceptions.HTTPException(status_code=404,
                                       detail="User with this email doesn't exist, Please registrate first")
    code = await send_email(user, email_var=False)
    await db.execute(update(User).where(User.email == email.email).values(email_var=code))
    await db.commit()
    await db.refresh(user)
    return encoders.jsonable_encoder({"message": "email verification code for changing password has been sent"})


@auth_router.get('/users')
async def list_all_users(authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    """
                    ## Lists all users info of `Owner`
                    This route is for retrieving stadiums.
                    ### Required:

                    ```- JWT  in header
                    ```
        """
    try:
        authorize.jwt_required()
        subject = authorize.get_jwt_subject()
    except Exception as e:
        raise exceptions.HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please provide a valid token")
    admin_query = select(User).where(or_(User.email == subject,User.username == subject,User.number == subject))
    admin = (await db.execute(admin_query)).scalar()
    if admin.is_staff:
        user_query = select(User)
        user = (await db.execute(user_query)).scalars()
        response = encoders.jsonable_encoder({"user": [i for i in user.all()]})
        return response
    else:
        raise exceptions.HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="you have no permission")

