<template>
  <cu-title title="Modules Settings" />

  <div v-for="(modules, group) in groupedModules" :key="group">
    <cu-horizontal-checkbox-group :label="group !== 'main' ? group : ''" :name="group" v-model="selectedModules"
      :options="modules" />
  </div>

  <div class="mt-4 mb-4 flex justify-center">
    <cu-button class="w-1/3" color="green" label="Save" @click="handleSave" />
  </div>
</template>

<script setup>
import { ref, onMounted, getCurrentInstance, computed } from 'vue'
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

    selectedModules.value = data.modules
  })

  await loadModuleData(proxy, module.value, 'configs', 'js', (data) => {
    if (!Object.hasOwn(data, 'available_modules')) return

    availableModules.value = data.available_modules
  })
}

const handleSave = async () => {
  await updateModuleData(proxy, module.value, 'instructions', 'js', {
    modules: selectedModules.value
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
