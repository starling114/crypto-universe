<template>
  <cu-title title="Testnet - Mitosis" />

  <div class="grid grid-cols-2 gap-2">
    <cu-textarea name="profiles" v-model="profiles" label="ADS profile"
      placeholder="Enter profile ids each on the new line..."
      tooltip="Profile ids you want to use in automation (124, 123, ..)" />
    <cu-textarea name="passwords" v-model="passwords" label="Rabby passwords"
      tooltip="Rabby passwords corresponding to the specific profile on the left. You could type only one if all the passwords are the same."
      placeholder="Enter passwords each on the new line..." />
  </div>

  <cu-label label="Tasks" />
  <cu-horizontal-checkbox-group v-model="tasks" :options="availableTasks" />

  <cu-collapsible-section name="additionalSettings" title="Additional Settings">
    <cu-checkbox name="parallelExecution" v-model="parallelExecution" label="Parallel execution"
      tooltip="Run profiles in parallel, set how many parallel processes to run." />
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
import { loadModuleData, updateModuleData, startModule, stopModule, beforeUnloadModule, beforeRouteLeaveModule } from '@/utils'
import { onBeforeRouteLeave } from 'vue-router'
import { initFlowbite } from 'flowbite'
import {
  CuTitle,
  CuTextarea,
  CuLabel,
  CuHorizontalCheckboxGroup,
  CuInput,
  CuCollapsibleSection,
  CuCheckbox,
  CuButton,
  CuLogs
} from '@/components/cu'

const profiles = ref('')
const passwords = ref('')

const availableTasks = ref([])
const tasks = ref([])

const parallelExecution = ref(true)
const maxProcesses = ref(5)

const logs = ref([])
const moduleRunning = ref(false)

const module = ref('testnet-mitosis')

const { proxy } = getCurrentInstance()

const handleAppendLogs = async (log) => logs.value.push(log)
const handleScriptFinish = async () => moduleRunning.value = false

const loadDefaults = async () => {
  await loadModuleData(proxy, module.value, 'instructions', 'python', (data) => {
    if (!Object.hasOwn(data, 'profiles')) return

    profiles.value = data.profiles.join('\n')
    passwords.value = data.passwords.join('\n')

    tasks.value = data.tasks

    parallelExecution.value = data.parallel_execution
    maxProcesses.value = data.max_processes
  }, logs)

  await loadModuleData(proxy, module.value, 'configs', 'python', (data) => {
    if (!Object.hasOwn(data, 'available_tasks')) return

    availableTasks.value = data.available_tasks

  }, logs)

}

const handleExecute = async () => {
  moduleRunning.value = true

  await updateModuleData(proxy, module.value, 'instructions', 'python', {
    profiles: profiles.value.split('\n').filter(Boolean),
    passwords: passwords.value.split('\n').filter(Boolean),
    tasks: tasks.value,
    parallel_execution: parallelExecution.value,
    max_processes: maxProcesses.value
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
