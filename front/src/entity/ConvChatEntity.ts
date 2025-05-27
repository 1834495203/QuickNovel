// 请求类型定义
export interface CreateConversationRequest {
  character_id: number;
  root_conversation_id?: number;
}

export interface CreateChatContentRequest {
  conversation_id: number;
  role: string;
  user_role_id: number;
  content: string;
  reasoning_content?: string;
  chat_type?: number; // ChatMessageType enum value
}

// 响应类型定义
export interface ConversationResponse {
  conversation_id: number;
  character_id: number;
  root_conversation_id: number;
  create_time: number;
}

export interface ChatContentResponse {
  cid: string;
  conversation_id?: number;
  user_role_id?: number;
  role: string;
  content: string;
  reasoning_content?: string;
  chat_type: number;
  create_time?: Date;
  timestamp: Date;
}

export interface ConversationWithChatsResponse {
  conversation: ConversationResponse;
  chats: ChatContentResponse[];
}