import type { AxiosResponse } from 'axios';
import apiClient from '../axios/axios';
import type { ResponseModel } from '../entity/ResponseEntity';
import { showNotifyResp } from '../utils/notify';
import type {
  CreateConversationRequest,
  Conversation,
  ChatContentResponse,
  ChatMessage
} from '../entity/ConvChatEntity';

const CONV_CHAT_API_BASE_PATH = '/api/chat';

// 创建会话
export const createConversation = async (request: CreateConversationRequest): Promise<ResponseModel<Conversation>> => {
  const responseData = await apiClient.post<ResponseModel>(`${CONV_CHAT_API_BASE_PATH}/conversations`, request);
  return responseData.data;
};

// 根据角色id获取对应的全部会话
export const getConversationsByCharacter = async (characterId: string): Promise<Conversation[]> => {
  const responseData = await apiClient.get<ResponseModel<Conversation[]>>(`${CONV_CHAT_API_BASE_PATH}/conversations/character/${characterId}`);
  showNotifyResp(responseData.data);
  return responseData.data.data ?? [];
};

// 根据id获取会话的对话内容
export const getChatsByConversation = async (conversationId: number | string | null): Promise<ChatContentResponse[]> => {
  // 构建查询参数
  const params = conversationId != null ? { conversation_id: conversationId } : {};
  const responseData = await apiClient.get<AxiosResponse<ChatContentResponse[]>>(`${CONV_CHAT_API_BASE_PATH}/conversations`, { params });
  return responseData.data.data ?? [];
};

// 根据会话和cid删除对应的对话内容
export const deleteChatContent = async (conversationId: number | string | null, cid: string): Promise<ResponseModel> => {
    const params = conversationId != null ? {conversation_id: conversationId, cid: cid} : { cid: cid };
  const responseData = await apiClient.delete<ResponseModel>(`${CONV_CHAT_API_BASE_PATH}/conversations/chats`, { params });
  return responseData.data;
};

// 更新对话
export const updateChatContent = async (chat_message: ChatMessage): Promise<ResponseModel> => {
  const responseData = await apiClient.put<ResponseModel>(`${CONV_CHAT_API_BASE_PATH}/conversations/chats`, chat_message);
  return responseData.data;
};

// 辅助函数 - 带通知的创建会话
export const createConversationWithNotify = async (request: CreateConversationRequest): Promise<Conversation | null> => {
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
