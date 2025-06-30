import type { AxiosResponse } from 'axios';
import apiClient from '../axios/axios';
import type { ResponseModel } from '../entity/ResponseEntity';
import type { ChapterEntity, CreateChapterDto } from '../entity/ChapterEntity';
import { showNotifyResp } from '../utils/notify';

const CHAPTER_API_BASE_PATH = '/api/chapter';

export const createChapter = async (chapterData: CreateChapterDto): Promise<ChapterEntity> => {
    const response: AxiosResponse<ResponseModel<ChapterEntity>> = await apiClient.post(`${CHAPTER_API_BASE_PATH}/`, chapterData);
    showNotifyResp(response.data);
    return response.data.data ?? {} as ChapterEntity;
};
