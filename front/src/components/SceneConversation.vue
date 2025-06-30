<script lang="ts" setup>
import { ref, nextTick, onMounted, onUpdated } from 'vue';
import type { CreateConversationDto } from '../entity/ConversationEntity';
import type { AllSceneDto } from '../entity/SceneEntity';
import type { AllChapterDto } from '../entity/ChapterEntity';
import { ElMessage } from 'element-plus';

interface Props {
  selectedScene: AllSceneDto;
  selectedChapter: AllChapterDto;
  isLatestScene: boolean;
  onConversationCreated?: () => void;
}

const props = defineProps<Props>();

const chatInput = ref('');
const conversationListRef = ref<HTMLElement>();
const isLoading = ref(false);

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (conversationListRef.value) {
      conversationListRef.value.scrollTop = conversationListRef.value.scrollHeight;
    }
  });
};

// 创建新对话
const handleSendMessage = async () => {
  if (!chatInput.value.trim() || !props.selectedScene || isLoading.value) return;

  const messageContent = chatInput.value.trim();
  isLoading.value = true;

  // 乐观地将用户消息添加到UI
  props.selectedScene.conversation!.push({
    role: 'user',
    content: messageContent,
    conversation_id: `temp-user-${Date.now()}`,
    create_time: new Date().toLocaleString(),
    sender_character: '你'
  } as any);
  chatInput.value = '';
  scrollToBottom();

  // 为AI响应添加占位符
  const aiMessage = {
    role: 'assistant',
    content: '',
    create_time: new Date().toLocaleString(),
    sender_character: 'AI助手'
  };
  props.selectedScene.conversation!.push(aiMessage as any);
  scrollToBottom();

  try {
    // 注意：请将此URL替换为您的实际后端流式API端点
    const response = await fetch('http://localhost:9000/api/conversation/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream'
      },
      body: JSON.stringify({
        role: 'user',
        content: messageContent,
        scene: props.selectedScene.scene_id
      } as CreateConversationDto)
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
        break;
      }

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n\n');
      buffer = lines.pop() || ''; // 保留不完整的行到缓冲区

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.substring(6);
          aiMessage.content += data;
          scrollToBottom();
        } else if (line.startsWith('event: end')) {
          console.log('接收到流结束事件。');
        }
      }
    }
  } catch (err) {
    console.error('发送消息或处理流时失败:', err);
    ElMessage.error('对话生成失败');
  } finally {
    isLoading.value = false;
    // 通知父组件刷新数据以获取持久化的对话
    if (props.onConversationCreated) {
      props.onConversationCreated();
    }
  }
};

// 处理键盘事件
const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    handleSendMessage();
  }
};

// 组件挂载和更新时滚动到底部
onMounted(scrollToBottom);
onUpdated(scrollToBottom);
</script>

<template>
  <div class="scene-conversation">
    <!-- 面包屑导航 -->
    <div class="conversation-header">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item>{{ selectedChapter.chapter_title }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ selectedScene.scene_name }}</el-breadcrumb-item>
      </el-breadcrumb>
      
      <!-- 情景描述 -->
      <div class="scene-description" v-if="selectedScene.scene_desc">
        <el-text type="info" size="small">{{ selectedScene.scene_desc }}</el-text>
      </div>
    </div>

    <el-divider style="margin: 16px 0;" />

    <!-- 对话区域 -->
    <div class="conversation-container">
      <div class="conversation-list" ref="conversationListRef">
        <div v-if="selectedScene.conversation && selectedScene.conversation.length > 0">
          <div 
            v-for="(convo, index) in selectedScene.conversation" 
            :key="convo.conversation_id || index"
            class="conversation-item"
            :class="{ 
              'user-message': convo.role === 'user', 
              'ai-message': convo.role === 'assistant' 
            }"
          >
            <div class="message-avatar">
              <el-avatar 
                :size="32" 
                :style="{ 
                  backgroundColor: convo.role === 'user' ? '#409EFF' : '#67C23A' 
                }"
              >
                {{ convo.role === 'user' ? '你' : 'AI' }}
              </el-avatar>
            </div>
            <div class="message-body">
              <div class="message-header">
                <span class="sender-name">
                  {{ convo.sender_character || (convo.role === 'user' ? '你' : 'AI助手') }}
                </span>
                <span class="message-time">{{ convo.create_time }}</span>
              </div>
              <div class="message-content">{{ convo.content }}</div>
            </div>
          </div>
        </div>
        <el-empty v-else description="还没有对话，开始你的冒险吧！" :image-size="80" />
      </div>

      <!-- 输入区域 - 只在最新情景中显示 -->
      <div v-if="isLatestScene" class="chat-input-area">
        <div class="input-container">
          <el-input
            v-model="chatInput"
            placeholder="描述你的行动或说出你的对话..."
            type="textarea"
            :rows="3"
            :disabled="isLoading"
            @keydown="handleKeydown"
            resize="none"
            maxlength="500"
            show-word-limit
          />
          <div class="input-actions">
            <el-button 
              type="primary" 
              @click="handleSendMessage" 
              :loading="isLoading"
              :disabled="!chatInput.trim()"
            >
              {{ isLoading ? '发送中...' : '发送' }}
            </el-button>
          </div>
        </div>
        <div class="input-hint">
          <el-text type="info" size="small">
            <el-icon><i class="el-icon-info"></i></el-icon>
            按 Enter 发送，Shift + Enter 换行
          </el-text>
        </div>
      </div>
      
      <!-- 非最新情景的提示 -->
      <div v-else class="readonly-notice">
        <el-alert
          title="历史情景"
          description="这是历史情景，仅供查看。请选择最新章节的情景来继续对话。"
          type="info"
          :closable="false"
          show-icon
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.scene-conversation {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.conversation-header {
  flex-shrink: 0;
}

.scene-description {
  margin-top: 8px;
  padding: 8px 12px;
  background-color: var(--el-fill-color-lighter);
  border-radius: 6px;
  line-height: 1.5;
}

.conversation-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.conversation-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 8px;
  margin-bottom: 16px;
}

.conversation-item {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  animation: fadeIn 0.3s ease-in;
}

.conversation-item.user-message {
  flex-direction: row-reverse;
}

.conversation-item.user-message .message-body {
  text-align: right;
}

.conversation-item.user-message .message-header {
  justify-content: flex-end;
}

.message-avatar {
  flex-shrink: 0;
}

.message-body {
  flex: 1;
  min-width: 0;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.sender-name {
  font-weight: 500;
  color: var(--el-text-color-primary);
  font-size: 14px;
}

.message-time {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.message-content {
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
  max-width: 70%;
}

.user-message .message-content {
  background-color: var(--el-color-primary);
  color: white;
  margin-left: auto;
}

.ai-message .message-content {
  background-color: var(--el-fill-color);
  color: var(--el-text-color-primary);
}

.chat-input-area {
  flex-shrink: 0;
  padding: 16px;
  border-top: 1px solid var(--el-border-color-light);
  background-color: var(--el-bg-color);
}

.input-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-actions {
  display: flex;
  justify-content: flex-end;
}

.input-hint {
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.readonly-notice {
  flex-shrink: 0;
  padding: 16px;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .message-content {
    max-width: 85%;
  }
  
  .conversation-item {
    margin-bottom: 12px;
  }
  
  .chat-input-area {
    padding: 12px;
  }
}

/* 滚动条样式 */
.conversation-list::-webkit-scrollbar {
  width: 6px;
}

.conversation-list::-webkit-scrollbar-track {
  background: var(--el-fill-color-lighter);
  border-radius: 3px;
}

.conversation-list::-webkit-scrollbar-thumb {
  background: var(--el-border-color);
  border-radius: 3px;
}

.conversation-list::-webkit-scrollbar-thumb:hover {
  background: var(--el-border-color-dark);
}
</style>