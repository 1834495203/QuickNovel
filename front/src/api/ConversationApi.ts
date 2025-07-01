import { baseURL } from '../axios/axios';
import type { CreateConversationDto } from '../entity/ConversationEntity';

const CONVERSATION_API_BASE_PATH = '/api/conversation';

export const createConversation = async (
    conversation: CreateConversationDto,
    onData: (data: string) => void,
    onEnd: () => void,
    onError: (error: Error) => void
): Promise<void> => {
  try {
    const response = await fetch(`${baseURL}${CONVERSATION_API_BASE_PATH}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream'
      },
      body: JSON.stringify(conversation)
    });

    if (!response.ok || !response.body) {
      throw new Error(`流式传输失败: ${response.statusText}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        onEnd();
        break;
      }

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n\n');
      buffer = lines.pop() || ''; // 保留不完整的行到缓冲区

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.substring(6);
          onData(data);
        } else if (line.startsWith('event: end')) {
          console.log('接收到流结束事件。');
          onEnd();
        }
      }
    }
  } catch (error) {
    onError(error instanceof Error ? error : new Error('未知错误'));
  }
}