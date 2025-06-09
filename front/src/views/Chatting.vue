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
import type { ChatContentResponse, Conversation } from '../entity/ConvChatEntity'
import ChatDialog from '../components/ChatDialog.vue'

// 响应式数据
const messages = reactive<ChatContentResponse[]>([])
const chatDialogRef = ref<InstanceType<typeof ChatDialog>>()

// 角色id
let character_id = useRoute().query.character_id as string
// 当前对话角色
let character = ref<CharacterCard>()
//角色所有会话
const conversations = ref<Conversation[]>([])
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

// 创建新会话
const createNewConversation = async () => {
    if (!character_id) return

    const request: Conversation = {
        character_id: parseInt(character_id),
        root_conversation_id: -1,
        conversation_id: selectedConversationId.value ?? -1,
        create_time: Math.floor(Date.now() / 1000),
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
</style>