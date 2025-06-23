import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from starlette.responses import JSONResponse

from core.entity.ResponseEntity import error
from core.utils.CustomizeException import ApiError

app = FastAPI(
    title="QuickNovel API",
    description="QuickNovel",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {"message": "欢迎使用QuickNovel API"}


@app.exception_handler(ApiError)
async def api_error_handler(request, exc: ApiError):
    logging.error(f"api error: {exc.message}, code: {exc.error_code}")
    return JSONResponse(
        status_code=exc.status_code,
        content=error(code=exc.status_code, message=exc.message).model_dump()
    )


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9000)
