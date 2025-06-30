export interface ConversationEntity {
    conversation_id: number;
    role: string;
    sender_character?: string;
    receiver_character?: string;
    content:string;
    create_time: Date;
    parent?: number; // Parent conversation ID
    scene?: number; // Associated scene ID
}

export interface CreateConversationDto {
    role: string;
    sender_character?: string;
    receiver_character?: string;
    content: string;
    parent?: number; // Parent conversation ID
    scene: number; // Associated scene ID
}