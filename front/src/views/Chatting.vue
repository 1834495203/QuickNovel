<template>
    <div class="chat-container">
        <ChatDialog :character="character" :conversation-id="selectedConversationId" :initial-messages="messages"
            @message-added="onMessageAdded" ref="chatDialogRef">
            <template #header>
                <div v-if="character" class="character-info">
                    <span>聊天对象：{{ character.name }}</span>
                    <div class="conversation-selector">
                        <label for="conversation-select">会话选择：</label>
                        <select id="conversation-select" v-model="selectedConversationId" @change="switchConversation"
                            class="conversation-select">
                            <option v-for="conv in conversations" :key="conv.conversation_id"
                                :value="conv.conversation_id">
                                会话 {{ conv.conversation_id }} ({{ formatDate(conv.create_time) }})
                            </option>
                        </select>
                        <button @click="createNewConversation" class="new-conversation-btn">
                            新建会话
                        </button>
                    </div>
                </div>
                <div v-else><span>无角色对话</span></div>
            </template>

            <template #messages="{ isStreaming, messages }">
                <div class="messages-list">
                    <div v-for="msg in messages" :key="msg.cid" :class="['message-item', `message-${msg.role}`]">
                        <div class="message-avatar">
                            <span class="role-indicator">{{ getRoleDisplay(msg.role) }}</span>
                        </div>

                        <div class="message-bubble">
                            <div class="message-text">{{ msg.content }}</div>

                            <div v-if="msg.reasoning_content" class="reasoning-text">
                                <span class="reasoning-label">推理:</span>
                                {{ msg.reasoning_content }}
                            </div>

                            <div class="message-time">
                                {{ formatTime(msg.create_time ?? 0) }}
                            </div>
                        </div>
                    </div>

                    <div v-if="isStreaming" class="streaming-message">
                        <div class="message-avatar">
                            <span class="role-indicator">AI</span>
                        </div>
                        <div class="typing-indicator">
                            <div class="typing-dots">
                                <span></span>
                                <span></span>
                                <span></span>
                            </div>
                        </div>
                    </div>
                </div>
            </template>
        </ChatDialog>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { showNotify } from '../utils/notify'
import { getConversationsByCharacter, getChatsByConversation, createConversationWithNotify } from '../api/ConvChatApi'
import { getCharacterById } from '../api/characterApi'
import type { CharacterCard } from '../entity/CharacterEntity'
import type { ChatContentResponse, ConversationResponse, CreateConversationRequest } from '../entity/ConvChatEntity'
import ChatDialog from '../components/ChatDialog.vue'

// 响应式数据
const messages = reactive<ChatContentResponse[]>([])
const chatDialogRef = ref<InstanceType<typeof ChatDialog>>()

// 角色id
let character_id = useRoute().query.character_id as string
// 当前对话角色
let character = ref<CharacterCard>()
//角色所有会话
const conversations = ref<ConversationResponse[]>([])
// 当前选中的会话ID
const selectedConversationId = ref<number | null>(null)

onMounted(async () => {
    // 初始化检查路由参数
    if (character_id) {
        showNotify({
            type: 'success',
            message: `与角色对话, 当前角色ID: ${character_id}`,
            duration: 3000
        })
        // 获取角色信息
        character.value = await getCharacterById(character_id)

        // 根据角色获取对应全部会话
        conversations.value = await getConversationsByCharacter(character_id)
    } else {
        showNotify({
            type: 'info',
            message: `无角色对话`,
            duration: 3000
        })
    }
    if (conversations.value.length === 0) {
        // 如果没有会话，创建一个新的会话
        await createNewConversation()
    } else {
        // 选择最新的会话（假设ID越大越新）
        const latestConversation = conversations.value.reduce((latest, current) =>
            current.conversation_id > latest.conversation_id ? current : latest
        )
        selectedConversationId.value = latestConversation.conversation_id
    }
    await loadConversationMessages(selectedConversationId.value ?? null)
})

const getRoleDisplay = (role: string): string => {
    const roleMap: Record<string, string> = {
        'user': '用户',
        'assistant': 'AI',
        'error': '错误'
    }
    return roleMap[role] || role
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

// 创建新会话
const createNewConversation = async () => {
    if (!character_id) return

    const request: CreateConversationRequest = {
        character_id: parseInt(character_id)
    }

    const newConversation = await createConversationWithNotify(request)
    if (newConversation) {
        conversations.value.push(newConversation)
        selectedConversationId.value = newConversation.conversation_id
        // 清空当前消息
        messages.length = 0
        chatDialogRef.value?.clearMessages()
        showNotify({
            type: 'success',
            message: '新会话创建成功',
            duration: 2000
        })
    }
}

// 切换会话
const switchConversation = async () => {
    if (selectedConversationId.value) {
        await loadConversationMessages(selectedConversationId.value)
    }
}

// 加载指定会话的消息
const loadConversationMessages = async (conversationId: number | string | null) => {
    try {
        // 清空当前消息
        messages.length = 0

        // 获取会话消息
        const conversationMessages = await getChatsByConversation(conversationId)
        messages.push(...conversationMessages)
    } catch (error) {
        console.error('加载会话消息失败:', error)
        showNotify({
            type: 'error',
            message: '加载会话消息失败',
            duration: 3000
        })
    }
}

// 格式化日期
const formatDate = (timestamp: number) => {
    const date = new Date(timestamp * 1000)
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    })
}

// 处理消息添加事件
const onMessageAdded = (message: ChatContentResponse) => {
    // 可以在这里处理消息添加后的逻辑，比如保存到数据库等
    console.log('新消息添加:', message)
}
</script>

<style scoped>
.chat-container {
    display: flex;
    flex-direction: column;
    height: 100vh;
    max-width: 1100px;
    margin: 0 auto;
    border: 1px solid #e1e5e9;
    border-radius: 8px;
    overflow: hidden;
}

/* 移除原有的 chat-header 相关样式，因为已经移到 ChatDialog 组件中 */
.messages-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
    padding: 16px;
}

.message-item {
    display: flex;
    gap: 12px;
    max-width: 85%;
}

.message-user {
    align-self: flex-end;
    flex-direction: row-reverse;
}

.message-assistant,
.message-error {
    align-self: flex-start;
}

.message-avatar {
    flex-shrink: 0;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.role-indicator {
    font-size: 12px;
    font-weight: 500;
    padding: 4px 8px;
    border-radius: 12px;
    background: #f0f0f0;
    color: #666;
}

.message-user .role-indicator {
    background: #007bff;
    color: white;
}

.message-assistant .role-indicator {
    background: #28a745;
    color: white;
}

.message-error .role-indicator {
    background: #dc3545;
    color: white;
}

.message-bubble {
    flex: 1;
    padding: 12px 16px;
    border-radius: 18px;
    position: relative;
}

.message-user .message-bubble {
    background: #007bff;
    color: white;
    border-bottom-right-radius: 4px;
}

.message-assistant .message-bubble {
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    border-bottom-left-radius: 4px;
}

.message-error .message-bubble {
    background: #f8d7da;
    border: 1px solid #f5c6cb;
    color: #721c24;
}

.message-text {
    line-height: 1.4;
    word-wrap: break-word;
}

.reasoning-text {
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px solid rgba(255, 255, 255, 0.2);
    font-size: 13px;
    opacity: 0.9;
}

.message-assistant .reasoning-text {
    border-top-color: #dee2e6;
}

.reasoning-label {
    font-weight: 500;
    margin-right: 4px;
}

.message-time {
    font-size: 11px;
    margin-top: 4px;
    opacity: 0.7;
}

.streaming-message {
    display: flex;
    gap: 12px;
    align-self: flex-start;
}

.typing-indicator {
    padding: 12px 16px;
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 18px;
    border-bottom-left-radius: 4px;
}

.typing-dots {
    display: flex;
    gap: 4px;
}

.typing-dots span {
    width: 6px;
    height: 6px;
    background: #6c757d;
    border-radius: 50%;
    animation: typing 1.4s infinite ease-in-out;
}

.typing-dots span:nth-child(1) {
    animation-delay: -0.32s;
}

.typing-dots span:nth-child(2) {
    animation-delay: -0.16s;
}

@keyframes typing {

    0%,
    80%,
    100% {
        transform: scale(0.8);
        opacity: 0.4;
    }

    40% {
        transform: scale(1);
        opacity: 1;
    }
}
</style>