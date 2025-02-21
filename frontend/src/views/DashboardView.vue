<template>
  <h1 class="mb-4 text-center text-3xl font-extrabold text-gray-900 dark:text-white md:text-5xl lg:text-6xl"><span
      class="text-transparent bg-clip-text bg-gradient-to-r to-orange-600 from-red-500">Crypto Universe</span> by
    Starling
  </h1>

  <div v-if="premiumMode">
    <cu-table>
      <cu-table-head>
        <cu-table-head-cell>Premium Module</cu-table-head-cell>
        <cu-table-head-cell>Status</cu-table-head-cell>
      </cu-table-head>
      <cu-table-body>
        <cu-table-row v-for="module in availablePremiumModules" :key="module">
          <cu-table-cell>{{ module }}</cu-table-cell>
          <cu-table-cell>
            <div class="flex items-center">
              <div v-if="premiumModuleEnabled(module)" class="h-2.5 w-2.5 rounded-full bg-green-500 me-2"></div>
              <div v-else class="h-2.5 w-2.5 rounded-full bg-red-500 me-2"></div>
              {{ premiumModuleEnabled(module) ? 'Enabled' : 'Disabled' }}
            </div>
          </cu-table-cell>
        </cu-table-row>
      </cu-table-body>
    </cu-table>

    <hr class="my-4 border-gray-200 dark:border-gray-700" />
  </div>

  <cu-table>
    <cu-table-head>
      <cu-table-head-cell>Module</cu-table-head-cell>
      <cu-table-head-cell>Status</cu-table-head-cell>
    </cu-table-head>
    <cu-table-body>
      <cu-table-row v-for="module in availableModules" :key="module">
        <cu-table-cell>{{ module }}</cu-table-cell>
        <cu-table-cell>
          <div class="flex items-center">
            <div v-if="moduleEnabled(module)" class="h-2.5 w-2.5 rounded-full bg-green-500 me-2"></div>
            <div v-else class="h-2.5 w-2.5 rounded-full bg-red-500 me-2"></div>
            {{ moduleEnabled(module) ? 'Enabled' : 'Disabled' }}
          </div>
        </cu-table-cell>
      </cu-table-row>
    </cu-table-body>
  </cu-table>
</template>

<script setup>
import { ref, onMounted, getCurrentInstance } from 'vue'
import { loadModuleData } from '@/utils'
import { initFlowbite } from 'flowbite'
import {
  CuTable,
  CuTableHead,
  CuTableHeadCell,
  CuTableBody,
  CuTableRow,
  CuTableCell
} from '@/components/cu'

const availableModules = ref([])
const modules = ref([])

const availablePremiumModules = ref([])
const premiumModules = ref([])

const premiumMode = ref(false)

const module = ref('crypto_universe')

const { proxy } = getCurrentInstance()

const loadDefaults = async () => {
  await loadModuleData(proxy, module.value, 'instructions', 'js', (data) => {
    if (!Object.hasOwn(data, 'modules')) return

    modules.value = data.modules ?? modules.value
    premiumModules.value = data.premium_modules ?? premiumModules.value
  })

  await loadModuleData(proxy, module.value, 'configs', 'js', (data) => {
    if (!Object.hasOwn(data, 'modules')) return

    availableModules.value = data.modules ?? availableModules.value
    availablePremiumModules.value = data.premium_modules ?? availablePremiumModules.value
  })

  premiumMode.value = proxy.$globalConfigs.premium_mode
}

const moduleEnabled = (module) => {
  return modules.value.includes(module)
}

const premiumModuleEnabled = (module) => {
  return premiumMode.value && premiumModules.value.includes(module)
}

onMounted(async () => {
  initFlowbite()
  await loadDefaults()
})
</script>
