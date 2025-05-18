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
      <CharacterInfo :character="character" @character-updated="handleCharacterUpdated"/>
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
</style>
