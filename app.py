import time
import inspect
import re
from fastapi import FastAPI, routing, encoders, exceptions, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse, FileResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.middleware.cors import CORSMiddleware
from utils import TimingMiddleware
from config import description
from routers import auth_router, order_router, stadium_router

app = FastAPI()
# app.mount('/static', StaticFiles(directory=BASE_DIR + '/statics/'), name='static')
app.include_router(auth_router)
app.include_router(order_router)
app.include_router(stadium_router)


@app.middleware("http")
async def measure_response_time(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    end_time = time.time()
    elapsed_time = end_time - start_time

    route = request.scope.get("fastapi_route", None)
    function_name = request.url.path

    print(f"Function: {function_name}, Elapsed Time: {elapsed_time} seconds")

    return response


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    file_path = "./"
    return FileResponse(file_path)


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


@app.get("/", status_code=200, include_in_schema=False)
async def main():
    return encoders.jsonable_encoder({"name": "API", "status": "ok"})


@app.exception_handler(exceptions.HTTPException)
async def handle_http_exception(request, exc):
    print(request)
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail}
    )


@app.exception_handler(Exception)
async def handle_exception(request, exc):
    print(request, exc)
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
