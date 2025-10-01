<template>
  <cu-title title="Farm - Lighter" />

  <div class="mb-2">
    <cu-label name="profiles" label="Profiles" tooltip="Choose profiles to run automation." />
    <VueMultiselect name="profiles" placeholder="Select profiles..." v-model="profiles" :options="availableProfiles"
      :multiple="true" :close-on-select="false" label="name" track-by="serial_number" />
    <cu-label name="assetsToTrade" label="Assets to trade" tooltip="Choose assets to trade." />
    <VueMultiselect name="assetsToTrade" placeholder="Select assets to trade..." v-model="assetsToTrade"
      :options="availableAssetsToTrade" :multiple="true" :close-on-select="false" label="name" track-by="name" />
    <cu-checkbox name="tradeExoticAssets" v-model="tradeExoticAssets" label="Trade exotic assets"
      tooltip="Trade exotic assets." />
    <div v-if="tradeExoticAssets">
      <cu-label name="exoticAssetsToTrade" label="Exotic assets to trade"
        tooltip="Choose exotic assets to trade and set probability of picking exotic asset instead of regular asset." />
      <VueMultiselect name="exoticAssetsToTrade" placeholder="Select exotic assets to trade..."
        v-model="exoticAssetsToTrade" :options="availableExoticAssetsToTrade" :multiple="true" :close-on-select="false"
        label="name" track-by="name" />
      <cu-input name="exoticAssetsProbability" size="small" v-model="exoticAssetsProbability" label="Probability"
        placeholder="Probability" />
    </div>
  </div>

  <cu-collapsible-section name="additionalSettings" title="Additional Settings">
    <cu-label name="positionSize" label="Position size in USD"
      tooltip="Position size will be a random value between these Min and Max" />
    <div class="mt-1 grid grid-cols-6 gap-2">
      <cu-input name="minPositionUsd" size="small" v-model="minPositionUsd" label="Min "
        placeholder="Min position in USD" />
      <cu-input name="maxPositionUsd" size="small" v-model="maxPositionUsd" label="Max"
        placeholder="Max position in USD" />
    </div>
    <cu-label name="leverage" label="Leverage"
      tooltip="Leverage will be a random value between these Min and Max. Random position size will be multiplied by these random generated leverage. For example if positions size value is 100 and leverage is 5 tham automation will create position of 500" />
    <div class="mt-1 grid grid-cols-6 gap-2">
      <cu-input name="minLeverage" size="small" v-model="minLeverage" label="Min" placeholder="Min leverage" />
      <cu-input name="maxLeverage" size="small" v-model="maxLeverage" label="Max" placeholder="Max leverage" />
    </div>
    <cu-label name="holdingTime" label="Holding time in minutes"
      tooltip="Position holding time will be a random value between these Min and Max in minutes." />
    <div class="mt-1 grid grid-cols-6 gap-2">
      <cu-input name="minHoldingMinutes" size="small" v-model="minHoldingMinutes" label="Min"
        placeholder="Min holding time in minutes" />
      <cu-input name="maxHoldingMinutes" size="small" v-model="maxHoldingMinutes" label="Max"
        placeholder="Max holding time in minutes" />
    </div>
    <cu-label name="openTime" label="Open time delay in minutes"
      tooltip="After closing position aiting time will be a random value between these Min and Max in minutes. Put 0.25 if you want 15 seconds or 0.5 if you want 30 seconds" />
    <div class="mt-1 grid grid-cols-6 gap-2">
      <cu-input name="minOpenDelayMinutes" size="small" v-model="minOpenDelayMinutes" label="Min" placeholder="Min" />
      <cu-input name="maxOpenDelayMinutes" size="small" v-model="maxOpenDelayMinutes" label="Max" placeholder="Max" />
    </div>
    <div class=" mt-1 grid grid-cols-3 gap-2">
      <cu-input name="sizeMismatchPercent" size="small" v-model="sizeMismatchPercent" label="Size mismatch (%)"
        placeholder="Size mismatch (%)"
        tooltip="Due to the min size in USd for each asset order position size of all hedges might be slightly different. This percentage defines maximum allowed value. For example if hedge position is 1000 and 'Size mismatch' value is set to 0.5 it means that if difference between main and hedge position is different >0.5% positions will be closed." />
    </div>
    <div class="mt-1 grid grid-cols-3 gap-2">
      <cu-input name="liquidationThresholdPercent" size="small" v-model="liquidationThresholdPercent"
        label="Liquidation threshold (%)" placeholder="Liquidation threshold (%)"
        tooltip="Allowed perscentage of price till liquidation. For example if market price and liquidation price defference is less than 'Liquidation threshold' value, positions will be closed." />
    </div>
    <div class="mb-2">
      <cu-checkbox name="limitOrder" v-model="limitOrder" label="Limit order"
        tooltip="Enable to create main position via limit order." />
    </div>
    <div v-if="limitOrder">
      <cu-label name="verifyOrderTime" label="Verify limit order time in minutes"
        tooltip="After placing limit order position verification time will be a random value between these Min and Max in minutes. After this time if position is not filled, order will be cancelled and new one will be openned." />
      <div class="mt-1 grid grid-cols-6 gap-2">
        <cu-input name="minVerifyOrderMinutes" size="small" v-model="minVerifyOrderMinutes" label="Min"
          placeholder="Min holding time in minutes" />
        <cu-input name="maxVerifyOrderMinutes" size="small" v-model="maxVerifyOrderMinutes" label="Max"
          placeholder="Max holding time in minutes" />
      </div>
    </div>
    <div class="mb-2">
      <cu-checkbox name="setMarketOrderSlippage" v-model="setMarketOrderSlippage"
        label="Set custom market order slippage" tooltip="Enable to set custom market order slippage." />
    </div>
    <div v-if="setMarketOrderSlippage" class="mt-1 grid grid-cols-3 gap-2">
      <cu-input name="marketOrderSlippage" size="small" v-model="marketOrderSlippage" label="Market order slippage (%)"
        placeholder="Market order slippage (%)" tooltip="Slippage for market orders." />
    </div>
    <div class="mb-2">
      <cu-checkbox name="setLeverage" v-model="setLeverage" label="Set Leverage on each run"
        tooltip="Set leverage to randomly generated on each run." />
    </div>
    <div class="mb-2">
      <cu-checkbox name="logVolumes" v-model="logVolumes" label="Log Volumes"
        tooltip="Log out volume changes between runs." />
    </div>
    <div class="mb-2">
      <cu-checkbox name="getLatestStats" v-model="getLatestStats" label="Only get latest balance and volume stats"
        tooltip="Only get latest balance and volume stats, don't run trading logic." />
    </div>
    <div class="mb-2">
      <cu-checkbox name="parallelExecution" v-model="parallelExecution" label="Parallel execution"
        tooltip="Run N profiles in parallel, set how many profiles to run in a batch." />
    </div>
    <div v-if="parallelExecution" class="mt-1 grid grid-cols-6 gap-2">
      <cu-input name="profilesInBatch" size="small" v-model="profilesInBatch" placeholder="Profiles in batch" />
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
import { loadModuleData, stopModule, updateModuleData, startModule, beforeUnloadModule, beforeRouteLeaveModule, loadAdsProfiles } from '@/utils'
import { onBeforeRouteLeave } from 'vue-router'
import { initFlowbite } from 'flowbite'
import {
  CuTitle,
  CuLabel,
  CuInput,
  CuCollapsibleSection,
  CuButton,
  CuCheckbox,
  CuLogs
} from '@/components/cu'
import VueMultiselect from 'vue-multiselect'

const availableProfiles = ref([])
const profiles = ref([])

const minLeverage = ref(5)
const maxLeverage = ref(7)
const minPositionUsd = ref(75)
const maxPositionUsd = ref(100)
const minHoldingMinutes = ref(13)
const maxHoldingMinutes = ref(25)
const minOpenDelayMinutes = ref(1)
const maxOpenDelayMinutes = ref(3)
const limitOrder = ref(false)
const minVerifyOrderMinutes = ref(1)
const maxVerifyOrderMinutes = ref(1.5)
const setMarketOrderSlippage = ref(false)
const marketOrderSlippage = ref(0.05)
const sizeMismatchPercent = ref(0.5)
const liquidationThresholdPercent = ref(5)
const setLeverage = ref(false)
const assetsToTrade = ref([])
const availableAssetsToTrade = ref([])
const availableExoticAssetsToTrade = ref([])
const tradeExoticAssets = ref(false)
const exoticAssetsToTrade = ref([])
const exoticAssetsProbability = ref(3)

const logVolumes = ref(false)
const parallelExecution = ref(false)
const profilesInBatch = ref(5)
const getLatestStats = ref(false)

const logs = ref([])
const moduleRunning = ref(false)

const module = ref('premium/farm-lighter')

const { proxy } = getCurrentInstance()

const handleAppendLogs = async (log) => logs.value.unshift(log)
const handleScriptFinish = async () => moduleRunning.value = false

const loadDefaults = async () => {
  await loadAdsProfiles(proxy, (profilesData) => {
    availableProfiles.value = profilesData
  }, logs)

  await loadModuleData(proxy, module.value, 'configs', 'python', (data) => {
    if (!Object.hasOwn(data, 'assets_to_trade')) return

    availableAssetsToTrade.value = (data.assets_to_trade ?? availableAssetsToTrade.value).map(asset => ({ name: asset }))
    availableExoticAssetsToTrade.value = (data.exotic_assets_to_trade ?? availableExoticAssetsToTrade.value).map(asset => ({ name: asset }))
  }, logs)

  await loadModuleData(proxy, module.value, 'instructions', 'python', (data) => {
    if (!Object.hasOwn(data, 'profiles')) return

    profiles.value = availableProfiles.value.filter(item => (data.profiles ?? []).includes(item.serial_number))
    minLeverage.value = data.min_leverage ?? minLeverage.value
    maxLeverage.value = data.max_leverage ?? maxLeverage.value
    minPositionUsd.value = data.min_position_usd ?? minPositionUsd.value
    maxPositionUsd.value = data.max_position_usd ?? maxPositionUsd.value
    minHoldingMinutes.value = data.min_holding_minutes ?? minHoldingMinutes.value
    maxHoldingMinutes.value = data.max_holding_minutes ?? maxHoldingMinutes.value
    minOpenDelayMinutes.value = data.min_open_delay_minutes ?? minOpenDelayMinutes.value
    maxOpenDelayMinutes.value = data.max_open_delay_minutes ?? maxOpenDelayMinutes.value
    limitOrder.value = data.limit_order ?? limitOrder.value
    minVerifyOrderMinutes.value = data.min_verify_order_minutes ?? minVerifyOrderMinutes.value
    maxVerifyOrderMinutes.value = data.max_verify_order_minutes ?? maxVerifyOrderMinutes.value
    setMarketOrderSlippage.value = data.set_market_order_slippage ?? setMarketOrderSlippage.value
    marketOrderSlippage.value = data.market_order_slippage ?? marketOrderSlippage.value
    sizeMismatchPercent.value = data.size_mismatch_percent ?? sizeMismatchPercent.value
    liquidationThresholdPercent.value = data.liquidation_threshold_percent ?? liquidationThresholdPercent.value
    parallelExecution.value = data.parallel_execution ?? parallelExecution.value
    profilesInBatch.value = data.profiles_in_batch ?? profilesInBatch.value
    logVolumes.value = data.log_volumes ?? logVolumes.value
    setLeverage.value = data.set_leverage ?? setLeverage.value
    assetsToTrade.value = availableAssetsToTrade.value.filter(asset => (data.assets_to_trade ?? []).includes(asset.name))
    tradeExoticAssets.value = data.trade_exotic_assets ?? tradeExoticAssets.value
    exoticAssetsToTrade.value = availableExoticAssetsToTrade.value.filter(asset => (data.exotic_assets_to_trade ?? []).includes(asset.name))
    exoticAssetsProbability.value = data.exotic_assets_probability ?? exoticAssetsProbability.value
    getLatestStats.value = data.get_latest_stats ?? getLatestStats.value
  }, logs)
}

const handleExecute = async () => {
  moduleRunning.value = true

  await updateModuleData(proxy, module.value, 'instructions', 'python', {
    profiles: profiles.value.map(profile => profile.serial_number),
    labels: profiles.value.map(profile => profile.name),
    min_leverage: parseFloat(minLeverage.value),
    max_leverage: parseFloat(maxLeverage.value),
    min_position_usd: parseFloat(minPositionUsd.value),
    max_position_usd: parseFloat(maxPositionUsd.value),
    min_holding_minutes: parseFloat(minHoldingMinutes.value),
    max_holding_minutes: parseFloat(maxHoldingMinutes.value),
    min_open_delay_minutes: parseFloat(minOpenDelayMinutes.value),
    max_open_delay_minutes: parseFloat(maxOpenDelayMinutes.value),
    limit_order: limitOrder.value,
    min_verify_order_minutes: parseFloat(minVerifyOrderMinutes.value),
    max_verify_order_minutes: parseFloat(maxVerifyOrderMinutes.value),
    set_market_order_slippage: setMarketOrderSlippage.value,
    market_order_slippage: parseFloat(marketOrderSlippage.value),
    size_mismatch_percent: parseFloat(sizeMismatchPercent.value),
    liquidation_threshold_percent: parseFloat(liquidationThresholdPercent.value),
    parallel_execution: parallelExecution.value,
    profiles_in_batch: profilesInBatch.value,
    log_volumes: logVolumes.value,
    set_leverage: setLeverage.value,
    assets_to_trade: assetsToTrade.value.map(asset => asset.name),
    trade_exotic_assets: tradeExoticAssets.value,
    exotic_assets_to_trade: exoticAssetsToTrade.value.map(asset => asset.name),
    exotic_assets_probability: parseFloat(exoticAssetsProbability.value),
    get_latest_stats: getLatestStats.value
  }, logs)

  await startModule(proxy, module.value, logs)
}

const handleStop = async () => {
  await stopModule(proxy, module.value)
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