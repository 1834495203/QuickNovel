export interface createWorldDto {
    world_name: string;
    world_desc: string;
    create_time?: Date;
}

export interface createWorldDetailDto {
    world_detail_name: string;
    world_detail_desc: string;
    world: number;
}

export interface worldEntity {
    world_id: number;
    world_name: string;
    world_desc: string;
    create_time: Date;
}

export interface worldDetailEntity {
    id: number;
    world_detail_name: string;
    world_detail_desc: string;
    create_time: Date;
}

export interface allWorldDetailDto extends worldEntity {
    world_details: worldDetailEntity[];
}