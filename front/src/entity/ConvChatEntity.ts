import type { CharacterCard } from "./CharacterEntity";

// 请求类型定义
export interface CreateConversationRequest {
  character_id: number;
  root_conversation_id?: number;
}

// 接收会话内容
export interface Conversation {
  conversation_id: number;
  character_id: number;
  root_conversation_id: number;
  create_time: number;
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

// 接口定义，前端显示消息实体类
export interface ChatMessage {
  cid: string
  role: string
  content: string
  chat_type: ChatMessageType
  reasoning_content?: string
  create_time: number
  conversation_id?: string
  user_role_id?: number
}

// 接收对话内容
export interface ChatContentResponse extends ChatMessage {
  character?: CharacterCard;
}

// 处理流式响应
export interface StreamResponse {
  cid: string
  role: string
  content: string
  chat_type: ChatMessageType
  reasoning_content?: string
}