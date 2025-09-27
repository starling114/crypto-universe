<template>
  <cu-title title="Mint - Kingdomly" />

  <cu-textarea name="addresses" v-model="addresses" label="Wallet Addresses"
    placeholder="Enter wallet addresses each on the new line..." />
  <div class="mt-2 grid gap-2 grid-cols-1 md:grid-cols-3 sm:grid-cols-2">
    <cu-select name="chain" v-model="chain" :options="availableChains" label="Network" />
    <cu-input name="contractAddress" v-model="contractAddress" label="Contract Address"
      placeholder="Enter contract address..." />
    <cu-input name="mintId" v-model="mintId" label="Mint ID" placeholder="Enter mint id..." />
    <cu-input name="quantity" v-model="quantity" label="Quantity" placeholder="Enter quantity..." />
    <cu-input name="mintTime" v-model="mintTime" label="Mint Time"
      tooltip="Time of mint in format `HH:MM:SS` (e.g. 12:00:00)" placeholder="Enter mint time..." />
  </div>

  <div class="mt-4 mb-4 flex justify-center">
    <cu-button class="w-1/3" color="green" label="Execute" @click="handleExecute" :disabled="moduleRunning" />
    <cu-button class="w-1/3 ml-4" color="red" label="Stop" @click="handleStop" :disabled="!moduleRunning" />
  </div>

  <cu-logs :logs="logs" :module="module" @append:logs="handleAppendLogs" @finished:script="handleScriptFinish" />
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, getCurrentInstance } from 'vue'
import { loadModuleData, stopModule, updateModuleData, startModule, beforeUnloadModule, beforeRouteLeaveModule } from '@/utils'
import { onBeforeRouteLeave } from 'vue-router'
import { initFlowbite } from 'flowbite'
import {
  CuTitle,
  CuTextarea,
  CuSelect,
  CuInput,
  CuButton,
  CuLogs
} from '@/components/cu'

const addresses = ref('')

const availableChains = ref([])
const chain = ref(null)

const mintId = ref('')
const quantity = ref('')
const contractAddress = ref('')
const mintTime = ref('10:00:00')

const logs = ref([])
const moduleRunning = ref(false)

const module = ref('premium/mint-kingdomly')

const { proxy } = getCurrentInstance()

const handleAppendLogs = async (log) => logs.value.unshift(log)
const handleScriptFinish = async () => moduleRunning.value = false

const loadDefaults = async () => {
  await loadModuleData(proxy, module.value, 'configs', 'python', (data) => {
    if (!Object.hasOwn(data, 'chains')) return

    availableChains.value = data.chains ?? availableChains.value
  }, logs)

  await loadModuleData(proxy, module.value, 'instructions', 'python', (data) => {
    if (!Object.hasOwn(data, 'addresses')) return

    addresses.value = data.addresses?.join('\n') ?? addresses.value
    chain.value = data.chain ?? chain.value
    mintId.value = data.mint_id ?? mintId.value
    quantity.value = data.quantity ?? quantity.value
    contractAddress.value = data.contract_address ?? contractAddress.value
    mintTime.value = data.mint_time ?? mintTime.value
  }, logs)
  chain.value = chain.value || availableChains.value[0]
}

const handleExecute = async () => {
  moduleRunning.value = true

  await updateModuleData(proxy, module.value, 'instructions', 'python', {
    addresses: addresses.value.split('\n').filter(Boolean),
    chain: chain.value,
    mint_id: mintId.value,
    quantity: quantity.value,
    contract_address: contractAddress.value,
    mint_time: mintTime.value
  }, logs)

  await startModule(proxy, module.value, logs)
}

const handleStop = async () => {
  await stopModule(proxy, module.value)
  moduleRunning.value = false
}

const handleBeforeUnload = beforeUnloadModule(moduleRunning)

onMounted(async () => {
  initFlowbite()
  await loadDefaults()
  window.addEventListener('beforeunload', handleBeforeUnload)
})

onBeforeUnmount(() => {
  window.removeEventListener('beforeunload', handleBeforeUnload)
})

onBeforeRouteLeave(beforeRouteLeaveModule(moduleRunning, handleStop))
</script>