import type { AxiosResponse } from 'axios';
import apiClient from '../axios/axios';
import type { ResponseModel } from '../entity/ResponseEntity';
import { showNotifyResp } from '../utils/notify';
import type {
  CreateConversationRequest,
  CreateChatContentRequest,
  ConversationResponse,
  ChatContentResponse
} from '../entity/ConvChatEntity';

const CONV_CHAT_API_BASE_PATH = '/api/chat';

// 创建会话
export const createConversation = async (request: CreateConversationRequest): Promise<ResponseModel<ConversationResponse>> => {
  const responseData = await apiClient.post<ResponseModel>(`${CONV_CHAT_API_BASE_PATH}/conversations`, request);
  return responseData.data;
};

// 根据角色id获取对应的全部会话
export const getConversationsByCharacter = async (characterId: string): Promise<ConversationResponse[]> => {
  const responseData = await apiClient.get<ResponseModel<ConversationResponse[]>>(`${CONV_CHAT_API_BASE_PATH}/conversations/character/${characterId}`);
  showNotifyResp(responseData.data);
  return responseData.data.data ?? [];
};

// 聊天内容相关 API
export const createChatContent = async (conversationId: number, request: CreateChatContentRequest): Promise<ChatContentResponse> => {
  const responseData = await apiClient.post<ChatContentResponse>(`${CONV_CHAT_API_BASE_PATH}/conversations/${conversationId}/chats`, request);
  return responseData.data;
};

// 根据id获取会话的对话内容
export const getChatsByConversation = async (conversationId: number | string | null): Promise<ChatContentResponse[]> => {
  // 构建查询参数
  const params = conversationId != null ? { conversation_id: conversationId } : {};
  const responseData = await apiClient.get<AxiosResponse<ChatContentResponse[]>>(`${CONV_CHAT_API_BASE_PATH}/conversations`, { params });
  return responseData.data.data ?? [];
};

// 辅助函数 - 带通知的创建会话
export const createConversationWithNotify = async (request: CreateConversationRequest): Promise<ConversationResponse | null> => {
  try {
    const result = await createConversation(request);
    console.log('创建会话结果:', result);
    showNotifyResp(result);
    return result.data ?? null;
  } catch (error) {
    showNotifyResp({ code: 500, message: '创建会话失败', data: null } as ResponseModel);
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
