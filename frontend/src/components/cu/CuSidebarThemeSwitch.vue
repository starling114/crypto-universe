<template>
  <div class="hidden absolute bottom-0 left-0 justify-center p-4 space-x-4 w-full lg:flex z-20">
    <button @click="toggleDarkMode"
      class="inline-flex justify-center p-2 text-gray-500 rounded cursor-pointer dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-600">
      <SunIcon v-if="isDarkMode" class="w-6 h-6" />
      <MoonIcon v-else class="w-6 h-6" />
    </button>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { SunIcon, MoonIcon } from "@heroicons/vue/24/solid"

const isDarkMode = ref(false)

const loadDarkMode = () => {
  document.body.classList.add('bg-white', 'dark:bg-gray-900')

  if (localStorage.getItem('theme') === 'dark') {
    isDarkMode.value = true
    document.documentElement.classList.add('dark')
  }
}

const toggleDarkMode = () => {
  isDarkMode.value = !isDarkMode.value
  document.documentElement.classList.toggle('dark', isDarkMode.value)
}

onMounted(() => {
  loadDarkMode()
})

watch(isDarkMode, (newValue) => {
  localStorage.setItem('theme', newValue ? 'dark' : 'light')
})
</script>