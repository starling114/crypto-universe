<template>
  <section>
    <cu-sidebar>
      <cu-sidebar-logo text="Crypto Universe" logo="logo.png" :debug="debugMode" :premium="premiumMode" />
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

      <cu-sidebar-item v-if="premiumModuleEnabled('mint-magiceden') || premiumModuleEnabled('mint-kingdomly')"
        mode="premium">
        <template #left>
          <RectangleStackIcon
            class="flex-shrink-0 w-6 h-6 text-red-700 transition duration-75 dark:text-red-300 group-hover:text-red-900 dark:group-hover:text-red-100" />
        </template>
        <template #center>Mint</template>

        <cu-sidebar-sub-item v-if="premiumModuleEnabled('mint-magiceden')" mode="premium" tag="router-link"
          link="/mint-magiceden"><template #left>
            <div
              class="flex-shrink-0 w-4 h-4 text-red-700 dark:text-red-300 group-hover:text-red-900 dark:group-hover:text-red-100"
              :style="{
                maskImage: 'url(magiceden.png)',
                WebkitMaskImage: 'url(magiceden.png)',
                maskSize: '100% 100%',
                WebkitMaskSize: '100% 100%',
                backgroundColor: 'currentColor'
              }" />
          </template>
          <template #center>Magiceden</template>
          <template #right>
            <router-link to="/mint-magiceden/settings">
              <AdjustmentsHorizontalIcon
                class="flex-shrink-0 w-6 h-6 text-red-700 hidden hover:text-red-900 group-hover:block transition duration-75 dark:text-red-400 dark:hover:text-white" />
            </router-link>
          </template>
        </cu-sidebar-sub-item>

        <cu-sidebar-sub-item v-if="premiumModuleEnabled('mint-kingdomly')" mode="premium" tag="router-link"
          link="/mint-kingdomly"><template #left>
            <div
              class="flex-shrink-0 w-4 h-4 text-red-700 dark:text-red-300 group-hover:text-red-900 dark:group-hover:text-red-100"
              :style="{
                maskImage: 'url(kingdomly.png)',
                WebkitMaskImage: 'url(kingdomly.png)',
                maskSize: '100% 100%',
                WebkitMaskSize: '100% 100%',
                backgroundColor: 'currentColor'
              }" />
          </template>
          <template #center>Kingdomly</template>
          <template #right>
            <router-link to="/mint-kingdomly/settings">
              <AdjustmentsHorizontalIcon
                class="flex-shrink-0 w-6 h-6 text-red-700 hidden hover:text-red-900 group-hover:block transition duration-75 dark:text-red-400 dark:hover:text-white" />
            </router-link>
          </template>
        </cu-sidebar-sub-item>
      </cu-sidebar-item>

      <cu-sidebar-item v-if="premiumModuleEnabled('airdrop-perps')" mode="premium">
        <template #left>
          <RocketLaunchIcon
            class="flex-shrink-0 w-6 h-6 text-red-700 transition duration-75 dark:text-red-300 group-hover:text-red-900 dark:group-hover:text-red-100" />
        </template>
        <template #center>Airdrop</template>

        <cu-sidebar-sub-item v-if="premiumModuleEnabled('airdrop-perps')" mode="premium" tag="router-link"
          link="/airdrop-perps">
          <template #left>
            <div
              class="flex-shrink-0 w-4 h-4 text-red-700 dark:text-red-300 group-hover:text-red-900 dark:group-hover:text-red-100"
              :style="{
                maskImage: 'url(hyperliquid.png)',
                WebkitMaskImage: 'url(hyperliquid.png)',
                maskSize: '100% 100%',
                WebkitMaskSize: '100% 100%',
                backgroundColor: 'currentColor'
              }" />
          </template>
          <template #center>Perps</template>
          <template #right>
            <router-link to="/airdrop-perps/settings">
              <AdjustmentsHorizontalIcon
                class="flex-shrink-0 w-6 h-6 text-red-700 hidden hover:text-red-900 group-hover:block transition duration-75 dark:text-red-400 dark:hover:text-white" />
            </router-link>
          </template>
        </cu-sidebar-sub-item>
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

      <cu-sidebar-item v-if="moduleEnabled('yt_tokens')" tag="router-link" link="/yt_tokens">
        <template #left>
          <div
            class="flex-shrink-0 w-4 h-4 text-gray-500 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white"
            :style="{
              maskImage: 'url(pendle.png)',
              WebkitMaskImage: 'url(pendle.png)',
              maskSize: '100% 100%',
              WebkitMaskSize: '100% 100%',
              backgroundColor: 'currentColor'
            }" />
        </template>
        <template #center>YT Tokens</template>
        <template #right>
          <router-link to="/yt_tokens/settings">
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

      <cu-sidebar-item
        v-if="moduleEnabled('bridge-jumper') || moduleEnabled('bridge-relay') || moduleEnabled('bridge-hyperlane')">
        <template #left>
          <PaperAirplaneIcon
            class="flex-shrink-0 w-6 h-6 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" />
        </template>
        <template #center>Bridge</template>

        <cu-sidebar-sub-item v-if="moduleEnabled('bridge-jumper')" tag="router-link" link="/bridge-jumper">
          <template #left>
            <div
              class="flex-shrink-0 w-4 h-4 text-gray-500 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white"
              :style="{
                maskImage: 'url(jumper.png)',
                WebkitMaskImage: 'url(jumper.png)',
                maskSize: '100% 100%',
                WebkitMaskSize: '100% 100%',
                backgroundColor: 'currentColor'
              }" />
          </template>
          <template #center>Jumper</template>
          <template #right>
            <router-link to="/bridge-jumper/settings">
              <AdjustmentsHorizontalIcon
                class="flex-shrink-0 w-6 h-6 text-gray-500 hidden hover:text-gray-900 group-hover:block transition duration-75 dark:text-gray-400 dark:hover:text-white" />
            </router-link> </template>
        </cu-sidebar-sub-item>

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

      <cu-sidebar-item v-if="moduleEnabled('swap-jumper') || moduleEnabled('swap-pancakeswap')">
        <template #left>
          <ArrowsRightLeftIcon
            class="flex-shrink-0 w-6 h-6 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" />
        </template>
        <template #center>Swap</template>

        <cu-sidebar-sub-item v-if="moduleEnabled('swap-jumper')" tag="router-link" link="/swap-jumper">
          <template #left>
            <div
              class="flex-shrink-0 w-4 h-4 text-gray-500 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white"
              :style="{
                maskImage: 'url(jumper.png)',
                WebkitMaskImage: 'url(jumper.png)',
                maskSize: '100% 100%',
                WebkitMaskSize: '100% 100%',
                backgroundColor: 'currentColor'
              }" />
          </template>
          <template #center>Jumper</template>
          <template #right>
            <router-link to="/swap-jumper/settings">
              <AdjustmentsHorizontalIcon
                class="flex-shrink-0 w-6 h-6 text-gray-500 hidden hover:text-gray-900 group-hover:block transition duration-75 dark:text-gray-400 dark:hover:text-white" />
            </router-link> </template>
        </cu-sidebar-sub-item>

        <cu-sidebar-sub-item v-if="moduleEnabled('swap-pancakeswap')" tag="router-link" link="/swap-pancakeswap">
          <template #left>
            <div
              class="flex-shrink-0 w-4 h-4 text-gray-500 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white"
              :style="{
                maskImage: 'url(pancakeswap.png)',
                WebkitMaskImage: 'url(pancakeswap.png)',
                maskSize: '100% 100%',
                WebkitMaskSize: '100% 100%',
                backgroundColor: 'currentColor'
              }" />
          </template>
          <template #center>Pancakeswap</template>
          <template #right>
            <router-link to="/swap-pancakeswap/settings">
              <AdjustmentsHorizontalIcon
                class="flex-shrink-0 w-6 h-6 text-gray-500 hidden hover:text-gray-900 group-hover:block transition duration-75 dark:text-gray-400 dark:hover:text-white" />
            </router-link> </template>
        </cu-sidebar-sub-item>
      </cu-sidebar-item>

      <cu-sidebar-item v-if="moduleEnabled('chore-rabby_import') || moduleEnabled('chore-phantom_import')">
        <template #left>
          <RectangleGroupIcon
            class="flex-shrink-0 w-6 h-6 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" />
        </template>
        <template #center>Chore</template>

        <cu-sidebar-sub-item v-if="moduleEnabled('chore-rabby_import')" tag="router-link" link="/chore-rabby_import">
          <template #left>
            <div
              class="flex-shrink-0 w-4 h-4 text-gray-500 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white"
              :style="{
                maskImage: 'url(rabby.png)',
                WebkitMaskImage: 'url(rabby.png)',
                maskSize: '100% 100%',
                WebkitMaskSize: '100% 100%',
                backgroundColor: 'currentColor'
              }" />
          </template>
          <template #center>Rabby Import</template>
        </cu-sidebar-sub-item>

        <cu-sidebar-sub-item v-if="moduleEnabled('chore-phantom_import')" tag="router-link"
          link="/chore-phantom_import">
          <template #left>
            <div
              class="flex-shrink-0 w-4 h-4 text-gray-500 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white"
              :style="{
                maskImage: 'url(phantom.png)',
                WebkitMaskImage: 'url(phantom.png)',
                maskSize: '100% 100%',
                WebkitMaskSize: '100% 100%',
                backgroundColor: 'currentColor'
              }" />
          </template>
          <template #center>Phantom Import</template>
        </cu-sidebar-sub-item>
      </cu-sidebar-item>

      <cu-sidebar-item v-if="moduleEnabled('testing-ads_execution')">
        <template #left>
          <BeakerIcon
            class="flex-shrink-0 w-6 h-6 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" />
        </template>
        <template #center>Testing</template>

        <cu-sidebar-sub-item tag="router-link" link="/testing-ads_execution">
          <template #left>
            <div
              class="flex-shrink-0 w-4 h-4 text-gray-500 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white"
              :style="{
                maskImage: 'url(ads.png)',
                WebkitMaskImage: 'url(ads.png)',
                maskSize: '100% 100%',
                WebkitMaskSize: '100% 100%',
                backgroundColor: 'currentColor'
              }" />
          </template>
          <template #center>ADS Execution</template>
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
  RectangleStackIcon,
  ArrowsRightLeftIcon,
  RectangleGroupIcon,
  BeakerIcon,
  RocketLaunchIcon
} from "@heroicons/vue/24/solid"

const modules = ref([])
const premiumModules = ref([])
const debugMode = ref(false)
const premiumMode = ref(false)

const module = ref('crypto_universe')

const { proxy } = getCurrentInstance()

const loadDefaults = async () => {
  await loadModuleData(proxy, module.value, 'instructions', 'js', (data) => {
    if (!Object.hasOwn(data, 'modules')) return

    modules.value = data.modules
    premiumModules.value = data.premium_modules
  })

  debugMode.value = proxy.$globalConfigs.debug_mode
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
