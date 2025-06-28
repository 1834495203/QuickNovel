<script setup lang="ts">
import { ref, onMounted } from 'vue';
import type { CharacterCard } from '../entity/CharacterEntity.ts';
import CharacterInfo from '../components/CharacterInfo.vue';
import { getAllCharacters } from '../api/characterApi.ts';

const characterList = ref<CharacterCard[]>([]);

onMounted(async () => {
  const characters = await getAllCharacters();
  console.log('characters', characters);
  characterList.value.push(...characters);
});

const handleCharacterUpdated = async () => {
  // 更新父组件的 character 数据
  characterList.value = await getAllCharacters();
};


</script>

<template>
  <div class="character-list-container">
    <div v-for="character in characterList" :key="character.id">
      <CharacterInfo :character="character" @character-updated="handleCharacterUpdated">
        <template #header-content="{ character: slotCharacter, isEditing }">
          <div v-if="!isEditing" style="flex-grow: 1;">
            <h2>{{ slotCharacter?.name }}</h2>
          </div>
          <div v-if="isEditing && slotCharacter" style="flex-grow: 1;">
            <input type="text" v-model="slotCharacter.name" placeholder="角色名称" class="form-input" />
          </div>
        </template>

        <template #header-actions="{ isEditing, startEdit, startChat }">
          <button v-if="!isEditing" @click.stop="startChat" class="chat-button">聊天</button>
          <button v-if="!isEditing" @click.stop="startEdit" class="edit-button">编辑</button>
        </template>

        <template #description="{ character: slotCharacter, isEditing }">
          <div v-if="!isEditing">
            <p class="description-preview"><strong>描述:</strong> {{ slotCharacter?.description }}</p>
          </div>
          <div v-if="isEditing && slotCharacter">
            <strong>描述:</strong>
            <textarea v-model="slotCharacter.description" placeholder="角色描述" class="form-textarea"></textarea>
          </div>
        </template>

        <template #details="{ character: slotCharacter, isEditing, addTrait, removeTrait, addSpeakingStyle, removeSpeakingStyle, addCustomField, removeCustomField }">
          <!-- Personality Traits -->
          <div v-if="!isEditing && slotCharacter && slotCharacter.trait">
            <h3>性格特点:</h3>
            <ul>
              <li v-for="(trait, index) in slotCharacter.trait" :key="index" class="trait-list-item">
                <div class="trait-label"><strong>{{ trait.label }}</strong></div>
                <div class="trait-description-text">{{ trait.description }}</div>
              </li>
            </ul>
          </div>
          <div v-if="isEditing && slotCharacter">
            <h3>性格特点:</h3>
            <ul v-if="slotCharacter && slotCharacter.trait">
              <li v-for="(trait, index) in slotCharacter.trait" :key="`trait-${index}`"
                class="trait-list-item-edit">
                <input type="text" v-model="trait.label" placeholder="特点标签" class="form-input" />
                <textarea v-model="trait.description" placeholder="特点描述" class="form-textarea"></textarea>
                <button @click="removeTrait(index)" class="remove-button">移除特点</button>
              </li>
            </ul>
            <button @click="addTrait" class="add-button">添加特点</button>
          </div>

          <!-- Background Story (View Mode) -->
          <div v-if="!isEditing && slotCharacter && slotCharacter.background_story">
            <h3>背景故事:</h3>
            <p>{{ slotCharacter.background_story }}</p>
          </div>
          <!-- Background Story (Edit Mode) -->
          <div v-if="isEditing && slotCharacter && slotCharacter.background_story !== undefined">
            <h3>背景故事:</h3>
            <textarea v-model="slotCharacter.background_story" placeholder="背景故事"
              class="form-textarea"></textarea>
          </div>

          <!-- Speaking Style (View Mode) -->
          <div
            v-if="!isEditing && slotCharacter && slotCharacter.speak && slotCharacter.speak.length > 0">
            <h3>说话风格:</h3>
            <ul>
              <li v-for="(style, index) in slotCharacter.speak" :key="`style-view-${index}`">
                <p><strong>角色:</strong> {{ style.role }}</p>
                <p><strong>内容:</strong> {{ style.content }}</p>
                <p><strong>回复:</strong> {{ style.reply }}</p>
              </li>
            </ul>
          </div>
          <!-- Speaking Style (Edit Mode) -->
          <div v-if="isEditing && slotCharacter && slotCharacter.speak">
            <h3>说话风格:</h3>
            <ul v-if="slotCharacter.speak">
              <li v-for="(style, index) in slotCharacter.speak" :key="`style-edit-${index}`"
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
            v-if="!isEditing && slotCharacter && slotCharacter.distinctive && slotCharacter.distinctive.length > 0">
            <h3>自定义字段:</h3>
            <ul>
              <li v-for="(field, index) in slotCharacter.distinctive" :key="`field-view-${index}`">
                <strong>{{ field.name }}:</strong> {{ field.content }}
              </li>
            </ul>
          </div>
          <!-- Custom Fields (Edit Mode) -->
          <div v-if="isEditing && slotCharacter && slotCharacter.distinctive">
            <h3>自定义字段:</h3>
            <ul v-if="slotCharacter.distinctive">
              <li v-for="(field, index) in slotCharacter.distinctive" :key="`field-edit-${index}`"
                class="list-item-edit">
                <input type="text" v-model="field.name" placeholder="字段名称" class="form-input" />
                <input type="text" v-model="field.content" placeholder="字段值" class="form-input" />
                <button @click="removeCustomField(index)" class="remove-button">移除字段</button>
              </li>
            </ul>
            <button @click="addCustomField" class="add-button">添加自定义字段</button>
          </div>
        </template>

        <template #edit-actions="{ confirmEdit, cancelEdit, deleteCharacter }">
          <button @click="confirmEdit" class="confirm-button">确认</button>
          <button @click="cancelEdit" class="cancel-button">取消</button>
          <button @click="deleteCharacter" class="delete-button">删除</button>
        </template>
      </CharacterInfo>
    </div>
  </div>
</template>

<style scoped>
.character-list-container {
  display: flex;
  flex-wrap: wrap;
  gap: 16px; /* Adjust gap between cards */
  padding: 16px;
  justify-content: center; /* Center cards if they don't fill the row */
}

:deep(h2) {
  margin-top: 0;
  margin-bottom: 0;
  color: #333;
  font-size: 1.2em;
  flex-grow: 1;
}

:deep(.chat-button) {
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

:deep(.edit-button) {
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

:deep(.edit-button:hover) {
  background-color: #28a745;
  color: white;
}

:deep(.description-preview) {
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

:deep(h3) {
  margin-top: 1em;
  margin-bottom: 0.5em;
  color: #555;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.25em;
  font-size: 1.1em;
}

:deep(ul) {
  list-style-type: none;
  padding-left: 0;
}

:deep(li) {
  margin-bottom: 0.75em;
  padding: 10px;
  background-color: #f9f9f9;
  border-radius: 6px;
  border-left: 4px solid #007bff;
}

:deep(.trait-label) {
  font-weight: bold;
  color: #333;
  margin-bottom: 4px;
}

:deep(.trait-description-text) {
  font-size: 0.9em;
  color: #555;
  padding-left: 8px;
  line-height: 1.5;
}

:deep(.form-input),
:deep(.form-textarea) {
  width: calc(100% - 16px);
  padding: 8px;
  margin-bottom: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 0.9em;
  box-sizing: border-box;
}

:deep(.form-textarea) {
  min-height: 60px;
  resize: vertical;
}

:deep(.trait-list-item-edit),
:deep(.list-item-edit) {
  padding: 10px;
  background-color: #f0f0f0;
  border-radius: 6px;
  margin-bottom: 10px;
  border-left: 4px solid #ffc107;
}

:deep(.trait-list-item-edit .form-input),
:deep(.trait-list-item-edit .form-textarea),
:deep(.list-item-edit .form-input),
:deep(.list-item-edit .form-textarea) {
  width: 100%;
}

:deep(.remove-button) {
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

:deep(.add-button) {
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

:deep(.remove-button:hover) {
  background-color: #c82333;
}

:deep(.add-button:hover) {
  background-color: #0056b3;
}

:deep(.confirm-button),
:deep(.cancel-button) {
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9em;
  margin-left: 8px;
}

:deep(.confirm-button) {
  background-color: #28a745;
  color: white;
  border: 1px solid #28a745;
}

:deep(.confirm-button:hover) {
  background-color: #218838;
}

:deep(.cancel-button) {
  background-color: #6c757d;
  color: white;
  border: 1px solid #6c757d;
}

:deep(.cancel-button:hover) {
  background-color: #5a6268;
}

:deep(.delete-button) {
  background-color: #dc3545;
  color: white;
  border: 1px solid #dc3545;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9em;
  margin-left: 8px;
}

:deep(.delete-button:hover) {
  background-color: #c82333;
}

@media (max-width: 480px) {
  :deep(h2) {
    font-size: 1.1em;
  }

  :deep(.description-preview) {
    font-size: 0.85em;
    -webkit-line-clamp: 2;
    min-height: calc(1.4em * 2);
  }

  :deep(h3) {
    font-size: 1em;
  }

  :deep(li) {
    padding: 8px;
  }
}
</style>
