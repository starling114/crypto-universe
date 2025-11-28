<template>
  <cu-title title="Airdrop - Perps" />

  <div v-if="editingBatchIndex !== null"
    class="mb-4 p-3 bg-yellow-100 dark:bg-yellow-900 rounded-lg border border-yellow-300 dark:border-yellow-700">
    <div class="text-sm font-semibold text-yellow-900 dark:text-yellow-200">
      Editing Batch #{{ editingBatchIndex + 1 }}
    </div>
  </div>

  <div class="mb-2">
    <cu-label name="assetsToTrade" label="Assets to trade" tooltip="Choose assets to trade." />
    <div class="mb-2">
      <cu-checkbox name="customAssets" v-model="customAssetsEnabled" label="Custom assets"
        tooltip="Enable to specify assets not present in the list." />
    </div>
    <div v-if="!customAssetsEnabled">
      <VueMultiselect name="assetsToTrade" placeholder="Select assets to trade..." v-model="assetsToTrade"
        :options="availableAssetsToTrade" :multiple="true" :close-on-select="false" label="name" track-by="name" />
    </div>
    <div v-else class="mt-1 grid grid-cols-3 gap-2">
      <cu-input name="customAssetsInput" size="small" v-model="customAssetsInput" placeholder="e.g., BTC, ETH, SOL"
        tooltip="Enter comma separated assets." />
    </div>
    <cu-checkbox name="tradeExoticAssets" v-model="tradeExoticAssets" label="Trade exotic assets"
      tooltip="Choose exotic assets to trade and set probability of picking exotic asset instead of regular asset." />
    <div v-if="tradeExoticAssets">
      <cu-label name="exoticAssetsToTrade" />
      <VueMultiselect name="exoticAssetsToTrade" placeholder="Select exotic assets to trade..."
        v-model="exoticAssetsToTrade" :options="availableExoticAssetsToTrade" :multiple="true" :close-on-select="false"
        label="name" track-by="name" />
      <cu-input name="exoticAssetsProbability" size="small" v-model="exoticAssetsProbability" label="Probability"
        placeholder="Probability" />
    </div>

    <div class="mt-2 grid grid-cols-2 gap-2">
      <cu-select name="mainPerpType" v-model="currentMainPerpType" :options="availablePerps" label="Main Perp" />
      <cu-select name="hedgePerpType" v-model="currentHedgePerpType" :options="availablePerps" label="Hedge Perp" />
    </div>
    <cu-label name="currentProfiles" label="Profiles for this batch" tooltip="Choose profiles for this batch." />
    <VueMultiselect name="currentProfiles" placeholder="Select profiles..." v-model="currentProfiles"
      :options="availableProfilesForSelection" :multiple="true" :close-on-select="false" label="name"
      track-by="serial_number" />
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
      <cu-checkbox name="limitCancelOrder" v-model="limitCancelOrder" label="Limit cancel order"
        tooltip="Enable to cancel main position via limit order." />
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
        label="Set custom market order slippage"
        tooltip="Enable to set custom market order slippage on perps where possible (Lighter)." />
    </div>
    <div v-if="setMarketOrderSlippage" class="mt-1 grid grid-cols-3 gap-2">
      <cu-input name="marketOrderSlippage" size="small" v-model="marketOrderSlippage" label="Market order slippage (%)"
        placeholder="Market order slippage (%)" tooltip="Slippage for market orders." />
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
      <cu-checkbox name="stopProcessing" v-model="stopProcessing" label="Close all orders and positions"
        tooltip="use this to close all orders and positions, trading cycle won't be executed." />
    </div>
    <div class="mb-2">
      <cu-checkbox name="minimumCycleBalanceCheck" v-model="minimumCycleBalanceCheck"
        label="Check minimum allowed balance value"
        tooltip="Enable to fail cycles if any of the balances is less than allowed one." />
    </div>
    <div v-if="minimumCycleBalanceCheck" class="mt-1 grid grid-cols-3 gap-2">
      <cu-input name="minimumCycleBalance" size="small" v-model="minimumCycleBalance" label="Minimum allowed balance"
        placeholder="Minimum allowed balance" />
    </div>
    <div class="mb-2">
      <cu-checkbox name="alwaysUseFirstAsMain" v-model="alwaysUseFirstAsMain" label="Always use first profile as main"
        tooltip="Always use the first profile in each batch as the main profile." />
    </div>
    <div v-if="alwaysUseFirstAsMain" class="mb-2">
      <cu-checkbox name="tradeMainAsSpot" v-model="tradeMainAsSpot" label="Trade main as spot"
        tooltip="Trade main as spot when always use first as main is enabled." />
    </div>
    <div class="mb-2">
      <cu-checkbox name="customMainPositionSide" v-model="customMainPositionSide" label="Custom main position side"
        tooltip="Enable to choose a fixed main position side." />
    </div>
    <div v-if="customMainPositionSide" class="mt-1 grid grid-cols-3 gap-2">
      <cu-select name="mainPositionSide" size="small" v-model="mainPositionSide" :options="availableSides"
        label="Main position side" />
    </div>
    <div class="mb-2">
      <cu-checkbox name="tradeCycles" v-model="tradeCycles" label="Trade N cycles"
        tooltip="Enable to set a specific number of trading cycles to execute." />
    </div>
    <div v-if="tradeCycles" class="mt-1 grid grid-cols-3 gap-2">
      <cu-input name="numberOfTradingCycles" size="small" v-model="numberOfTradingCycles"
        label="Number of trading cycles" placeholder="Number of trading cycles" />
    </div>
  </cu-collapsible-section>

  <div class="mb-2">
    <div class="mt-4 flex justify-start gap-2">
      <cu-button v-if="editingBatchIndex == null" color="green" size="small" label="Add Batch" @click="addBatch" />
      <cu-button v-if="editingBatchIndex !== null" color="yellow" size="small" label="Update Batch"
        @click="updateBatch" />
      <cu-button v-if="editingBatchIndex !== null" size="small" label="Cancel Edit" @click="cancelEdit" />
    </div>

    <div v-if="batches.length > 0" class="mt-4">
      <cu-label name="batches" label="Configured Batches" />
      <div class="space-y-2">
        <div v-for="(batch, index) in batches" :key="index"
          :class="['p-3 rounded-lg border', batch.enabled ? 'bg-gray-100 dark:bg-gray-800 border-gray-300 dark:border-gray-600' : 'bg-gray-50 dark:bg-gray-900 border-gray-200 dark:border-gray-700 opacity-60']">
          <div class="flex justify-between items-start">
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-2">
                <div class="flex items-center gap-2">
                  <template v-if="editingBatchNameIndex === index">
                    <div class="mb-0">
                      <cu-input :ref="el => { if (el) batchNameInputRefs[index] = el; }" :name="`batchName-${index}`"
                        :model-value="batch.name || `Batch #${index + 1}`"
                        @update:model-value="(value) => { batches[index].name = value }" size="xsmall"
                        placeholder="Batch name"
                        class="!mb-0 [&_input]:!text-sm [&_input]:!font-semibold [&_input]:!w-auto [&_input]:!min-w-[100px] [&_input]:!max-w-[200px] [&_input]:!focus:ring-orange-500" />
                    </div>
                  </template>
                  <template v-else>
                    <span class="text-sm font-semibold text-gray-900 dark:text-white">
                      {{ batch.name || `Batch #${index + 1}` }}
                    </span>
                    <button type="button" @click="startEditingBatchName(index)"
                      class="p-0.5 text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
                      title="Edit batch name">
                      <PencilSquareIcon class="w-3.5 h-3.5" />
                    </button>
                  </template>
                </div>
                <cu-toggle :name="`batchEnabled-${index}`" :model-value="batch.enabled"
                  @update:model-value="(value) => handleBatchEnabledChange(index, value)"
                  tooltip="Enable or disable this batch. Disabled batches are stored but not executed." />
              </div>
              <div class="text-xs text-gray-700 dark:text-gray-300 space-y-1">
                <div>
                  <span class="font-medium">Assets:</span>
                  {{(batch.customAssetsEnabled ? batch.customAssetsInput : batch.assetsToTrade?.map(a =>
                    a.name)?.join(', ')) || 'None'
                  }}
                  <span v-if="batch.tradeExoticAssets" class="ml-1 text-orange-600 dark:text-orange-400">
                    (+ {{batch.exoticAssetsToTrade?.map(a => a.name)?.join(', ') || 'None'}} exotic)
                  </span>
                </div>
                <div>
                  <span class="font-medium">Main:</span> {{ batch.mainPerpType }} |
                  <span class="font-medium">Hedge:</span> {{ batch.hedgePerpType }} |
                  <span class="font-medium">Profiles ({{ batch.profiles.length }}):</span>
                  {{batch.profiles.map(p => p.name).join(', ')}}
                </div>
                <div>
                  <span class="font-medium">Position:</span> ${{ batch.minPositionUsd }}-${{ batch.maxPositionUsd }} |
                  <span class="font-medium">Leverage:</span> {{ batch.minLeverage }}-{{ batch.maxLeverage }}x |
                  <span class="font-medium">Hold:</span> {{ batch.minHoldingMinutes }}-{{ batch.maxHoldingMinutes }}min
                  |
                  <span class="font-medium">Delay:</span> {{ batch.minOpenDelayMinutes }}-{{
                    batch.maxOpenDelayMinutes }}min |
                  <span class="font-medium"> Size Mismatch:</span> {{ batch.sizeMismatchPercent }}% |
                  <span class="font-medium"> Liquidation:</span> {{ batch.liquidationThresholdPercent }}%
                </div>
                <div class="text-xs text-gray-600 dark:text-gray-400">
                  <span v-if="batch.limitOrder">
                    <span class="mr-2">| Limit Order: {{ batch.minVerifyOrderMinutes }}-{{ batch.maxVerifyOrderMinutes
                    }}min</span>
                    <span v-if="batch.limitCancelOrder" class="mr-2">| Limit Cancel Order</span>
                  </span>
                  <span v-if="batch.setMarketOrderSlippage" class="mr-2">| Custom Slippage: {{ batch.marketOrderSlippage
                    }}%</span>
                  <span v-if="batch.alwaysUseFirstAsMain" class="mr-2">| First as main</span>
                  <span v-if="batch.alwaysUseFirstAsMain && batch.tradeMainAsSpot" class="mr-2">| Trade main as
                    spot</span>
                  <span v-if="batch.customMainPositionSide" class="mr-2">| Main side: {{ batch.mainPositionSide
                  }}</span>
                  <span v-if="batch.tradeCycles" class="mr-2">| {{ batch.numberOfTradingCycles }} cycles</span>
                </div>
              </div>
            </div>
            <div class="flex gap-1 ml-2">
              <cu-button @click="editBatch(index)" color="yellow" size="small" label="Edit" />
              <cu-button @click="removeBatch(index)" color="red" size="small" label="Remove" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="mt-4 mb-4 flex justify-center">
    <cu-button class="w-1/3" color="green" label="Execute" @click="handleExecute" :disabled="moduleRunning" />
    <cu-button class="w-1/3 ml-4" color="red" label="Stop" @click="handleStop" :disabled="!moduleRunning" />
  </div>

  <cu-logs :logs="logs" :clear="true" :module="module" @append:logs="handleAppendLogs" @clear:logs="handleClearLogs"
    @finished:script="handleScriptFinish" />
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, getCurrentInstance, watch, computed, nextTick } from 'vue'
import { loadModuleData, stopModule, updateModuleData, startModule, statusModule, beforeUnloadModule, beforeRouteLeaveModule, loadAdsProfiles } from '@/utils'
import { onBeforeRouteLeave } from 'vue-router'
import { initFlowbite } from 'flowbite'
import {
  CuTitle,
  CuLabel,
  CuInput,
  CuCollapsibleSection,
  CuButton,
  CuSelect,
  CuCheckbox,
  CuToggle,
  CuLogs
} from '@/components/cu'
import { PencilSquareIcon } from '@heroicons/vue/24/solid'
import VueMultiselect from 'vue-multiselect'

const availablePerps = ref([])
const currentMainPerpType = ref(null)
const currentHedgePerpType = ref(null)
const currentProfiles = ref([])

const availableProfiles = ref([])

const batches = ref([])
const editingBatchIndex = ref(null)
const editingBatchNameIndex = ref(null)
const batchNameInputRefs = ref({})
const batchNameKeydownHandlers = ref({})

const minLeverage = ref(5)
const maxLeverage = ref(7)
const minPositionUsd = ref(75)
const maxPositionUsd = ref(100)
const minHoldingMinutes = ref(13)
const maxHoldingMinutes = ref(25)
const minOpenDelayMinutes = ref(1)
const maxOpenDelayMinutes = ref(3)
const limitOrder = ref(false)
const limitCancelOrder = ref(false)
const minVerifyOrderMinutes = ref(1)
const maxVerifyOrderMinutes = ref(1.5)
const setMarketOrderSlippage = ref(false)
const marketOrderSlippage = ref(0.05)
const sizeMismatchPercent = ref(0.5)
const liquidationThresholdPercent = ref(5)
const customAssetsEnabled = ref(false)
const customAssetsInput = ref('')
const assetsToTrade = ref([])
const availableAssetsToTrade = ref([])
const availableExoticAssetsToTrade = ref([])
const tradeExoticAssets = ref(false)
const exoticAssetsToTrade = ref([])
const exoticAssetsProbability = ref(3)
const minimumCycleBalanceCheck = ref(false)
const minimumCycleBalance = ref(1000)
const alwaysUseFirstAsMain = ref(false)
const tradeMainAsSpot = ref(false)
const customMainPositionSide = ref(false)
const mainPositionSide = ref('buy')
const availableSides = ref(['buy', 'sell'])
const tradeCycles = ref(false)
const numberOfTradingCycles = ref(10)

const logVolumes = ref(false)
const getLatestStats = ref(false)
const stopProcessing = ref(false)

const logs = ref([])
const moduleRunning = ref(false)

const module = ref('premium/airdrop-perps')

const { proxy } = getCurrentInstance()

const handleAppendLogs = async (log) => logs.value.unshift(log)
const handleClearLogs = async () => logs.value = []
const handleScriptFinish = async () => moduleRunning.value = false

const availableProfilesForSelection = computed(() => {
  const usedSerialNumbers = batches.value
    .filter((batch, index) => index !== editingBatchIndex.value && batch.enabled)
    .flatMap(batch => batch.profiles.map(p => p.serial_number))

  return availableProfiles.value.filter(
    profile => !usedSerialNumbers.includes(profile.serial_number)
  )
})

const resetFormToDefaults = () => {
  currentProfiles.value = []
  currentMainPerpType.value = availablePerps.value[0]
  currentHedgePerpType.value = availablePerps.value[0]
}

const getCurrentBatchSettings = () => {
  return {
    customAssetsEnabled: customAssetsEnabled.value,
    customAssetsInput: customAssetsInput.value,
    assetsToTrade: assetsToTrade.value,
    tradeExoticAssets: tradeExoticAssets.value,
    exoticAssetsToTrade: exoticAssetsToTrade.value,
    exoticAssetsProbability: exoticAssetsProbability.value,
    mainPerpType: currentMainPerpType.value,
    hedgePerpType: currentHedgePerpType.value,
    profiles: currentProfiles.value,
    minLeverage: minLeverage.value,
    maxLeverage: maxLeverage.value,
    minPositionUsd: minPositionUsd.value,
    maxPositionUsd: maxPositionUsd.value,
    minHoldingMinutes: minHoldingMinutes.value,
    maxHoldingMinutes: maxHoldingMinutes.value,
    minOpenDelayMinutes: minOpenDelayMinutes.value,
    maxOpenDelayMinutes: maxOpenDelayMinutes.value,
    limitOrder: limitOrder.value,
    limitCancelOrder: limitCancelOrder.value,
    minVerifyOrderMinutes: minVerifyOrderMinutes.value,
    maxVerifyOrderMinutes: maxVerifyOrderMinutes.value,
    setMarketOrderSlippage: setMarketOrderSlippage.value,
    marketOrderSlippage: marketOrderSlippage.value,
    sizeMismatchPercent: sizeMismatchPercent.value,
    liquidationThresholdPercent: liquidationThresholdPercent.value,
    logVolumes: logVolumes.value,
    getLatestStats: getLatestStats.value,
    stopProcessing: stopProcessing.value,
    minimumCycleBalanceCheck: minimumCycleBalanceCheck.value,
    minimumCycleBalance: minimumCycleBalance.value,
    alwaysUseFirstAsMain: alwaysUseFirstAsMain.value,
    tradeMainAsSpot: tradeMainAsSpot.value,
    customMainPositionSide: customMainPositionSide.value,
    mainPositionSide: mainPositionSide.value,
    tradeCycles: tradeCycles.value,
    numberOfTradingCycles: numberOfTradingCycles.value,
    enabled: true,
    name: null
  }
}

const loadBatchSettingsToForm = (batch) => {
  customAssetsEnabled.value = batch.customAssetsEnabled ?? customAssetsEnabled.value
  customAssetsInput.value = batch.customAssetsInput ?? customAssetsInput.value
  assetsToTrade.value = batch.assetsToTrade ?? assetsToTrade.value
  tradeExoticAssets.value = batch.tradeExoticAssets ?? tradeExoticAssets.value
  exoticAssetsToTrade.value = batch.exoticAssetsToTrade ?? exoticAssetsToTrade.value
  exoticAssetsProbability.value = batch.exoticAssetsProbability ?? exoticAssetsProbability.value
  currentMainPerpType.value = batch.mainPerpType ?? availablePerps.value[0]
  currentHedgePerpType.value = batch.hedgePerpType ?? availablePerps.value[0]
  currentProfiles.value = batch.profiles ?? currentProfiles.value
  minLeverage.value = batch.minLeverage ?? minLeverage.value
  maxLeverage.value = batch.maxLeverage ?? maxLeverage.value
  minPositionUsd.value = batch.minPositionUsd ?? minPositionUsd.value
  maxPositionUsd.value = batch.maxPositionUsd ?? maxPositionUsd.value
  minHoldingMinutes.value = batch.minHoldingMinutes ?? minHoldingMinutes.value
  maxHoldingMinutes.value = batch.maxHoldingMinutes ?? maxHoldingMinutes.value
  minOpenDelayMinutes.value = batch.minOpenDelayMinutes ?? minOpenDelayMinutes.value
  maxOpenDelayMinutes.value = batch.maxOpenDelayMinutes ?? maxOpenDelayMinutes.value
  limitOrder.value = batch.limitOrder ?? limitOrder.value
  limitCancelOrder.value = batch.limitCancelOrder ?? limitCancelOrder.value
  minVerifyOrderMinutes.value = batch.minVerifyOrderMinutes ?? minVerifyOrderMinutes.value
  maxVerifyOrderMinutes.value = batch.maxVerifyOrderMinutes ?? maxVerifyOrderMinutes.value
  setMarketOrderSlippage.value = batch.setMarketOrderSlippage ?? setMarketOrderSlippage.value
  marketOrderSlippage.value = batch.marketOrderSlippage ?? marketOrderSlippage.value
  sizeMismatchPercent.value = batch.sizeMismatchPercent ?? sizeMismatchPercent.value
  liquidationThresholdPercent.value = batch.liquidationThresholdPercent ?? liquidationThresholdPercent.value
  logVolumes.value = batch.logVolumes ?? logVolumes.value
  getLatestStats.value = batch.getLatestStats ?? getLatestStats.value
  stopProcessing.value = batch.stopProcessing ?? stopProcessing.value
  minimumCycleBalanceCheck.value = batch.minimumCycleBalanceCheck ?? minimumCycleBalanceCheck.value
  minimumCycleBalance.value = batch.minimumCycleBalance ?? minimumCycleBalance.value
  alwaysUseFirstAsMain.value = batch.alwaysUseFirstAsMain ?? alwaysUseFirstAsMain.value
  tradeMainAsSpot.value = batch.tradeMainAsSpot ?? tradeMainAsSpot.value
  customMainPositionSide.value = batch.customMainPositionSide ?? customMainPositionSide.value
  mainPositionSide.value = batch.mainPositionSide ?? mainPositionSide.value
  tradeCycles.value = batch.tradeCycles ?? tradeCycles.value
  numberOfTradingCycles.value = batch.numberOfTradingCycles ?? numberOfTradingCycles.value
}

const validateBatch = () => {
  if (customAssetsEnabled.value) {
    if (!customAssetsInput.value || customAssetsInput.value.trim() === '') {
      alert('Please enter custom assets or disable custom assets and select from the list')
      return false
    }
  } else {
    if (!assetsToTrade.value || assetsToTrade.value.length === 0) {
      alert('Please select at least one asset to trade')
      return false
    }
  }

  if (!currentProfiles.value || currentProfiles.value.length < 2) {
    alert('Please select at least two profiles')
    return false
  }

  if (!currentMainPerpType.value || !currentHedgePerpType.value) {
    alert('Please select both main perp and hedge perp')
    return false
  }

  if (tradeExoticAssets.value) {
    if (!exoticAssetsToTrade.value || exoticAssetsToTrade.value.length === 0) {
      alert('Please select at least one exotic asset when trade exotic assets is enabled')
      return false
    }
    if (!exoticAssetsProbability.value || isNaN(parseFloat(exoticAssetsProbability.value)) || parseFloat(exoticAssetsProbability.value) <= 0) {
      alert('Please enter a valid probability value for exotic assets')
      return false
    }
  }

  return true
}

const addBatch = () => {
  if (!validateBatch()) return

  batches.value.push(getCurrentBatchSettings())
  resetFormToDefaults()
}

const editBatch = (index) => {
  const batch = batches.value[index]
  loadBatchSettingsToForm(batch)
  editingBatchIndex.value = index
}

const updateBatch = () => {
  if (editingBatchIndex.value === null) return

  if (!validateBatch()) return

  const currentBatch = batches.value[editingBatchIndex.value]
  const currentEnabled = currentBatch.enabled
  const currentName = currentBatch.name ?? null
  const updatedBatch = getCurrentBatchSettings()
  updatedBatch.enabled = currentEnabled
  updatedBatch.name = currentName
  batches.value[editingBatchIndex.value] = updatedBatch
  cancelEdit()
}

const updateBatchName = (index, newName) => {
  if (batches.value[index]) {
    const trimmedName = newName?.trim() || null
    if (trimmedName && trimmedName.match(/^Batch #\d+$/)) {
      batches.value[index].name = null
    } else {
      batches.value[index].name = trimmedName || null
    }
  }
}

const startEditingBatchName = (index) => {
  editingBatchNameIndex.value = index
  nextTick(() => {
    const inputRef = batchNameInputRefs.value[index]
    if (inputRef) {
      const input = inputRef.$el?.querySelector('input')
      if (input) {
        input.focus()
        input.select()

        const handleBlur = () => {
          finishEditingBatchName(index, input.value)
        }
        const handleKeydown = (e) => {
          if (e.key === 'Enter') {
            e.preventDefault()
            input.blur()
          } else if (e.key === 'Escape') {
            e.preventDefault()
            editingBatchNameIndex.value = null
            input.removeEventListener('keydown', handleKeydown)
            batchNameKeydownHandlers.value[index] = null
          }
        }

        input.addEventListener('blur', handleBlur, { once: true })
        input.addEventListener('keydown', handleKeydown)
        batchNameKeydownHandlers.value[index] = { input, handleKeydown }
      }
    }
  })
}

const finishEditingBatchName = (index, newName) => {
  updateBatchName(index, newName)
  const handler = batchNameKeydownHandlers.value[index]
  if (handler) {
    handler.input.removeEventListener('keydown', handler.handleKeydown)
    delete batchNameKeydownHandlers.value[index]
  }
  editingBatchNameIndex.value = null
}

const cancelEdit = () => {
  editingBatchIndex.value = null
  resetFormToDefaults()
}

const removeBatch = (index) => {
  batches.value.splice(index, 1)
  if (editingBatchIndex.value === index) {
    cancelEdit()
  }
}

const validateBatchEnable = (batchIndex) => {
  const batch = batches.value[batchIndex]
  if (!batch || batch.enabled) return true

  const batchProfileSerialNumbers = batch.profiles.map(p => p.serial_number)
  const conflictingBatches = batches.value
    .filter((b, index) => index !== batchIndex && b.enabled)
    .filter(b => b.profiles.some(p => batchProfileSerialNumbers.includes(p.serial_number)))

  if (conflictingBatches.length > 0) {
    const conflictingProfiles = conflictingBatches
      .flatMap(b => b.profiles.filter(p => batchProfileSerialNumbers.includes(p.serial_number)))
      .map(p => p.name)
      .filter((name, index, self) => self.indexOf(name) === index) // Remove duplicates

    alert(`Cannot enable batch: The following profiles are already used in other enabled batches: ${conflictingProfiles.join(', ')}`)
    return false
  }

  return true
}

const handleBatchEnabledChange = (index, newValue) => {
  if (newValue === true) {
    if (!validateBatchEnable(index)) {
      return
    }
  }
  batches.value[index].enabled = newValue
}

const loadDefaults = async () => {
  await loadAdsProfiles(proxy, (profilesData) => {
    availableProfiles.value = profilesData
  }, logs)

  await loadModuleData(proxy, module.value, 'configs', 'python', (data) => {
    if (!Object.hasOwn(data, 'assets_to_trade')) return

    availableAssetsToTrade.value = (data.assets_to_trade ?? availableAssetsToTrade.value).map(asset => ({ name: asset }))
    availableExoticAssetsToTrade.value = (data.exotic_assets_to_trade ?? availableExoticAssetsToTrade.value).map(asset => ({ name: asset }))
    availablePerps.value = (data.perps ?? availablePerps.value)
  }, logs)

  await loadModuleData(proxy, module.value, 'instructions', 'python', (data) => {
    customAssetsEnabled.value = data.custom_assets_enabled ?? customAssetsEnabled.value
    if (customAssetsEnabled.value) {
      customAssetsInput.value = data.assets_to_trade?.join(', ') ?? customAssetsInput.value
    } else {
      customAssetsInput.value = ''
    }
    assetsToTrade.value = availableAssetsToTrade.value.filter(asset => (data.assets_to_trade ?? []).includes(asset.name))
    tradeExoticAssets.value = data.trade_exotic_assets ?? tradeExoticAssets.value
    exoticAssetsToTrade.value = availableExoticAssetsToTrade.value.filter(asset => (data.exotic_assets_to_trade ?? []).includes(asset.name))
    exoticAssetsProbability.value = data.exotic_assets_probability ?? exoticAssetsProbability.value
    currentMainPerpType.value = data.main_perp_type ?? availablePerps.value[0]
    currentHedgePerpType.value = data.hedge_perp_type ?? availablePerps.value[0]
    currentProfiles.value = (data.profiles ?? []).map(serialNumber => availableProfiles.value.find(profile => profile.serial_number === serialNumber)).filter(Boolean)
    minLeverage.value = data.min_leverage ?? minLeverage.value
    maxLeverage.value = data.max_leverage ?? maxLeverage.value
    minPositionUsd.value = data.min_position_usd ?? minPositionUsd.value
    maxPositionUsd.value = data.max_position_usd ?? maxPositionUsd.value
    minHoldingMinutes.value = data.min_holding_minutes ?? minHoldingMinutes.value
    maxHoldingMinutes.value = data.max_holding_minutes ?? maxHoldingMinutes.value
    minOpenDelayMinutes.value = data.min_open_delay_minutes ?? minOpenDelayMinutes.value
    maxOpenDelayMinutes.value = data.max_open_delay_minutes ?? maxOpenDelayMinutes.value
    limitOrder.value = data.limit_order ?? limitOrder.value
    limitCancelOrder.value = data.limit_cancel_order ?? limitCancelOrder.value
    minVerifyOrderMinutes.value = data.min_verify_order_minutes ?? minVerifyOrderMinutes.value
    maxVerifyOrderMinutes.value = data.max_verify_order_minutes ?? maxVerifyOrderMinutes.value
    setMarketOrderSlippage.value = data.set_market_order_slippage ?? setMarketOrderSlippage.value
    marketOrderSlippage.value = data.market_order_slippage ?? marketOrderSlippage.value
    sizeMismatchPercent.value = data.size_mismatch_percent ?? sizeMismatchPercent.value
    liquidationThresholdPercent.value = data.liquidation_threshold_percent ?? liquidationThresholdPercent.value
    logVolumes.value = data.log_volumes ?? logVolumes.value
    getLatestStats.value = data.get_latest_stats ?? getLatestStats.value
    stopProcessing.value = data.stop_processing ?? stopProcessing.value
    minimumCycleBalanceCheck.value = data.minimum_cycle_balance_check ?? minimumCycleBalanceCheck.value
    minimumCycleBalance.value = data.minimum_cycle_balance ?? minimumCycleBalance.value
    alwaysUseFirstAsMain.value = data.always_use_first_as_main ?? alwaysUseFirstAsMain.value
    tradeMainAsSpot.value = data.trade_main_as_spot ?? tradeMainAsSpot.value
    customMainPositionSide.value = data.custom_main_position_side ?? customMainPositionSide.value
    mainPositionSide.value = data.main_position_side ?? mainPositionSide.value
    tradeCycles.value = data.trade_cycles ?? tradeCycles.value
    numberOfTradingCycles.value = data.number_of_trading_cycles ?? numberOfTradingCycles.value

    batches.value = (data.batches ?? []).map(batch => ({
      name: batch.name || null,
      customAssetsEnabled: batch.custom_assets_enabled ?? customAssetsEnabled.value,
      customAssetsInput: (batch.custom_assets_enabled ?? customAssetsEnabled.value) ? batch.assets_to_trade?.join(', ') ?? customAssetsInput.value : '',
      assetsToTrade: availableAssetsToTrade.value.filter(asset => (batch.assets_to_trade ?? []).includes(asset.name)),
      tradeExoticAssets: batch.trade_exotic_assets ?? tradeExoticAssets.value,
      exoticAssetsToTrade: availableExoticAssetsToTrade.value.filter(asset => (batch.exotic_assets_to_trade ?? []).includes(asset.name)),
      exoticAssetsProbability: batch.exotic_assets_probability ?? exoticAssetsProbability.value,
      mainPerpType: batch.main_perp_type || availablePerps.value[0],
      hedgePerpType: batch.hedge_perp_type || availablePerps.value[0],
      profiles: (batch.profiles ?? []).map(serialNumber => availableProfiles.value.find(profile => profile.serial_number === serialNumber)).filter(Boolean),
      minLeverage: batch.min_leverage ?? minLeverage.value,
      maxLeverage: batch.max_leverage ?? maxLeverage.value,
      minPositionUsd: batch.min_position_usd ?? minPositionUsd.value,
      maxPositionUsd: batch.max_position_usd ?? maxPositionUsd.value,
      minHoldingMinutes: batch.min_holding_minutes ?? minHoldingMinutes.value,
      maxHoldingMinutes: batch.max_holding_minutes ?? maxHoldingMinutes.value,
      minOpenDelayMinutes: batch.min_open_delay_minutes ?? minOpenDelayMinutes.value,
      maxOpenDelayMinutes: batch.max_open_delay_minutes ?? maxOpenDelayMinutes.value,
      limitOrder: batch.limit_order ?? limitOrder.value,
      limitCancelOrder: batch.limit_cancel_order ?? limitCancelOrder.value,
      minVerifyOrderMinutes: batch.min_verify_order_minutes ?? minVerifyOrderMinutes.value,
      maxVerifyOrderMinutes: batch.max_verify_order_minutes ?? maxVerifyOrderMinutes.value,
      setMarketOrderSlippage: batch.set_market_order_slippage ?? setMarketOrderSlippage.value,
      marketOrderSlippage: batch.market_order_slippage ?? marketOrderSlippage.value,
      sizeMismatchPercent: batch.size_mismatch_percent ?? sizeMismatchPercent.value,
      liquidationThresholdPercent: batch.liquidation_threshold_percent ?? liquidationThresholdPercent.value,
      logVolumes: batch.log_volumes ?? logVolumes.value,
      getLatestStats: batch.get_latest_stats ?? getLatestStats.value,
      stopProcessing: batch.stop_processing ?? stopProcessing.value,
      minimumCycleBalanceCheck: batch.minimum_cycle_balance_check ?? minimumCycleBalanceCheck.value,
      minimumCycleBalance: batch.minimum_cycle_balance ?? minimumCycleBalance.value,
      alwaysUseFirstAsMain: batch.always_use_first_as_main ?? alwaysUseFirstAsMain.value,
      tradeMainAsSpot: batch.trade_main_as_spot ?? tradeMainAsSpot.value,
      customMainPositionSide: batch.custom_main_position_side ?? customMainPositionSide.value,
      mainPositionSide: batch.main_position_side ?? mainPositionSide.value,
      tradeCycles: batch.trade_cycles ?? tradeCycles.value,
      numberOfTradingCycles: batch.number_of_trading_cycles ?? numberOfTradingCycles.value,
      enabled: batch.enabled ?? false
    }))
  }, logs)

  moduleRunning.value = (await statusModule(proxy, module.value, logs)) ?? moduleRunning.value
}

const handleExecute = async () => {
  if (batches.value.length === 0) {
    alert('Please add at least one batch before executing')
    return
  }

  const enabledBatches = batches.value.filter(batch => batch.enabled)
  if (enabledBatches.length === 0) {
    alert('Please enable at least one batch before executing')
    return
  }

  moduleRunning.value = true

  await updateModuleData(proxy, module.value, 'instructions', 'python', {
    batches: batches.value.map(batch => ({
      name: batch.name || null,
      custom_assets_enabled: batch.customAssetsEnabled,
      assets_to_trade: batch.customAssetsEnabled
        ? batch.customAssetsInput.split(',').map(a => a.trim()).filter(Boolean)
        : batch.assetsToTrade.map(asset => asset.name),
      trade_exotic_assets: batch.tradeExoticAssets,
      exotic_assets_to_trade: batch.exoticAssetsToTrade.map(asset => asset.name),
      exotic_assets_probability: parseFloat(batch.exoticAssetsProbability),
      main_perp_type: batch.mainPerpType,
      hedge_perp_type: batch.hedgePerpType,
      profiles: batch.profiles.map(profile => profile.serial_number),
      labels: batch.profiles.map(profile => profile.name),
      min_leverage: parseFloat(batch.minLeverage),
      max_leverage: parseFloat(batch.maxLeverage),
      min_position_usd: parseFloat(batch.minPositionUsd),
      max_position_usd: parseFloat(batch.maxPositionUsd),
      min_holding_minutes: parseFloat(batch.minHoldingMinutes),
      max_holding_minutes: parseFloat(batch.maxHoldingMinutes),
      min_open_delay_minutes: parseFloat(batch.minOpenDelayMinutes),
      max_open_delay_minutes: parseFloat(batch.maxOpenDelayMinutes),
      limit_order: batch.limitOrder,
      limit_cancel_order: batch.limitCancelOrder,
      min_verify_order_minutes: parseFloat(batch.minVerifyOrderMinutes),
      max_verify_order_minutes: parseFloat(batch.maxVerifyOrderMinutes),
      set_market_order_slippage: batch.setMarketOrderSlippage,
      market_order_slippage: parseFloat(batch.marketOrderSlippage),
      size_mismatch_percent: parseFloat(batch.sizeMismatchPercent),
      liquidation_threshold_percent: parseFloat(batch.liquidationThresholdPercent),
      log_volumes: batch.logVolumes,
      get_latest_stats: batch.getLatestStats,
      stop_processing: batch.stopProcessing,
      minimum_cycle_balance_check: batch.minimumCycleBalanceCheck,
      minimum_cycle_balance: parseFloat(batch.minimumCycleBalance),
      always_use_first_as_main: batch.alwaysUseFirstAsMain,
      trade_main_as_spot: batch.tradeMainAsSpot,
      custom_main_position_side: batch.customMainPositionSide,
      main_position_side: batch.mainPositionSide,
      trade_cycles: batch.tradeCycles,
      number_of_trading_cycles: parseInt(batch.numberOfTradingCycles),
      enabled: batch.enabled
    })),
    custom_assets_enabled: customAssetsEnabled.value,
    assets_to_trade: customAssetsEnabled.value
      ? customAssetsInput.value.split(',').map(a => a.trim()).filter(Boolean)
      : assetsToTrade.value.map(asset => asset.name),
    trade_exotic_assets: tradeExoticAssets.value,
    exotic_assets_to_trade: exoticAssetsToTrade.value.map(asset => asset.name),
    exotic_assets_probability: parseFloat(exoticAssetsProbability.value),
    main_perp_type: currentMainPerpType.value,
    hedge_perp_type: currentHedgePerpType.value,
    profiles: currentProfiles.value.map(profile => profile.serial_number),
    min_leverage: parseFloat(minLeverage.value),
    max_leverage: parseFloat(maxLeverage.value),
    min_position_usd: parseFloat(minPositionUsd.value),
    max_position_usd: parseFloat(maxPositionUsd.value),
    min_holding_minutes: parseFloat(minHoldingMinutes.value),
    max_holding_minutes: parseFloat(maxHoldingMinutes.value),
    min_open_delay_minutes: parseFloat(minOpenDelayMinutes.value),
    max_open_delay_minutes: parseFloat(maxOpenDelayMinutes.value),
    limit_order: limitOrder.value,
    limit_cancel_order: limitCancelOrder.value,
    min_verify_order_minutes: parseFloat(minVerifyOrderMinutes.value),
    max_verify_order_minutes: parseFloat(maxVerifyOrderMinutes.value),
    set_market_order_slippage: setMarketOrderSlippage.value,
    market_order_slippage: parseFloat(marketOrderSlippage.value),
    size_mismatch_percent: parseFloat(sizeMismatchPercent.value),
    liquidation_threshold_percent: parseFloat(liquidationThresholdPercent.value),
    log_volumes: logVolumes.value,
    get_latest_stats: getLatestStats.value,
    stop_processing: stopProcessing.value,
    minimum_cycle_balance_check: minimumCycleBalanceCheck.value,
    minimum_cycle_balance: parseFloat(minimumCycleBalance.value),
    always_use_first_as_main: alwaysUseFirstAsMain.value,
    trade_main_as_spot: tradeMainAsSpot.value,
    custom_main_position_side: customMainPositionSide.value,
    main_position_side: mainPositionSide.value,
    trade_cycles: tradeCycles.value,
    number_of_trading_cycles: parseInt(numberOfTradingCycles.value)
  }, logs)

  await startModule(proxy, module.value, logs)
}

const handleStop = async () => {
  await stopModule(proxy, module.value)
}

const handleBeforeUnload = beforeUnloadModule(moduleRunning)


watch([setMarketOrderSlippage, tradeExoticAssets, limitOrder, customAssetsEnabled, tradeCycles, alwaysUseFirstAsMain], () => {
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
