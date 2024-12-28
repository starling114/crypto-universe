<template>
  <li v-if="$slots.default">
    <button type="button" @click="toggleSubSection"
      :class="['flex items-center w-full p-2 text-base transition duration-75 rounded-lg group', availableModeClasses[props.mode]]">
      <slot name="left" />
      <span class="flex-1 ms-3 text-left rtl:text-right whitespace-nowrap">
        <slot name="center" />
      </span>
      <svg
        :class="['w-3 h-3 transition-transform duration-300', isDropdownOpenned ? 'transform rotate-180' : 'transform rotate-0']"
        aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 10 6">
        <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m1 1 4 4 4-4" />
      </svg>
    </button>
    <ul v-if="isDropdownOpenned" class="py-2 space-y-2">
      <li>
        <slot />
      </li>
    </ul>
  </li>
  <li v-else>
    <component :is="tag || 'div'" :to="tag === 'router-link' ? link : undefined"
      :class="['flex items-center p-2 rounded-lg group', availableModeClasses[props.mode]]">
      <slot name="left" />
      <span class="flex-1 ms-2 whitespace-nowrap">
        <slot name="center" />
      </span>
      <slot name="right"></slot>
    </component>
  </li>
</template>

<script setup>
import { defineProps, ref } from 'vue'

const props = defineProps({
  tag: { type: String, default: null },
  link: { type: String, default: '' },
  openned: { type: Boolean, default: false },
  mode: { type: String, default: 'default' }
})

const availableModeClasses = {
  default: 'text-gray-900 dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700',
  premium: 'text-red-800 dark:text-red-300 hover:bg-red-100 dark:hover:bg-red-900'
}

const isDropdownOpenned = ref(props.openned)

const toggleSubSection = () => {
  isDropdownOpenned.value = !isDropdownOpenned.value
}
</script>