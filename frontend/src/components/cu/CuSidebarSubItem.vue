<template>
  <component :is="tag || 'div'" :to="tag === 'router-link' ? link : undefined"
    :class="['flex items-center w-full p-2 text-base pl-11 transition duration-75 rounded-lg group', availableModeClasses[props.mode]]">
    <slot name="left" />
    <span class="flex-1 ms-2 whitespace-nowrap">
      <slot name="center" />
    </span>
    <slot name="right"></slot>
  </component>
</template>

<script setup>
import { defineProps } from 'vue'

const props = defineProps({
  tag: { type: String, default: null },
  link: { type: String, default: '' },
  mode: { type: String, default: 'default' }
})

const availableModeClasses = {
  default: 'text-gray-900 dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700',
  premium: 'text-red-800 dark:text-red-300 hover:bg-red-100 dark:hover:bg-red-900'
}
</script>