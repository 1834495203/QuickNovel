import type { AllChapterDto } from './ChapterEntity';

export interface NovelEntity {
    novel_id: number;
    novel_name: string;
    novel_desc?: string;
    create_time: Date;
}

// 对应后端的ResponseAllNovelDto
export interface AllNovelDto extends NovelEntity {
    chapters: AllChapterDto[];
}
