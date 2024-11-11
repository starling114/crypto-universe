<template>
  <button type="button" :disabled="disabled || null" @click="handleClick" :class="computedClasses">
    {{ label }}
  </button>

</template>

<script setup>
import { defineProps, defineEmits, computed } from 'vue'

const props = defineProps({
  label: { type: String },
  disabled: { type: Boolean, default: false },
  color: { type: String, default: 'default' },
  size: { type: String, default: 'default' }
})

const emit = defineEmits(['click'])

const availableSizeClasses = {
  xsmall: 'px-3 py-2 text-xs',
  small: 'px-3 py-2 text-sm',
  default: 'px-5 py-2.5 text-sm'
}

const availableColorClasses = {
  disabled: 'bg-gray-200 text-gray-400 dark:bg-gray-700 dark:text-gray-500 cursor-not-allowed',
  red: 'text-white bg-red-600 hover:bg-red-700 dark:bg-red-600 dark:hover:bg-red-700',
  green: 'text-white bg-green-600 hover:bg-green-700 dark:bg-green-600 dark:hover:bg-green-700',
  orange: 'text-white bg-orange-600 hover:bg-orange-700 dark:bg-orange-600 dark:hover:bg-orange-700',
  default: 'text-gray-500 hover:text-gray-900 bg-white border border-gray-200 hover:bg-gray-200 dark:bg-gray-800 dark:dark:text-gray-400 dark:hover:text-white dark:border-gray-600 dark:hover:bg-gray-700 dark:hover:border-gray-700'
}

const computedClasses = computed(() => {
  const baseClasses = ['font-medium text-center rounded-lg focus:ring-0 focus:outline-none']

  baseClasses.push(availableSizeClasses[props.size])

  if (props.disabled) {
    baseClasses.push(availableColorClasses.disabled)
  } else {
    baseClasses.push(availableColorClasses[props.color])
  }

  return baseClasses.join(' ')
})

const handleClick = (event) => {
  if (!props.disabled) {
    emit('click', event)
  }
}
</script>
