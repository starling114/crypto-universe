<template>
  <cu-title title="Mint - Magiceden" />

  <cu-textarea name="addresses" v-model="addresses" label="Wallet Addresses"
    placeholder="Enter wallet addresses each on the new line..." />
  <div class="mt-2 grid gap-2 grid-cols-6">
    <cu-select name="chain" v-model="chain" :options="availableChains" label="Network" />
    <cu-input name="launchSymbol" v-model="launchSymbol" label="Launch Symbol" placeholder="Enter launch symbol..." />
    <cu-input name="stage" v-model="stage" label="Stage" placeholder="Enter stage number..." />
    <cu-input name="quantity" v-model="quantity" label="Quantity" placeholder="Enter quantity..." />
    <cu-input name="maxFee" v-model="maxFee" label="Max Fee" placeholder="Enter max fee..." />
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

const stage = ref('')
const quantity = ref('')
const launchSymbol = ref('')
const maxFee = ref(0.2)
const mintTime = ref('10:00:00')

const logs = ref([])
const moduleRunning = ref(false)

const module = ref('premium/mint-magiceden')

const { proxy } = getCurrentInstance()

const handleAppendLogs = async (log) => logs.value.push(log)
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
    stage.value = data.stage ?? stage.value
    quantity.value = data.quantity ?? quantity.value
    maxFee.value = data.max_fee ?? maxFee.value
    launchSymbol.value = data.launch_symbol ?? launchSymbol.value
    mintTime.value = data.mint_time ?? mintTime.value
  }, logs)
  chain.value = chain.value || availableChains.value[0]
}

const handleExecute = async () => {
  moduleRunning.value = true

  await updateModuleData(proxy, module.value, 'instructions', 'python', {
    addresses: addresses.value.split('\n').filter(Boolean),
    chain: chain.value,
    stage: stage.value,
    quantity: quantity.value,
    max_fee: maxFee.value,
    launch_symbol: launchSymbol.value,
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