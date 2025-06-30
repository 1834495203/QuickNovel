import type { AxiosResponse } from 'axios';
import apiClient from '../axios/axios';
import type { ResponseModel } from '../entity/ResponseEntity';
import { showNotifyResp } from '../utils/notify';
import type { CreateConversationDto } from '../entity/ConversationEntity';

const CONVERSATION_API_BASE_PATH = '/api/conversation';

export const createConversation = async (conversation: CreateConversationDto) => {
    const response = await fetch(`${CONVERSATION_API_BASE_PATH}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream'
        },
        body: JSON.stringify(conversation)
    })
}