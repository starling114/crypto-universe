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
      <cu-sidebar-logo text="Crypto Universe" logo="logo.svg" :debug="debugMode" :premium="premiumMode" />
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

      <cu-sidebar-item v-if="premiumModuleEnabled('farm-lighter')" mode="premium">
        <template #left>
          <RectangleStackIcon
            class="flex-shrink-0 w-6 h-6 text-red-700 transition duration-75 dark:text-red-300 group-hover:text-red-900 dark:group-hover:text-red-100" />
        </template>
        <template #center>Farm</template>

        <cu-sidebar-sub-item mode="premium" tag="router-link" link="/farm-lighter">
          <template #left>
            <div
              class="flex-shrink-0 w-4 h-4 text-red-700 dark:text-red-300 group-hover:text-red-900 dark:group-hover:text-red-100"
              :style="{
                maskImage: 'url(lighter.png)',
                WebkitMaskImage: 'url(lighter.png)',
                maskSize: '100% 100%',
                WebkitMaskSize: '100% 100%',
                backgroundColor: 'currentColor'
              }" />
          </template>
          <template #center>Lighter</template>
          <template #right>
            <router-link to="/farm-lighter/settings">
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

      <cu-sidebar-item v-if="moduleEnabled('testnet-mitosis')">
        <template #left>
          <RectangleStackIcon
            class="flex-shrink-0 w-6 h-6 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" />
        </template>
        <template #center>Testnet</template>

        <cu-sidebar-sub-item tag="router-link" link="/testnet-mitosis">
          <template #left>
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

      <cu-sidebar-item v-if="moduleEnabled('activity-treehouse_prize')">
        <template #left>
          <FingerPrintIcon
            class="flex-shrink-0 w-6 h-6 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" />
        </template>
        <template #center>Activity</template>

        <cu-sidebar-sub-item tag="router-link" link="/activity-treehouse_prize">
          <template #left>
            <div
              class="flex-shrink-0 w-4 h-4 text-gray-500 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white"
              :style="{
                maskImage: 'url(treehouse.png)',
                WebkitMaskImage: 'url(treehouse.png)',
                maskSize: '100% 100%',
                WebkitMaskSize: '100% 100%',
                backgroundColor: 'currentColor'
              }" />
          </template>
          <template #center>Treehouse Prize</template>
        </cu-sidebar-sub-item>
      </cu-sidebar-item>

      <cu-sidebar-item v-if="moduleEnabled('chore-rabby_import')">
        <template #left>
          <RectangleGroupIcon
            class="flex-shrink-0 w-6 h-6 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" />
        </template>
        <template #center>Chore</template>

        <cu-sidebar-sub-item tag="router-link" link="/chore-rabby_import">
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
  XMarkIcon,
  ArrowsRightLeftIcon,
  FingerPrintIcon,
  RectangleGroupIcon
} from "@heroicons/vue/24/solid"

const modules = ref([])
const premiumModules = ref([])
const versionUpToDate = ref(true)
const debugMode = ref(false)
const premiumMode = ref(false)
const showVersionBanner = ref(true)

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
  versionUpToDate.value = proxy.$globalConfigs.version_up_to_date
}

const moduleEnabled = (module) => {
  return modules.value.includes(module)
}

const premiumModuleEnabled = (module) => {
  return premiumMode.value && premiumModules.value.includes(module)
}

const handleBannderDismiss = () => {
  showVersionBanner.value = false
}

onMounted(async () => {
  initFlowbite()
  await loadDefaults()
})
</script>
