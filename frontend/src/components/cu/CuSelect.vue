<template>
  <div>
    <cu-label v-if="label" :name="name" :label="label" :tooltip="tooltip" />
    <select :id="name" :value="modelValue" @change="handleChange"
      @input="$emit('update:modelValue', $event.target.value)" :class="[
        'mb-2 bg-white border border-gray-300 text-gray-900 rounded-lg focus:ring-gray-600 focus:border-gray-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-white dark:focus:border-white',
        sizeClasses]">
      <option v-if="placeholder" disabled selected>{{ placeholder }}</option>
      <option v-for="option in options" :key="getOptionValue(option)" :value="getOptionValue(option)">
        {{ getOptionLabel(option) }}
      </option>
    </select>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, computed } from 'vue'
import { CuLabel } from '@/components/cu'

const props = defineProps({
  name: { type: String, required: true },
  modelValue: { type: [String, Number, null], required: true },
  label: { type: String },
  tooltip: { type: String },
  placeholder: { type: String },
  options: { type: Array, required: true },
  size: { type: String, default: 'normal' },
  labelProp: { type: String, default: 'label' },
  valueProp: { type: String, default: 'value' }
})

const emit = defineEmits(['change'])

const availableSizeClasses = {
  small: 'text-xs p-2',
  normal: 'p-2.5'
}

const sizeClasses = computed(() => {
  return availableSizeClasses[props.size]
})

const getOptionLabel = (option) => {
  if (typeof option === 'object' && option !== null) {
    return option[props.labelProp] || option.toString()
  }
  return option
}

const getOptionValue = (option) => {
  if (typeof option === 'object' && option !== null) {
    return option[props.valueProp] || option.toString()
  }
  return option
}

const handleChange = (event) => {
  emit('change', event)
}
</script>
