<template>
  <label v-if="tooltip && name" :for="name" class="block font-medium text-gray-900 dark:text-white flex items-center">
    {{ label }}
    <button :data-tooltip-target="name + '-tooltip'" type="button" data-tooltip-placement="right"
      class="ml-0.5 text-gray-500 hover:text-orange-600 dark:text-gray-400 dark:hover:text-orange-600"
      aria-label="More information">
      <QuestionMarkCircleIcon class="w-4 h-4" />
    </button>
    <div :id="name + '-tooltip'" role="tooltip"
      class="max-w-sm text-center absolute z-10 invisible inline-block px-3 py-2 text-xs font-normal text-white transition-opacity duration-300 bg-orange-600 rounded-lg shadow-sm opacity-0 tooltip">
      {{ tooltip }}
      <div class="text-left tooltip-arrow" data-popper-arrow></div>
    </div>
  </label>
  <label v-else-if="name" :for="name" class="block font-medium text-gray-900 dark:text-white">
    {{ label }}
  </label>
  <label v-else class="block font-medium text-gray-900 dark:text-white">
    {{ label }}
  </label>
</template>

<script setup>
import { defineProps } from 'vue'
import { QuestionMarkCircleIcon } from '@heroicons/vue/16/solid'

defineProps({
  label: { type: String, required: true },
  name: { type: String },
  tooltip: { type: String }
})
</script>
