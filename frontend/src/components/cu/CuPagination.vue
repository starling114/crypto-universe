<template>
  <nav class="flex items-center flex-col flex-wrap md:flex-row justify-between pt-4" aria-label="Table navigation">
    <span class="text-sm font-normal text-gray-500 dark:text-gray-400 mb-4 md:mb-0 block w-full md:inline md:w-auto">
      Showing
      <span class="font-semibold text-gray-900 dark:text-white">{{ startItem }}-{{ endItem }}</span> of
      <span class="font-semibold text-gray-900 dark:text-white">{{ totalItems }}</span>
    </span>
    <ul class="inline-flex -space-x-px rtl:space-x-reverse text-sm h-8">
      <li>
        <button @click.prevent="previousPage" :class="['border rounded-s-lg flex items-center justify-center px-3 h-8 ms-0 leading-tight',
          {
            'text-gray-500 bg-white border-gray-300 hover:bg-gray-100 hover:text-gray-900 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-white': currentPage > 1,
            'bg-gray-200 text-gray-400 dark:border-gray-700 dark:bg-gray-700 dark:text-gray-500 cursor-not-allowed': currentPage === 1
          }]" :disabled="currentPage === 1">
          Previous
        </button>
      </li>
      <li>
        <button @click.prevent="nextPage" :class="['border rounded-e-lg flex items-center justify-center px-3 h-8 ms-0 leading-tight',
          {
            'text-gray-500 bg-white border-gray-300 hover:bg-gray-100 hover:text-gray-900 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-white': currentPage < totalPages,
            'bg-gray-200 text-gray-400 dark:border-gray-700 dark:bg-gray-700 dark:text-gray-500 cursor-not-allowed': currentPage >= totalPages
          }]" :disabled="currentPage >= totalPages">
          Next
        </button>
      </li>
    </ul>
  </nav>
</template>

<script setup>
import { computed, defineProps, toRefs, defineEmits } from 'vue'

const props = defineProps({
  currentPage: { type: Number, required: true },
  totalItems: { type: Number, required: true },
  itemsPerPage: { type: Number, default: 10 }
})

const { currentPage, totalItems, itemsPerPage } = toRefs(props)
const emit = defineEmits(['update:currentPage'])

const totalPages = computed(() => Math.ceil(totalItems.value / itemsPerPage.value))
const startItem = computed(() => totalItems.value === 0 ? 0 : (currentPage.value - 1) * itemsPerPage.value + 1)
const endItem = computed(() => totalItems.value === 0 ? 0 : Math.min(currentPage.value * itemsPerPage.value, totalItems.value))

const previousPage = () => {
  if (currentPage.value > 1) {
    emit('update:currentPage', currentPage.value - 1)
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    emit('update:currentPage', currentPage.value + 1)
  }
}
</script>