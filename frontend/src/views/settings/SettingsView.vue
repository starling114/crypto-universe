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

  <cu-collapsible-section name="premium" title="Premium">
    <cu-label label="License Key"></cu-label>
    <div>
      <input type="text" id="licenseKey" v-model="lisenceKey" placeholder="Enter license..."
        class="w-1/3 mr-2 bg-white border border-gray-300 text-gray-900 rounded-lg focus:ring-gray-600 focus:border-gray-600 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-white dark:focus:border-white" />
      <cu-button class="w-1/3" color="orange" label="Activate" @click="handleSave" />
    </div>
    <span v-if="lisenceKeyValidationError" class="text-red-600">License key is no valid</span>
  </cu-collapsible-section>
</template>

<script setup>
import { ref, onMounted, getCurrentInstance, computed } from 'vue'
import { loadModuleData, updateModuleData } from '@/utils'
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
  await loadModuleData(proxy, module.value, 'instructions', 'js', (data) => {
    if (!Object.hasOwn(data, 'modules')) return

    modules.value = data.modules
    premiumModules.value = data.premium_modules || []
    lisenceKey.value = data.lisence_key
  })

  await loadModuleData(proxy, module.value, 'configs', 'js', (data) => {
    if (!Object.hasOwn(data, 'available_modules')) return

    availableModules.value = data.available_modules
    availablePremiumModules.value = data.available_premium_modules
  })

  premiumMode.value = proxy.$globalConfigs.premium_mode
}

const handleSave = async () => {
  let data = { modules: modules.value, premium_modules: premiumModules.value }

  if (lisenceKey.value) {
    data.lisence_key = lisenceKey.value
  }

  await updateModuleData(proxy, module.value, 'instructions', 'js', {
    modules: modules.value,
    premium_modules: premiumModules.value,
    lisence_key: lisenceKey.value
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
  await loadDefaults()
})
</script>
