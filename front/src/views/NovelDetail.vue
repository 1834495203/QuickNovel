<script lang="ts" setup>
import { ref, onMounted, nextTick } from 'vue';
import { useRoute } from 'vue-router';
import type { AllNovelDto } from '../entity/NovelEntity';
import { getNovelById } from '../api/NovelApi';
import type { CreateConversationDto } from '../entity/ConversationEntity';
import { createConversation } from '../api/ConversationApi';

const route = useRoute();

const prompt = ref('');

const currentNovel = ref<AllNovelDto>();

// 定义异步函数来获取小说数据
const fetchNovelById = async (novelId: string) => {
  currentNovel.value = await getNovelById(novelId);
  console.log('当前小说数据:', currentNovel.value);
  // 数据加载后，确保章节和情景的 ID 存在，以便平滑滚动
};

const sendConversation = async () => {
  if (!currentNovel.value || !prompt.value) {
    return;
  }

  const chapters = currentNovel.value.chapter;
  if (!chapters || chapters.length === 0) {
    return;
  }
  const lastChapter = chapters[chapters.length - 1];

  const scenes = lastChapter.scene;
  if (!scenes || scenes.length === 0) {
    return;
  }
  const lastScene = scenes[scenes.length - 1];

  if (!lastScene.conversation) {
    lastScene.conversation = [];
  }

  const userPrompt = prompt.value;
  prompt.value = '';

  // 在本地添加用户消息（作为阅读历史的一部分，但可以视觉上弱化）
  lastScene.conversation.push({
    role: 'user',
    content: userPrompt,
  });

  // 添加一个占位符用于显示助手的流式响应
  const assistantResponse = ref({
    role: 'assistant',
    content: '',
  });
  lastScene.conversation.push(assistantResponse.value);

  const createConversationDto = {
    role: 'user',
    content: userPrompt,
    scene: lastScene.scene_id,
    novel: currentNovel.value.novel_id, // 关联小说ID
  } as CreateConversationDto;

  await createConversation(
    createConversationDto,
    (data) => {
      console.log('对话流数据:', data);
      assistantResponse.value.content += data;
      // 每次有新数据时，滚动到底部，确保流式内容可见
      nextTick(() => {
        const mainContent = document.querySelector('.novel-content-main');
        if (mainContent) {
          mainContent.scrollTop = mainContent.scrollHeight;
        }
      });
    },
    () => {
      // 流结束时的处理
      console.log('流已结束');
    },
    (error) => {
      console.error('对话发送错误:', error);
      assistantResponse.value.content = `发生错误: ${error.message}`;
    }
  );
};

// 平滑滚动到指定元素
const scrollToElement = (id: string) => {
  const element = document.getElementById(id);
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
};

onMounted(async () => {
  const novelId = route.params.id;
  await fetchNovelById(novelId as string);
});
</script>

<template>
  <el-container v-if="currentNovel" class="novel-page-container">
    <el-header class="novel-header">
      <h1 class="novel-title">{{ currentNovel.novel_name }}</h1>
      <p class="novel-desc">{{ currentNovel.novel_desc }}</p>
    </el-header>

    <el-container class="content-with-aside">
      <el-aside width="250px" class="novel-aside">
        <h3 class="aside-title">目录</h3>
        <el-menu :default-openeds="['chapter-0']" class="novel-menu">
          <el-sub-menu
            v-for="(chapter, cIndex) in currentNovel.chapter"
            :key="chapter.chapter_id"
            :index="`chapter-${cIndex}`"
          >
            <template #title>
              <span @click="scrollToElement(`chapter-${chapter.chapter_id}`)">
                第{{ chapter.chapter_number }}章：{{ chapter.chapter_title }}
              </span>
            </template>
            <el-menu-item
              v-for="scene in chapter.scene"
              :key="scene.scene_id"
              :index="`scene-${scene.scene_id}`"
              @click="scrollToElement(`scene-${scene.scene_id}`)"
            >
              {{ scene.scene_name }}
            </el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-aside>

      <el-main class="novel-content-main">
        <div v-for="chapter in currentNovel.chapter" :key="chapter.chapter_id" class="chapter-section" :id="`chapter-${chapter.chapter_id}`">
          <h2 class="chapter-title-main">第{{ chapter.chapter_number }}章：{{ chapter.chapter_title }}</h2>
          <p v-if="chapter.chapter_desc" class="chapter-desc-main">{{ chapter.chapter_desc }}</p>

          <div v-for="scene in chapter.scene" :key="scene.scene_id" class="scene-block" :id="`scene-${scene.scene_id}`">
            <h3 class="scene-name-main">{{ scene.scene_name }}</h3>
            <p v-if="scene.scene_desc" class="scene-desc-main">{{ scene.scene_desc }}</p>

            <div v-if="scene.conversation" class="conversation-display">
              <div v-for="(conv, index) in scene.conversation" :key="index" :class="['conversation-item', conv.role]">
                <p v-if="conv.role === 'assistant'" class="assistant-content">
                  {{ conv.content }}
                </p>
                <p v-else-if="conv.role === 'user'" class="user-content">
                  <span class="user-label">你的输入:</span> {{ conv.content }}
                </p>
                <p v-else class="other-content">
                  <b>{{ conv.role }}:</b> {{ conv.content }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </el-main>
    </el-container>

    <el-footer class="novel-footer">
      <el-input
        v-model="prompt"
        :autosize="{ minRows: 3, maxRows: 6 }"
        type="textarea"
        placeholder="输入你的想法，推动故事发展..."
        class="chat-input"
        @keyup.enter.native="sendConversation"
      ></el-input>
      <el-button type="primary" @click="sendConversation" class="send-button" :disabled="!prompt.trim()">发送</el-button>
    </el-footer>
  </el-container>

  <el-empty v-else description="小说加载中或数据为空..."></el-empty>
</template>

<style scoped>
/* 全局容器 */
.novel-page-container {
  min-height: 100vh;
  background-color: #f5f7fa; /* 整体背景色 */
}

/* 头部样式 */
.novel-header {
  background-color: #ffffff;
  padding: 20px 40px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  text-align: center;
  border-bottom: 1px solid #ebeef5;
}

.novel-title {
  font-size: 2.5em;
  color: #303133;
  margin-bottom: 8px;
  font-weight: bold;
  letter-spacing: 1px;
}

.novel-desc {
  font-size: 1.2em;
  color: #606266;
  line-height: 1.6;
  margin-top: 0;
}

/* 内容区域，包含侧边栏和主内容 */
.content-with-aside {
  flex: 1; /* 占据剩余垂直空间 */
}

/* 侧边栏样式 */
.novel-aside {
  background-color: #ffffff;
  padding: 20px 0;
  border-right: 1px solid #ebeef5;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.03);
  overflow-y: auto; /* 侧边栏内容可滚动 */
}

.aside-title {
  font-size: 1.3em;
  color: #303133;
  padding: 0 20px 15px;
  margin-top: 0;
  border-bottom: 1px solid #e4e7ed;
  font-weight: bold;
}

.novel-menu {
  border-right: none; /* 移除 Element UI 默认的右侧边框 */
}

.novel-menu .el-sub-menu__title span,
.novel-menu .el-menu-item {
  font-size: 1em;
  color: #606266;
  line-height: 40px; /* 增加行高，点击区域更大 */
}

.novel-menu .el-sub-menu__title:hover,
.novel-menu .el-menu-item:hover {
  background-color: #ecf5ff; /* 悬停背景色 */
  color: #409eff; /* 悬停字体颜色 */
}

/* 主内容区样式 */
.novel-content-main {
  padding: 30px 40px;
  background-color: #ffffff;
  overflow-y: auto; /* 主内容区可滚动 */
  line-height: 1.8;
  font-size: 1.1em;
  color: #303133;
}

/* 章节区块 */
.chapter-section {
  margin-bottom: 40px;
  padding-bottom: 20px;
  border-bottom: 1px dashed #e4e7ed; /* 章节之间用虚线分隔 */
}

.chapter-section:last-child {
  border-bottom: none; /* 最后一个章节没有底边框 */
}

.chapter-title-main {
  font-size: 2em;
  color: #212121;
  margin-top: 0;
  margin-bottom: 15px;
  font-weight: bold;
  text-align: center; /* 章节标题居中 */
  padding-top: 20px;
}

.chapter-desc-main {
  font-size: 1em;
  color: #909399;
  line-height: 1.5;
  text-align: center;
  margin-bottom: 30px;
}

/* 情景区块 */
.scene-block {
  margin-top: 30px;
  padding: 25px;
  background-color: #f9f9f9; /* 情景背景色略浅 */
  border-radius: 8px;
  box-shadow: 0 1px 5px rgba(0, 0, 0, 0.05);
}

.scene-name-main {
  font-size: 1.6em;
  color: #333;
  margin-top: 0;
  margin-bottom: 12px;
  font-weight: 600;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.scene-desc-main {
  font-size: 0.95em;
  color: #777;
  line-height: 1.6;
  margin-bottom: 25px;
}

/* 对话内容显示 */
.conversation-display {
  padding: 15px 0;
  border-top: 1px dashed #e9e9eb; /* 对话区域顶部虚线 */
  margin-top: 20px;
}

.conversation-item {
  margin-bottom: 15px;
  line-height: 1.7;
}

.assistant-content {
  font-size: 1.1em;
  color: #2c3e50; /* 深色文字，突出显示 */
  background-color: #f0f4f7; /* 浅蓝灰色背景，区分于普通阅读内容 */
  padding: 12px 18px;
  border-radius: 6px;
  border-left: 4px solid #409eff; /* 左侧蓝色边框 */
  margin-left: 0; /* 移除默认段落缩进 */
}

.user-content {
  font-size: 0.95em;
  color: #909399; /* 灰色，弱化显示 */
  padding: 8px 12px;
  background-color: #fdfdfd;
  border-left: 2px solid #dcdfe6;
  border-radius: 4px;
  margin-left: 0; /* 移除默认段落缩进 */
}

.user-label {
  font-weight: bold;
  color: #b0b0b0; /* 标签颜色更浅 */
  margin-right: 5px;
}

.other-content {
  font-size: 1em;
  color: #606266;
}

/* 底部输入区域 */
.novel-footer {
  background-color: #ffffff;
  padding: 20px 40px;
  border-top: 1px solid #ebeef5;
  display: flex;
  align-items: flex-end; /* 底部对齐 */
  gap: 15px;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.05);
}

.chat-input {
  flex: 1;
  font-size: 1em;
}

.send-button {
  height: 40px;
  padding: 0 25px;
  font-size: 1.1em;
}

/* ElEmpty 样式 */
.el-empty {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
}
</style>