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

      <div style="flex-grow: 1;">
        <slot name="header-content" :character="isEditing ? editableCharacter : character" :is-editing="isEditing"></slot>
      </div>
      <slot name="header-actions" :is-editing="isEditing" :start-edit="startEdit" :start-chat="startChat"></slot>
      <button @click.stop="toggleExpand" class="expand-toggle-button" v-if="!isEditing">
        {{ isExpanded ? '收起' : '展开' }}
      </button>
    </div>

    <div>
      <slot name="description" :character="isEditing ? editableCharacter : character" :is-editing="isEditing"></slot>
    </div>

    <div v-if="isExpanded || isEditing" class="details-section">
      <slot name="details" 
            :character="isEditing ? editableCharacter : character" 
            :is-editing="isEditing"
            :add-trait="addTrait" 
            :remove-trait="removeTrait" 
            :add-speaking-style="addSpeakingStyle" 
            :remove-speaking-style="removeSpeakingStyle" 
            :add-custom-field="addCustomField" 
            :remove-custom-field="removeCustomField">
      </slot>

      <div v-if="isEditing" class="edit-actions">
        <slot name="edit-actions" :confirm-edit="confirmEdit" :cancel-edit="cancelEdit" :delete-character="deleteCharacter"></slot>
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
import { updateCharacterAvatarById, updateCharacterById } from '../api/characterApi';
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
      return `${baseURL}/${props.character.avatar}`;
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
    if (!editableCharacter.value.trait) {
      editableCharacter.value.trait = [];
    } else if (!editableCharacter.value.trait) {
      editableCharacter.value.trait = [];
    }
    if (!editableCharacter.value.background_story) {
      editableCharacter.value.background_story = '';
    }
    if (!editableCharacter.value.speak) {
      editableCharacter.value.speak = [];
    } else if (!editableCharacter.value.speak) {
      editableCharacter.value.speak = [];
    }
    if (!editableCharacter.value.distinctive) {
      editableCharacter.value.distinctive = [];
    } else if (!editableCharacter.value.distinctive) {
      editableCharacter.value.distinctive = [];
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
      await updateCharacterById(props.character.id, characterData);
      if (selectedAvatarFileRef.value) {
        // If a new avatar file is selected, update the avatar
        await updateCharacterAvatarById(props.character.id, selectedAvatarFileRef.value);
      }
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
    if (!editableCharacter.value.trait) {
      editableCharacter.value.trait = [];
    }
    if (!editableCharacter.value.trait) {
      editableCharacter.value.trait = [];
    }
    editableCharacter.value.trait.push({ label: '', description: '' });
  }
};

const removeTrait = (index: number) => {
  if (editableCharacter.value && editableCharacter.value.trait && editableCharacter.value.trait) {
    editableCharacter.value.trait.splice(index, 1);
  }
};

const addSpeakingStyle = () => {
  if (editableCharacter.value) {
    if (!editableCharacter.value.speak) {
      editableCharacter.value.speak = [];
    }
    if (!editableCharacter.value.speak) {
      editableCharacter.value.speak = [];
    }
    editableCharacter.value.speak.push({ role: '', content: '', reply: '' });
  }
};

const removeSpeakingStyle = (index: number) => {
  if (editableCharacter.value && editableCharacter.value.speak && editableCharacter.value.speak) {
    editableCharacter.value.speak.splice(index, 1);
  }
};

const addCustomField = () => {
  if (editableCharacter.value) {
    if (!editableCharacter.value.distinctive) {
      editableCharacter.value.distinctive = [];
    }
    if (!editableCharacter.value.distinctive) {
      editableCharacter.value.distinctive = [];
    }
    editableCharacter.value.distinctive.push({ name: '', content: '' });
  }
};

const removeCustomField = (index: number) => {
  if (editableCharacter.value && editableCharacter.value.distinctive && editableCharacter.value.distinctive) {
    editableCharacter.value.distinctive.splice(index, 1);
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

.details-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #eee;
  overflow-y: auto;
}

.edit-actions {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
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

  .expand-toggle-button {
    font-size: 0.75em;
    padding: 3px 6px;
  }
}
</style>