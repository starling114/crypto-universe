<template>
  <div class="flex items-center ps-2.5 mb-5">
    <img :src="logo" class="h-6 me-3 sm:h-7" alt="Flowbite Logo" />
    <span class="self-center text-xl font-semibold whitespace-nowrap dark:text-white">{{ text }}</span>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'

defineProps({
  text: { type: String, required: true },
  logo: { type: String, required: true }
})
</script>