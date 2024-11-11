<template>
  <nav class="flex items-center flex-col md:flex-row justify-between pt-4 w-full" aria-label="Table navigation">
    <span class="text-sm font-normal text-gray-500 dark:text-gray-400 mb-4 md:mb-0">
      Showing
      <span class="font-semibold text-gray-900 dark:text-white">{{ startItem }}-{{ endItem }}</span> of
      <span class="font-semibold text-gray-900 dark:text-white">{{ totalItems }}</span>
    </span>

    <ul class="inline-flex -space-x-px rtl:space-x-reverse text-sm h-8 mb-4 md:mb-0">
      <li>
        <button @click.prevent="previousPage" :class="['w-20 border rounded-s-lg flex items-center justify-center px-3 h-8 leading-tight',
          {
            'text-gray-500 bg-white border-gray-300 hover:bg-gray-100 hover:text-gray-900 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-white': currentPage > 1,
            'bg-gray-200 text-gray-400 dark:border-gray-700 dark:bg-gray-700 dark:text-gray-500 cursor-not-allowed': currentPage === 1
          }]" :disabled="currentPage === 1">
          Previous
        </button>
      </li>
      <li>
        <button @click.prevent="nextPage" :class="['w-20 border rounded-e-lg flex items-center justify-center px-3 h-8 leading-tight',
          {
            'text-gray-500 bg-white border-gray-300 hover:bg-gray-100 hover:text-gray-900 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-white': currentPage < totalPages,
            'bg-gray-200 text-gray-400 dark:border-gray-700 dark:bg-gray-700 dark:text-gray-500 cursor-not-allowed': currentPage >= totalPages
          }]" :disabled="currentPage >= totalPages">
          Next
        </button>
      </li>
    </ul>

    <div class="mb-4 md:mb-0">
      <select id="itemsPerPage" v-model="selectedItemsPerPage" @change="updateItemsPerPage"
        class="px-2 py-1 border border-gray-300 text-gray-900 rounded-md text-sm dark:text-gray-400 dark:bg-gray-800 focus:ring-0 focus:border-gray-300 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:border-gray-600">
        <option v-for="option in availableItemsPerPage" :key="option" :value="option">
          {{ option }}
        </option>
        <option :value="totalItems">All</option>
      </select>
    </div>
  </nav>
</template>

<script setup>
import { computed, defineProps, toRefs, defineEmits, ref } from 'vue'

const props = defineProps({
  currentPage: { type: Number, required: true },
  totalItems: { type: Number, required: true },
  itemsPerPage: { type: Number, default: 10 }
})
const availableItemsPerPage = [5, 10, 15, 25, 50]

const { currentPage, totalItems, itemsPerPage } = toRefs(props)
const emit = defineEmits(['update:currentPage', 'update:itemsPerPage'])

const selectedItemsPerPage = ref(itemsPerPage.value)

const totalPages = computed(() => Math.ceil(totalItems.value / selectedItemsPerPage.value))
const startItem = computed(() => totalItems.value === 0 ? 0 : (currentPage.value - 1) * selectedItemsPerPage.value + 1)
const endItem = computed(() => totalItems.value === 0 ? 0 : Math.min(currentPage.value * selectedItemsPerPage.value, totalItems.value))

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

const updateItemsPerPage = () => {
  emit('update:itemsPerPage', selectedItemsPerPage.value)
  emit('update:currentPage', 1)
}
</script>