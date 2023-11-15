# from fastapi.requests import Request
# from werkzeug.security import check_password_hash
# from fastapi.responses import RedirectResponse
# from sqladmin import ModelView
# from sqladmin.authentication import AuthenticationBackend
# from sqlalchemy.sql import select

# from database import User, Stadium, Order
# from app import admin
# from database import Session


# class AdminAuth(AuthenticationBackend):
#     async def login(self, request: Request) -> bool:
#         form = await request.form()
#         username, password = form["username"], form["password"]
#         user_query = select(User).where(User.username == username)

#         async with Session.begin() as db:
#             user = (await db.execute(user_query)).scalar()
#             if user and check_password_hash(user.password, password):
#                 return True

#         request.session.update({"token": "..."})

#         return True

#     async def logout(self, request: Request) -> bool:
#         # Usually you'd want to just clear the session
#         request.session.clear()
#         return True

#     async def authenticate(self, request: Request):
#         token = request.session.get("token")

#         if not token:
#             return RedirectResponse(request.url_for("admin:login"), status_code=302)

#         # Check the token in depth


# class UserAdmin(ModelView, model=User):
#     column_list = [User.id, User.username]


# class StadiumAdmin(ModelView, model=Stadium):
#     column_list = [Stadium.id, Stadium.name]


# class OrderAdmin(ModelView, model=Order):
#     column_list = [Order.id, Order.stadium_id]


# admin.add_view(UserAdmin)
# admin.add_view(StadiumAdmin)
# admin.add_view(OrderAdmin)
