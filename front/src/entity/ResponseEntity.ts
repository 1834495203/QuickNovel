// 基础响应接口
export interface ResponseModel<T = any> {
    code: number;
    message: string;
    data?: T;
}

// 响应状态码常量
export const ResponseCode = {
    SUCCESS: 200,
    BAD_REQUEST: 400,
    NOT_FOUND: 404,
    SERVER_ERROR: 500
} as const;

// 辅助函数
export const createResponse = {
    success<T>(data?: T, message: string = "操作成功"): ResponseModel<T> {
        return {
            code: ResponseCode.SUCCESS,
            message,
            data
        };
    },

    error<T>(code: number = ResponseCode.BAD_REQUEST, message: string = "操作失败", data?: T): ResponseModel<T> {
        return {
            code,
            message,
            data
        };
    },

    warning<T>(code: number, message: string, data?: T): ResponseModel<T> {
        return {
            code,
            message,
            data
        };
    }
};
