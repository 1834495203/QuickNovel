<script lang="ts" setup>
import { onMounted, ref, reactive } from 'vue';
import { useRoute } from 'vue-router';
import { getNovelById } from '../api/NovelApi';
import { createChapter } from '../api/ChapterApi';
import { createScene } from '../api/SceneApi';
import type { AllNovelDto } from '../entity/NovelEntity';
import type { AllChapterDto } from '../entity/ChapterEntity';
import { ElMessage } from 'element-plus';

const route = useRoute();
const novel = ref<AllNovelDto | null>(null);

// 章节相关
const chapterDialogVisible = ref(false);
const chapterForm = reactive({
  chapter_title: '',
  chapter_desc: ''
});

// 情景相关
const sceneDialogVisible = ref(false);
const currentChapterId = ref<number | null>(null);
const sceneForm = reactive({
  scene_name: '',
  scene_desc: ''
});

const fetchNovelDetail = async () => {
  const novelId = route.params.id as string;
  if (novelId) {
    try {
      const response = await getNovelById(novelId);
      novel.value = response;
    } catch (error) {
      console.error('Failed to fetch novel details:', error);
    }
  }
};

// 创建新章节
const handleCreateChapter = async () => {
  if (!novel.value) return;
  
  try {
    await createChapter({
      novel_id: novel.value.novel_id,
      chapter_title: chapterForm.chapter_title,
      chapter_desc: chapterForm.chapter_desc
    });
    
    ElMessage.success('章节创建成功');
    chapterDialogVisible.value = false;
    resetChapterForm();
    await fetchNovelDetail(); // 重新加载数据
  } catch (error) {
    ElMessage.error('章节创建失败');
    console.error('Failed to create chapter:', error);
  }
};

// 打开创建情景对话框
const openSceneDialog = (chapterId: number) => {
  currentChapterId.value = chapterId;
  sceneDialogVisible.value = true;
};

// 创建新情景
const handleCreateScene = async () => {
  if (!currentChapterId.value) return;
  
  try {
    await createScene({
      chapter_id: currentChapterId.value,
      scene_name: sceneForm.scene_name,
      scene_desc: sceneForm.scene_desc
    });
    
    ElMessage.success('情景创建成功');
    sceneDialogVisible.value = false;
    resetSceneForm();
    await fetchNovelDetail(); // 重新加载数据
  } catch (error) {
    ElMessage.error('情景创建失败');
    console.error('Failed to create scene:', error);
  }
};

// 重置表单
const resetChapterForm = () => {
  chapterForm.chapter_title = '';
  chapterForm.chapter_desc = '';
};

const resetSceneForm = () => {
  sceneForm.scene_name = '';
  sceneForm.scene_desc = '';
  currentChapterId.value = null;
};

onMounted(fetchNovelDetail);
</script>

<template>
  <div v-loading="!novel" class="novel-detail-container">
    <el-card v-if="novel">
      <template #header>
        <div class="card-header">
          <h1>{{ novel.novel_name }}</h1>
        </div>
      </template>
      <p class="novel-description">{{ novel.novel_desc || '暂无简介' }}</p>
      <el-divider />
      <div class="section-header">
        <h2>章节列表</h2>
        <el-button type="primary" @click="chapterDialogVisible = true">新增章节</el-button>
      </div>
      <el-collapse v-if="novel.chapter && novel.chapter.length > 0" accordion>
        <el-collapse-item
          v-for="chapter in novel.chapter"
          :key="(chapter as AllChapterDto).chapter_id"
          :title="(chapter as AllChapterDto).chapter_title"
          :name="(chapter as AllChapterDto).chapter_id"
        >
          <div class="chapter-content">
            <p v-if="(chapter as AllChapterDto).chapter_desc" class="chapter-desc">
              {{ (chapter as AllChapterDto).chapter_desc }}
            </p>
            <div class="scene-section">
              <div class="scene-header-actions">
                <h3>情景列表</h3>
                <el-button size="small" @click="openSceneDialog((chapter as AllChapterDto).chapter_id)">新增情景</el-button>
              </div>
              <el-timeline v-if="(chapter as AllChapterDto).scene && (chapter as AllChapterDto).scene.length > 0" style="padding-left: 10px;">
                <el-timeline-item
                  v-for="scene in (chapter as AllChapterDto).scene"
                  :key="scene.scene_id"
                  placement="top"
                >
                  <el-card>
                    <template #header>
                      <div class="scene-header">
                        <span>{{ scene.scene_name }}</span>
                      </div>
                    </template>
                    <p>{{ scene.scene_desc }}</p>
                  </el-card>
                </el-timeline-item>
              </el-timeline>
              <el-empty v-else description="本章暂无情景"></el-empty>
            </div>
          </div>
        </el-collapse-item>
      </el-collapse>
      <el-empty v-else description="暂无章节"></el-empty>
    </el-card>

    <!-- 创建章节对话框 -->
    <el-dialog v-model="chapterDialogVisible" title="新增章节" width="500px">
      <el-form :model="chapterForm" label-width="80px">
        <el-form-item label="章节标题" required>
          <el-input v-model="chapterForm.chapter_title" placeholder="请输入章节标题"></el-input>
        </el-form-item>
        <el-form-item label="章节描述">
          <el-input
            v-model="chapterForm.chapter_desc"
            type="textarea"
            :rows="4"
            placeholder="请输入章节描述（可选）"
          ></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="chapterDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreateChapter">确定</el-button>
      </template>
    </el-dialog>

    <!-- 创建情景对话框 -->
    <el-dialog v-model="sceneDialogVisible" title="新增情景" width="500px">
      <el-form :model="sceneForm" label-width="80px">
        <el-form-item label="情景名称" required>
          <el-input v-model="sceneForm.scene_name" placeholder="请输入情景名称"></el-input>
        </el-form-item>
        <el-form-item label="情景描述">
          <el-input
            v-model="sceneForm.scene_desc"
            type="textarea"
            :rows="4"
            placeholder="请输入情景描述"
          ></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="sceneDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreateScene">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.novel-detail-container {
  padding: 20px;
  min-height: 200px;
}

.card-header h1 {
  margin: 0;
  font-size: 24px;
}

.novel-description {
  font-size: 16px;
  color: #606266;
  line-height: 1.6;
}

.chapter-content {
  padding: 10px 0;
}

.chapter-desc {
  padding: 0 20px 15px;
  font-style: italic;
  color: #606266;
}

.scene-header {
  font-weight: bold;
}

.el-card p {
  margin: 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  margin: 0;
}

.scene-section {
  margin-top: 20px;
}

.scene-header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.scene-header-actions h3 {
  margin: 0;
  font-size: 18px;
}
</style>
