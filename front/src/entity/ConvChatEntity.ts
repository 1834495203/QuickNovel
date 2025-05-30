import type { CharacterCard } from "./CharacterEntity";

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
  create_time?: number;
  timestamp: number;
  character?: CharacterCard;
}

export interface ConversationWithChatsResponse {
  conversation: ConversationResponse;
  chats: ChatContentResponse[];
}

// 枚举定义
export const ChatMessageType = {
  SYSTEM_PROMPT: 0,
  CHARACTER_TYPE: 1,
  USER_TYPE: 2,
  NORMAL_MESSAGE_USER: 3,
  NORMAL_MESSAGE_ASSISTANT: 4,
  ASIDE_MESSAGE: 5,
  ONLINE_MESSAGE: 6,
  NORMAL_MESSAGE_ASSISTANT_PART: 7,
  EXCLUDE_MESSAGE_EXCEPTION: 8
} as const

export type ChatMessageType = typeof ChatMessageType[keyof typeof ChatMessageType]

// 接口定义
export interface ChatMessage {
  cid: string
  role: string
  content: string
  chat_type: ChatMessageType
  reasoning_content?: string
  timestamp: Date
  conversation_id?: string
  user_role_id?: number
}

export interface StreamResponse {
  cid: string
  role: string
  content: string
  is_complete: boolean
  is_partial: boolean
  chat_type: ChatMessageType
  reasoning_content?: string
}