<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import type { AllNovelDto } from '../entity/NovelEntity';
import { getNovelById } from '../api/NovelApi';
import type { CreateConversationDto } from '../entity/ConversationEntity';
import { createConversation } from '../api/ConversationApi';

const route = useRoute();

const prompt = ref()

const currentNovel = ref<AllNovelDto>();

// 定义异步函数来获取小说数据
const fetchNovelById = async (novelId: string) => {
  currentNovel.value = await getNovelById(novelId);
  console.log('当前小说数据:', currentNovel.value);
};

const sendConversation = async () => {
  const createConversationDto = {
    role: 'user',
    content: prompt.value,
    scene: currentNovel.value!.chapter[0].scene[0].scene_id
  } as CreateConversationDto;

  // 发送请求
  await createConversation(createConversationDto);
}

onMounted(async () => {
  const novelId = route.params.id;
  await fetchNovelById(novelId as string);
});
</script>

<template>
  <el-container v-if="currentNovel">
    <el-main>
      <h1>{{ currentNovel.novel_name }}</h1>
      <p>{{ currentNovel.novel_desc }}</p>
      <div v-for="chapter in currentNovel.chapter" :key="chapter.chapter_id" :id="`chapter-${chapter.chapter_id}`">
        <h2>第{{ chapter.chapter_number }}章：{{ chapter.chapter_title }}</h2>
        <div v-for="scene in chapter.scene" :key="scene.scene_id" :id="`scene-${scene.scene_id}`">
          <h3>{{ scene.scene_name }}</h3>
          <p v-if="scene.scene_desc">{{ scene.scene_desc }}</p>
          <div v-if="scene.conversation">
            <div v-for="conv in scene.conversation" :key="conv.conversation_id">
              <p><b>{{ conv.role }}:</b> {{ conv.content }}</p>
            </div>
          </div>
        </div>
      </div>

      <el-input v-model="prompt" :autosize="{minRows: 3}" type="textarea"></el-input>
      <el-button @click="sendConversation">发送</el-button>
    </el-main>
  </el-container>
</template>

<style scoped>
</style>