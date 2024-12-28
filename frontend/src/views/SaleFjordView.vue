<template>
  <cu-title title="Sale - Fjord" />

  <div class="mb-2">
    <cu-label name="profiles" label="Profiles" tooltip="Choose profiles to run automation." />
    <VueMultiselect name="profiles" placeholder="Select profiles..." v-model="profiles" :options="availableProfiles"
      :multiple="true" :close-on-select="false" label="name" track-by="serial_number" />
  </div>
  <cu-input name="password" v-model="password" label="Rabby password"
    tooltip="Rabby password. All profiles should have the same rabby password." placeholder="Enter password..." />
  <cu-input name="tokenContractAddress" v-model="tokenContractAddress" label="Token Contract Address"
    tooltip="Time of sale in format `HH:MM:SS` (e.g. 12:00:00)" placeholder="Enter contract address..." />
  <cu-input name="saleTime" v-model="saleTime" label="Sale Time"
    tooltip="Time of sale in format `HH:MM:SS` (e.g. 12:00:00)" placeholder="Enter sale time..." />
  <cu-input name="moveHours" v-model="moveHours" label="Move Time Hours"
    tooltip="Move time N hours ahead to show sale form." placeholder="Enter hours..." />

  <div class="mt-4 mb-4 flex justify-center">
    <cu-button class="w-1/3" color="green" label="Execute" @click="handleExecute" :disabled="moduleRunning" />
    <cu-button class="w-1/3 ml-4" color="red" label="Stop" @click="handleStop" :disabled="!moduleRunning" />
  </div>

  <cu-logs :logs="logs" :module="module" @append:logs="handleAppendLogs" @finished:script="handleScriptFinish" />
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, getCurrentInstance } from 'vue'
import { loadModuleData, stopModule, updateModuleData, startModule, beforeUnloadModule, beforeRouteLeaveModule, loadAdsProfiles } from '@/utils'
import { onBeforeRouteLeave } from 'vue-router'
import { initFlowbite } from 'flowbite'
import {
  CuTitle,
  CuLabel,
  CuInput,
  CuButton,
  CuLogs
} from '@/components/cu'
import VueMultiselect from 'vue-multiselect'

const availableProfiles = ref([])
const profiles = ref([])
const password = ref('')

const tokenContractAddress = ref('')
const saleTime = ref('10:00:00')

const moveHours = ref(6)

const logs = ref([])
const moduleRunning = ref(false)

const module = ref('premium/sale-fjord')

const { proxy } = getCurrentInstance()

const handleAppendLogs = async (log) => logs.value.push(log)
const handleScriptFinish = async () => moduleRunning.value = false

const loadDefaults = async () => {
  await loadAdsProfiles(proxy, (profiles) => {
    availableProfiles.value = profiles
  }, logs)

  await loadModuleData(proxy, module.value, 'instructions', 'python', (data) => {
    if (!Object.hasOwn(data, 'profiles')) return

    profiles.value = availableProfiles.value.filter(item => data.profiles.includes(item.serial_number))
    password.value = data.password
    tokenContractAddress.value = data.token_contract_address
    saleTime.value = data.sale_time
    moveHours.value = data.move_hours
  }, logs)
}

const handleExecute = async () => {
  moduleRunning.value = true

  await updateModuleData(proxy, module.value, 'instructions', 'python', {
    profiles: profiles.value.map(profile => profile.serial_number),
    password: password.value,
    token_contract_address: tokenContractAddress.value,
    sale_time: saleTime.value,
    move_hours: moveHours.value
  }, logs)

  await startModule(proxy, module.value, logs)
}

const handleStop = async () => {
  await stopModule(proxy, module.value)
  moduleRunning.value = false
}

const handleBeforeUnload = beforeUnloadModule(moduleRunning)

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