<template>
  <cu-title title="Swap Jumper" />

  <cu-checkbox name="leaveBalance" v-model="leaveBalance" label="Leave Balance Amount"
    tooltip="Leave this amount on the balance after the operation." />
  <div v-if="leaveBalance" class="mt-1 grid grid-cols-4 gap-2">
    <cu-input name="leaveBalanceAmount" v-model="leaveBalanceAmount" placeholder="Leave amount..." />
  </div>

  <div class="mt-2" :class="{ 'grid grid-cols-2 gap-2': !leaveBalance }">
    <cu-textarea name="addresses" v-model="addresses" label="Wallet Addresses"
      placeholder="Enter wallet addresses each on the new line..." />
    <cu-textarea v-if="!leaveBalance" name="amounts" v-model="amounts" label="Amounts"
      tooltip="Amounts corresponding to the specific wallet address on the left."
      placeholder="Enter amounts each on the new line..." />
  </div>

  <cu-checkbox name="useCustomSymbols" v-model="useCustomSymbols" label="Custom Symbols"
    tooltip="Use custom symbols by specifying their contract address." />

  <div class="mt-2" :class="{ 'grid grid-cols-3 gap-2': !useCustomSymbols }">
    <cu-select name=" chain" v-model="chain" :options="availableChains" @change="handleChainChange" label="Network" />
    <cu-select v-if="!useCustomSymbols" name="fromSymbol" v-model="fromSymbol" :options="availableSymbols"
      @change="handleFromSymbolChange" label="From Token" />
    <cu-select v-if="!useCustomSymbols" name="toSymbol" v-model="toSymbol" :options="availableSymbols"
      @change="handleToSymbolChange" label="To Token" />
  </div>

  <div v-if="useCustomSymbols" class="mb-2 mt-1 grid grid-cols-2 gap-2">
    <cu-input name="customFromSymbol" v-model="customFromSymbol" label="Custom From Token"
      placeholder="Contract Address..."
      tooltip="Enter `0x0000000000000000000000000000000000000000` for native token." />
    <cu-input name="customToSymbol" v-model="customToSymbol" label="Custom To Token" placeholder="Contract Address..."
      tooltip="Enter `0x0000000000000000000000000000000000000000` for native token." />
  </div>

  <cu-collapsible-section name="additionalSettings" title="Additional Settings">
    <cu-checkbox name="amountIncludesFee" v-model="amountIncludesFee" label="Amount Includes Fee"
      tooltip="Deduct fee from the amount entered in `amounts` field. Usefull when you want that exact amount to be used in the operation using native token." />
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
import { ref, onMounted, onBeforeUnmount, getCurrentInstance, watch } from 'vue'
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
const chain = ref(null)

const useCustomSymbols = ref(false)
const customFromSymbol = ref('')
const customToSymbol = ref('')

const availableSymbols = ref([])
const fromSymbol = ref(null)
const toSymbol = ref(null)
const previousFromSymbol = ref(null)
const previousToSymbol = ref(null)

const amountIncludesFee = ref(true)
const randomize = ref(true)
const sleep = ref(true)
const sleepDelays = ref(['120', '240'])

const chains = ref({})

const logs = ref([])
const moduleRunning = ref(false)

const module = ref('swap-jumper')

const { proxy } = getCurrentInstance()

const handleAppendLogs = async (log) => logs.value.push(log)
const handleScriptFinish = async () => moduleRunning.value = false

const loadDefaults = async () => {
  await loadModuleData(proxy, module.value, 'instructions', 'python', (data) => {
    if (!Object.hasOwn(data, 'leave_balance')) return

    leaveBalance.value = data.leave_balance ?? leaveBalance.value
    leaveBalanceAmount.value = data.leave_balance_amount ?? leaveBalanceAmount.value

    addresses.value = data.addresses.join('\n')
    amounts.value = data.amounts.join('\n')

    chain.value = data.chain ?? chain.value
    useCustomSymbols.value = data.use_custom_symbols ?? useCustomSymbols.value
    customFromSymbol.value = data.custom_from_symbol ?? customFromSymbol.value
    customToSymbol.value = data.custom_to_symbol ?? customToSymbol.value
    fromSymbol.value = data.from_symbol ?? fromSymbol.value
    toSymbol.value = data.to_symbol ?? toSymbol.value

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
  fromSymbol.value = fromSymbol.value || availableSymbols.value[0]
  previousFromSymbol.value = fromSymbol.value
  toSymbol.value = toSymbol.value || availableSymbols.value[1]
  previousToSymbol.value = toSymbol.value
}

const handleExecute = async () => {
  moduleRunning.value = true

  await updateModuleData(proxy, module.value, 'instructions', 'python', {
    leave_balance: leaveBalance.value,
    leave_balance_amount: leaveBalanceAmount.value,
    addresses: addresses.value.split('\n').filter(Boolean),
    amounts: amounts.value.split('\n').filter(Boolean),
    chain: chain.value,
    use_custom_symbols: useCustomSymbols.value,
    custom_from_symbol: customFromSymbol.value,
    custom_to_symbol: customToSymbol.value,
    from_symbol: fromSymbol.value,
    to_symbol: toSymbol.value,
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

const handleChainChange = async () => {
  availableSymbols.value = chainSymbols(chain.value)
  fromSymbol.value = availableSymbols.value[0]
  previousFromSymbol.value = fromSymbol.value
  toSymbol.value = availableSymbols.value[1]
  previousToSymbol.value = toSymbol.value
}

const handleFromSymbolChange = async () => {
  const oldFromSymbol = previousFromSymbol.value
  previousFromSymbol.value = fromSymbol.value

  if (fromSymbol.value === toSymbol.value) {
    fromSymbol.value = toSymbol.value
    toSymbol.value = oldFromSymbol
    previousToSymbol.value = toSymbol.value
  }
}

const handleToSymbolChange = async () => {
  const oldToSymbol = previousToSymbol.value
  previousToSymbol.value = toSymbol.value

  if (toSymbol.value === fromSymbol.value) {
    toSymbol.value = fromSymbol.value
    fromSymbol.value = oldToSymbol
    previousFromSymbol.value = fromSymbol.value
  }
}

const chainSymbols = (chain) => {
  return chains.value[chain] ? chains.value[chain].tokens : []
}

const handleBeforeUnload = beforeUnloadModule(moduleRunning)

watch([leaveBalance, useCustomSymbols], () => {
  setTimeout(() => {
    initFlowbite()
  }, 10)
})

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
