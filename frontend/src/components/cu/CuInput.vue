<template>
  <div>
    <cu-label v-if="label" :name="name" :label="label" :tooltip="tooltip" />
    <input type="text" :id="name" :value="modelValue" @input="$emit('update:modelValue', $event.target.value)"
      :placeholder="placeholder || ''" :class="[
        'mb-2 bg-white border border-gray-300 text-gray-900 rounded-lg focus:ring-gray-600 focus:border-gray-600 block w-full dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-white dark:focus:border-white',
        sizeClasses]" />
  </div>
</template>

<script setup>
import { defineProps, computed } from 'vue'
import { CuLabel } from '@/components/cu'

const props = defineProps({
  name: { type: String, reqiured: true },
  modelValue: { type: [String, Number], reqiured: true },
  label: { type: String },
  placeholder: { type: String },
  tooltip: { type: String },
  size: { type: String, default: 'normal' }
})

const availableSizeClasses = {
  small: 'text-xs p-2',
  normal: 'p-2.5'
}

const sizeClasses = computed(() => {
  return availableSizeClasses[props.size]
})
</script>
