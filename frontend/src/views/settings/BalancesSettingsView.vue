<template>
  <cu-title title="Balances Settings" />

  <cu-textarea name="addresses" v-model="addresses" label="Wallet Addresses"
    placeholder="Enter addresses each on the new line..." />

  <cu-input name="minBalanceHighlight" v-model="minBalanceHighlight" label="Highlight balance threshold"
    tooltip="Highlight balance with red color if it is lower than this value." />

  <cu-select name="namingStrategy" v-model="namingStrategy" :options="availableNamingStrategies"
    placeholder="Select strategy" label="Wallet naming strategy"
    tooltip="Choose how to show wallet labels in the table." />

  <div
    class="mt-2 mb-2 p-5 text-sm font-normal border bg-white rounded-lg border-gray-200 dark:text-white dark:border-gray-700 dark:bg-gray-800">
    <cu-checkbox name="totalRow" v-model="totalRow" label="Total row"
      tooltip="Show total row on each page to see the summ of all the columns." />
  </div>

  <cu-horizontal-checkbox-group label="Networks" v-model="selectedNetworks" :options="availableNetworks" />

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
  CuInput,
  CuSelect,
  CuHorizontalCheckboxGroup,
  CuButton,
  CuLogs,
  CuCheckbox
} from '@/components/cu'

const addresses = ref('')
const minBalanceHighlight = ref('')
const availableNamingStrategies = ref([])
const namingStrategy = ref('')
const totalRow = ref(false)
const availableNetworks = ref([])
const selectedNetworks = ref([])

const logs = ref([])

const module = ref('balances')

const { proxy } = getCurrentInstance()

const handleAppendLogs = async (log) => logs.value.push(log)

const loadDefaults = async () => {
  await loadModuleData(proxy, module.value, 'instructions', 'js', (data) => {
    if (!Object.hasOwn(data, 'addresses')) return

    addresses.value = data.addresses.join('\n')
    minBalanceHighlight.value = data.min_balance_highlight
    namingStrategy.value = data.naming_strategy
    totalRow.value = data.total_row ?? totalRow.value

    selectedNetworks.value = Object.entries(data.networks)
      .filter(([, config]) => config.enabled)
      .map(([value]) => value)
  }, logs)

  await loadModuleData(proxy, module.value, 'configs', 'js', (data) => {
    if (!Object.hasOwn(data, 'available_networks')) return

    availableNetworks.value = data.available_networks ?? availableNetworks.value
    availableNamingStrategies.value = data.available_naming_strategies ?? availableNamingStrategies.value
  }, logs)
}

const handleSave = async () => {
  updateModuleData(proxy, module.value, 'instructions', 'js', {
    addresses: addresses.value.split('\n').filter(Boolean),
    min_balance_highlight: minBalanceHighlight.value.toString(),
    naming_strategy: namingStrategy.value,
    total_row: totalRow.value,
    networks: availableNetworks.value.reduce((acc, value) => {
      acc[value] = { enabled: selectedNetworks.value.includes(value) }
      return acc
    }, {})
  }, logs)
}

onMounted(async () => {
  initFlowbite()
  await loadDefaults()
})
</script>
