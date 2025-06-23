class ApiError(Exception):

    def __init__(self, message: str, status_code: int, error_code: str):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code


class NotFoundError(ApiError):

    def __init__(self, entity_id: int):
        super().__init__(
            message=f"id为{entity_id}的数据未找到",
            status_code=404,
            error_code="not found"
        )


class DatabaseError(ApiError):

    def __init__(self, message: str):
        super().__init__(
            message,
            status_code=500,
            error_code="DATABASE_ERROR"
        )


class FileError(ApiError):

    def __init__(self, message: str):
        super().__init__(
            message,
            status_code=500,
            error_code="FILE_OPERATION_ERROR"
        )