import asyncio
import inspect
import logging
import re
from fastapi import FastAPI, routing, encoders, exceptions, Form, Depends
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from telebot.async_telebot import logger
from telebot.types import Update
# from fastapi.staticfiles import StaticFiles
# from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from database import populate_enums
from utils import description, MeasureResponseTimeMiddleware, get_db
from routers import *
from utils import WEBHOOK_URL, TOKEN
from bot import bot, bot_meta

# app.mount('/static', StaticFiles(directory=BASE_DIR + '/statics/'), name='static')
app = FastAPI()
app.include_router(auth_router)
app.include_router(order_router)
app.include_router(stadium_router)
app.middleware("http")(MeasureResponseTimeMiddleware(app))


@app.get("/", status_code=200, include_in_schema=False)
async def main():
    return encoders.jsonable_encoder({"name": "API", "status": "ok"})


@app.on_event("startup")
async def on_startup():
    populate_enums()
    webhook_info = await bot.get_webhook_info(30)
    if webhook_info.url != WEBHOOK_URL:
        logger.debug(
            f"updating webhook url, old: {webhook_info.url}, new: {WEBHOOK_URL}"
        )
        await bot_meta()
        if not await bot.set_webhook(url=WEBHOOK_URL):
            raise RuntimeError("unable to set webhook")


@app.post(f"/webhook/{TOKEN}/", include_in_schema=False)
async def handle_telegram_message(update: dict):
    if update:
        update = Update.de_json(update)
        await bot.process_new_updates([update])
        await asyncio.sleep(0.1)


@app.exception_handler(exceptions.HTTPException)
async def handle_http_exception(request, exc):
    print(request)
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail}
    )


@app.exception_handler(Exception)
async def handle_exception(request, exc):
    logging.log(logging.WARNING, exc)
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error"}
    )


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="SmartArena API",
        description=description,
        version="1.1",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Enter: **'Bearer &lt;JWT&gt;'**, where JWT is the access token"
        }
    }

    # Get all routes where jwt_optional() or jwt_required
    api_router = [route for route in app.routes if isinstance(route, routing.APIRoute)]

    for route in api_router:
        path = getattr(route, "path")
        endpoint = getattr(route, "endpoint")
        methods = [method.lower() for method in getattr(route, "methods")]

        for method in methods:
            # access_token
            if (
                    re.search("jwt_required", inspect.getsource(endpoint)) or
                    re.search("fresh_jwt_required", inspect.getsource(endpoint)) or
                    re.search("jwt_optional", inspect.getsource(endpoint))
            ):
                openapi_schema["paths"][path][method]["security"] = [
                    {
                        "Bearer Auth": []
                    }
                ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# CORS

# origins = [
#     "http://localhost.tiangolo.com",
#     "https://localhost.tiangolo.com",
#     "http://localhost",
#     "http://localhost:8080",
# ]
#
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
