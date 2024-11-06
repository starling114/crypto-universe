<template>
  <cu-title title="Transfer" />

  <cu-checkbox name="leaveBalance" v-model="leaveBalance" label="Leave Balance Amount"
    tooltip="Leave this amount on the balance and transfer everything else. Use this option and set amount to 0 to withdraw all the funds." />
  <div v-if="leaveBalance" class="mt-1 grid grid-cols-4 gap-2">
    <cu-input name="leaveBalanceAmount" v-model="leaveBalanceAmount" placeholder="Leave amount..." />
  </div>

  <div class="mt-2 grid gap-2" :class="leaveBalance ? 'grid-cols-2 ' : 'grid-cols-3'">
    <cu-textarea name="sourceAddresses" v-model="sourceAddresses" label="Source Addresses"
      placeholder="Enter addresses each on the new line..." tooltip="Addresses you want to transfer funds from." />
    <cu-textarea v-if="!leaveBalance" name="amounts" v-model="amounts" label="Transfer Amounts"
      tooltip="Amounts for the transfer operation corresponding to the specific address on the left and right."
      placeholder="Enter amounts each on the new line..." />
    <cu-textarea name="destinationAddresses" v-model="destinationAddresses" label="Destination Addresses"
      placeholder="Enter addresses each on the new line..." tooltip="Addresses you want to transfer  funds to." />
  </div>

  <cu-checkbox name="useCustomAsset" v-model="useCustomAsset" label="Custom Asset"
    tooltip="Use custom asset by specifying its contract address." />
  <div v-if="useCustomAsset" class="mb-2 mt-1">
    <cu-input name="customAsset" v-model="customAsset" placeholder="Contract Address..." />
  </div>

  <div class="mt-2" :class="{ 'grid grid-cols-2 gap-2': !useCustomAsset }">
    <cu-select name="chain" v-model="chain" :options="availableChains" label="Network" @change="handleChainChange" />
    <cu-select v-if="!useCustomAsset" name="symbol" v-model="symbol" :options="availableSymbols" label="Asset" />
  </div>

  <cu-collapsible-section name="additionalSettings" title="Additional Settings">
    <cu-checkbox name="randomize" v-model="randomize" label="Randomize"
      tooltip="Shuffle addresses during execution." />
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

const leaveBalance = ref(false)
const leaveBalanceAmount = ref('')

const sourceAddresses = ref('')
const amounts = ref('')
const destinationAddresses = ref('')

const useCustomAsset = ref(false)
const customAsset = ref('')
const availableChains = ref([])
const chain = ref(null)
const availableSymbols = ref([])
const symbol = ref(null)

const randomize = ref(true)
const sleep = ref(true)
const sleepDelays = ref(['120', '240'])

const chains = ref({})

const logs = ref([])
const moduleRunning = ref(false)

const module = ref('transfer')

const { proxy } = getCurrentInstance()

const handleAppendLogs = async (log) => logs.value.push(log)
const handleScriptFinish = async () => moduleRunning.value = false

const loadDefaults = async () => {
  await loadModuleData(proxy, module.value, 'instructions', 'python', (data) => {
    if (!Object.hasOwn(data, 'leave_balance')) return

    leaveBalance.value = data.leave_balance
    leaveBalanceAmount.value = data.leave_balance_amount

    sourceAddresses.value = data.source_addresses.join('\n')
    amounts.value = data.amounts.join('\n')
    destinationAddresses.value = data.destinaion_addresses.join('\n')

    useCustomAsset.value = data.use_custom_asset
    customAsset.value = data.custom_asset
    chain.value = data.chain
    symbol.value = data.symbol

    randomize.value = data.randomize
    sleep.value = data.sleep
    sleepDelays.value = data.sleep_delays
  }, logs)

  await loadModuleData(proxy, module.value, 'configs', 'python', (data) => {
    if (!Object.hasOwn(data, 'chains')) return

    chains.value = data.chains
    availableChains.value = Object.keys(data.chains)
  }, logs)

  chain.value = chain.value || availableChains.value[0]
  availableSymbols.value = chainSymbols(chain.value)
  symbol.value = symbol.value || availableSymbols.value[0]
}

const handleExecute = async () => {
  moduleRunning.value = true

  await updateModuleData(proxy, module.value, 'instructions', 'python', {
    leave_balance: leaveBalance.value,
    leave_balance_amount: leaveBalanceAmount.value,
    source_addresses: sourceAddresses.value.split('\n').filter(Boolean),
    amounts: amounts.value.split('\n').filter(Boolean),
    destinaion_addresses: destinationAddresses.value.split('\n').filter(Boolean),
    use_custom_asset: useCustomAsset.value,
    custom_asset: customAsset.value,
    chain: chain.value,
    symbol: symbol.value,
    randomize: randomize.value,
    sleep: sleep.value,
    sleep_delays: sleepDelays.value
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
