<template>
  <cu-title title="Balances Settings" />

  <cu-textarea name="addresses" v-model="addresses" label="Wallet Addresses"
    placeholder="Enter addresses each on the new line..." />

  <cu-input name="minBalanceHighlight" v-model="minBalanceHighlight" label="Highlight balance threshold"
    tooltip="Highlight balance with red color if it is lower than this value." />

  <cu-select name="namingStrategy" v-model="namingStrategy" :options="availableNamingStrategies"
    placeholder="Select strategy" label="Wallet naming strategy"
    tooltip="Choose how to show wallet labels in the table." />

  <cu-label label="Networks" />
  <cu-horizontal-checkbox-group v-model="selectedNetworks" :options="availableNetworks" />

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
  CuLabel,
  CuHorizontalCheckboxGroup,
  CuButton,
  CuLogs
} from '@/components/cu'

const addresses = ref('')
const minBalanceHighlight = ref('')
const availableNamingStrategies = ref([])
const namingStrategy = ref('')
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

    selectedNetworks.value = Object.entries(data.networks)
      .filter(([, config]) => config.enabled)
      .map(([value]) => value)
  }, logs)

  await loadModuleData(proxy, module.value, 'configs', 'js', (data) => {
    if (!Object.hasOwn(data, 'available_networks')) return

    availableNetworks.value = data.available_networks
    availableNamingStrategies.value = data.available_naming_strategies
  }, logs)
}

const handleSave = async () => {
  updateModuleData(proxy, module.value, 'instructions', 'js', {
    addresses: addresses.value.split('\n').filter(Boolean),
    min_balance_highlight: minBalanceHighlight.value.toString(),
    naming_strategy: namingStrategy.value,
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
