<script setup lang="ts">
import { ref, watch } from 'vue';
import { CharacterCard } from './entity/CharacterCard.ts';
import  CharacterInfo  from './components/CharacterInfo.vue';

const characterData = ref<CharacterCard>({
  avatar: 'https://via.placeholder.com/100',
  name: '神秘人物',
  description: '一个充满谜团的角色。',
  personality: {
    traits: [
      { label: '内向' },
      { label: '好奇' },
      { label: '冷静' },
    ],
    description: '他是一个内向而好奇的人，喜欢独处并思考。',
  },
  background: {
    background_story: '在遥远的山脉中长大，经历了一系列不为人知的事件。',
  },
  behaviors: {
    speakingStyle: [
      { role: '初次见面', content: '你好。', reply: '很高兴认识你。' },
      { role: '思考时', content: '嗯...', reply: '让我想想。' },
    ],
  },
  abilities: {
    knowledge: ['古代语言', '炼金术'],
    hobby: ['观星', '阅读'],
  },
  customize: {
    fields: [
      { fieldName: '年龄', fieldValue: '未知' },
      { fieldName: '特殊能力', fieldValue: '心灵感应' },
    ],
  },
});

watch(characterData, (newValue) => {
  console.log('Character data updated:', newValue);
});
</script>

<template>
    <CharacterInfo :characterCard="characterData" />
</template>

<style scoped>
</style>
