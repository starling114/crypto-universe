<template>
  <div class="mb-2 flex items-center">
    <ul
      class="items-center w-full font-medium text-gray-900 bg-white border border-gray-200 rounded-lg sm:flex dark:bg-gray-700 dark:border-gray-600 dark:text-white">
      <li v-for="option in options" :key="option"
        class="w-full border-b border-gray-200 sm:border-b-0 sm:border-r dark:border-gray-600">
        <div class="flex items-center ps-3">
          <input type="checkbox" :id="option" :value="option" :checked="modelValue.includes(option)"
            @change="handleCheckboxChange(option, $event.target.checked)"
            class="mr-1 w-4 h-4 text-orange-600 bg-gray-100 border-gray-300 rounded focus:ring-offset-0 focus:ring-0 dark:ring-offset-gray-700 dark:bg-gray-600 dark:border-gray-500">
          <label :for="option" class="w-full py-3 ms-2 font-medium text-gray-900 dark:text-gray-300">
            {{ option }}
          </label>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  name: { type: String, reqiured: true },
  modelValue: { type: Array, reqiured: true },
  label: { type: String },
  tooltip: { type: String },
  options: { type: Array, required: true }
})

const emit = defineEmits(['update:modelValue'])

const handleCheckboxChange = (value, isChecked) => {
  const newValue = isChecked
    ? [...props.modelValue, value]
    : props.modelValue.filter(item => item !== value)

  emit('update:modelValue', newValue)
}
</script>
