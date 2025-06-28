import type { AxiosResponse } from 'axios';
import apiClient from '../axios/axios'; // 从 ../axios/axios.ts 导入配置好的 axios 实例
import type { CharacterCard, CreateCharacterDto } from '../entity/CharacterEntity';
import type { ResponseModel } from '../entity/ResponseEntity';
import { showNotifyResp } from '../utils/notify'; // 导入通知函数

const CHARACTER_API_BASE_PATH = '/api/character'; // API 的基础路径

// axios.ts 中的拦截器会处理 ResponseModel 并返回其 data 字段 (T)
// 因此，这里的函数签名应为 Promise<T>

export const getAllCharacters = async (): Promise<CharacterCard[]> => {
  // apiClient.get<T> 中的 T 是期望从拦截器返回的数据类型
  const responseData = await apiClient.get<AxiosResponse<CharacterCard[]>>(`${CHARACTER_API_BASE_PATH}/`);
  return responseData.data.data.map((char)=>{
    if (char.avatar === null || char.avatar === undefined) {
      char.avatar = '../src/assets/header.png'; // 设置默认头像
    }
    return char;
  }); // 返回实际的数据数组
};

export const getCharacterById = async (characterId: number | string): Promise<CharacterCard> => {
  const responseData = await apiClient.get<ResponseModel>(`${CHARACTER_API_BASE_PATH}/${characterId}`);
  return responseData.data.data;
};

export const createCharacter = async (character: CreateCharacterDto): Promise<CharacterCard> => {
  // 假设后端在成功创建后，在 ResponseModel.data 中返回 CharacterCard
  const responseData = await apiClient.post<CharacterCard>(`${CHARACTER_API_BASE_PATH}/`, character);
  return responseData.data;
};

export const updateCharacterById = async (characterId: number, character: CharacterCard): Promise<ResponseModel> => {
  // 使用 FormData 发送 character 和 avatar
  const responseData = await apiClient.post<ResponseModel>(
    `${CHARACTER_API_BASE_PATH}/${characterId}`, character
  );
  showNotifyResp(responseData.data); // 显示通知
  return responseData.data;
};

export const updateCharacterAvatarById = async (characterId: number, avatar: File): Promise<ResponseModel> => {
  // 使用 FormData 发送 avatar
  const formData = new FormData();
  formData.append('avatar', avatar);

  const responseData = await apiClient.post<ResponseModel>(
    `${CHARACTER_API_BASE_PATH}/${characterId}/avatar`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );
  showNotifyResp(responseData.data); // 显示通知
  return responseData.data;
};

export const deleteCharacterById = async (characterId: number): Promise<ResponseModel> => {
  const responseData = await apiClient.delete<ResponseModel>(`${CHARACTER_API_BASE_PATH}/${characterId}`);
  showNotifyResp(responseData.data); // 显示通知
  return responseData.data;
};
