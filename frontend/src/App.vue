<template>
  <div v-if="!versionUpToDate && showVersionBanner"
    class="fixed bottom-0 start-0 z-50 flex justify-between w-full p-4 border-t border-orange-400 bg-orange-200 dark:bg-orange-900 dark:border-orange-600">
    <div class="flex items-center mx-auto">
      <p class="flex items-center text-sm font-normal text-gray-900 dark:text-white">
        <FireIcon class="mr-1 flex-shrink-0 w-6 h-6" />

        <span>Crypto Universe is out of date, please update it running `git pull`</span>
      </p>
    </div>
    <div class="flex items-center">
      <button @click="handleBannderDismiss" type="button"
        class="flex-shrink-0 inline-flex justify-center w-7 h-7 items-center text-gray-400 hover:bg-none hover:text-gray-900 rounded-lg text-sm p-1.5 dark:hover:text-white">
        <XMarkIcon class="flex-shrink-0 w-6 h-6" />
      </button>
    </div>
  </div>
  <section>
    <cu-sidebar>
      <cu-sidebar-logo text="Crypto Universe" logo="logo.svg" :debug="debugMode" />
      <cu-sidebar-item tag="router-link" link="/">
        <template #left>
          <ChartPieIcon
            class="flex-shrink-0 w-6 h-6 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" />
        </template>
        <template #center>Dashboard</template>
        <template #right>
          <router-link to="/settings">
            <AdjustmentsHorizontalIcon
              class="flex-shrink-0 w-6 h-6 text-gray-500 hidden hover:text-gray-900 group-hover:block transition duration-75 dark:text-gray-400 dark:hover:text-white" />
          </router-link>
        </template>
      </cu-sidebar-item>

      <cu-sidebar-item v-if="moduleEnabled('balances')" tag="router-link" link="/balances">
        <template #left>
          <BanknotesIcon
            class="flex-shrink-0 w-6 h-6 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" />
        </template>
        <template #center>Balances</template>
        <template #right>
          <router-link to="/balances/settings">
            <AdjustmentsHorizontalIcon
              class="flex-shrink-0 w-6 h-6 text-gray-500 hidden hover:text-gray-900 group-hover:block transition duration-75 dark:text-gray-400 dark:hover:text-white" />
          </router-link>
        </template>
      </cu-sidebar-item>

      <cu-sidebar-item v-if="moduleEnabled('withdraw-okx')">
        <template #left>
          <ArrowDownOnSquareStackIcon
            class="flex-shrink-0 w-6 h-6 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" />
        </template>
        <template #center>Withdraw</template>

        <cu-sidebar-sub-item tag="router-link" link="/withdraw-okx"><template #left>
            <div
              class="flex-shrink-0 w-4 h-4 text-gray-500 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white"
              :style="{
                maskImage: 'url(okx.png)',
                WebkitMaskImage: 'url(okx.png)',
                maskSize: '100% 100%',
                WebkitMaskSize: '100% 100%',
                backgroundColor: 'currentColor'
              }" />
          </template>
          <template #center>OKX</template>
          <template #right>
            <router-link to="/withdraw-okx/settings">
              <AdjustmentsHorizontalIcon
                class="flex-shrink-0 w-6 h-6 text-gray-500 hidden hover:text-gray-900 group-hover:block transition duration-75 dark:text-gray-400 dark:hover:text-white" />
            </router-link> </template>
        </cu-sidebar-sub-item>
      </cu-sidebar-item>

      <cu-sidebar-item v-if="moduleEnabled('bridge-relay') || moduleEnabled('bridge-hyperlane')">
        <template #left>
          <PaperAirplaneIcon
            class="flex-shrink-0 w-6 h-6 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" />
        </template>
        <template #center>Bridge</template>

        <cu-sidebar-sub-item v-if="moduleEnabled('bridge-relay')" tag="router-link" link="/bridge-relay">
          <template #left>
            <div
              class="flex-shrink-0 w-4 h-4 text-gray-500 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white"
              :style="{
                maskImage: 'url(relay.png)',
                WebkitMaskImage: 'url(relay.png)',
                maskSize: '100% 100%',
                WebkitMaskSize: '100% 100%',
                backgroundColor: 'currentColor'
              }" />
          </template>
          <template #center>Relay</template>
          <template #right>
            <router-link to="/bridge-relay/settings">
              <AdjustmentsHorizontalIcon
                class="flex-shrink-0 w-6 h-6 text-gray-500 hidden hover:text-gray-900 group-hover:block transition duration-75 dark:text-gray-400 dark:hover:text-white" />
            </router-link> </template>
        </cu-sidebar-sub-item>

        <cu-sidebar-sub-item v-if="moduleEnabled('bridge-hyperlane')" tag="router-link" link="/bridge-hyperlane">
          <template #left>
            <div
              class="flex-shrink-0 w-4 h-4 text-gray-500 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white"
              :style="{
                maskImage: 'url(hyperlane.png)',
                WebkitMaskImage: 'url(hyperlane.png)',
                maskSize: '100% 100%',
                WebkitMaskSize: '100% 100%',
                backgroundColor: 'currentColor'
              }" />
          </template>
          <template #center>Hyperlane</template>
          <template #right>
            <router-link to="/bridge-hyperlane/settings">
              <AdjustmentsHorizontalIcon
                class="flex-shrink-0 w-6 h-6 text-gray-500 hidden hover:text-gray-900 group-hover:block transition duration-75 dark:text-gray-400 dark:hover:text-white" />
            </router-link> </template>
        </cu-sidebar-sub-item>
      </cu-sidebar-item>

      <cu-sidebar-item v-if="moduleEnabled('transfer')" tag="router-link" link="/transfer">
        <template #left>
          <ArrowUpOnSquareStackIcon
            class="transform rotate-270 flex-shrink-0 w-6 h-6 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" />
        </template>
        <template #center>Transfer</template>
        <template #right>
          <router-link to="/transfer/settings">
            <AdjustmentsHorizontalIcon
              class="flex-shrink-0 w-6 h-6 text-gray-500 hidden hover:text-gray-900 group-hover:block transition duration-75 dark:text-gray-400 dark:hover:text-white" />
          </router-link>
        </template>
      </cu-sidebar-item>

      <cu-sidebar-item v-if="moduleEnabled('testnet-mitosis')">
        <template #left>
          <RectangleStackIcon
            class="flex-shrink-0 w-6 h-6 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" />
        </template>
        <template #center>Testnets</template>

        <cu-sidebar-sub-item tag="router-link" link="/testnet-mitosis"><template #left>
            <div
              class="flex-shrink-0 w-4 h-4 text-gray-500 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white"
              :style="{
                maskImage: 'url(mitosis.png)',
                WebkitMaskImage: 'url(mitosis.png)',
                maskSize: '100% 100%',
                WebkitMaskSize: '100% 100%',
                backgroundColor: 'currentColor'
              }" />
          </template>
          <template #center>Mitosis</template>
        </cu-sidebar-sub-item>
      </cu-sidebar-item>

      <cu-sidebar-theme-switch />
    </cu-sidebar>

    <main class="p-6 sm:ml-64 bg-white dark:bg-gray-900">
      <div class="bg-gray-50 shadow-2xl rounded-lg p-4 dark:shadow-none dark:bg-gray-800">
        <router-view />
      </div>
    </main>
  </section>
</template>

<script setup>
import { ref, onMounted, getCurrentInstance } from 'vue'
import { loadModuleData } from '@/utils'
import { initFlowbite } from 'flowbite'
import {
  CuSidebar,
  CuSidebarLogo,
  CuSidebarItem,
  CuSidebarSubItem,
  CuSidebarThemeSwitch
} from '@/components/cu'
import {
  ChartPieIcon,
  AdjustmentsHorizontalIcon,
  BanknotesIcon,
  ArrowDownOnSquareStackIcon,
  PaperAirplaneIcon,
  ArrowUpOnSquareStackIcon,
  FireIcon,
  RectangleStackIcon,
  XMarkIcon
} from "@heroicons/vue/24/solid"

const modules = ref({})
const versionUpToDate = ref(true)
const debugMode = ref(false)
const showVersionBanner = ref(true)

const module = ref('crypto_universe')

const { proxy } = getCurrentInstance()

const loadDefaults = async () => {
  await loadModuleData(proxy, module.value, 'instructions', 'js', (data) => {
    if (!Object.hasOwn(data, 'modules')) return

    modules.value = data.modules
  })

  await proxy.$axios.get('/api/configs').then((response) => {
    if (!Object.hasOwn(response.data, 'debug_mode')) return

    debugMode.value = response.data.debug_mode
    versionUpToDate.value = response.data.version_up_to_date
  })
}

const moduleEnabled = (module) => {
  return modules.value[module] ? modules.value[module].enabled : false
}

const handleBannderDismiss = () => {
  showVersionBanner.value = false
}

onMounted(async () => {
  initFlowbite()
  await loadDefaults()
})
</script>
