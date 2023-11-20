import time
from fastapi import Request


class MeasureResponseTimeMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        end_time = time.time()
        elapsed_time = end_time - start_time

        function_name = request.url.path

        print(f"Function: {function_name}, Elapsed Time: {elapsed_time} seconds")

        return response
