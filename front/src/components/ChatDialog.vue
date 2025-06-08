<template>
    <div class="chat-dialog">
        <!-- Header 插槽 -->
        <div class="chat-header">
            <slot name="header">
                <h2>QuickNovel</h2>
            </slot>
        </div>

        <!-- Messages 插槽 -->
        <div class="chat-messages" ref="messagesContainer">
            <slot name="messages" :messages="messages" :isStreaming="isStreaming">
                <div v-for="msg in messages" :key="msg.cid" :class="['message', msg.role]">
                    <div class="message-content">
                        <div class="message-header">
                            <span class="role-tag">{{ msg.role === 'user' ? '用户' : 'AI' }}</span>
                            <div class="message-actions">
                                <button 
                                    @click="handleEditMessage(msg.cid)" 
                                    class="action-btn edit-btn"
                                    title="编辑"
                                    v-if="!editingMessageId || editingMessageId !== msg.cid"
                                >
                                    编辑
                                </button>
                                <button 
                                    @click="handleSaveEdit(msg)" 
                                    class="action-btn save-btn"
                                    title="保存"
                                    v-if="editingMessageId === msg.cid"
                                >
                                    保存
                                </button>
                                <button 
                                    @click="handleCancelEdit()" 
                                    class="action-btn cancel-btn"
                                    title="取消"
                                    v-if="editingMessageId === msg.cid"
                                >
                                    取消
                                </button>
                                <button 
                                    @click="handleDeleteMessage(msg.cid, msg.role)" 
                                    class="action-btn delete-btn"
                                    title="删除"
                                >
                                    删除
                                </button>
                            </div>
                        </div>
                        <div class="content" v-if="editingMessageId !== msg.cid">{{ msg.content }}</div>
                        <textarea 
                            v-if="editingMessageId === msg.cid"
                            v-model="editingContent"
                            class="edit-textarea"
                            rows="3"
                            @keydown.ctrl.enter="handleSaveEdit(msg)"
                            @keydown.esc="handleCancelEdit()"
                        ></textarea>
                        <div v-if="msg.reasoning_content" class="reasoning">
                            <small>推理: {{ msg.reasoning_content }}</small>
                        </div>
                    </div>

                    <div class="message-time">
                        {{ formatTime(msg.create_time ?? 0) }}
                    </div>
                </div>

                <div v-if="isStreaming" class="streaming-indicator">
                    <div class="typing-dots">
                        <span></span><span></span><span></span>
                    </div>
                </div>
            </slot>
        </div>

        <!-- Input 插槽 -->
        <div class="chat-input">
            <slot name="input" :inputMessage="inputMessage" :isStreaming="isStreaming" :handleSend="handleSend">
                <div class="input-group">
                    <textarea v-model="inputMessage" @keydown.enter.prevent="handleSend"
                        @keydown.shift.enter="inputMessage += '\n'" placeholder="输入消息... (Enter发送, Shift+Enter换行)"
                        :disabled="isStreaming" rows="3"></textarea>
                    <button @click="handleSend" :disabled="!inputMessage.trim() || isStreaming" class="send-btn">
                        {{ isStreaming ? '发送中...' : '发送' }}
                    </button>
                </div>
            </slot>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive, nextTick, onUnmounted, watch } from 'vue'
import type { CharacterCard } from '../entity/CharacterEntity'
import type { ChatContentResponse, ChatMessage, StreamResponse } from '../entity/ConvChatEntity'
import { ChatMessageType } from '../entity/ConvChatEntity'
import { deleteChatContent, updateChatContent } from '../api/ConvChatApi'
import { v4 as uuidv4 } from 'uuid';
import { showNotify, showNotifyResp } from '../utils/notify'

// Props
interface Props {
    character?: CharacterCard
    conversationId?: number | null
    initialMessages?: ChatContentResponse[]
}

const props = withDefaults(defineProps<Props>(), {
    initialMessages: () => []
})

// Emits
const emit = defineEmits<{
    messageAdded: [message: ChatContentResponse]
}>()

// 响应式数据
const messages = reactive<ChatMessage[]>([])
const inputMessage = ref('')
const isStreaming = ref(false)
const messagesContainer = ref<HTMLElement>()

// 编辑相关状态
const editingMessageId = ref<string | null>(null)
const editingContent = ref('')
const originalContent = ref('')

// 滚动到底部
const scrollToBottom = async () => {
    await nextTick()
    if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
}

// 监听初始消息变化
watch(() => props.initialMessages, (newMessages) => {
    messages.length = 0
    messages.push(...newMessages)
    scrollToBottom()
}, { immediate: true, deep: true })

// 添加消息
const addMessage = (message: Partial<ChatMessage>) => {
    const newMessage: ChatMessage = {
        cid: uuidv4(),
        role: message.role || 'user',
        content: message.content || '',
        chat_type: message.chat_type || ChatMessageType.NORMAL_MESSAGE_USER,
        reasoning_content: message.reasoning_content,
        create_time: (new Date()).getTime(),
    }
    messages.push(newMessage)
    emit('messageAdded', newMessage)
    scrollToBottom()
    return newMessage
}

// 删除消息
const handleDeleteMessage = async (cid: string, role: string) => {
    try {
        if (role !== "error") {
            // 调用删除API
            const resp = await deleteChatContent(props.conversationId ?? null, cid)
            showNotifyResp(resp)
        }

        // 从本地消息列表中移除
        const index = messages.findIndex(msg => msg.cid === cid)
        if (index !== -1) {
            messages.splice(index, 1)
        }

    } catch (error) {
        showNotify({
            type: 'error',
            message: '删除消息失败',
        })
    }
}

// 开始编辑消息
const handleEditMessage = (cid: string) => {
    const message = messages.find(msg => msg.cid === cid)
    if (message) {
        editingMessageId.value = cid
        editingContent.value = message.content
        originalContent.value = message.content
    }
}

// 保存编辑
const handleSaveEdit = async (message: ChatMessage) => {
    if (!editingContent.value.trim()) {
        showNotify({
            type: 'warning',
            message: '消息内容不能为空'
        })
        return
    }

    try {
        // 更新本地消息
        const updatedMessage = {
            ...message,
            content: editingContent.value.trim()
        }

        // 调用API更新
        const resp = await updateChatContent(updatedMessage)
        showNotifyResp(resp)

        if (resp.code === 200) {
            // 更新本地消息列表
            const index = messages.findIndex(msg => msg.cid === message.cid)
            if (index !== -1) {
                messages[index].content = editingContent.value.trim()
            }
            
            // 退出编辑模式
            editingMessageId.value = null
            editingContent.value = ''
            originalContent.value = ''
        }
    } catch (error) {
        showNotify({
            type: 'error',
            message: '更新消息失败'
        })
    }
}

// 取消编辑
const handleCancelEdit = () => {
    editingMessageId.value = null
    editingContent.value = ''
    originalContent.value = ''
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
                    reasoning_content: response.reasoning_content
                })
            }
            scrollToBottom()
        } else if (response.chat_type === ChatMessageType.NORMAL_MESSAGE_ASSISTANT) {
            // 完整响应 - 替换或添加完整消息
            const lastMessage = messages[messages.length - 1]
            if (lastMessage && lastMessage.role === 'assistant') {
                lastMessage.content = response.content
                lastMessage.reasoning_content = response.reasoning_content
            } else {
                addMessage({
                    role: 'assistant',
                    content: response.content,
                    chat_type: response.chat_type,
                    reasoning_content: response.reasoning_content
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
        chat_type: ChatMessageType.NORMAL_MESSAGE_USER,
        create_time: Date.now(),
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
            conversation_id: props.conversationId ?? null,
            content: message,
            chat_type: ChatMessageType.NORMAL_MESSAGE_USER,
            character: props.character ?? null
        }

        console.log('发送消息:', requestBody)

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
        let errorMessage = '未知错误'
        if (error instanceof Error) {
            errorMessage = error.message
        } else if (typeof error === 'string') {
            errorMessage = error
        }
        addMessage({
            role: 'error',
            content: `发送失败: ${errorMessage}`,
            chat_type: ChatMessageType.EXCLUDE_MESSAGE_EXCEPTION
        })
        isStreaming.value = false
    }
}

function formatTime(timestamp: number): string {
    // 创建 Date 对象，时间戳需要乘以 1000 转换为毫秒
    const date = new Date(timestamp * 1000);

    // 获取月、日和时间
    const month = date.getMonth() + 1; // 月份从 0 开始，所以加 1
    const day = date.getDate();
    const hours = date.getHours().toString().padStart(2, '0'); // 补零
    const minutes = date.getMinutes().toString().padStart(2, '0');
    const seconds = date.getSeconds().toString().padStart(2, '0');

    // 返回格式化的字符串，例如 "MM-DD HH:mm:ss"
    return `${month}-${day} ${hours}:${minutes}:${seconds}`;
}

// 清理资源
onUnmounted(() => {
    messages.length = 0
})

// 暴露方法给父组件
defineExpose({
    clearMessages: () => {
        messages.length = 0
    },
    addMessage,
    deleteMessage: handleDeleteMessage
})
</script>

<style scoped>
.chat-dialog {
    display: flex;
    flex-direction: column;
    height: 100%;
    background: #fafafa;
}

.chat-header {
    background: #fff;
    padding: 1rem;
    border-bottom: 1px solid #e0e0e0;
    text-align: center;
}

.chat-header h2 {
    margin: 0;
    color: #333;
    font-weight: 500;
    font-size: 1.2rem;
}

.chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 1rem;
    background: #fafafa;
}

.message {
    margin-bottom: 1rem;
    padding: 0.75rem;
    border-radius: 8px;
    background: #fff;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.message.user {
    margin-left: 2rem;
    border-left: 3px solid #2196f3;
}

.message.assistant {
    margin-right: 2rem;
    border-left: 3px solid #4caf50;
}

.message.error {
    background: #fff5f5;
    border-left: 3px solid #f44336;
}

.message-content {
    word-wrap: break-word;
}

.message-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
}

.role-tag {
    font-size: 0.75rem;
    color: #666;
    font-weight: 500;
}

.message-actions {
    display: flex;
    gap: 0.25rem;
    opacity: 0;
    transition: opacity 0.2s;
}

.message:hover .message-actions {
    opacity: 1;
}

.action-btn {
    background: none;
    border: 1px solid #e0e0e0;
    color: #666;
    font-size: 0.75rem;
    cursor: pointer;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    transition: all 0.2s;
}

.action-btn:hover {
    background: #f5f5f5;
}

.edit-btn:hover {
    border-color: #2196f3;
    color: #2196f3;
}

.save-btn:hover {
    border-color: #4caf50;
    color: #4caf50;
}

.cancel-btn:hover {
    border-color: #f44336;
    color: #f44336;
}

.delete-btn:hover {
    border-color: #f44336;
    color: #f44336;
}

.content {
    line-height: 1.5;
    color: #333;
}

.reasoning {
    margin-top: 0.5rem;
    padding: 0.5rem;
    background: #f8f9fa;
    border-radius: 4px;
    color: #666;
}

.message-time {
    font-size: 0.7rem;
    margin-top: 0.5rem;
    color: #999;
    text-align: right;
}

.streaming-indicator {
    display: flex;
    justify-content: center;
    padding: 1rem;
}

.typing-dots {
    display: flex;
    gap: 0.25rem;
}

.typing-dots span {
    width: 6px;
    height: 6px;
    background: #ccc;
    border-radius: 50%;
    animation: typing 1.4s infinite ease-in-out;
}

.typing-dots span:nth-child(1) { animation-delay: -0.32s; }
.typing-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
    0%, 80%, 100% { transform: scale(0); }
    40% { transform: scale(1); }
}

.chat-input {
    background: #fff;
    padding: 1rem;
    border-top: 1px solid #e0e0e0;
}

.input-group {
    display: flex;
    gap: 0.75rem;
    align-items: flex-end;
}

textarea {
    flex: 1;
    resize: vertical;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    padding: 0.75rem;
    font-family: inherit;
    font-size: 14px;
    line-height: 1.4;
    background: #fff;
    transition: border-color 0.2s;
}

textarea:focus {
    outline: none;
    border-color: #2196f3;
}

.edit-textarea {
    width: 100%;
    resize: vertical;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    padding: 0.75rem;
    font-family: inherit;
    font-size: 14px;
    line-height: 1.4;
    background: #fff;
    transition: border-color 0.2s;
}

.edit-textarea:focus {
    outline: none;
    border-color: #2196f3;
}

.send-btn {
    padding: 0.75rem 1.5rem;
    background: #2196f3;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    transition: background 0.2s;
    white-space: nowrap;
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
    width: 4px;
}

.chat-messages::-webkit-scrollbar-track {
    background: transparent;
}

.chat-messages::-webkit-scrollbar-thumb {
    background: #ddd;
    border-radius: 2px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
    background: #bbb;
}
</style>
