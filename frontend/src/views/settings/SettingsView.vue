<template>
  <cu-title title="Modules Settings" />
  <cu-horizontal-checkbox-group name="modules" label="Modules" v-model="modules" :options="availableModules" />
  <cu-horizontal-checkbox-group v-if="premiumMode" name="premiumModules" label="Premium Modules"
    v-model="premiumModules" :options="availablePremiumModules" />
  <div class="mt-4 mb-4 flex justify-center">
    <cu-button class="w-1/3" color="green" label="Save" @click="handleSave" />
  </div>

  <cu-collapsible-section name="premium" title="Premium">
    <cu-label label="License Key"></cu-label>
    <div>
      <input type="text" id="licenseKey" v-model="lisenceKey" placeholder="Enter license..."
        class="w-1/3 mr-2 bg-white border border-gray-300 text-gray-900 rounded-lg focus:ring-gray-600 focus:border-gray-600 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-white dark:focus:border-white" />
      <cu-button class="w-1/3" color="orange" label="Activate" @click="handleLisenceActivation" />
    </div>
    <span v-if="lisenceKeyValidationError" class="text-red-600">License key is no valid</span>
  </cu-collapsible-section>
</template>

<script setup>
import { ref, onMounted, getCurrentInstance } from 'vue'
import { loadModuleData, updateModuleData, activateLicense, loadConfigs } from '@/utils'
import {
  CuTitle,
  CuHorizontalCheckboxGroup,
  CuLabel,
  CuCollapsibleSection,
  CuButton
} from '@/components/cu'

const availableModules = ref([])
const modules = ref([])
const availablePremiumModules = ref([])
const premiumModules = ref([])
const premiumMode = ref(false)
const lisenceKey = ref('')
const lisenceKeyValidationError = ref(false)

const module = ref('crypto_universe')

const { proxy } = getCurrentInstance()

const loadDefaults = async () => {

  await loadConfigs(proxy, (data) => {
    premiumMode.value = data.premium_mode
  })

  await loadModuleData(proxy, module.value, 'instructions', 'js', (data) => {
    if (!Object.hasOwn(data, 'modules')) return

    modules.value = data.modules
    premiumModules.value = data.premium_modules
    lisenceKey.value = data.lisence_key
  })

  await loadModuleData(proxy, module.value, 'configs', 'js', (data) => {
    if (!Object.hasOwn(data, 'available_modules')) return

    availableModules.value = data.available_modules
    availablePremiumModules.value = data.available_premium_modules
  })
}

const handleSave = async () => {
  let data = { modules: modules.value, premium_modules: premiumModules.value }

  if (lisenceKey.value) {
    data.lisence_key = lisenceKey.value
  }

  await updateModuleData(proxy, module.value, 'instructions', 'js', data)

  window.location.reload()
}

const handleLisenceActivation = async () => {
  const activated = await activateLicense(proxy, lisenceKey.value)

  if (activated) {
    window.location.reload()
  } else {
    lisenceKeyValidationError.value = true
  }
}

onMounted(async () => {
  await loadDefaults()
})
</script>
