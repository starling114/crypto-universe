<template>
  <div
    class="bg-white border border-gray-300 text-gray-900 rounded-lg block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:text-white">
    <div v-if="logs.length === 0" class="text-center">No logs available.</div>
    <div v-else class="overflow-x-auto">
      <ul class="whitespace-nowrap">
        <li v-for="(log, index) in logs" :key="index" v-html="log"></li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, ref, onMounted, onBeforeUnmount, getCurrentInstance } from 'vue'

const props = defineProps({
  logs: { type: Array, reqiured: true },
  module: { type: String, reqiured: true }
})

const emit = defineEmits(['append:logs', 'finished:script'])


const eventSource = ref(null)
const { proxy } = getCurrentInstance()

const clickableLinks = (text) => {
  const urlPattern = /https?:\/\/[^\s]+/g
  return text.replace(urlPattern, (url) =>
    `<a href="${url}" target="_blank" rel="noopener noreferrer" class="font-medium text-blue-600 dark:text-blue-500 hover:underline">${url}</a>`
  )
}

const startLogStreaming = () => {
  eventSource.value = new EventSource(`${proxy.$axios.defaults.baseURL}/api/logs?module=${props.module}`)

  eventSource.value.onmessage = (event) => {
    emit('append:logs', clickableLinks(event.data))
    if (event.data.includes("finished with exit code")) emit('finished:script')
  }

  eventSource.value.onerror = (error) => {
    emit('append:logs', error.toString())
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
