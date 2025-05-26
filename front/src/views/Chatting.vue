<template>
  <div class="chat-container">
    <div class="chat-header">
      <h2>QuickNovel</h2>
    </div>
    
    <div class="chat-messages" ref="messagesContainer">
      <div v-for="msg in messages" :key="msg.id" :class="['message', msg.role]">
        <div class="message-content">
          <span class="role-tag">{{ msg.role === 'user' ? '用户' : 'AI' }}</span>
          <div class="content">{{ msg.content }}</div>
          <div v-if="msg.reasoning" class="reasoning">
            <small>推理: {{ msg.reasoning }}</small>
          </div>
        </div>
      </div>
      
      <div v-if="isStreaming" class="streaming-indicator">
        <div class="typing-dots">
          <span></span><span></span><span></span>
        </div>
      </div>
    </div>
    
    <div class="chat-input">
      <div class="input-group">
        <textarea
          v-model="inputMessage"
          @keydown.enter.prevent="handleSend"
          @keydown.shift.enter="inputMessage += '\n'"
          placeholder="输入消息... (Enter发送, Shift+Enter换行)"
          :disabled="isStreaming"
          rows="3"
        ></textarea>
        <button 
          @click="handleSend" 
          :disabled="!inputMessage.trim() || isStreaming"
          class="send-btn"
        >
          {{ isStreaming ? '发送中...' : '发送' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, nextTick, onUnmounted } from 'vue'

// 枚举定义
enum ChatMessageType {
  SYSTEM_PROMPT = 0,
  CHARACTER_TYPE = 1,
  USER_TYPE = 2,
  NORMAL_MESSAGE_USER = 3,
  NORMAL_MESSAGE_ASSISTANT = 4,
  ASIDE_MESSAGE = 5,
  ONLINE_MESSAGE = 6,
  NORMAL_MESSAGE_ASSISTANT_PART = 7,
  EXCLUDE_MESSAGE_EXCEPTION = 8
}

// 接口定义
interface ChatMessage {
  id: string
  role: string
  content: string
  chat_type: ChatMessageType
  reasoning?: string
  timestamp: Date
}

interface StreamResponse {
  cid: string
  role: string
  content: string
  is_complete: boolean
  is_partial: boolean
  chat_type: ChatMessageType
  reasoning_content?: string
}

// 响应式数据
const messages = reactive<ChatMessage[]>([])
const inputMessage = ref('')
const isStreaming = ref(false)
const messagesContainer = ref<HTMLElement>()
let currentEventSource: EventSource | null = null

// 滚动到底部
const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 添加消息
const addMessage = (message: Partial<ChatMessage>) => {
  const newMessage: ChatMessage = {
    id: Date.now().toString(),
    role: message.role || 'user',
    content: message.content || '',
    chat_type: message.chat_type || ChatMessageType.NORMAL_MESSAGE_USER,
    reasoning: message.reasoning,
    timestamp: new Date()
  }
  messages.push(newMessage)
  scrollToBottom()
  return newMessage
}

// 处理流式响应
const handleStreamResponse = (data: string) => {
  try {
    const response: StreamResponse = JSON.parse(data)
    
    if (response.chat_type === ChatMessageType.NORMAL_MESSAGE_ASSISTANT_PART) {
      // 流式部分响应 - 追加到最后一条AI消息
      const lastMessage = messages[messages.length - 1]
      if (lastMessage && lastMessage.role === 'assistant') {
        lastMessage.content += response.content
      } else {
        addMessage({
          role: 'assistant',
          content: response.content,
          chat_type: response.chat_type,
          reasoning: response.reasoning_content
        })
      }
      scrollToBottom()
    } else if (response.chat_type === ChatMessageType.NORMAL_MESSAGE_ASSISTANT) {
      // 完整响应 - 替换或添加完整消息
      const lastMessage = messages[messages.length - 1]
      if (lastMessage && lastMessage.role === 'assistant') {
        lastMessage.content = response.content
        lastMessage.reasoning = response.reasoning_content
      } else {
        addMessage({
          role: 'assistant',
          content: response.content,
          chat_type: response.chat_type,
          reasoning: response.reasoning_content
        })
      }
      isStreaming.value = false
      scrollToBottom()
    } else if (response.chat_type === ChatMessageType.EXCLUDE_MESSAGE_EXCEPTION) {
      // 错误响应
      addMessage({
        role: 'error',
        content: `错误: ${response.content}`,
        chat_type: response.chat_type
      })
      isStreaming.value = false
    }
  } catch (error) {
    console.error('解析响应失败:', error)
    addMessage({
      role: 'error',
      content: '解析响应失败',
      chat_type: ChatMessageType.EXCLUDE_MESSAGE_EXCEPTION
    })
    isStreaming.value = false
  }
}

// 发送消息
const handleSend = async () => {
  const message = inputMessage.value.trim()
  if (!message || isStreaming.value) return

  // 添加用户消息
  addMessage({
    role: 'user',
    content: message,
    chat_type: ChatMessageType.NORMAL_MESSAGE_USER
  })

  // 清空输入
  inputMessage.value = ''
  isStreaming.value = true

  try {
    // 构建请求体
    const requestBody = {
      cid: Date.now().toString(),
      role: 'user',
      user_role_id: 1,
      conversation_id: 1,
      content: message,
      is_complete: true,
      is_partial: false,
      chat_type: ChatMessageType.NORMAL_MESSAGE_USER
    }

    // 使用fetch发送POST请求
    const response = await fetch('http://localhost:9000/api/providers/llm', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody)
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    // 处理流式响应
    const reader = response.body?.getReader()
    const decoder = new TextDecoder()

    if (!reader) {
      throw new Error('无法获取响应流')
    }

    try {
      while (true) {
        const { done, value } = await reader.read()
        
        if (done) break

        // 解码数据块
        const chunk = decoder.decode(value, { stream: true })
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.trim()) {
            handleStreamResponse(line)
          }
        }
      }
    } finally {
      reader.releaseLock()
    }

  } catch (error) {
    console.error('发送消息失败:', error)
    addMessage({
      role: 'error',
      content: `发送失败: ${error.message}`,
      chat_type: ChatMessageType.EXCLUDE_MESSAGE_EXCEPTION
    })
    isStreaming.value = false
  }
}

// 清理资源
onUnmounted(() => {
  currentEventSource?.close()
})

// 注意：currentEventSource现在主要用于兼容性，实际使用fetch + ReadableStream
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-width: 800px;
  margin: 0 auto;
  border: 1px solid #e1e5e9;
  border-radius: 8px;
  overflow: hidden;
}

.chat-header {
  background: #f8f9fa;
  padding: 1rem;
  border-bottom: 1px solid #e1e5e9;
  text-align: center;
}

.chat-header h2 {
  margin: 0;
  color: #2c3e50;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  background: #ffffff;
}

.message {
  margin-bottom: 1rem;
  padding: 0.5rem;
  border-radius: 8px;
}

.message.user {
  background: #e3f2fd;
  margin-left: 2rem;
}

.message.assistant {
  background: #f5f5f5;
  margin-right: 2rem;
}

.message.error {
  background: #ffebee;
  border-left: 4px solid #f44336;
}

.message-content {
  word-wrap: break-word;
}

.role-tag {
  display: inline-block;
  padding: 0.2rem 0.5rem;
  background: #2196f3;
  color: white;
  border-radius: 4px;
  font-size: 0.8rem;
  margin-bottom: 0.5rem;
}

.message.user .role-tag {
  background: #4caf50;
}

.message.error .role-tag {
  background: #f44336;
}

.content {
  white-space: pre-wrap;
  line-height: 1.5;
}

.reasoning {
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: rgba(0,0,0,0.05);
  border-radius: 4px;
  font-style: italic;
}

.streaming-indicator {
  text-align: center;
  padding: 1rem;
}

.typing-dots {
  display: inline-block;
}

.typing-dots span {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #2196f3;
  margin: 0 2px;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-dots span:nth-child(1) { animation-delay: -0.32s; }
.typing-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
  0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
  40% { transform: scale(1); opacity: 1; }
}

.chat-input {
  padding: 1rem;
  background: #f8f9fa;
  border-top: 1px solid #e1e5e9;
}

.input-group {
  display: flex;
  gap: 0.5rem;
}

textarea {
  flex: 1;
  resize: vertical;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 0.5rem;
  font-family: inherit;
  font-size: 14px;
}

textarea:focus {
  outline: none;
  border-color: #2196f3;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2);
}

.send-btn {
  padding: 0.5rem 1rem;
  background: #2196f3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;
}

.send-btn:hover:not(:disabled) {
  background: #1976d2;
}

.send-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* 滚动条样式 */
.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>