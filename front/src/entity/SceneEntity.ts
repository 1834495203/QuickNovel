export interface SceneEntity {
    scene_id: number;
    scene_name: string;
    scene_desc?: string;
    create_time: Date;
    parent?: number;
    chapter?: number;
}

export interface CreateSceneDto {
    scene_name: string;
    scene_desc?: string;
    parent?: number;
    chapter?: number;
}
