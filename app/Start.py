import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from starlette.responses import JSONResponse

from controller.ChapterController import chapter_router
from controller.CharacterController import character_router
from controller.NovelController import novel_router
from controller.SceneController import scene_router
from core.entity.ResponseEntity import error
from core.mapper.config.DatabaseConfig import db
from core.utils.CustomizeException import ApiError
from core.utils.LogConfig import init_log, get_logger

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(api: FastAPI):
    # 配置日志
    init_log()

    # 确保在应用启动时生成数据库映射
    logger.info("生成数据库映射...")
    # Pony ORM 的 generate_mapping 不需要 await
    db.generate_mapping(create_tables=True)
    yield
    logger.info("数据库映射生成完毕。")

app = FastAPI(
    title="QuickNovel API",
    description="QuickNovel",
    version="1.0.0",
    lifespan=lifespan,
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
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(character_router)
app.include_router(chapter_router)
app.include_router(novel_router)
app.include_router(scene_router)

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
