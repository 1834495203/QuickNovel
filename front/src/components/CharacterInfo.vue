<template>
  <div v-if="character" class="character-info" :class="{ 'is-expanded': isExpanded }">
    <div @click="!isEditing && toggleExpand()" class="card-header"
      :style="{ cursor: isEditing ? 'default' : 'pointer' }">
      <img 
        :src="computedAvatarDisplayPath" 
        alt="Avatar" 
        v-if="computedAvatarDisplayPath" 
        class="avatar-small"
        @click="isEditing && handleAvatarAreaClick()" 
        :style="{ cursor: isEditing ? 'pointer' : 'default' }" 
      />
      <div v-if="!computedAvatarDisplayPath && isEditing" 
           class="avatar-placeholder avatar-small"
           @click="handleAvatarAreaClick()"
           :style="{ cursor: 'pointer' }">
        点击上传
      </div>
      <div v-else-if="!computedAvatarDisplayPath" class="avatar-placeholder avatar-small">无头像</div>

      <input type="file" ref="avatarInputRef" @change="handleAvatarFileChange" accept="image/*" style="display: none;" />

      <div v-if="!isEditing" style="flex-grow: 1;">
        <h2>{{ character.name }}</h2>
      </div>
      <div v-if="isEditing && editableCharacter" style="flex-grow: 1;">
        <input type="text" v-model="editableCharacter.name" placeholder="角色名称" class="form-input" />
      </div>
      <button v-if="!isEditing" @click.stop="startChat" class="chat-button">聊天</button>
      <button v-if="!isEditing" @click.stop="startEdit" class="edit-button">编辑</button>
      <button @click.stop="toggleExpand" class="expand-toggle-button" v-if="!isEditing">
        {{ isExpanded ? '收起' : '展开' }}
      </button>
    </div>

    <div v-if="!isEditing">
      <p class="description-preview"><strong>描述:</strong> {{ character.description }}</p>
    </div>
    <div v-if="isEditing && editableCharacter">
      <strong>描述:</strong>
      <textarea v-model="editableCharacter.description" placeholder="角色描述" class="form-textarea"></textarea>
    </div>

    <div v-if="isExpanded || isEditing" class="details-section">
      <!-- Personality Traits -->
      <div v-if="!isEditing && character && character.traits">
        <h3>性格特点:</h3>
        <ul>
          <li v-for="(trait, index) in character.traits" :key="index" class="trait-list-item">
            <div class="trait-label"><strong>{{ trait.label }}</strong></div>
            <div class="trait-description-text">{{ trait.description }}</div>
          </li>
        </ul>
      </div>
      <div v-if="isEditing && editableCharacter">
        <h3>性格特点:</h3>
        <ul v-if="editableCharacter && editableCharacter.traits">
          <li v-for="(trait, index) in editableCharacter.traits" :key="`trait-${index}`"
            class="trait-list-item-edit">
            <input type="text" v-model="trait.label" placeholder="特点标签" class="form-input" />
            <textarea v-model="trait.description" placeholder="特点描述" class="form-textarea"></textarea>
            <button @click="removeTrait(index)" class="remove-button">移除特点</button>
          </li>
        </ul>
        <button @click="addTrait" class="add-button">添加特点</button>
      </div>

      <!-- Background Story (View Mode) -->
      <div v-if="!isEditing && character && character.background_story">
        <h3>背景故事:</h3>
        <p>{{ character.background_story }}</p>
      </div>
      <!-- Background Story (Edit Mode) -->
      <div v-if="isEditing && editableCharacter && editableCharacter.background_story">
        <h3>背景故事:</h3>
        <textarea v-model="editableCharacter.background_story" placeholder="背景故事"
          class="form-textarea"></textarea>
      </div>

      <!-- Speaking Style (View Mode) -->
      <div
        v-if="!isEditing && character && character.speakings && character.speakings.length > 0">
        <h3>说话风格:</h3>
        <ul>
          <li v-for="(style, index) in character.speakings" :key="`style-view-${index}`">
            <p><strong>角色:</strong> {{ style.role }}</p>
            <p><strong>内容:</strong> {{ style.content }}</p>
            <p><strong>回复:</strong> {{ style.reply }}</p>
          </li>
        </ul>
      </div>
      <!-- Speaking Style (Edit Mode) -->
      <div v-if="isEditing && editableCharacter && editableCharacter.speakings">
        <h3>说话风格:</h3>
        <ul v-if="editableCharacter.speakings">
          <li v-for="(style, index) in editableCharacter.speakings" :key="`style-edit-${index}`"
            class="list-item-edit">
            <input type="text" v-model="style.role" placeholder="角色" class="form-input" />
            <textarea v-model="style.content" placeholder="内容" class="form-textarea"></textarea>
            <textarea v-model="style.reply" placeholder="回复" class="form-textarea"></textarea>
            <button @click="removeSpeakingStyle(index)" class="remove-button">移除风格</button>
          </li>
        </ul>
        <button @click="addSpeakingStyle" class="add-button">添加说话风格</button>
      </div>

      <!-- Custom Fields (View Mode) -->
      <div
        v-if="!isEditing && character && character.distinct && character.distinct.length > 0">
        <h3>自定义字段:</h3>
        <ul>
          <li v-for="(field, index) in character.distinct" :key="`field-view-${index}`">
            <strong>{{ field.name }}:</strong> {{ field.content }}
          </li>
        </ul>
      </div>
      <!-- Custom Fields (Edit Mode) -->
      <div v-if="isEditing && editableCharacter && editableCharacter.distinct">
        <h3>自定义字段:</h3>
        <ul v-if="editableCharacter.distinct">
          <li v-for="(field, index) in editableCharacter.distinct" :key="`field-edit-${index}`"
            class="list-item-edit">
            <input type="text" v-model="field.name" placeholder="字段名称" class="form-input" />
            <input type="text" v-model="field.content" placeholder="字段值" class="form-input" />
            <button @click="removeCustomField(index)" class="remove-button">移除字段</button>
          </li>
        </ul>
        <button @click="addCustomField" class="add-button">添加自定义字段</button>
      </div>

      <div v-if="isEditing" class="edit-actions">
        <button @click="confirmEdit" class="confirm-button">确认</button>
        <button @click="cancelEdit" class="cancel-button">取消</button>
        <button @click="deleteCharacter" class="delete-button">删除</button>
      </div>
    </div>
  </div>
  <div v-else>
    <p>没有角色信息可供显示。</p>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, defineProps, defineEmits, computed } from 'vue';
import { useRouter } from 'vue-router';
import type { CharacterCard } from '../entity/CharacterEntity.ts';
import { updateCharacterById } from '../api/characterApi';
import { deleteCharacterById } from '../api/characterApi';
import { showConfirm } from '../utils/showConfirm.ts';
import { baseURL } from '../axios/axios.ts';

// props 和 emits
const props = defineProps<{
  character: CharacterCard
}>();
const emit = defineEmits<{
  (e: 'character-updated'): void
}>();

const router = useRouter();

const isExpanded = ref(false);
const isEditing = ref(false);
const editableCharacter = ref<CharacterCard | null>(null);

const avatarInputRef = ref<HTMLInputElement | null>(null);
const selectedAvatarFileRef = ref<File | null>(null);
const avatarPreviewUrlRef = ref<string | null>(null);

const computedAvatarDisplayPath = computed(() => {
  if (isEditing.value) {
    if (avatarPreviewUrlRef.value) { // New avatar selected for preview
      return avatarPreviewUrlRef.value;
    }
    // Existing avatar in edit mode (from editableCharacter)
    if (editableCharacter.value && editableCharacter.value.avatar) {
      return `${baseURL}/static/${editableCharacter.value.avatar}`;
    }
  } else { // View mode (from props)
    if (props.character && props.character.avatar) {
      return `${baseURL}/static/${props.character.avatar}`;
    }
  }
  return ''; // Return empty string or a path to a default placeholder avatar
});

const handleAvatarAreaClick = () => {
  if (isEditing.value) {
    avatarInputRef.value?.click();
  }
};

const handleAvatarFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files[0]) {
    const file = target.files[0];
    selectedAvatarFileRef.value = file;
    if (avatarPreviewUrlRef.value) {
      URL.revokeObjectURL(avatarPreviewUrlRef.value); // Revoke old blob URL if any
    }
    avatarPreviewUrlRef.value = URL.createObjectURL(file);
  }
};

const toggleExpand = () => {
  if (!isEditing.value) {
    isExpanded.value = !isExpanded.value;
  }
};

const startEdit = () => {
  editableCharacter.value = JSON.parse(JSON.stringify(props.character));
  
  selectedAvatarFileRef.value = null;
  if (avatarPreviewUrlRef.value) {
    URL.revokeObjectURL(avatarPreviewUrlRef.value);
  }
  avatarPreviewUrlRef.value = null;

  if (editableCharacter.value) {
    if (!editableCharacter.value.traits) {
      editableCharacter.value.traits = [];
    } else if (!editableCharacter.value.traits) {
      editableCharacter.value.traits = [];
    }
    if (!editableCharacter.value.background_story) {
      editableCharacter.value.background_story = '';
    }
    if (!editableCharacter.value.speakings) {
      editableCharacter.value.speakings = [];
    } else if (!editableCharacter.value.speakings) {
      editableCharacter.value.speakings = [];
    }
    if (!editableCharacter.value.distinct) {
      editableCharacter.value.distinct = [];
    } else if (!editableCharacter.value.distinct) {
      editableCharacter.value.distinct = [];
    }
  }
  isEditing.value = true;
  isExpanded.value = true;
};

const confirmEdit = async () => {
  if (editableCharacter.value && props.character.id !== undefined) {
    const confirm = await showConfirm({
      title: '确认修改',
      message: '您确定要保存对角色的修改吗？',
      confirmText: '保存',
      cancelText: '取消'
    });
    if (!confirm) {
      return;
    }

    const characterData = { ...editableCharacter.value };
    console.log('characterData', characterData);
    
    try {
      await updateCharacterById(props.character.id, characterData, selectedAvatarFileRef.value); 
      emit('character-updated');
      isEditing.value = false;
      isExpanded.value = false;
      
      if (avatarPreviewUrlRef.value) {
        URL.revokeObjectURL(avatarPreviewUrlRef.value);
      }
      avatarPreviewUrlRef.value = null;
      selectedAvatarFileRef.value = null;
      editableCharacter.value = null;
    } catch (error) {
      console.error('Failed to update character:', error);
    }
  }
};

const cancelEdit = () => {
  if (avatarPreviewUrlRef.value) {
    URL.revokeObjectURL(avatarPreviewUrlRef.value);
  }
  avatarPreviewUrlRef.value = null;
  selectedAvatarFileRef.value = null;
  
  isEditing.value = false;
  isExpanded.value = false;
  editableCharacter.value = null;
};

const deleteCharacter = async () => {
  if (props.character.id !== undefined) {
    const confirmed = await showConfirm({
      title: '确认删除',
      message: '您确定要删除此项目吗？此操作不可撤销。',
      confirmText: '删除',
      cancelText: '取消'
    })
    if (!confirmed) {
      return;
    }
    try {
      await deleteCharacterById(props.character.id);
      emit('character-updated');
      isEditing.value = false;
      isExpanded.value = false;
      editableCharacter.value = null;
    } catch (error) {
      console.error('Failed to delete character:', error);
    }
  }
};

const addTrait = () => {
  if (editableCharacter.value) {
    if (!editableCharacter.value.traits) {
      editableCharacter.value.traits = [];
    }
    if (!editableCharacter.value.traits) {
      editableCharacter.value.traits = [];
    }
    editableCharacter.value.traits.push({ label: '', description: '' });
  }
};

const removeTrait = (index: number) => {
  if (editableCharacter.value && editableCharacter.value.traits && editableCharacter.value.traits) {
    editableCharacter.value.traits.splice(index, 1);
  }
};

const addSpeakingStyle = () => {
  if (editableCharacter.value) {
    if (!editableCharacter.value.speakings) {
      editableCharacter.value.speakings = [];
    }
    if (!editableCharacter.value.speakings) {
      editableCharacter.value.speakings = [];
    }
    editableCharacter.value.speakings.push({ role: '', content: '', reply: '' });
  }
};

const removeSpeakingStyle = (index: number) => {
  if (editableCharacter.value && editableCharacter.value.speakings && editableCharacter.value.speakings) {
    editableCharacter.value.speakings.splice(index, 1);
  }
};

const addCustomField = () => {
  if (editableCharacter.value) {
    if (!editableCharacter.value.distinct) {
      editableCharacter.value.distinct = [];
    }
    if (!editableCharacter.value.distinct) {
      editableCharacter.value.distinct = [];
    }
    editableCharacter.value.distinct.push({ name: '', content: '' });
  }
};

const removeCustomField = (index: number) => {
  if (editableCharacter.value && editableCharacter.value.distinct && editableCharacter.value.distinct) {
    editableCharacter.value.distinct.splice(index, 1);
  }
};

const startChat = () => {
  if (props.character.id !== undefined) {
    router.push(`/chatting?character_id=${props.character.id}`);
  }
};

watch(() => props.character, (newCharacter, oldCharacter) => {
  if (!isEditing.value) {
    editableCharacter.value = null;
    if (newCharacter && oldCharacter && newCharacter.id !== oldCharacter.id) {
      isExpanded.value = false;
    } else if (!oldCharacter && newCharacter) {
      isExpanded.value = false;
    }
  }
}, { deep: true });
</script>

<style scoped>
.character-info {
  background-color: #fff;
  border: 1px solid #e0e0e0;
  padding: 16px;
  margin: 16px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  width: 450px;
  min-height: 125px;
  transition: max-width 0.3s ease-in-out, height 0.3s ease-in-out, box-shadow 0.3s ease-in-out, min-height 0.3s ease-in-out;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.character-info.is-expanded {
  max-width: 800px;
  height: auto;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  flex-shrink: 0;
}

.avatar-small {
  width: 50px;
  height: 50px;
  object-fit: cover;
  border-radius: 50%;
  margin-right: 12px;
  border: 2px solid #eee;
}

.avatar-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f0f0f0;
  color: #888;
  font-size: 0.7em;
  text-align: center;
  line-height: 1.2;
  word-break: break-all;
}

.character-info h2 {
  margin-top: 0;
  margin-bottom: 0;
  color: #333;
  font-size: 1.2em;
  flex-grow: 1;
}

.expand-toggle-button {
  background: none;
  border: 1px solid #007bff;
  color: #007bff;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8em;
  margin-left: 8px;
  white-space: nowrap;
}

.chat-button {
  background: none;
  border: 1px solid #17a2b8;
  color: #17a2b8;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8em;
  margin-left: 8px;
  white-space: nowrap;
}

.edit-button {
  background: none;
  border: 1px solid #28a745;
  color: #28a745;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8em;
  margin-left: 8px;
  white-space: nowrap;
}

.edit-button:hover {
  background-color: #28a745;
  color: white;
}

.description-preview {
  font-size: 0.9em;
  color: #555;
  line-height: 1.4;
  margin-bottom: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  flex-grow: 1;
  min-height: calc(1.4em * 3);
}

.details-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #eee;
  overflow-y: auto;
}

.character-info h3 {
  margin-top: 1em;
  margin-bottom: 0.5em;
  color: #555;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.25em;
  font-size: 1.1em;
}

.character-info ul {
  list-style-type: none;
  padding-left: 0;
}

.character-info li {
  margin-bottom: 0.75em;
  padding: 10px;
  background-color: #f9f9f9;
  border-radius: 6px;
  border-left: 4px solid #007bff;
}

.trait-label {
  font-weight: bold;
  color: #333;
  margin-bottom: 4px;
}

.trait-description-text {
  font-size: 0.9em;
  color: #555;
  padding-left: 8px;
  line-height: 1.5;
}

.form-input,
.form-textarea {
  width: calc(100% - 16px);
  padding: 8px;
  margin-bottom: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 0.9em;
  box-sizing: border-box;
}

.form-textarea {
  min-height: 60px;
  resize: vertical;
}

.trait-list-item-edit,
.list-item-edit {
  padding: 10px;
  background-color: #f0f0f0;
  border-radius: 6px;
  margin-bottom: 10px;
  border-left: 4px solid #ffc107;
}

.trait-list-item-edit .form-input,
.trait-list-item-edit .form-textarea,
.list-item-edit .form-input,
.list-item-edit .form-textarea {
  width: 100%;
}

.remove-button {
  background-color: #dc3545;
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8em;
  margin-left: 5px;
  display: block;
  margin-top: 8px;
}

.add-button {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8em;
  margin-top: 10px;
  display: block;
  margin-bottom: 10px;
}

.remove-button:hover {
  background-color: #c82333;
}

.add-button:hover {
  background-color: #0056b3;
}

.edit-actions {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
}

.confirm-button,
.cancel-button {
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9em;
  margin-left: 8px;
}

.confirm-button {
  background-color: #28a745;
  color: white;
  border: 1px solid #28a745;
}

.confirm-button:hover {
  background-color: #218838;
}

.cancel-button {
  background-color: #6c757d;
  color: white;
  border: 1px solid #6c757d;
}

.cancel-button:hover {
  background-color: #5a6268;
}

.delete-button {
  background-color: #dc3545;
  color: white;
  border: 1px solid #dc3545;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9em;
  margin-left: 8px;
}

.delete-button:hover {
  background-color: #c82333;
}

@media (max-width: 768px) {
  .character-info {
    width: calc(100% - 32px);
    max-width: 350px;
  }

  .character-info.is-expanded {
    max-width: 90%;
    margin-left: auto;
    margin-right: auto;
    height: auto;
  }
}

@media (max-width: 480px) {
  .character-info {
    padding: 12px;
    width: calc(100% - 24px);
    min-height: 210px;
  }

  .avatar-small {
    width: 40px;
    height: 40px;
  }

  .character-info h2 {
    font-size: 1.1em;
  }

  .expand-toggle-button {
    font-size: 0.75em;
    padding: 3px 6px;
  }

  .description-preview {
    font-size: 0.85em;
    -webkit-line-clamp: 2;
    min-height: calc(1.4em * 2);
  }

  .character-info.is-expanded h3 {
    font-size: 1em;
  }

  .character-info.is-expanded li {
    padding: 8px;
  }
}
</style>
