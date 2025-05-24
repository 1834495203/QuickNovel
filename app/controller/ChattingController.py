import httpx
from fastapi import WebSocket, APIRouter
import json

from starlette.websockets import WebSocketDisconnect

from controller.ProvidersController import LLMInput, stream_llm_response

chatting_router = APIRouter(prefix="/api/chatting", tags=["chatting"])


# WebSocket 端点
@chatting_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            try:
                # 接收前端发送的消息
                data = await websocket.receive_text()
                user_message = json.loads(data)["message"]

                # 直接调用流式生成器
                input_data = LLMInput(message=user_message)
                async for line in stream_llm_response(input_data):
                    if line:
                        await websocket.send_text(line.strip())

            except WebSocketDisconnect:
                print("WebSocket 客户端断开连接")
                break  # 退出循环，不发送消息

    except Exception as e:
        print(f"WebSocket 错误: {str(e)}")
    finally:
        await websocket.close()  # 确保连接关闭
