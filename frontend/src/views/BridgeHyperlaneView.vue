<template>
  <cu-title title="Bridge Hyperlane" />

  <cu-checkbox name="leaveBalance" v-model="leaveBalance" label="Leave Balance Amount"
    tooltip="Leave this amount on the balance and withdraw everything else." />
  <div v-if="leaveBalance" class="mt-1 grid grid-cols-4 gap-2">
    <cu-input name="leaveBalanceAmount" v-model="leaveBalanceAmount" placeholder="Leave amount..." />
  </div>

  <div class="mt-2" :class="{ 'grid grid-cols-2 gap-2': !leaveBalance }">
    <cu-textarea name="addresses" v-model="addresses" label="Wallet Addresses"
      placeholder="Enter wallet addresses each on the new line..."
      tooltip="Wallet addresses for the bridge operation." />
    <cu-textarea v-if="!leaveBalance" name="amounts" v-model="amounts" label="Bridge Amounts"
      tooltip="Amounts for the bridge operation corresponding to the specific wallet address on the left."
      placeholder="Enter amounts each on the new line..." />
  </div>

  <div class="grid grid-cols-3 gap-3">
    <cu-select name="fromChain" v-model="fromChain" :options="availableChains" @change="handleFromChainChange"
      label="Source Network" />
    <cu-select name="toChain" v-model="toChain" :options="availableChains" @change="handleToChainChange"
      label="Destination Network" />
    <cu-select name="fromSymbol" v-model="fromSymbol" :options="availableFromSymbols" label="Token" />
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
  CuCheckbox,
  CuInput,
  CuTextarea,
  CuSelect,
  CuCollapsibleSection,
  CuButton,
  CuLogs
} from '@/components/cu'

const leaveBalance = ref(false)
const leaveBalanceAmount = ref('0.0005')
const addresses = ref('')
const amounts = ref('')
const availableChains = ref([])
const fromChain = ref(null)
const toChain = ref(null)
const previousFromChain = ref(null)
const previousToChain = ref(null)
const availableFromSymbols = ref([])
const fromSymbol = ref(null)

const amountIncludesFee = ref(true)
const randomize = ref(true)
const sleep = ref(true)
const sleepDelays = ref(['120', '240'])

const chains = ref({})

const logs = ref([])
const moduleRunning = ref(false)

const module = ref('bridge-hyperlane')

const { proxy } = getCurrentInstance()

const handleAppendLogs = async (log) => logs.value.push(log)
const handleScriptFinish = async () => moduleRunning.value = false

const loadDefaults = async () => {
  await loadModuleData(proxy, module.value, 'instructions', 'python', (data) => {
    if (!Object.hasOwn(data, 'leave_balance')) return

    leaveBalance.value = data.leave_balance
    leaveBalanceAmount.value = data.leave_balance_amount

    addresses.value = data.addresses.join('\n')
    amounts.value = data.amounts.join('\n')

    fromChain.value = data.from_chain
    toChain.value = data.to_chain
    fromSymbol.value = data.from_symbol

    amountIncludesFee.value = data.amount_includes_fee
    randomize.value = data.randomize
    sleep.value = data.sleep
    sleepDelays.value = data.sleep_delays
  }, logs)

  await loadModuleData(proxy, module.value, 'configs', 'python', (data) => {
    if (!Object.hasOwn(data, 'chains')) return

    chains.value = data.chains
    availableChains.value = Object.keys(data.chains)
  }, logs)

  fromChain.value = fromChain.value || availableChains.value[0]
  previousFromChain.value = fromChain.value
  toChain.value = toChain.value || availableChains.value[1]
  previousToChain.value = toChain.value
  availableFromSymbols.value = chainSymbols(fromChain.value)
  fromSymbol.value = fromSymbol.value || availableFromSymbols.value[0]
}

const handleExecute = async () => {
  moduleRunning.value = true

  await updateModuleData(proxy, module.value, 'instructions', 'python', {
    leave_balance: leaveBalance.value,
    leave_balance_amount: leaveBalanceAmount.value,
    addresses: addresses.value.split('\n').filter(Boolean),
    amounts: amounts.value.split('\n').filter(Boolean),
    from_chain: fromChain.value,
    to_chain: toChain.value,
    from_symbol: fromSymbol.value,
    amount_includes_fee: amountIncludesFee.value,
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

const handleFromChainChange = async () => {
  const oldFromChain = previousFromChain.value
  previousFromChain.value = fromChain.value

  if (fromChain.value === toChain.value) {
    fromChain.value = toChain.value
    toChain.value = oldFromChain
    previousToChain.value = toChain.value
  }

  availableFromSymbols.value = chainSymbols(fromChain.value)
  fromSymbol.value = availableFromSymbols.value[0]
}

const handleToChainChange = async () => {
  const oldToChain = previousToChain.value
  previousToChain.value = toChain.value

  if (toChain.value === fromChain.value) {
    toChain.value = fromChain.value
    fromChain.value = oldToChain
    previousFromChain.value = fromChain.value
  }
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
