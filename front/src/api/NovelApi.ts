import type { AxiosResponse } from 'axios';
import apiClient from '../axios/axios'; // 从 ../axios/axios.ts 导入配置好的 axios 实例
import type { ResponseModel } from '../entity/ResponseEntity';
import type { AllNovelDto, NovelEntity } from '../entity/NovelEntity';
import { showNotifyResp } from '../utils/notify';

const CHARACTER_API_BASE_PATH = '/api/novel'; // API 的基础路径

export const getAllNovels = async (): Promise<NovelEntity[]> => {
    const response: AxiosResponse<ResponseModel<NovelEntity[]>> = await apiClient.get(`${CHARACTER_API_BASE_PATH}/`);
    showNotifyResp(response.data); // 显示通知
    return response.data.data ?? []; // 返回实际的数据数组
};

export const getNovelById = async (novelId: number | string): Promise<AllNovelDto> => {
    const response: AxiosResponse<ResponseModel<AllNovelDto>> = await apiClient.get(`${CHARACTER_API_BASE_PATH}/${novelId}`);
    showNotifyResp(response.data); // 显示通知
    return response.data.data ?? {} as AllNovelDto; // 返回实际的数据，若无数据则返回空对象
};