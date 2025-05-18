from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from controller.CharacterController import characters_router

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

app.include_router(characters_router)

@app.get("/")
async def root():
    return {"message": "欢迎使用QuickNovel API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9000)
