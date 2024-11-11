<template>
  <component :is="tag || 'div'" :to="tag === 'router-link' ? link : undefined"
    class="flex items-center w-full p-2 text-gray-900 transition duration-75 rounded-lg pl-11 group hover:bg-gray-100 dark:text-white dark:hover:bg-gray-700">
    <span class="flex-1 ms-3 whitespace-nowrap">
      <slot name="center" />
    </span>
    <slot name="right"></slot>
  </component>
</template>

<script setup>
import { defineProps } from 'vue'

defineProps({
  tag: { type: String, default: null },
  link: { type: String, default: '' }
})
</script>