<template>
  <div class="flex items-center">
    <input type="checkbox" :id="name" :checked="modelValue" @change="$emit('update:modelValue', $event.target.checked)"
      class="mr-1 w-4 h-4 text-orange-600 bg-gray-100 border-gray-300 rounded focus:ring-offset-0 focus:ring-0 dark:bg-gray-600 dark:border-gray-500">
    <cu-label v-if="label" :name="name" :label="label" :tooltip="tooltip" />
  </div>
</template>

<script setup>
import { defineProps } from 'vue'
import { CuLabel } from '@/components/cu'

defineProps({
  name: { type: String, reqiured: true },
  modelValue: { type: Boolean, reqiured: true },
  label: { type: String },
  tooltip: { type: String }
})
</script>
