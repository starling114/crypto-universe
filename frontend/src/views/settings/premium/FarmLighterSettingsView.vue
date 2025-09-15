<template>
  <cu-title title="Farm - Lighter Settings" />
  <div class="mb-2">
    <cu-checkbox name="enableProxies" v-model="enableProxies" label="Proxies Check"
      tooltip="Enable proxies check between runs, usefull with unstable proxies" />
  </div>
  <div v-if="enableProxies" class="mt-1 grid grid-cols-6 gap-2">
    <cu-input name="profilesInBatch" size="small" v-model="profilesInBatch" placeholder="Profiles in batch" />
  </div>
  <div class="grid gap-2" :class="enableProxies ? 'grid-cols-3 ' : 'grid-cols-2'">
    <cu-textarea name="labels" v-model="labels" label="Profile Labels"
      placeholder="Enter profile labels each on the new line..."
      tooltip="Profile Labels to be used in the operations." />
    <cu-textarea v-if="enableProxies" name="proxies" v-model="proxies" label="Proxies"
      placeholder="Enter proxies in format user:password@ip:port" />
    <cu-textarea name="passwords" v-model="passwords" label="Passwords"
      placeholder="Enter passwords each on the new line..." tooltip="Password for rabby in each profile." />
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
  CuCheckbox,
  CuButton,
  CuLogs
} from '@/components/cu'


const enableProxies = ref(false)
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

    labels.value = data.labels?.join('\n') ?? labels.value
    enableProxies.value = data.enable_proxies ?? enableProxies.value
    proxies.value = data.proxies?.join('\n') ?? proxies.value
    passwords.value = data.passwords?.join('\n') ?? passwords.value
  }, logs)
}

const handleSave = async () => {
  await updateModuleData(proxy, module.value, 'secrets', 'python', {
    labels: labels.value.split('\n').filter(Boolean),
    enable_proxies: enableProxies.value,
    proxies: proxies.value.split('\n').filter(Boolean),
    passwords: passwords.value.split('\n').filter(Boolean),
  }, logs)
}

onMounted(async () => {
  initFlowbite()
  await loadDefaults()
})
</script>
