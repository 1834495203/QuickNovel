<template>
  <div class="character-create">
    <h1>创建新角色</h1>
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label>角色名称</label>
        <input v-model="character.name" type="text" class="form-input" required />
      </div>
      <div class="form-group">
        <label>头像</label>
        <input type="file" @change="handleAvatarUpload" accept="image/*" class="form-input" />
        <img v-if="character.avatar" :src="character.avatar" alt="Avatar Preview" class="avatar-preview" />
      </div>
      <div class="form-group">
        <label>描述</label>
        <textarea v-model="character.description" class="form-textarea" />
      </div>
      <div class="form-group">
        <label>性格特点</label>
        <ul>
          <li v-for="(trait, idx) in character!.traits" :key="idx" class="trait-list-item-edit">
            <input v-model="trait.label" type="text" class="form-input" placeholder="特点标签" />
            <textarea v-model="trait.description" class="form-textarea" placeholder="特点描述" />
            <button type="button" class="remove-button" @click="removeTrait(idx)">移除</button>
          </li>
        </ul>
        <button type="button" class="add-button" @click="addTrait">添加性格特点</button>
      </div>
      <div class="form-group">
        <label>背景故事</label>
        <textarea v-model="character!.background_story" class="form-textarea" />
      </div>
      <div class="form-group">
        <label>说话风格</label>
        <div>
          <div v-for="(style, idx) in character!.speakings" :key="idx" class="list-item-edit">
            <input v-model="style.role" type="text" class="form-input" placeholder="角色" />
            <textarea v-model="style.content" class="form-textarea" placeholder="内容" />
            <textarea v-model="style.reply" class="form-textarea" placeholder="回复" />
            <button type="button" class="remove-button" @click="removeSpeakingStyle(idx)">移除</button>
          </div>
        </div>
        <button type="button" class="add-button" @click="addSpeakingStyle">添加说话风格</button>
      </div>
      <div class="form-group">
        <label>自定义字段</label>
        <ul>
          <li v-for="(field, idx) in character.distinct!" :key="idx" class="list-item-edit">
            <input v-model="field.name" type="text" class="form-input" placeholder="字段名称" />
            <input v-model="field.content" type="text" class="form-input" placeholder="字段值" />
            <button type="button" class="remove-button" @click="removeCustomField(idx)">移除</button>
          </li>
        </ul>
        <button type="button" class="add-button" @click="addCustomField">添加自定义字段</button>
      </div>
      <div class="form-actions">
        <button type="submit" class="confirm-button" :disabled="loading">创建</button>
        <button type="button" class="cancel-button" @click="goBack">取消</button>
      </div>
      <div v-if="error" class="error-message">{{ error }}</div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import type { CharacterCard } from '../entity/CharacterEntity';
import { createCharacter } from '../api/characterApi';

const router = useRouter();
const loading = ref(false);
const error = ref('');

const character = reactive<CharacterCard>({
    id: 1,
  name: '',
  avatar: '', 
  description: '',
  traits: [],
  background_story: '',
  speakings: [],
  distinct: []
});

function handleAvatarUpload(event: Event) {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files[0]) {
    const file = target.files[0];
    const reader = new FileReader();
    reader.onload = (e) => {
      if (e.target && typeof e.target.result === 'string') {
        character.avatar = e.target.result;
      }
    };
    reader.readAsDataURL(file);
  }
}

function addTrait() {
  if (!character.traits) {
    character.traits = [];
  } else if (character.traits === undefined) {
    character.traits = [];
  }
  character.traits!.push({ label: '', description: '' });
}
function removeTrait(idx: number) {
  character?.traits?.splice(idx, 1);
}
function addSpeakingStyle() {
  if (!character.speakings) {
    character.speakings = [];
  }
  character.speakings.push({ role: '', content: '', reply: '' });
}
function removeSpeakingStyle(idx: number) {
  character?.speakings?.splice(idx, 1);
}
function addCustomField() {
  if (!character.distinct) {
    character.distinct = [];
  }
  character.distinct.push({ name: '', content: '' });
}
function removeCustomField(idx: number) {
  character.distinct?.splice(idx, 1);
}

async function handleSubmit() {
  loading.value = true;
  error.value = '';
  try {
    await createCharacter(character);
  } catch (e: any) {
    error.value = e?.message || '创建失败';
  } finally {
    loading.value = false;
  }
}

function goBack() {
  router.back();
}
</script>

<style scoped>
.character-create {
  max-width: 600px;
  margin: 32px auto;
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.form-group {
  margin-bottom: 18px;
}
.form-input, .form-textarea {
  width: 100%;
  padding: 8px;
  margin-top: 4px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1em;
  box-sizing: border-box;
}
.form-textarea {
  min-height: 60px;
  resize: vertical;
}
.trait-list-item-edit, .list-item-edit {
  background: #f9f9f9;
  border-radius: 6px;
  margin-bottom: 10px;
  border-left: 4px solid #ffc107;
  padding: 10px;
  margin: 10px;
}
.remove-button {
  background: #dc3545;
  color: #fff;
  border: none;
  border-radius: 4px;
  padding: 4px 8px;
  cursor: pointer;
  margin-top: 8px;
}
.add-button {
  background: #007bff;
  color: #fff;
  border: none;
  border-radius: 4px;
  padding: 4px 8px;
  cursor: pointer;
  margin-top: 8px;
}
.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}
.confirm-button {
  background: #28a745;
  color: #fff;
  border: 1px solid #28a745;
  border-radius: 4px;
  padding: 8px 16px;
  cursor: pointer;
}
.cancel-button {
  background: #6c757d;
  color: #fff;
  border: 1px solid #6c757d;
  border-radius: 4px;
  padding: 8px 16px;
  cursor: pointer;
}
.error-message {
  color: #dc3545;
  margin-top: 12px;
}
.avatar-preview {
  max-width: 100px;
  max-height: 100px;
  margin-top: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
</style>
