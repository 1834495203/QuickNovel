from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from controller.CharacterController import characters_router
from controller.ConvChatController import conv_chat_router
from controller.ProvidersController import providers_router

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

app.include_router(characters_router)

app.include_router(providers_router)

app.include_router(conv_chat_router)

@app.get("/")
async def root():
    return {"message": "欢迎使用QuickNovel API"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9000)
