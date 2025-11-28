<template>
  <cu-title title="Modules Settings" />
  <div v-if="premiumMode">
    <cu-label class="text-red-800" name="premiumModules" label="Premium Modules" />
    <cu-horizontal-checkbox-group name="premiumModules" v-model="premiumModules" :options="availablePremiumModules" />
  </div>
  <div v-for="(modulesFromGroup, group) in groupedModules" :key="group">
    <cu-horizontal-checkbox-group :label="group !== 'main' ? group : ''" :name="group" v-model="modules"
      :options="modulesFromGroup" />
  </div>
  <div class="mt-4 mb-4 flex justify-center">
    <cu-button class="w-1/3" color="green" label="Save" @click="handleSave" />
  </div>

  <cu-collapsible-section name="privateKeys" title="Wallets and Private Keys" class="mb-2">
    <div class="grid grid-cols-2 gap-2">
      <cu-textarea name="addresses" v-model="addresses" label="Wallet Addresses"
        placeholder="Enter wallet addresses each on the new line..."
        tooltip="Add wallet addresses here and they will be shared across all the modules." />
      <cu-textarea name="privateKeys" v-model="privateKeys" label="Private Keys"
        tooltip="Add private keys here and they will be shared across all the modules."
        placeholder="Enter private keys each on the new line..." />
    </div>
    <div class="mt-4 mb-4 flex justify-center">
      <cu-button class="w-1/3" color="green" label="Save" @click="handlePrivateKeysSave" />
    </div>
  </cu-collapsible-section>

  <cu-collapsible-section name="premium" title="Premium" class="mb-2">
    <cu-label label="License Key"></cu-label>
    <div>
      <input type="text" id="licenseKey" v-model="licenseKey" placeholder="Enter license..."
        class="w-1/3 mr-2 bg-white border border-gray-300 text-gray-900 rounded-lg focus:ring-gray-600 focus:border-gray-600 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-white dark:focus:border-white" />
      <cu-button class="w-1/3" color="orange" label="Activate" @click="handleSave" />
    </div>
    <span v-if="licenseKeyValidationError" class="text-red-600">License key is no valid</span>
  </cu-collapsible-section>

  <cu-collapsible-section name="additionalSettings" title="Additional Settings">
    <div class="mt-1 grid grid-cols-2 gap-2">
      <cu-input name="adsUrl" label="ADS Url" size="small" v-model="adsUrl" placeholder="ADS Api url" />
    </div>
    <div class="mt-1 grid grid-cols-2 gap-2">
      <cu-input name="afinaApiKey" label="Afina Api Key" size="small" v-model="afinaApiKey"
        placeholder="Afina Api Key" />
    </div>
    <div class="grid grid-cols-2 gap-2">
      <cu-checkbox name="debugMode" v-model="debugMode" label="Debug Mode" tooltip="Turn on to enable debug mode." />
    </div>
    <div class="mt-4 mb-4 flex justify-center">
      <cu-button class="w-1/3" color="green" label="Save" @click="handleSave" />
    </div>
  </cu-collapsible-section>
</template>

<script setup>
import { ref, onMounted, getCurrentInstance, computed } from 'vue'
import { loadModuleData, updateModuleData } from '@/utils'
import { initFlowbite } from 'flowbite'
import {
  CuTitle,
  CuHorizontalCheckboxGroup,
  CuLabel,
  CuCollapsibleSection,
  CuButton,
  CuTextarea,
  CuCheckbox,
  CuInput,
} from '@/components/cu'

const availableModules = ref([])
const modules = ref([])

const addresses = ref('')
const privateKeys = ref('')

const availablePremiumModules = ref([])
const premiumModules = ref([])
const premiumMode = ref(false)
const licenseKey = ref('')
const licenseKeyValidationError = ref(false)
const debugMode = ref(false)
const adsUrl = ref('')
const afinaApiKey = ref('')

const module = ref('crypto_universe')

const { proxy } = getCurrentInstance()

const loadDefaults = async () => {
  await loadModuleData(proxy, module.value, 'instructions', 'js', (data) => {
    if (!Object.hasOwn(data, 'modules')) return

    modules.value = data.modules ?? modules.value
    premiumModules.value = data.premium_modules ?? premiumModules.value
    licenseKey.value = data.license_key ?? licenseKey.value
    debugMode.value = data.debug_mode ?? debugMode.value
    adsUrl.value = data.ads_url ?? adsUrl.value
    afinaApiKey.value = data.afina_api_key ?? afinaApiKey.value
  })

  await loadModuleData(proxy, module.value, 'secrets', 'js', (data) => {
    if (!Object.hasOwn(data, 'private_keys')) return

    addresses.value = Object.keys(data.private_keys).join('\n')
    privateKeys.value = Object.values(data.private_keys).join('\n')
  })

  await loadModuleData(proxy, module.value, 'configs', 'js', (data) => {
    if (!Object.hasOwn(data, 'modules')) return

    availableModules.value = data.modules ?? availableModules.value
    availablePremiumModules.value = data.premium_modules ?? availablePremiumModules.value
  })

  premiumMode.value = proxy.$globalConfigs.premium_mode
}

const handleSave = async () => {
  let data = { modules: modules.value, premium_modules: premiumModules.value }

  if (licenseKey.value) {
    data.license_key = licenseKey.value
  }

  await updateModuleData(proxy, module.value, 'instructions', 'js', {
    modules: modules.value,
    premium_modules: premiumModules.value,
    license_key: licenseKey.value,
    debug_mode: debugMode.value,
    ads_url: adsUrl.value,
    afina_api_key: afinaApiKey.value,
  })

  window.location.reload()
}

const handlePrivateKeysSave = async () => {
  const formattedAddresses = addresses.value.split('\n').filter(Boolean)
  const formattedPrivateKeys = privateKeys.value.split('\n').filter(Boolean)

  await updateModuleData(proxy, module.value, 'secrets', 'js', {
    private_keys: formattedAddresses.reduce((acc, address, index) => {
      acc[address] = formattedPrivateKeys[index]
      return acc
    }, {})
  })

  window.location.reload()
}

const groupedModules = computed(() => {
  const groups = { Main: [] }

  availableModules.value.forEach(item => {
    if (item.includes('-')) {
      let [prefix] = item.split('-')
      prefix = prefix.charAt(0).toUpperCase() + prefix.slice(1)
      if (!groups[prefix]) {
        groups[prefix] = []
      }
      groups[prefix].push(item)
    } else {
      groups.Main.push(item)
    }
  })

  return groups
})

onMounted(async () => {
  initFlowbite()
  await loadDefaults()
})
</script>
