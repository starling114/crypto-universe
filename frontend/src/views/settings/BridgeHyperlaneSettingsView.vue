<template>
  <cu-title title="Bridge Hyperlane Settings" />

  <div class="grid grid-cols-2 gap-2">
    <cu-textarea name="addresses" v-model="addresses" label="Wallet Addresses"
      placeholder="Enter wallet addresses each on the new line..."
      tooltip="Wallet addresses to be used in the bridge operations." />
    <cu-textarea name="privateKeys" v-model="privateKeys" label="Pravate Keys"
      tooltip="Private keys corresponding to the specific wallet address on the left."
      placeholder="Enter private keys each on the new line..." />
  </div>

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
  CuButton,
  CuLogs
} from '@/components/cu'


const addresses = ref('')
const privateKeys = ref('')

const module = ref('bridge-hyperlane')

const logs = ref([])

const { proxy } = getCurrentInstance()

const handleAppendLogs = async (log) => logs.value.push(log)

const loadDefaults = async () => {
  await loadModuleData(proxy, module.value, 'secrets', 'python', (data) => {
    if (!Object.hasOwn(data, 'private_keys')) return

    addresses.value = Object.keys(data.private_keys).join('\n')
    privateKeys.value = Object.values(data.private_keys).join('\n')
  }, logs)
}

const handleSave = async () => {
  const formattedAddresses = addresses.value.split('\n').filter(Boolean)
  const formattedPrivateKeys = privateKeys.value.split('\n').filter(Boolean)

  await updateModuleData(proxy, module.value, 'secrets', 'python', {
    private_keys: formattedAddresses.reduce((acc, address, index) => {
      acc[address] = formattedPrivateKeys[index]
      return acc
    }, {})
  }, logs)
}

onMounted(async () => {
  initFlowbite()
  await loadDefaults()
})
</script>
