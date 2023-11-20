import time
from fastapi import Request
from app import app


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
