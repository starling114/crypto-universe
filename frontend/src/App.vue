<template>
  <section>
    <cu-sidebar>
      <cu-sidebar-logo text="Crypto Universe" logo="logo.svg" />
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

      <cu-sidebar-item v-if="moduleEnabled('withdraw_okx')">
        <template #left>
          <ArrowDownOnSquareStackIcon
            class="flex-shrink-0 w-6 h-6 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" />
        </template>
        <template #center>Withdraw</template>

        <cu-sidebar-sub-item tag="router-link" link="/withdraw_okx">
          <template #center>OKX</template>
          <template #right>
            <router-link to="/withdraw_okx/settings">
              <AdjustmentsHorizontalIcon
                class="flex-shrink-0 w-6 h-6 text-gray-500 hidden hover:text-gray-900 group-hover:block transition duration-75 dark:text-gray-400 dark:hover:text-white" />
            </router-link> </template>
        </cu-sidebar-sub-item>
      </cu-sidebar-item>

      <cu-sidebar-item v-if="moduleEnabled('bridge_relay')">
        <template #left>
          <PaperAirplaneIcon
            class="flex-shrink-0 w-6 h-6 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" />
        </template>
        <template #center>Bridge</template>

        <cu-sidebar-sub-item tag="router-link" link="/bridge_relay">
          <template #center>Relay</template>
          <template #right>
            <router-link to="/bridge_relay/settings">
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
  ArrowUpOnSquareStackIcon
} from "@heroicons/vue/24/solid"

const modules = ref({})

const module = ref('crypto_universe')

const { proxy } = getCurrentInstance()

const loadDefaults = async () => {
  await loadModuleData(proxy, module.value, 'instructions', 'js', (data) => {
    if (!Object.hasOwn(data, 'modules')) return

    modules.value = data.modules
  })
}

const moduleEnabled = (module) => {
  return modules.value[module] ? modules.value[module].enabled : false
}

onMounted(async () => {
  initFlowbite()
  await loadDefaults()
})
</script>
