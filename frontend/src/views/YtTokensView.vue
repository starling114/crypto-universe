<template>
  <cu-title title="YT Tokens via Pendle" />

  <div class="mt-2 grid grid-cols-2 gap-2">
    <cu-select name="chain" v-model="chain" :options="availableChains" label="Network" @change="handleChainChange" />
    <cu-select name="symbol" v-model="symbol" :options="availableSymbols" label="Token"
      tooltip="Token used to swap to YT token" />
  </div>

  <div class="mb-2">
    <cu-label name="ytToken" label="YT Token" tooltip="Choose YT Token to buy." />
    <VueMultiselect name="ytToken" placeholder="Select YT token..." v-model="ytToken" :options="availableYtTokens"
      :loading="ytTokensLoading" label="symbol" track-by="symbol" />
  </div>

  <div class="mt-2 grid grid-cols-2 gap-2">
    <cu-textarea name="addresses" v-model="addresses" label="Wallet Addresses"
      placeholder="Enter wallet addresses each on the new line..." tooltip="Wallet addresses for the swap operation." />
    <cu-textarea name="amounts" v-model="amounts" label="Swap Amounts"
      tooltip="Amounts for the swap operation corresponding to the specific wallet address on the left."
      placeholder="Enter amounts each on the new line..." />
  </div>

  <cu-collapsible-section name="additionalSettings" title="Additional Settings">
    <div v-if="chain == 'ethereum'" class="mt-1 grid grid-cols-4 gap-2">
      <cu-input name="maxEthereumGasPrice" size="small" v-model="maxEthereumGasPrice" label="Max Ethereum Gas Price"
        tooltip="Fail execution if gas price exceeds this value" placeholder="Enter gas price in gwei..." />
    </div>
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
  CuLabel,
  CuTextarea,
  CuInput,
  CuSelect,
  CuCollapsibleSection,
  CuCheckbox,
  CuButton,
  CuLogs
} from '@/components/cu'
import VueMultiselect from 'vue-multiselect'

const availableChains = ref([])
const chain = ref(null)
const availableSymbols = ref([])
const symbol = ref(null)
const availableYtTokens = ref([])
const ytTokensLoading = ref(false)
const ytToken = ref(null)
const addresses = ref('')
const amounts = ref('')

const maxEthereumGasPrice = ref(5)
const randomize = ref(true)
const sleep = ref(true)
const sleepDelays = ref(['120', '240'])

const chains = ref({})

const logs = ref([])
const moduleRunning = ref(false)

const module = ref('yt_tokens')

const { proxy } = getCurrentInstance()

const handleAppendLogs = async (log) => logs.value.unshift(log)
const handleScriptFinish = async () => moduleRunning.value = false

const loadDefaults = async () => {
  await loadModuleData(proxy, module.value, 'instructions', 'python', (data) => {
    if (!Object.hasOwn(data, 'chain')) return

    chain.value = data.chain ?? chain.value
    symbol.value = data.symbol ?? symbol.value
    ytToken.value = data.yt_token ?? ytToken.value
    addresses.value = data.addresses.join('\n')
    amounts.value = data.amounts.join('\n')
    maxEthereumGasPrice.value = data.max_ethereum_gas_price ?? maxEthereumGasPrice.value

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
  availableYtTokens.value = await pendleYtTokens(chain.value)
  ytToken.value = ytToken.value || availableYtTokens.value[0]
}

const handleExecute = async () => {
  moduleRunning.value = true

  await updateModuleData(proxy, module.value, 'instructions', 'python', {
    chain: chain.value,
    symbol: symbol.value,
    yt_token: ytToken.value,
    addresses: addresses.value.split('\n').filter(Boolean),
    amounts: amounts.value.split('\n').filter(Boolean),
    max_ethereum_gas_price: maxEthereumGasPrice.value,
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
  availableYtTokens.value = await pendleYtTokens(chain.value)
  ytToken.value = availableYtTokens.value[0]
}

const chainSymbols = (chain) => {
  return chains.value[chain] ? chains.value[chain].tokens : []
}

const pendleYtTokens = async (chain) => {
  ytTokensLoading.value = true
  const chainId = proxy.$globalConfigs.configs.chains[chain].chain_id

  return await proxy.$axios.get(`https://api-v2.pendle.finance/core/v1/${chainId}/markets`, {
    is_expired: 'false',
    is_active: 'true'
  }).then((response) => {
    ytTokensLoading.value = false

    return response.data.results.map(market => {
      return {
        market_address: market.address,
        symbol: `${market.yt.proSymbol} (${market.yt.symbol})`,
        address: market.yt.address
      }
    })
  }).catch((error) => {
    ytTokensLoading.value = false
    logs.value.push(`Error fetching data from Pendle: ${error}`)
    return []
  })
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

<style src="vue-multiselect/dist/vue-multiselect.css"></style>

<style>
.multiselect__tags {
  @apply bg-white border border-gray-300 text-gray-900 rounded-lg focus:ring-gray-600 focus:border-gray-600 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-white dark:focus:border-white;
}

.multiselect__single {
  @apply bg-white text-gray-900 focus:ring-gray-600 dark:bg-gray-700 dark:placeholder-gray-400 dark:text-white;
}

.multiselect__tag {
  @apply bg-orange-600 hover:bg-orange-700 dark:bg-orange-600 dark:hover:bg-orange-700;
}

.multiselect__tag-icon:after {
  @apply text-white;
}

.multiselect__input {
  @apply bg-white text-sm focus:border-gray-300 focus:ring-gray-600 dark:focus:ring-gray-600 text-gray-900 dark:bg-gray-800 dark:focus:border-gray-600 dark:placeholder-gray-400 dark:text-white;
}

.multiselect__content-wrapper {
  @apply bg-white text-gray-900 border-gray-300 dark:bg-gray-700 dark:text-white dark:border-gray-600;
}

.multiselect__option--selected,
.multiselect__option--selected:after {
  @apply bg-gray-200 text-gray-900 dark:text-white dark:bg-gray-800;
}

.multiselect__option--highlight,
.multiselect__option--highlight:after {
  @apply bg-green-600 dark:bg-green-600;
}

.multiselect__option--selected.multiselect__option--highlight,
.multiselect__option--selected.multiselect__option--highlight:after {
  @apply bg-orange-600 dark:bg-orange-600;
}
</style>