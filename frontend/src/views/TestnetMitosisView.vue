<template>
  <cu-title title="Testnet - Mitosis" />

  <div class="mb-2">
    <cu-label name="profiles" label="Profiles" tooltip="Choose profiles to run automation." />
    <VueMultiselect name="profiles" placeholder="Select profiles..." v-model="profiles" :options="availableProfiles"
      :multiple="true" :close-on-select="false" label="name" track-by="serial_number" />
  </div>
  <cu-input name="password" v-model="password" label="Rabby password"
    tooltip="Rabby password. All profiles should have the same rabby password." placeholder="Enter password..." />

  <cu-label name="tasks" label="Tasks" tooltip="
    `mito_game` - play MITO game N minutes, 
    `faceuts` - claim faceuts, 
    `make_deposits` - deposit funds from other networks to Mitosis, 
    `opt_in` - wrap assets to mi*,
    `telo_wrap_mito` - wrap MITO to WMITO for swap volume (leaves 25 MITO on balance)
    `telo_withdraw` - repay and withdraw Telo LBTC and ETH pools,
    `chromo_swaps` - swaps all the assets to miETH and then executes N swaps. At the end swaps 75% of funds back to WMITO, 17.5% leaves in miETH and 7.5% in miLBTC,
    `telo_supply` - is this is chosen at the end of chromo_swaps swaps 50% of funds back to WMITO, 25% leaves in miETH, 25% supplies to Telo pool (ETH or LBTC),
    `telo_unwrap_mito` - unwrap WMITO to MITO" />
  <cu-horizontal-checkbox-group name="tasks" v-model="tasks" :options="availableTasks" :batchSize=4 />

  <cu-collapsible-section name="additionalSettings" title="Additional Settings">
    <div class="mb-2">
      <cu-checkbox name="parallelExecution" v-model="parallelExecution" label="Parallel execution"
        tooltip="Run profiles in parallel, set how many parallel processes to run." />
    </div>
    <div v-if="parallelExecution" class="mt-1 grid grid-cols-6 gap-2">
      <cu-input name="maxProcesses" size="small" v-model="maxProcesses" placeholder="Max processes" />
    </div>
    <div v-if="tasks.includes('mito_game')" class="mt-1 grid grid-cols-4 gap-2">
      <cu-input name="mitoGameTime" size="small" v-model="mitoGameTime" label="MITO game play time"
        tooltip="Number of minutes to play MITO game." placeholder="Enter minutes..." />
    </div>
    <div v-if="tasks.includes('chromo_swaps')" class="mt-1 grid grid-cols-4 gap-2">
      <cu-input name="chromoSwapsCount" size="small" v-model="chromoSwapsCount" label="Number of chromo swaps"
        tooltip="Number of chomo swaps." placeholder="Enter number..." />
    </div>
  </cu-collapsible-section>

  <div class="mt-4 mb-4 flex justify-center">
    <cu-button class="w-1/3" color="green" label="Execute" @click="handleExecute" :disabled="moduleRunning" />
    <cu-button class="w-1/3 ml-4" color="red" label="Stop" @click="handleStop" :disabled="!moduleRunning" />
  </div>

  <cu-logs :logs="logs" :module="module" @append:logs="handleAppendLogs" @finished:script="handleScriptFinish" />
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, getCurrentInstance, watch } from 'vue'
import { loadModuleData, stopModule, updateModuleData, startModule, beforeUnloadModule, beforeRouteLeaveModule, loadAdsProfiles } from '@/utils'
import { onBeforeRouteLeave } from 'vue-router'
import { initFlowbite } from 'flowbite'
import {
  CuTitle,
  CuLabel,
  CuHorizontalCheckboxGroup,
  CuInput,
  CuCollapsibleSection,
  CuCheckbox,
  CuButton,
  CuLogs
} from '@/components/cu'
import VueMultiselect from 'vue-multiselect'

const availableProfiles = ref([])
const profiles = ref([])
const password = ref('')

const availableTasks = ref([])
const tasks = ref([])

const parallelExecution = ref(true)
const maxProcesses = ref(5)
const mitoGameTime = ref(5)
const chromoSwapsCount = ref(25)
const supplyEverySwap = ref(5)

const logs = ref([])
const moduleRunning = ref(false)

const module = ref('testnet-mitosis')

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

    tasks.value = data.tasks

    parallelExecution.value = data.parallel_execution
    maxProcesses.value = data.max_processes
    mitoGameTime.value = data.mito_game_time
    chromoSwapsCount.value = data.chromo_swaps_count
    supplyEverySwap.value = data.supply_every_swap
  }, logs)

  await loadModuleData(proxy, module.value, 'configs', 'python', (data) => {
    if (!Object.hasOwn(data, 'available_tasks')) return

    availableTasks.value = data.available_tasks

  }, logs)

  console.log(availableProfiles.value)
}

const handleExecute = async () => {
  moduleRunning.value = true

  await updateModuleData(proxy, module.value, 'instructions', 'python', {
    profiles: profiles.value.map(profile => profile.serial_number),
    password: password.value,
    tasks: tasks.value,
    parallel_execution: parallelExecution.value,
    max_processes: parseInt(maxProcesses.value),
    mito_game_time: parseFloat(mitoGameTime.value),
    chromo_swaps_count: parseInt(chromoSwapsCount.value),
    supply_every_swap: parseInt(supplyEverySwap.value)
  }, logs)

  await startModule(proxy, module.value, logs)
}

const handleStop = async () => {
  await stopModule(proxy, module.value)
  moduleRunning.value = false
}

watch(tasks, () => {
  setTimeout(() => {
    initFlowbite()
  }, 10)
})

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