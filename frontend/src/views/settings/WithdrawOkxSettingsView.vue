<template>
  <cu-title title="Withdraw OKX Settings" />

  <cu-input name="apiKey" v-model="apiKey" label="API Key" tooltip="API Key from OKX API integration section" />

  <cu-input name="apiSecret" v-model="apiSecret" label="API Secret"
    tooltip="API Secret from OKX API integration section" />

  <cu-input name="password" v-model="password" label="Passphrase"
    tooltip="Passphrase from OKX API integration section" />


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
  CuInput,
  CuButton,
  CuLogs
} from '@/components/cu'

const apiKey = ref('')
const apiSecret = ref('')
const password = ref('')

const logs = ref([])

const module = ref('withdraw-okx')

const { proxy } = getCurrentInstance()

const handleAppendLogs = async (log) => logs.value.push(log)

const loadDefaults = async () => {
  await loadModuleData(proxy, module.value, 'secrets', 'python', (data) => {
    if (!Object.hasOwn(data, 'api_key')) return

    apiKey.value = data.api_key
    apiSecret.value = data.api_secret
    password.value = data.password
  }, logs)
}

const handleSave = async () => {
  await updateModuleData(proxy, module.value, 'secrets', 'python', {
    api_key: apiKey.value,
    api_secret: apiSecret.value,
    password: password.value
  }, logs)
}

onMounted(async () => {
  initFlowbite()
  await loadDefaults()
})
</script>
