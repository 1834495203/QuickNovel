import type { AxiosResponse } from 'axios';
import apiClient from '../axios/axios';
import type { ResponseModel } from '../entity/ResponseEntity';
import { showNotifyResp } from '../utils/notify';

const CONV_CHAT_API_BASE_PATH = '/api/chat';

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
  conversation_id: number;
  user_role_id: number;
  role: string;
  content: string;
  reasoning_content?: string;
  chat_type: number;
  create_time: number;
}

export interface ConversationWithChatsResponse {
  conversation: ConversationResponse;
  chats: ChatContentResponse[];
}

// 会话相关 API
export const createConversation = async (request: CreateConversationRequest): Promise<ConversationResponse> => {
  const responseData = await apiClient.post<ConversationResponse>(`${CONV_CHAT_API_BASE_PATH}/conversations`, request);
  return responseData.data;
};

export const getConversationsByCharacter = async (characterId: number): Promise<ConversationResponse[]> => {
  const responseData = await apiClient.get<AxiosResponse<ConversationResponse[]>>(`${CONV_CHAT_API_BASE_PATH}/conversations/character/${characterId}`);
  return responseData.data.data;
};

// 聊天内容相关 API
export const createChatContent = async (conversationId: number, request: CreateChatContentRequest): Promise<ChatContentResponse> => {
  const responseData = await apiClient.post<ChatContentResponse>(`${CONV_CHAT_API_BASE_PATH}/conversations/${conversationId}/chats`, request);
  return responseData.data;
};

export const getChatsByConversation = async (conversationId: number): Promise<ChatContentResponse[]> => {
  const responseData = await apiClient.get<AxiosResponse<ChatContentResponse[]>>(`${CONV_CHAT_API_BASE_PATH}/conversations/${conversationId}/chats`);
  return responseData.data.data;
};

// 综合查询 API
export const getConversationsWithChatsByCharacter = async (characterId: number): Promise<ConversationWithChatsResponse[]> => {
  const responseData = await apiClient.get<AxiosResponse<ConversationWithChatsResponse[]>>(`${CONV_CHAT_API_BASE_PATH}/characters/${characterId}/conversations-with-chats`);
  return responseData.data.data;
};

// 辅助函数 - 带通知的创建会话
export const createConversationWithNotify = async (request: CreateConversationRequest): Promise<ConversationResponse | null> => {
  try {
    const result = await createConversation(request);
    showNotifyResp({ code: 200, message: '会话创建成功', data: result } as ResponseModel);
    return result;
  } catch (error) {
    console.error('创建会话失败:', error);
    return null;
  }
};

// 辅助函数 - 带通知的创建聊天内容
export const createChatContentWithNotify = async (conversationId: number, request: CreateChatContentRequest): Promise<ChatContentResponse | null> => {
  try {
    const result = await createChatContent(conversationId, request);
    showNotifyResp({ code: 200, message: '消息发送成功', data: result } as ResponseModel);
    return result;
  } catch (error) {
    console.error('发送消息失败:', error);
    return null;
  }
};
