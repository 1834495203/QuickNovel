import type { AxiosResponse } from 'axios';
import apiClient from '../axios/axios';
import type { ResponseModel } from '../entity/ResponseEntity';
import type { SceneEntity } from '../entity/SceneEntity';
import { showNotifyResp } from '../utils/notify';

const SCENE_API_BASE_PATH = '/api/scene';

export interface CreateSceneDto {
    chapter_id: number;
    scene_name: string;
    scene_desc?: string;
}

export const createScene = async (sceneData: CreateSceneDto): Promise<SceneEntity> => {
    const response: AxiosResponse<ResponseModel<SceneEntity>> = await apiClient.post(`${SCENE_API_BASE_PATH}/`, sceneData);
    showNotifyResp(response.data);
    return response.data.data ?? {} as SceneEntity;
};
