<script lang="ts" setup>
import { onMounted, ref } from 'vue';
import type { CharacterCard } from '../entity/CharacterEntity';
import { getAllCharacters, updateCharacterById, deleteCharacterById, updateCharacterAvatarById } from '../api/characterApi';
import { ElMessage, ElMessageBox, type UploadProps } from 'element-plus';
import { Plus, Delete } from '@element-plus/icons-vue';
import { baseURL } from '../axios/axios';

const characters = ref<CharacterCard[]>([]);
const editDialogVisible = ref(false);
const currentCharacter = ref<CharacterCard | null>(null);

const fetchCharacters = async () => {
  try {
    characters.value = await getAllCharacters();
    console.log('Fetched characters:', characters.value);
  } catch (error) {
    console.error('Failed to fetch characters:', error);
    ElMessage.error('获取角色列表失败。');
  }
};

onMounted(fetchCharacters);

const handleEdit = (character: CharacterCard) => {
  // 使用深拷贝以避免在保存前修改原始数据，并确保数组存在
  const characterCopy = JSON.parse(JSON.stringify(character));
  characterCopy.trait = characterCopy.trait || [];
  characterCopy.speak = characterCopy.speak || [];
  characterCopy.distinctive = characterCopy.distinctive || [];
  currentCharacter.value = characterCopy;
  editDialogVisible.value = true;
};

const handleUpdate = async () => {
  if (!currentCharacter.value) return;
  try {
    await updateCharacterById(currentCharacter.value.id, currentCharacter.value);
    editDialogVisible.value = false;
    ElMessage.success('角色更新成功。');
    await fetchCharacters(); // 刷新列表
  } catch (error) {
    console.error('Failed to update character:', error);
    ElMessage.error('角色更新失败。');
  }
};

const handleDelete = async (characterId: number) => {
  try {
    await ElMessageBox.confirm(
      '此操作将永久删除该角色，是否继续？',
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );
    await deleteCharacterById(characterId);
    ElMessage.success('删除成功。');
    await fetchCharacters(); // 刷新列表
  } catch {
    ElMessage.info('已取消删除。');
  }
};

const handleAvatarUpload: UploadProps['httpRequest'] = async (options) => {
  if (!currentCharacter.value) return;
  try {
    await updateCharacterAvatarById(currentCharacter.value.id, options.file);
    ElMessage.success('头像更新成功。');
    // 刷新角色数据以获取新的头像URL
    const characterInDialogId = currentCharacter.value.id;
    await fetchCharacters();
    const updatedChar = characters.value.find(c => c.id === characterInDialogId);
    if (updatedChar) {
        currentCharacter.value = { ...updatedChar };
    }
  } catch (error) {
    console.error('Failed to upload avatar:', error);
    ElMessage.error('头像上传失败。');
  }
};

// Trait helpers
const addTrait = () => {
  currentCharacter.value?.trait?.push({ label: '', description: '' });
};
const removeTrait = (index: number) => {
  currentCharacter.value?.trait?.splice(index, 1);
};

// Speak helpers
const addSpeak = () => {
  currentCharacter.value?.speak?.push({ role: '', content: '', reply: '' });
};
const removeSpeak = (index: number) => {
  currentCharacter.value?.speak?.splice(index, 1);
};

// Distinctive helpers
const addDistinctive = () => {
  currentCharacter.value?.distinctive?.push({ name: '', content: '' });
};
const removeDistinctive = (index: number) => {
  currentCharacter.value?.distinctive?.splice(index, 1);
};
</script>

<template>
  <div class="container">    
    <el-row :gutter="20">
      <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="character in characters" :key="character.id">
        <el-card class="character-card">
          <template #header>
            <div class="card-header">
              <span>{{ character.name }}</span>
            </div>
          </template>
          <el-image :src="`${baseURL}/uploads/avatars/${character.avatar}`" fit="cover" class="avatar-image">
            <template #error>
              <div class="image-slot">
                <img src="../assets/header.png" alt="default avatar" class="default-avatar" />
              </div>
            </template>
          </el-image>
          <p class="character-desc">{{ character.description }}</p>

          <el-collapse class="details-collapse">
            <el-collapse-item title="查看详情" name="1">
              <div v-if="character.background_story">
                <h4>背景故事</h4>
                <p class="detail-content">{{ character.background_story }}</p>
              </div>

              <div v-if="character.trait && character.trait.length > 0">
                <h4>特征 (Trait)</h4>
                <ul class="detail-list">
                  <li v-for="(t, i) in character.trait" :key="`trait-${i}`">
                    <strong>{{ t.label }}:</strong> {{ t.description }}
                  </li>
                </ul>
              </div>

              <div v-if="character.speak && character.speak.length > 0">
                <h4>说话方式 (Speak)</h4>
                <ul class="detail-list">
                  <li v-for="(s, i) in character.speak" :key="`speak-${i}`">
                    <strong>{{ s.role }}:</strong> "{{ s.content }}" (回应: {{ s.reply }})
                  </li>
                </ul>
              </div>

              <div v-if="character.distinctive && character.distinctive.length > 0">
                <h4>显著特点 (Distinctive)</h4>
                <ul class="detail-list">
                  <li v-for="(d, i) in character.distinctive" :key="`distinctive-${i}`">
                    <strong>{{ d.name }}:</strong> {{ d.content }}
                  </li>
                </ul>
              </div>
              <div v-if="!character.background_story && (!character.trait || character.trait.length === 0) && (!character.speak || character.speak.length === 0) && (!character.distinctive || character.distinctive.length === 0)">
                <p>暂无更多详细信息。</p>
              </div>
            </el-collapse-item>
          </el-collapse>

          <div class="card-footer">
            <el-button type="primary" size="small" @click="handleEdit(character)">编辑</el-button>
            <el-button type="danger" size="small" @click="handleDelete(character.id)">删除</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="editDialogVisible" title="编辑角色" width="80%" @closed="currentCharacter = null">
      <el-form v-if="currentCharacter" :model="currentCharacter" label-position="top">
        <el-tabs type="border-card">
          <el-tab-pane label="基本信息">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="头像">
                  <el-upload
                    class="avatar-uploader"
                    action="#"
                    :show-file-list="false"
                    :http-request="handleAvatarUpload"
                  >
                    <img 
                    v-if="currentCharacter.avatar" 
                    :src="`${baseURL}/uploads/avatars/${currentCharacter.avatar}`" class="avatar" />
                    <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
                    <template #tip>
                        <div class="el-upload__tip">
                        点击上传新头像。
                        </div>
                    </template>
                  </el-upload>
                </el-form-item>
              </el-col>
              <el-col :span="16">
                <el-form-item label="名称">
                  <el-input v-model="currentCharacter.name"></el-input>
                </el-form-item>
                <el-form-item label="简短描述">
                  <el-input type="textarea" :rows="4" v-model="currentCharacter.description"></el-input>
                </el-form-item>
              </el-col>
            </el-row>
          </el-tab-pane>

          <el-tab-pane label="背景故事">
            <el-form-item label="详细背景故事">
              <el-input type="textarea" :rows="10" v-model="currentCharacter.background_story"></el-input>
            </el-form-item>
          </el-tab-pane>

          <el-tab-pane label="特征 (Trait)">
            <div v-for="(t, index) in currentCharacter.trait" :key="index" class="dynamic-form-item">
              <el-row :gutter="20" align="middle">
                <el-col :span="8"><el-input v-model="t.label" placeholder="标签 (如：性格)"></el-input></el-col>
                <el-col :span="14"><el-input v-model="t.description" placeholder="描述 (如：勇敢、善良)"></el-input></el-col>
                <el-col :span="2"><el-button type="danger" @click="removeTrait(index)" :icon="Delete" circle></el-button></el-col>
              </el-row>
            </div>
            <el-button @click="addTrait" type="primary" plain>添加特征</el-button>
          </el-tab-pane>

          <el-tab-pane label="说话方式 (Speak)">
            <div v-for="(s, index) in currentCharacter.speak" :key="index" class="dynamic-form-item">
              <el-row :gutter="20" align="middle">
                <el-col :span="6"><el-input v-model="s.role" placeholder="角色/场景"></el-input></el-col>
                <el-col :span="8"><el-input v-model="s.content" placeholder="内容/口头禅"></el-input></el-col>
                <el-col :span="8"><el-input v-model="s.reply" placeholder="回应方式"></el-input></el-col>
                <el-col :span="2"><el-button type="danger" @click="removeSpeak(index)" :icon="Delete" circle></el-button></el-col>
              </el-row>
            </div>
            <el-button @click="addSpeak" type="primary" plain>添加说话方式</el-button>
          </el-tab-pane>

          <el-tab-pane label="显著特点 (Distinctive)">
            <div v-for="(d, index) in currentCharacter.distinctive" :key="index" class="dynamic-form-item">
              <el-row :gutter="20" align="middle">
                <el-col :span="8"><el-input v-model="d.name" placeholder="特点名称 (如：外貌)"></el-input></el-col>
                <el-col :span="14"><el-input v-model="d.content" placeholder="具体内容 (如：金发碧眼)"></el-input></el-col>
                <el-col :span="2"><el-button type="danger" @click="removeDistinctive(index)" :icon="Delete" circle></el-button></el-col>
              </el-row>
            </div>
            <el-button @click="addDistinctive" type="primary" plain>添加显著特点</el-button>
          </el-tab-pane>
        </el-tabs>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleUpdate">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.container {
  padding: 20px;
}

h1 {
  font-size: 24px;
  margin-bottom: 10px;
}

p {
  margin: 5px 0;
  color: #606266;
}

.character-card {
  margin-bottom: 20px;
}

.card-header {
  font-weight: bold;
}

.avatar-image {
  width: 100%;
  height: 200px;
  background-color: #f5f7fa;
  display: flex;
  justify-content: center;
  align-items: center;
}

.image-slot {
    width: 100%;
    height: 100%;
}

.default-avatar {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.character-desc {
  font-size: 14px;
  color: #606266;
  min-height: 63px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  /* -webkit-line-clamp: 3; */
  -webkit-box-orient: vertical;
  margin-top: 10px;
}

.details-collapse {
  margin-top: 15px;
}

.details-collapse h4 {
  font-size: 15px;
  font-weight: bold;
  margin-top: 12px;
  margin-bottom: 8px;
  color: #303133;
}

.details-collapse h4:first-child {
  margin-top: 0;
}

.detail-content {
  white-space: pre-wrap;
  font-size: 14px;
  color: #606266;
  line-height: 1.5;
}

.detail-list {
  list-style-type: none;
  padding-left: 0;
  font-size: 14px;
  color: #606266;
}

.detail-list li {
  margin-bottom: 5px;
  padding-left: 10px;
  border-left: 2px solid #e4e7ed;
}

.card-footer {
  margin-top: 15px;
  text-align: right;
}

.avatar-uploader .avatar {
  width: 120px;
  height: 120px;
  display: block;
}

.dynamic-form-item {
  padding: 10px;
  margin-bottom: 10px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}
</style>

<style>
/* Global style for el-upload */
.avatar-uploader .el-upload {
  border: 1px dashed var(--el-border-color);
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration-fast);
}

.avatar-uploader .el-upload:hover {
  border-color: var(--el-color-primary);
}

.el-icon.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 120px;
  height: 120px;
  text-align: center;
}
</style>