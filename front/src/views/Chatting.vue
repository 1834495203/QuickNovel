<template>
  <div class="chat-container">
    <div class="chat-header">
      <h2>QuickNovel</h2>
      <div class="connection-controls">
        <button 
          @click="toggleConnection" 
          :class="['btn', connectionType === 'websocket' ? 'btn-danger' : 'btn-success']"
        >
          {{ connectionType === 'websocket' ? '断开WebSocket' : '连接WebSocket' }}
        </button>
        <select v-model="connectionType" class="connection-select">
          <option value="http">HTTP流式</option>
          <option value="websocket">WebSocket</option>
        </select>
      </div>
    </div>

    <div class="chat-messages" ref="messagesContainer">
      <div 
        v-for="(message, index) in messages" 
        :key="index" 
        :class="['message', message.role === 'user' ? 'user-message' : 'assistant-message']"
      >
        <div class="message-content">
          <strong>{{ message.role === 'user' ? '用户' : 'AI' }}:</strong>
          <div class="message-text">
            <span 
              v-if="message.role === 'assistant' && message.isStreaming"
              v-for="(char, charIndex) in message.displayedContent" 
              :key="charIndex"
              :class="['char', { 'char-animate': charIndex === (message.displayedContent ? message.displayedContent.length - 1 : -1) }]"
            >{{ char }}</span>
            <span v-else>{{ message.content }}</span>
            <span v-if="message.role === 'assistant' && message.isStreaming" class="cursor">|</span>
          </div>
          <div class="message-time">{{ formatTime(message.timestamp) }}</div>
        </div>
      </div>
      
      <div v-if="isLoading && !currentStreamingMessage" class="message assistant-message">
        <div class="message-content">
          <strong>AI:</strong>
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>

    <div class="chat-input">
      <div class="input-group">
        <input
          v-model="inputMessage"
          @keyup.enter="sendMessage"
          :disabled="isLoading"
          placeholder="输入您的消息..."
          class="message-input"
        />
        <button 
          @click="sendMessage" 
          :disabled="isLoading || !inputMessage.trim()"
          class="send-button"
        >
          发送
        </button>
      </div>
    </div>

    <div v-if="error" class="error-message">
      {{ error }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'

// 类型定义
interface Message {
  role: 'user' | 'assistant'
  content: string
  displayedContent?: string
  isStreaming?: boolean
  timestamp: Date
}

interface LLMResponse {
  role: string
  response: string
  is_complete: boolean
  is_partial: boolean
}

// 响应式数据
const messages = ref<Message[]>([])
const inputMessage = ref('')
const isLoading = ref(false)
const error = ref('')
const connectionType = ref<'http' | 'websocket'>('http')
const messagesContainer = ref<HTMLElement>()

// WebSocket 相关
let websocket: WebSocket | null = null
const wsConnected = ref(false)

// API 配置
const API_BASE_URL = 'http://localhost:9000' // 根据你的后端地址调整
const WS_URL = 'ws://localhost:9000/api/chatting/ws'

// 工具函数
const formatTime = (date: Date): string => {
  return date.toLocaleTimeString('zh-CN', { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const addMessage = (role: 'user' | 'assistant', content: string, isStreaming = false) => {
  const message: Message = {
    role,
    content,
    displayedContent: isStreaming ? '' : content,
    isStreaming,
    timestamp: new Date()
  }
  messages.value.push(message)
  
  if (isStreaming && role === 'assistant') {
    currentStreamingMessage.value = message
  }
  
  scrollToBottom()
  return message
}

// 新增响应式数据
const currentStreamingMessage = ref<Message | null>(null)
const typewriterSpeed = ref(50) // 打字机效果速度（毫秒）
let eventSource: EventSource | null = null

// 逐字显示效果
const typewriterEffect = (message: Message, fullText: string) => {
  if (!message.isStreaming) return
  
  let currentIndex = 0
  message.displayedContent = ''
  
  const typeInterval = setInterval(() => {
    if (currentIndex < fullText.length) {
      message.displayedContent += fullText[currentIndex]
      currentIndex++
      scrollToBottom()
    } else {
      clearInterval(typeInterval)
      message.isStreaming = false
      message.content = fullText
      currentStreamingMessage.value = null
    }
  }, typewriterSpeed.value)
}

// EventSource 流式请求
const sendEventSourceRequest = async (message: string) => {
  try {
    isLoading.value = true
    
    // 关闭之前的连接
    if (eventSource) {
      eventSource.close()
    }
    
    const url = new URL(`${API_BASE_URL}/api/providers/llm/stream`)
    url.searchParams.append('message', message)
    
    eventSource = new EventSource(url.toString())
    
    let assistantMessage: Message | null = null
    let fullResponse = ''
    
    eventSource.onmessage = (event) => {
      try {
        const data: LLMResponse = JSON.parse(event.data)
        
        if (data.response) {
          if (!assistantMessage) {
            assistantMessage = addMessage('assistant', '', true)
          }
          
          if (data.is_complete && !data.is_partial) {
            // 流式响应片段
            fullResponse += data.response
            typewriterEffect(assistantMessage, fullResponse)
          } else if (!data.is_complete && data.is_partial) {
            // 最终完整响应
            fullResponse = data.response
            typewriterEffect(assistantMessage, fullResponse)
          }
        }
      } catch (parseError) {
        console.warn('解析EventSource消息失败:', parseError)
      }
    }
    
    eventSource.onerror = (err) => {
      console.error('EventSource错误:', err)
      error.value = 'EventSource连接错误'
      isLoading.value = false
      eventSource?.close()
      eventSource = null
    }
    
    eventSource.addEventListener('end', () => {
      isLoading.value = false
      eventSource?.close()
      eventSource = null
    })
    
  } catch (err) {
    console.error('EventSource请求错误:', err)
    error.value = `请求失败: ${err instanceof Error ? err.message : '未知错误'}`
    isLoading.value = false
  }
}

// HTTP 流式请求（保留作为备选方案）
const sendHttpStreamRequest = async (message: string) => {
  try {
    isLoading.value = true
    
    const response = await fetch(`${API_BASE_URL}/api/providers/llm`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message })
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body?.getReader()
    if (!reader) {
      throw new Error('无法获取响应流')
    }

    let assistantMessage: Message | null = null
    let fullResponse = ''

    try {
      while (true) {
        const { done, value } = await reader.read()
        
        if (done) break

        const chunk = new TextDecoder().decode(value)
        const lines = chunk.split('\n').filter(line => line.trim())
        
        for (const line of lines) {
          try {
            const data: LLMResponse = JSON.parse(line)
            
            if (data.response) {
              if (!assistantMessage) {
                assistantMessage = addMessage('assistant', '', true)
              }
              
              if (data.is_complete && !data.is_partial) {
                fullResponse += data.response
                typewriterEffect(assistantMessage, fullResponse)
              } else if (!data.is_complete && data.is_partial) {
                fullResponse = data.response
                typewriterEffect(assistantMessage, fullResponse)
              }
            }
          } catch (parseError) {
            console.warn('解析响应行失败:', parseError, line)
          }
        }
      }
    } finally {
      reader.releaseLock()
    }
  } catch (err) {
    console.error('HTTP请求错误:', err)
    error.value = `请求失败: ${err instanceof Error ? err.message : '未知错误'}`
  } finally {
    isLoading.value = false
  }
}

// WebSocket 连接管理
const connectWebSocket = () => {
  if (websocket?.readyState === WebSocket.OPEN) {
    return
  }

  websocket = new WebSocket(WS_URL)
  
  websocket.onopen = () => {
    wsConnected.value = true
    console.log('WebSocket 连接已建立')
  }
  
  websocket.onmessage = (event) => {
    try {
      const data: LLMResponse = JSON.parse(event.data)
      
      if (data.response) {
        let assistantMessage = currentStreamingMessage.value
        
        if (!assistantMessage) {
          assistantMessage = addMessage('assistant', '', true)
        }
        
        if (data.is_complete && !data.is_partial) {
          // 流式响应片段
          const currentContent = assistantMessage.content + data.response
          typewriterEffect(assistantMessage, currentContent)
        } else if (!data.is_complete && data.is_partial) {
          // 最终完整响应
          typewriterEffect(assistantMessage, data.response)
          isLoading.value = false
        }
      }
    } catch (err) {
      console.error('解析WebSocket消息失败:', err)
    }
  }
  
  websocket.onerror = (err) => {
    console.error('WebSocket错误:', err)
    error.value = 'WebSocket连接错误'
    isLoading.value = false
  }
  
  websocket.onclose = () => {
    wsConnected.value = false
    isLoading.value = false
    console.log('WebSocket 连接已关闭')
  }
}

const disconnectWebSocket = () => {
  if (websocket) {
    websocket.close()
    websocket = null
    wsConnected.value = false
  }
}

const toggleConnection = () => {
  if (connectionType.value === 'websocket') {
    if (wsConnected.value) {
      disconnectWebSocket()
    } else {
      connectWebSocket()
    }
  }
}

// WebSocket 发送消息
const sendWebSocketMessage = (message: string) => {
  if (!websocket || websocket.readyState !== WebSocket.OPEN) {
    error.value = 'WebSocket未连接'
    return
  }

  try {
    isLoading.value = true
    websocket.send(JSON.stringify({ message }))
  } catch (err) {
    console.error('发送WebSocket消息失败:', err)
    error.value = '发送消息失败'
    isLoading.value = false
  }
}

// 主发送函数
const sendMessage = async () => {
  const message = inputMessage.value.trim()
  if (!message || isLoading.value) return

  // 添加用户消息
  addMessage('user', message)
  inputMessage.value = ''

  if (connectionType.value === 'websocket') {
    sendWebSocketMessage(message)
  } else {
    // 优先使用 EventSource，如果不支持则回退到 fetch
    if (typeof EventSource !== 'undefined') {
      await sendEventSourceRequest(message)
    } else {
      await sendHttpStreamRequest(message)
    }
  }
}

// 监听连接类型变化
watch(connectionType, (newType, oldType) => {
  if (oldType === 'websocket') {
    disconnectWebSocket()
  }
  if (newType === 'websocket') {
    connectWebSocket()
  }
})

// 生命周期
onMounted(() => {
  // 添加欢迎消息
  addMessage('assistant', '你好！我是AI助手，有什么可以帮助您的吗？')
})

onUnmounted(() => {
  disconnectWebSocket()
  if (eventSource) {
    eventSource.close()
  }
})
</script>

<style scoped>
.chat-container {
  max-width: 800px;
  margin: 0 auto;
  height: 600px;
  display: flex;
  flex-direction: column;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  background: white;
}

.chat-header {
  padding: 16px;
  background: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-header h2 {
  margin: 0;
  color: #333;
}

.connection-controls {
  display: flex;
  gap: 10px;
  align-items: center;
}

.connection-select {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
}

.btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}

.btn-success {
  background: #28a745;
  color: white;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn:hover {
  opacity: 0.9;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #fafafa;
}

.message {
  margin-bottom: 16px;
  display: flex;
}

.user-message {
  justify-content: flex-end;
}

.assistant-message {
  justify-content: flex-start;
}

.message-content {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 18px;
  position: relative;
}

.user-message .message-content {
  background: #007bff;
  color: white;
}

.assistant-message .message-content {
  background: white;
  border: 1px solid #e0e0e0;
  color: #333;
}

.message-text {
  margin: 4px 0;
  line-height: 1.4;
  white-space: pre-wrap;
  min-height: 1.4em; /* 确保流式消息有最小高度 */
}

.message-time {
  font-size: 0.75rem;
  opacity: 0.7;
  margin-top: 4px;
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  margin: 8px 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #999;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.chat-input {
  padding: 16px;
  background: white;
  border-top: 1px solid #e0e0e0;
}

.input-group {
  display: flex;
  gap: 8px;
}

.message-input {
  flex: 1;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 24px;
  outline: none;
  font-size: 14px;
}

.message-input:focus {
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.message-input:disabled {
  background: #f8f9fa;
  cursor: not-allowed;
}

.send-button {
  padding: 12px 24px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 24px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.2s;
}

.send-button:hover:not(:disabled) {
  background: #0056b3;
}

.send-button:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.error-message {
  padding: 12px 16px;
  background: #f8d7da;
  color: #721c24;
  border-top: 1px solid #f5c6cb;
  text-align: center;
}

.char {
  display: inline;
}

.char-animate {
  animation: charAppear 0.1s ease-in;
}

@keyframes charAppear {
  from {
    opacity: 0;
    transform: translateY(-2px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.cursor {
  display: inline-block;
  animation: blink 1s infinite;
  color: #007bff;
  font-weight: bold;
}

@keyframes blink {
  0%, 50% {
    opacity: 1;
  }
  51%, 100% {
    opacity: 0;
  }
}
</style>