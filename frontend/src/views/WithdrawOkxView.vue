<template>
  <cu-title title="Withdraw OKX" />

  <div class="grid grid-cols-2 gap-2">
    <cu-textarea name="addresses" v-model="addresses" label="Destination Addresses"
      placeholder="Enter addresses each on the new line..." tooltip="Addresses you want to withdraw funds to." />
    <cu-textarea name="amounts" v-model="amounts" label="Withdrawal Amounts"
      tooltip="Amounts for the withdrawal operation corresponding to the specific address on the left."
      placeholder="Enter amounts each on the new line..." />
  </div>

  <div class="grid grid-cols-2 gap-2">
    <cu-select name="chain" v-model="chain" :options="availableChains" label="Network" @change="handleChainChange" />
    <cu-select name="symbol" v-model="symbol" :options="availableSymbols" label="Token" />
  </div>

  <cu-collapsible-section name="additionalSettings" title="Additional Settings">
    <cu-checkbox name="amountIncludesFee" v-model="amountIncludesFee" label="Amount Includes Fee"
      tooltip="Deduct fee from the amount entered in `amounts` field. Usefull when you want that exact amount to be used in the operation." />
    <cu-checkbox name="randomize" v-model="randomize" label="Randomize" tooltip="Shuffle addresses during execution." />
    <cu-checkbox name="sleep" v-model="sleep" label="Sleep"
      tooltip="Sleep between each execution, random delay is seconds based on min and max sleep is chosen." />
    <div v-if="sleep" class="mt-1 grid grid-cols-6 gap-2">
      <cu-input name="sleepDelayMin" size="small" v-model="sleepDelays[0]" placeholder="Sleep min (s)" />
      <cu-input name="sleepDelayMax" size="small" v-model="sleepDelays[1]" placeholder="Sleep max (s)" />
    </div>
  </cu-collapsible-section>

  <div class="mt-4 mb-4 flex justify-center">
    <cu-button class="w-1/3" color="green" label="Execute" @click="handleExecute" :disabled="moduleRunning" />
    <cu-button class="w-1/3 ml-4" color="red" label="Stop" @click="handleStop" :disabled="!moduleRunning" />
  </div>

  <cu-logs :logs="logs" :module="module" @append:logs="handleAppendLogs" @finished:script="handleScriptFinish" />
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, getCurrentInstance } from 'vue'
import { loadModuleData, updateModuleData, startModule, stopModule, beforeUnloadModule, beforeRouteLeaveModule } from '@/utils'
import { onBeforeRouteLeave } from 'vue-router'
import { initFlowbite } from 'flowbite'
import {
  CuTitle,
  CuTextarea,
  CuInput,
  CuSelect,
  CuCollapsibleSection,
  CuCheckbox,
  CuButton,
  CuLogs
} from '@/components/cu'

const addresses = ref('')
const amounts = ref('')

const chains = ref({})
const availableChains = ref([])
const chain = ref(null)
const availableSymbols = ref([])
const symbol = ref(null)

const amountIncludesFee = ref(true)
const randomize = ref(true)
const sleep = ref(true)
const sleepDelays = ref(['120', '240'])

const logs = ref([])
const moduleRunning = ref(false)

const module = ref('withdraw-okx')

const { proxy } = getCurrentInstance()

const handleAppendLogs = async (log) => logs.value.unshift(log)
const handleScriptFinish = async () => moduleRunning.value = false

const loadDefaults = async () => {
  await loadModuleData(proxy, module.value, 'instructions', 'python', (data) => {
    if (!Object.hasOwn(data, 'addresses')) return

    addresses.value = data.addresses.join('\n')
    amounts.value = data.amounts.join('\n')

    chain.value = data.chain ?? chain.value
    symbol.value = data.symbol ?? symbol.value

    amountIncludesFee.value = data.amount_includes_fee ?? amountIncludesFee.value
    randomize.value = data.randomize ?? randomize.value
    sleep.value = data.sleep ?? sleep.value
    sleepDelays.value = data.sleep_delays ?? sleepDelays.value
  }, logs)

  await loadModuleData(proxy, module.value, 'configs', 'python', (data) => {
    if (!Object.hasOwn(data, 'chains')) return

    chains.value = data.chains ?? chains.value
    availableChains.value = Object.keys(data.chains)
  }, logs)

  chain.value = chain.value || availableChains.value[0]
  availableSymbols.value = chainSymbols(chain.value)
  symbol.value = symbol.value || availableSymbols.value[0]
}

const handleExecute = async () => {
  moduleRunning.value = true

  await updateModuleData(proxy, module.value, 'instructions', 'python', {
    randomize: randomize.value,
    sleep: sleep.value,
    sleep_delays: sleepDelays.value,
    amount_includes_fee: amountIncludesFee.value,
    chain: chain.value,
    symbol: symbol.value,
    addresses: addresses.value.split('\n').filter(Boolean),
    amounts: amounts.value.split('\n').filter(Boolean)
  }, logs)

  await startModule(proxy, module.value, logs)
}

const handleStop = async () => {
  await stopModule(proxy, module.value)
  moduleRunning.value = false
}

const handleChainChange = async () => {
  availableSymbols.value = chainSymbols(chain.value)
  symbol.value = availableSymbols.value[0]
}

const chainSymbols = (chain) => {
  return chains.value[chain] ? chains.value[chain].tokens : []
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
