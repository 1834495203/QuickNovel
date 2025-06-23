from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

# 定义泛型类型变量
T = TypeVar('T')  # 用于表示任意类型的返回数据


# 统一返回类
class ResponseModel(BaseModel, Generic[T]):
    code: int  # 状态码
    message: str  # 返回消息
    data: Optional[T] = None  # 返回数据，可以为空

    class Config:
        from_attributes = True  # 支持从对象转换为 Pydantic 模型


# 预定义常见状态码（可选）
class ResponseCode:
    SUCCESS = 200  # 成功
    BAD_REQUEST = 400  # 请求错误
    NOT_FOUND = 404  # 未找到
    SERVER_ERROR = 500  # 服务器错误


# 辅助函数，用于快速生成返回结果
def success(data: T = None, message: str = "操作成功") -> ResponseModel[T]:
    return ResponseModel(code=ResponseCode.SUCCESS, message=message, data=data)


def error(code: int = ResponseCode.BAD_REQUEST, message: str = "操作失败", data: T = None) -> ResponseModel[T]:
    return ResponseModel(code=code, message=message, data=data)


def warning(code: int = None, message: str = None, data: T = None) -> ResponseModel[T]:
    return ResponseModel(code=code, message=message, data=data)
