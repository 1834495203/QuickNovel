<template>
  <div class="character-info">
    <div v-if="!isEditing" class="basic-info">
      <img :src="characterCard.avatar" alt="角色头像" class="avatar" />
      <h2>{{ characterCard.name }}</h2>
      <p class="description">{{ characterCard.description }}</p>
      <button @click="startEditing">编辑</button>
    </div>

    <div v-else class="basic-info edit-mode">
      <label for="avatar">头像 URL:</label>
      <input type="text" id="avatar" v-model="editableCharacterCard.avatar" />

      <label for="name">名称:</label>
      <input type="text" id="name" v-model="editableCharacterCard.name" />

      <label for="description">描述:</label>
      <textarea id="description" v-model="editableCharacterCard.description"></textarea>
    </div>

    <div v-if="!isEditing && characterCard.personality?.traits" class="personality-section">
      <h3>性格特征</h3>
      <span v-for="trait in characterCard.personality.traits" :key="trait.label" class="tag">
        {{ trait.label }}
      </span>

      <h3>性格描述</h3>
      <p>{{ characterCard.personality.description }}</p>
    </div>

    <div v-else-if="isEditing" class="personality-section edit-mode">
      <h3>性格特征</h3>
      <div v-for="(trait, index) in editableCharacterCard.personality.traits" :key="trait.label" class="tag-input-group">
        <input type="text" v-model="editableCharacterCard.personality.traits[index].label" />
        <button @click="removeTrait(index)">移除</button>
      </div>
      <h3>性格描述</h3>
      <textarea id="description" v-model="editableCharacterCard.personality.description"></textarea>
      <button @click="addTrait">添加特征</button>
    </div>

    <div v-if="!isEditing && characterCard.background?.background_story" class="background-section">
      <h3>背景故事</h3>
      <p>{{ characterCard.background.background_story }}</p>
    </div>

    <div v-else-if="isEditing && characterCard.background" class="background-section edit-mode">
      <h3>背景故事</h3>
      <textarea v-model="editableCharacterCard.background.background_story"></textarea>
    </div>

    <div v-if="!isEditing && characterCard.behaviors?.speakingStyle" class="speaking-section">
      <h3>说话方式</h3>
      <div v-for="(speak, index) in characterCard.behaviors.speakingStyle" :key="index" class="collapse-item">
        <h4>{{ speak.role }}</h4>
        <p><strong>内容：</strong>{{ speak.content }}</p>
        <p><strong>回复：</strong>{{ speak.reply }}</p>
      </div>
    </div>

    <div v-else-if="isEditing && characterCard.behaviors?.speakingStyle" class="speaking-section edit-mode">
      <h3>说话方式</h3>
      <div v-for="(speak, index) in editableCharacterCard.behaviors.speakingStyle" :key="index" class="collapse-item">
        <label :for="'role-' + index">角色:</label>
        <input type="text" :id="'role-' + index" v-model="editableCharacterCard.behaviors.speakingStyle[index].role" />

        <label :for="'content-' + index">内容:</label>
        <textarea :id="'content-' + index" v-model="editableCharacterCard.behaviors.speakingStyle[index].content"></textarea>

        <label :for="'reply-' + index">回复:</label>
        <textarea :id="'reply-' + index" v-model="editableCharacterCard.behaviors.speakingStyle[index].reply"></textarea>
        <button @click="removeSpeakingStyle(index)">移除</button>
      </div>
      <button @click="addSpeakingStyle">添加说话方式</button>
    </div>

    <div v-if="!isEditing && characterCard.abilities" class="abilities-section">
      <h3>能力和专长</h3>
      <div v-if="characterCard.abilities.knowledge">
        <h4>知识领域</h4>
        <span v-for="know in characterCard.abilities.knowledge" :key="know" class="tag success">
          {{ know }}
        </span>
      </div>
      <div v-if="characterCard.abilities.hobby">
        <h4>兴趣爱好</h4>
        <span v-for="hobby in characterCard.abilities.hobby" :key="hobby" class="tag warning">
          {{ hobby }}
        </span>
      </div>
    </div>

    <div v-else-if="isEditing && characterCard.abilities" class="abilities-section edit-mode">
      <h3>能力和专长</h3>
      <div v-if="editableCharacterCard.abilities.knowledge">
        <h4>知识领域</h4>
        <div v-for="(know, index) in editableCharacterCard.abilities.knowledge" :key="know" class="tag-input-group">
          <input type="text" v-model="editableCharacterCard.abilities.knowledge[index]" />
          <button @click="removeKnowledge(index)">移除</button>
        </div>
        <button @click="addKnowledge">添加知识</button>
      </div>
      <div v-if="editableCharacterCard.abilities.hobby">
        <h4>兴趣爱好</h4>
        <div v-for="(hobby, index) in editableCharacterCard.abilities.hobby" :key="hobby" class="tag-input-group">
          <input type="text" v-model="editableCharacterCard.abilities.hobby[index]" />
          <button @click="removeHobby(index)">移除</button>
        </div>
        <button @click="addHobby">添加爱好</button>
      </div>
    </div>

    <div v-if="!isEditing && characterCard.customize?.fields" class="customize-section">
      <h3>自定义信息</h3>
      <div v-for="field in characterCard.customize.fields" :key="field.fieldName" class="description-item">
        <strong>{{ field.fieldName }}:</strong> {{ field.fieldValue }}
      </div>
    </div>

    <div v-else-if="isEditing && characterCard.customize?.fields" class="customize-section edit-mode">
      <h3>自定义信息</h3>
      <div v-for="(field, index) in editableCharacterCard.customize.fields" :key="field.fieldName" class="description-item">
        <label :for="'fieldName-' + index">字段名:</label>
        <input type="text" :id="'fieldName-' + index" v-model="editableCharacterCard.customize.fields[index].fieldName" />

        <label :for="'fieldValue-' + index">字段值:</label>
        <input type="text" :id="'fieldValue-' + index" v-model="editableCharacterCard.customize.fields[index].fieldValue" />
      </div>
      <button @click="addCustomField">添加自定义字段</button>
    </div>

    <div v-if="isEditing" class="edit-actions">
      <button @click="saveChanges">保存</button>
      <button @click="cancelEditing">取消</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, ref, watch, toRefs } from 'vue';
import { CharacterCard, Trait, SpeakingStyle, CustomField } from '../entity/CharacterCard'; // 确保路径正确

const props = defineProps<{
  characterCard: CharacterCard;
}>();

const { characterCard } = toRefs(props);
const isEditing = ref(false);
const editableCharacterCard = ref<CharacterCard>(JSON.parse(JSON.stringify(characterCard.value))); // 深拷贝用于编辑

watch(editableCharacterCard.value, (newValue) => {
    console.log('CharacterCard prop changed:', newValue);
  // 当传入的 characterCard prop 变化时，更新 editableCharacterCard (如果不在编辑状态)
  if (!isEditing.value) {
    editableCharacterCard.value = JSON.parse(JSON.stringify(newValue));
  }
});

const startEditing = () => {
  isEditing.value = true;
};

const cancelEditing = () => {
  isEditing.value = false;
  // 恢复到原始数据
  editableCharacterCard.value = JSON.parse(JSON.stringify(characterCard.value));
};

const saveChanges = () => {
  // 在这里触发一个事件，将 editableCharacterCard.value 传递给父组件
  emit('update:characterCard', editableCharacterCard.value);
  isEditing.value = false;
};

// 性格特征编辑
const addTrait = () => {
  if (!editableCharacterCard.value.personality) {
    editableCharacterCard.value.personality = { traits: [] };
  }
  editableCharacterCard.value.personality.traits.push({ label: '' });
};

const removeTrait = (index: number) => {
  editableCharacterCard.value.personality?.traits.splice(index, 1);
};

// 说话方式编辑
const addSpeakingStyle = () => {
  if (!editableCharacterCard.value.behaviors) {
    editableCharacterCard.value.behaviors = { speakingStyle: [] };
  }
  editableCharacterCard.value.behaviors.speakingStyle.push({ role: '', content: '', reply: '' });
};

const removeSpeakingStyle = (index: number) => {
  editableCharacterCard.value.behaviors?.speakingStyle.splice(index, 1);
};

// 知识领域编辑
const addKnowledge = () => {
  if (!editableCharacterCard.value.abilities) {
    editableCharacterCard.value.abilities = { knowledge: [], hobby: [] };
  } else if (!editableCharacterCard.value.abilities.knowledge) {
    editableCharacterCard.value.abilities.knowledge = [];
  }
  editableCharacterCard.value.abilities.knowledge.push('');
};

const removeKnowledge = (index: number) => {
  editableCharacterCard.value.abilities?.knowledge?.splice(index, 1);
};

// 兴趣爱好编辑
const addHobby = () => {
  if (!editableCharacterCard.value.abilities) {
    editableCharacterCard.value.abilities = { knowledge: [], hobby: [] };
  } else if (!editableCharacterCard.value.abilities.hobby) {
    editableCharacterCard.value.abilities.hobby = [];
  }
  editableCharacterCard.value.abilities.hobby.push('');
};

const removeHobby = (index: number) => {
  editableCharacterCard.value.abilities?.hobby?.splice(index, 1);
};

// 自定义字段编辑
const addCustomField = () => {
  if (!editableCharacterCard.value.customize) {
    editableCharacterCard.value.customize = { fields: [] };
  }
  editableCharacterCard.value.customize.fields.push({ fieldName: '', fieldValue: '' });
};

// TODO: 实现移除自定义字段的功能
// const removeCustomField = (index: number) => {
//   editableCharacterCard.value.customize?.fields.splice(index, 1);
// };

const emit = defineEmits(['update:characterCard']);
</script>

<style scoped>
.character-info {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
  font-family: sans-serif;
}

.basic-info {
  text-align: center;
  margin-bottom: 20px;
}

.avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  margin-bottom: 10px;
}

.description {
  color: #555;
  margin: 10px 0;
}

.tag {
  display: inline-block;
  background-color: #eee;
  color: #333;
  padding: 5px 10px;
  border-radius: 5px;
  margin-right: 5px;
  margin-bottom: 5px;
}

.tag.success {
  background-color: #d4edda;
  color: #155724;
}

.tag.warning {
  background-color: #fff3cd;
  color: #856404;
}

.personality-section,
.background-section,
.speaking-section,
.abilities-section,
.customize-section {
  margin-bottom: 20px;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 5px;
}

h3 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #333;
}

h4 {
  margin-top: 10px;
  margin-bottom: 5px;
  color: #555;
}

.collapse-item {
  margin-bottom: 10px;
  padding: 10px;
  border: 1px solid #eee;
  border-radius: 3px;
}

.collapse-item h4 {
  margin-top: 0;
}

.description-item {
  margin-bottom: 8px;
}

.edit-mode label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.edit-mode input[type="text"],
.edit-mode textarea {
  width: 100%;
  padding: 8px;
  margin-bottom: 10px;
  border: 1px solid #ccc;
  border-radius: 3px;
  box-sizing: border-box;
}

.edit-mode textarea {
  min-height: 80px;
}

.edit-actions {
  margin-top: 20px;
  text-align: right;
}

.edit-actions button {
  padding: 8px 15px;
  margin-left: 10px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
}

.edit-actions button:first-child {
  background-color: #4CAF50;
  color: white;
}

.edit-actions button:last-child {
  background-color: #f44336;
  color: white;
}

.tag-input-group {
  display: flex;
  align-items: center;
  margin-bottom: 5px;
}

.tag-input-group input[type="text"] {
  flex-grow: 1;
  margin-right: 5px;
}

.tag-input-group button {
  padding: 5px 10px;
  border: none;
  border-radius: 3px;
  background-color: #f44336;
  color: white;
  cursor: pointer;
}

.edit-mode .description-item {
  display: flex;
  flex-direction: column;
  margin-bottom: 15px;
}

.edit-mode .description-item label {
  margin-bottom: 3px;
}
</style>