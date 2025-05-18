import axios from "axios";
import { showNotify } from "../utils/notify";

// 创建 Axios 实例
const instance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:9000",
  timeout: 10000, // 请求超时时间
  headers: {
    "Content-Type": "application/json",
  },
});

// 请求拦截器
instance.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    showNotify({
      type: "error",
      message: "请求发送失败，请检查网络",
      duration: 2000,
    });
    return Promise.reject(error);
  }
);

// 响应拦截器
instance.interceptors.response.use(
  (response) => {
    const res = response.data;
    // 根据 ResponseModel 结构处理
    if (res.code === 200) {
      // 成功，返回 data
      return response;
    } else {
      // 非 200 状态码，显示错误信息
      showNotify(res);
      return Promise.reject(new Error(res.message || "操作失败"));
    }
  },
  (error) => {
    // 网络错误或服务器未响应
    if (error.response) {
      // 服务器返回了状态码
      const status = error.response.status;
      let message = "服务器错误";
      if (status === 404) {
        message = "请求的资源不存在";
      } else if (status === 500) {
        message = "服务器内部错误";
      } else if (status === 400) {
        message = "请求参数错误";
      } else if (status === 403) {
        message = "无权限访问";
      }
      showNotify({
        type: "error",
        message: message,
        duration: 2000,
      });
    } else if (error.request) {
      // 请求发出但未收到响应
      showNotify({
        type: "error",
        message: "网络连接失败，请检查网络",
        duration: 2000,
      });
    } else {
      // 其他错误
      showNotify({
        type: "error",
        message: "请求失败：" + error.message,
        duration: 2000,
      });
    }
    return Promise.reject(error);
  }
);

export default instance;
