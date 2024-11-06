<template>
  <cu-title title="Modules Settings" />

  <cu-horizontal-checkbox-group v-model="selectedModules" :options="availableModules" />

  <div class="mt-4 mb-4 flex justify-center">
    <cu-button class="w-1/3" color="green" label="Save" @click="handleSave" />
  </div>
</template>

<script setup>
import { ref, onMounted, getCurrentInstance } from 'vue'
import { loadModuleData, updateModuleData } from '@/utils'
import {
  CuTitle,
  CuHorizontalCheckboxGroup,
  CuButton
} from '@/components/cu'

const availableModules = ref([])
const selectedModules = ref([])

const module = ref('crypto_universe')

const { proxy } = getCurrentInstance()

const loadDefaults = async () => {
  await loadModuleData(proxy, module.value, 'instructions', 'js', (data) => {
    if (!Object.hasOwn(data, 'modules')) return

    selectedModules.value = Object.entries(data.modules)
      .filter(([, config]) => config.enabled)
      .map(([value]) => value)
  })

  await loadModuleData(proxy, module.value, 'configs', 'js', (data) => {
    if (!Object.hasOwn(data, 'available_modules')) return

    availableModules.value = data.available_modules
  })
}

const handleSave = async () => {
  await updateModuleData(proxy, module.value, 'instructions', 'js', {
    modules: availableModules.value.reduce((acc, module) => {
      acc[module] = { enabled: selectedModules.value.includes(module) }
      return acc
    }, {})
  })

  window.location.reload()
}

onMounted(async () => {
  await loadDefaults()
})
</script>
