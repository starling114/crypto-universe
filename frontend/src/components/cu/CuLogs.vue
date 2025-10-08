<template>
  <div
    class="bg-white border border-gray-300 text-gray-900 rounded-lg block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:text-white flex flex-col relative">
    <div v-if="logs.length === 0" class="text-center">No logs available.</div>
    <div v-else class="overflow-x-auto flex-1" ref="logContainer">
      <ul class="whitespace-nowrap">
        <li v-for="(log, index) in logs" :key="index" v-html="log"></li>
      </ul>
    </div>
    <div v-if="logs.length >= 50" class="absolute top-2 right-2 flex flex-col space-y-2">
      <button @click="toggleAutoScroll"
        class="px-3 py-2 text-xs font-medium text-center rounded-lg text-gray-700 bg-white border-white hover:bg-gray-300 hover:border-gray-300 dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:hover:bg-gray-900 focus:ring-0 focus:outline-none">
        To Bottom
      </button>
      <button v-if="clear" @click="clearLogs"
        class="px-3 py-2 text-xs font-medium text-center rounded-lg text-gray-700 bg-white border-white hover:bg-gray-300 hover:border-gray-300 dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:hover:bg-gray-900 focus:ring-0 focus:outline-none">
        Clear Logs
      </button>
    </div>
    <button v-if="logs.length >= 50" @click="toggleAutoScroll"
      class="px-3 py-2 text-xs font-medium text-center rounded-lg text-gray-700 bg-white border-white hover:bg-gray-300 hover:border-gray-300 dark:bg-gray-700 dark:border-gray-700 dark:text-white dark:hover:bg-gray-900 focus:ring-0 focus:outline-none self-end">
      To Top
    </button>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, ref, onMounted, onBeforeUnmount, getCurrentInstance } from 'vue'

const props = defineProps({
  logs: { type: Array, required: true },
  module: { type: String, required: true },
  clear: { type: Boolean, default: false }
})

const emit = defineEmits(['append:logs', 'finished:script', 'clear:logs'])

const eventSource = ref(null)
const isAutoScrolling = ref(false)

const { proxy } = getCurrentInstance()

const formatLogs = (text) => {
  let newText = text
  const replaces = [
    {
      regex: /https?:\/\/[^\s]+/g,
      replaceText: (match) =>
        `<a href="${match}" target="_blank" rel="noopener noreferrer" class="font-medium text-blue-600 dark:text-blue-500 hover:underline">${match}</a>`,
    },
    {
      regex: /\b0x[a-fA-F0-9]{40}\b/g,
      replaceText: (match) =>
        `<a href="https://debank.com/profile/${match}/history" target="_blank" rel="noopener noreferrer" class="font-medium text-blue-600 dark:text-blue-500 hover:underline">${match}</a>`,
    }
  ]

  replaces.forEach(({ regex, replaceText }) => {
    newText = newText.replace(regex, replaceText)
  })

  return newText
}

const startLogStreaming = () => {
  eventSource.value = new EventSource(`${proxy.$axios.defaults.baseURL}/api/logs?module=${props.module}`)

  eventSource.value.onmessage = (event) => {
    emit('append:logs', formatLogs(event.data))
    if (event.data.includes("finished with exit code")) emit('finished:script')
    if (isAutoScrolling.value) {
      scrollToBottom()
    }
  }

  eventSource.value.onerror = () => {
    emit('append:logs', 'Logs fetching error')
  }
}

const scrollToBottom = () => {
  window.scrollTo(0, document.body.scrollHeight)
}

const scrollToTop = () => {
  window.scrollTo(0, 0)
}

const clearLogs = () => {
  emit('clear:logs')
}

const toggleAutoScroll = () => {
  isAutoScrolling.value = !isAutoScrolling.value
  if (isAutoScrolling.value) {
    scrollToBottom()
  } else {
    scrollToTop()
  }
}

onMounted(() => {
  startLogStreaming()
})

onBeforeUnmount(() => {
  if (eventSource.value) {
    eventSource.value.close()
  }
})
</script>
