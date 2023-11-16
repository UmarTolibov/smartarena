import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl, EmailStr, constr, validator


class ProductImageSchema(BaseModel):
    url: HttpUrl
    name: str


class StadiumModel(BaseModel):
    name: str
    description: str = ''
    image_url: Optional[ProductImageSchema] = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f" \
                                              "/Example_image.svg/600px-Example_image.svg.png"
    price: float = 0.0
    opening_time: Optional[str] = "08:00:00"
    closing_time: Optional[str] = "00:00:00"
    is_active: Optional[bool] = True
    region: str = "Tashkent"
    district: str = "Yakka Saroy"
    location: str = "2-uy"

    class Config:
        orm_mode = True
        schema_extra = {
            'example': {
                "name": "admin",
                "description": "a@gmail.com",
                "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Example_image.svg/600px"
                         "-Example_image.svg.png",
                "price": 100.23,
                "opening_time": "00:00:00",
                "closing_time": "00:00:00",
                "is_active": True,
                "region": "Tashkent",
                "district": "Yakka Saroy",
                "location": "2-uy"

            }
        }


class OrderModel(BaseModel):
    status: str = "PENDING"
    stadium_id: int = 0
    start_time: Optional[datetime.datetime]
    hour: float = 1.0

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "status": "APPROVED",
                "stadium_id": 1,
                "start_time": "2023-07-08 15:34:33.170394",
                "hour": 1
            },
            "required_field": ["stadium_id", "start_timr", "hour"]
        }


class SignUpModel(BaseModel):
    id: Optional[int]
    username: constr(min_length=3, max_length=50)
    number: constr(regex=r"^\+998\d{9}$")
    email: EmailStr
    password: constr(min_length=6, max_length=32)
    is_staff: Optional[bool]
    is_active: Optional[bool]
    email_var: Optional[int] = None

    @validator('password')
    def validate_password(cls, value):
        # Custom password validation logic
        if not any(char.isupper() for char in value):
            raise ValueError('Password must contain at least one uppercase letter')

        if not any(char.isdigit() for char in value):
            raise ValueError('Password must contain at least one digit')

        return value

    class Config:
        orm_mode = True
        schema_extra = {
            'example': {
                "username": "admin",
                "number": "+9981234567",
                "email": "a@gmail.com",
                "password": "@#$%^&&&&&^%$",
                "is_staff": False,
                "is_active": False
            }
        }


class LogInModel(BaseModel):
    email: Optional[str] = None
    number: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str]

    @validator('password', pre=True, always=True)
    def validate_password(cls, value):
        if not value:
            raise ValueError('Password is required')
        return value

    @validator('email', 'number', 'username', pre=True, always=True)
    def validate_at_least_one_field(cls, values):
        email = values.get('email')
        number = values.get('number')
        username = values.get('username')

        if email is None and number is None and username is None:
            raise ValueError('At least one of email, number, or username must be provided')

        return values


class Settings(BaseModel):
    authjwt_secret_key: str = '9090f713f30ea645d7183efb2461f690c19704364dcf3e40488e3c0cafed80e5'


class ChangePassword(BaseModel):
    old_password: str
    new_password: str
    r_new_password: str


class Email(BaseModel):
    email: str
