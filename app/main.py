import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.api_v1.api import api_router
from app.api.exceptions import CustomException

app = FastAPI(title="Report service", description="Reports service", version="0.8.1")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


app.include_router(api_router)


@app.exception_handler(CustomException)
async def unicorn_exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": exc.status, "message": exc.message},
    )


if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8014, log_level="debug")
