import type { AllSceneDto } from './SceneEntity';

export interface ChapterEntity {
    chapter_id: number;
    chapter_number: number;
    chapter_title: string;
    chapter_desc?: string;
    create_time: Date;
    parent?: number;
    novel: number;
}

export interface CreateChapterDto {
    chapter_number: number;
    chapter_title: string;
    chapter_desc?: string;
    parent?: number;
    novel: number;
}

// 对应后端的ResponseAllChapterDto
export interface AllChapterDto extends ChapterEntity {  
    scene: AllSceneDto[];
}
