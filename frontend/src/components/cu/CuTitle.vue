<template>
  <h1 class="mb-4 text-center text-3xl font-extrabold leading-none tracking-tight text-gray-900 dark:text-white">
    {{ title }}
  </h1>
</template>

<script setup>
import { defineProps } from 'vue'

defineProps({
  title: { type: String, required: true }
})
</script>
