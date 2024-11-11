<template>
  <div>
    <h2>
      <button type="button" @click="toggleSection" :class="[
        'flex items-center text-sm justify-between w-full text-gray-700 bg-gray-200 border-gray-200 hover:bg-gray-300 hover:border-gray-300 dark:bg-gray-700 dark:border-gray-700 dark:text-white dark:hover:bg-gray-900 p-2  font-normal rtl:text-right border focus:ring-0 focus:outline-none',
        isOpen ? 'rounded-t-lg' : 'rounded-lg'
      ]">
        <span>{{ title }}</span>
        <ChevronDownIcon
          :class="['w-6 h-6 transition-transform duration-300 dark:text-gray-500', isOpen ? 'transform rotate-180' : 'transform rotate-0']" />
      </button>
    </h2>
    <div :id="name" v-show="isOpen"
      class="p-5 text-sm font-normal border border-t-0 bg-white rounded-b-lg border-gray-200 dark:text-white dark:border-gray-700 dark:bg-gray-800"
      :aria-labelledby="name">
      <slot />
    </div>
  </div>
</template>

<script setup>
import { ref, defineProps } from 'vue'
import { ChevronDownIcon } from "@heroicons/vue/16/solid"

const props = defineProps({
  name: { type: String, required: true },
  title: { type: String, required: true },
  openned: { type: Boolean, default: false }
})

const isOpen = ref(props.openned)

const toggleSection = () => {
  isOpen.value = !isOpen.value
}
</script>
