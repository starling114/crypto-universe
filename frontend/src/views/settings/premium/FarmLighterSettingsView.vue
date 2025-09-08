<template>
  <cu-title title="Farm - Lighter Settings" />
  <div class="grid grid-cols-3 gap-2">
    <cu-textarea name="labels" v-model="labels" label="Profile Labels"
      placeholder="Enter profile labels each on the new line..."
      tooltip="Profile Labels to be used in the operations." />
    <cu-textarea name="proxies" v-model="proxies" label="Proxies" placeholder="Enter proxies each on the new line..." />
    <cu-textarea name="passwords" v-model="passwords" label="Passwords"
      placeholder="Enter passwords each on the new line..." />
  </div>

  <div class="mt-4 mb-4 flex justify-center">
    <cu-button class="w-1/3" color="green" label="Save" @click="handleSave" />
  </div>

  <cu-logs :logs="logs" :module="module" @append:logs="handleAppendLogs" />
</template>

<script setup>
import { ref, onMounted, getCurrentInstance } from 'vue'
import { loadModuleData, updateModuleData } from '@/utils'
import { initFlowbite } from 'flowbite'
import {
  CuTitle,
  CuTextarea,
  CuButton,
  CuLogs
} from '@/components/cu'


const labels = ref('')
const proxies = ref('')
const passwords = ref('')

const module = ref('premium/farm-lighter')

const logs = ref([])

const { proxy } = getCurrentInstance()

const handleAppendLogs = async (log) => logs.value.push(log)

const loadDefaults = async () => {
  await loadModuleData(proxy, module.value, 'secrets', 'python', (data) => {
    if (!Object.hasOwn(data, 'labels')) return

    labels.value = data.labels.join('\n')
    proxies.value = data.proxies.join('\n')
    passwords.value = data.passwords.join('\n')
  }, logs)
}

const handleSave = async () => {
  await updateModuleData(proxy, module.value, 'secrets', 'python', {
    labels: labels.value.split('\n').filter(Boolean),
    proxies: proxies.value.split('\n').filter(Boolean),
    passwords: passwords.value.split('\n').filter(Boolean),
  }, logs)
}

onMounted(async () => {
  initFlowbite()
  await loadDefaults()
})
</script>
