<template>
  <cu-title title="Chore - Phantom Import" />

  <div class="mb-2">
    <cu-label name="profiles" label="Profiles" tooltip="Choose profiles to run automation." />
    <VueMultiselect name="profiles" placeholder="Select profiles..." v-model="profiles" :options="availableProfiles"
      :multiple="true" :close-on-select="false" label="name" track-by="serial_number" />
  </div>

  <div class="mt-2 grid gap-2 grid-cols-3">
    <cu-textarea name="labels" v-model="labels" label="Labels" placeholder="Enter labels each on the new line..." />
    <cu-textarea name="passwords" v-model="passwords" label="Passwords"
      placeholder="Enter passwords each on the new line..." />
    <cu-textarea name="seedPhrases" v-model="seedPhrases" label="Seed Phrases"
      placeholder="Enter seed phrase each on the new line..." />
  </div>

  <cu-collapsible-section name="additionalSettings" title="Additional Settings">
    <div class="mb-2">
      <cu-checkbox name="parallelExecution" v-model="parallelExecution" label="Parallel execution"
        tooltip="Run profiles in parallel, set how many parallel processes to run." />
    </div>
    <div v-if="parallelExecution" class="mt-1 grid grid-cols-6 gap-2">
      <cu-input name="maxProcesses" size="small" v-model="maxProcesses" placeholder="Max processes" />
    </div>
  </cu-collapsible-section>

  <div class="mt-4 mb-4 flex justify-center">
    <cu-button class="w-1/3" color="green" label="Execute" @click="handleExecute" :disabled="moduleRunning" />
    <cu-button class="w-1/3 ml-4" color="red" label="Stop" @click="handleStop" :disabled="!moduleRunning" />
  </div>

  <cu-logs :logs="logs" :module="module" @append:logs="handleAppendLogs" @finished:script="handleScriptFinish" />
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, getCurrentInstance } from 'vue'
import { loadModuleData, stopModule, updateModuleData, startModule, beforeUnloadModule, beforeRouteLeaveModule, loadProfiles } from '@/utils'
import { onBeforeRouteLeave } from 'vue-router'
import { initFlowbite } from 'flowbite'
import {
  CuTitle,
  CuLabel,
  CuInput,
  CuTextarea,
  CuCollapsibleSection,
  CuCheckbox,
  CuButton,
  CuLogs
} from '@/components/cu'
import VueMultiselect from 'vue-multiselect'

const availableProfiles = ref([])
const profiles = ref([])

const labels = ref('')
const passwords = ref('')
const seedPhrases = ref('')

const parallelExecution = ref(true)
const maxProcesses = ref(5)

const logs = ref([])
const moduleRunning = ref(false)

const module = ref('chore-phantom_import')

const { proxy } = getCurrentInstance()

const handleAppendLogs = async (log) => logs.value.unshift(log)
const handleScriptFinish = async () => moduleRunning.value = false

const loadDefaults = async () => {
  await loadProfiles(proxy, (profiles) => {
    availableProfiles.value = profiles
  }, logs)

  await loadModuleData(proxy, module.value, 'instructions', 'python', (data) => {
    if (!Object.hasOwn(data, 'profiles')) return

    profiles.value = availableProfiles.value.filter(item => data.profiles.includes(item.serial_number))
    labels.value = data.labels?.join('\n') ?? labels.value
    passwords.value = data.passwords?.join('\n') ?? passwords.value
    seedPhrases.value = data.seed_phrases?.join('\n') ?? seedPhrases.value
    parallelExecution.value = data.parallel_execution ?? parallelExecution.value
    maxProcesses.value = data.max_processes ?? maxProcesses.value
  }, logs)
}

const handleExecute = async () => {
  moduleRunning.value = true

  await updateModuleData(proxy, module.value, 'instructions', 'python', {
    profiles: profiles.value.map(profile => profile.serial_number),
    labels: labels.value.split('\n').filter(Boolean),
    passwords: passwords.value.split('\n').filter(Boolean),
    seed_phrases: seedPhrases.value.split('\n').filter(Boolean),
    parallel_execution: parallelExecution.value,
    max_processes: parseInt(maxProcesses.value)
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
