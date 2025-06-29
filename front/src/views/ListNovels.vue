<script lang="ts" setup>
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { getAllNovels } from '../api/NovelApi';
import type { NovelEntity } from '../entity/NovelEntity';

const novels = ref<NovelEntity[]>([]);
const router = useRouter();

const fetchNovels = async () => {
  const response = await getAllNovels();
  novels.value = response;
};

const goToNovelDetail = (novelId: number) => {
  router.push(`/novel/${novelId}`);
};

onMounted(fetchNovels);
</script>

<template>
  <div class="novel-list-container">
    <el-row :gutter="20">
      <el-col
        v-for="novel in novels"
        :key="novel.novel_id"
        :xs="24"
        :sm="12"
        :md="8"
        :lg="6"
        :xl="4"
        class="novel-col"
      >
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>{{ novel.novel_name }}</span>
            </div>
          </template>
          <p class="novel-desc">{{ novel.novel_desc || '暂无简介' }}</p>
          <div class="bottom">
            <time class="time">{{ new Date(novel.create_time).toLocaleDateString() }}</time>
            <el-button text class="button" @click="goToNovelDetail(novel.novel_id)">查看详情</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.novel-list-container {
  padding: 20px;
}

.novel-col {
  margin-bottom: 20px;
}

.card-header {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.novel-desc {
  font-size: 14px;
  color: #606266;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  /* -webkit-line-clamp: 3; */
  overflow: hidden;
  text-overflow: ellipsis;
  min-height: 63px; /* For 3 lines of text */
  margin: 0 0 10px 0;
}

.bottom {
  margin-top: 13px;
  line-height: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.time {
  font-size: 13px;
  color: #999;
}

.button {
  padding: 0;
  min-height: auto;
}
</style>