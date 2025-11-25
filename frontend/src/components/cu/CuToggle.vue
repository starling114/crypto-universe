<template>
  <div class="flex items-center gap-2">
    <cu-label v-if="label" :name="name" :label="label" :tooltip="tooltip" />
    <div class="flex items-center gap-2">
      <span
        :class="['text-xs font-medium transition-colors', modelValue ? 'text-green-600 dark:text-green-400' : 'text-gray-500 dark:text-gray-400']">
        {{ modelValue ? 'Enabled' : 'Disabled' }}
      </span>
      <button type="button" :id="name" :class="[
        'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2',
        modelValue ? 'bg-green-500 dark:bg-green-600' : 'bg-gray-300 dark:bg-gray-600'
      ]" :aria-pressed="modelValue" @click="$emit('update:modelValue', !modelValue)"
        :title="tooltip || (modelValue ? 'Click to disable' : 'Click to enable')">
        <span :class="[
          'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out',
          modelValue ? 'translate-x-5' : 'translate-x-0'
        ]" />
      </button>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'
import { CuLabel } from '@/components/cu'

defineProps({
  name: { type: String, required: true },
  modelValue: { type: Boolean, required: true },
  label: { type: String },
  tooltip: { type: String }
})
</script>
