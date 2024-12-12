<template>
  <div v-for="optionsBatch in optionsBatches" :key="optionsBatch" class="mb-1 flex items-center">
    <ul
      class="items-center w-full font-medium text-gray-900 bg-white border border-gray-200 rounded-lg sm:flex dark:bg-gray-700 dark:border-gray-600 dark:text-white">
      <li v-for="(option, index) in optionsBatch" :key="option"
        :class="['w-full border-b border-gray-200 sm:border-b-0 dark:border-gray-600', index !== optionsBatch.length - 1 ? 'sm:border-r' : '']">
        <div class="flex items-center ps-3">
          <input type="checkbox" :id="option" :value="option" :checked="modelValue.includes(option)"
            @change="handleCheckboxChange(option, $event.target.checked)"
            class="mr-1 w-4 h-4 text-orange-600 bg-gray-100 border-gray-300 rounded focus:ring-offset-0 focus:ring-0 dark:ring-offset-gray-700 dark:bg-gray-600 dark:border-gray-500">
          <label :for="option" class="w-full py-3 ms-2 text-sm font-medium text-gray-900 dark:text-gray-300">
            {{ option }}
          </label>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, computed } from 'vue'

const props = defineProps({
  name: { type: String, required: true },
  modelValue: { type: Array, required: true },
  label: { type: String },
  tooltip: { type: String },
  options: { type: Array, required: true },
  batchSize: { type: Number, default: 5 }
})

const emit = defineEmits(['update:modelValue'])

const optionsBatches = computed(() => {
  return Array.from({ length: Math.ceil(props.options.length / props.batchSize) }, (_, i) =>
    props.options.slice(i * props.batchSize, i * props.batchSize + props.batchSize)
  )
})

const handleCheckboxChange = (value, isChecked) => {
  const newValue = isChecked
    ? [...props.modelValue, value]
    : props.modelValue.filter(item => item !== value)

  emit('update:modelValue', newValue)
}
</script>
