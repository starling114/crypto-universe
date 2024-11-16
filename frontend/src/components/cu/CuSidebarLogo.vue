<template>
  <div class="mb-5">
    <div class="flex items-center ps-2.5">
      <img :src="logo" class="h-6 me-3 sm:h-7" alt="Flowbite Logo" />
      <span class="self-center text-xl font-semibold whitespace-nowrap dark:text-white">{{ text }}</span>
    </div>
    <div v-if="debug" class="flex items-center ps-2.5 mt-2">
      <span
        class="w-full text-center h-5 bg-blue-100 text-blue-800 text-xs font-medium me-2 px-2.5 py-0.5 rounded dark:bg-blue-900 dark:text-blue-300">Debug
        Mode</span>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'

defineProps({
  text: { type: String, required: true },
  logo: { type: String, required: true },
  debug: { type: Boolean, default: false }
})
</script>