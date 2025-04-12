import { createApp } from 'vue'
import App from './App.vue'

import { createRouter, createWebHashHistory } from 'vue-router'
import axios from 'axios'
import './assets/tailwind.css'
import { loadConfigs } from '@/utils'
import DashboardView from "@/views/DashboardView"
import MintKingdomlyView from "@/views/premium/MintKingdomlyView"
import MintKingdomlySettingsView from "@/views/settings/premium/MintKingdomlySettingsView"
import MintMagicedenView from "@/views/premium/MintMagicedenView"
import MintMagicedenSettingsView from "@/views/settings/premium/MintMagicedenSettingsView"
import SettingsView from '@/views/settings/SettingsView.vue'
import BalancesView from "@/views/BalancesView"
import BalancesSettingsView from '@/views/settings/BalancesSettingsView.vue'
import WithdrawOkxView from '@/views/WithdrawOkxView.vue'
import WithdrawOkxSettingsView from '@/views/settings/WithdrawOkxSettingsView.vue'
import BridgeJumperView from '@/views/BridgeJumperView.vue'
import BridgeJumperSettingsView from '@/views/settings/BridgeJumperSettingsView.vue'
import BridgeRelayView from '@/views/BridgeRelayView.vue'
import BridgeRelaySettingsView from '@/views/settings/BridgeRelaySettingsView.vue'
import BridgeHyperlaneView from '@/views/BridgeHyperlaneView.vue'
import BridgeHyperlaneSettingsView from '@/views/settings/BridgeHyperlaneSettingsView.vue'
import SwapJumperView from '@/views/SwapJumperView.vue'
import SwapJumperSettingsView from '@/views/settings/SwapJumperSettingsView.vue'
import SwapPancakeswapView from '@/views/SwapPancakeswapView.vue'
import SwapPancakeswapSettingsView from '@/views/settings/SwapPancakeswapSettingsView.vue'
import TransferView from '@/views/TransferView.vue'
import TransferSettingsView from '@/views/settings/TransferSettingsView.vue'
import TestnetMitosisView from '@/views/TestnetMitosisView.vue'
import YtTokensView from '@/views/YtTokensView.vue'
import YtTokensSettingsView from '@/views/settings/YtTokensSettingsView.vue'
import ActivityTreehousePrizeView from '@/views/ActivityTreehousePrizeView.vue'
import ChoreRabbyImportView from '@/views/ChoreRabbyImportView.vue'

const app = createApp(App)

app.config.globalProperties.$axios = axios.create({
  // baseURL: 'http://' + window.location.host,
  baseURL: 'http://localhost:3000',
})
loadConfigs(app.config.globalProperties, (data) => { app.config.globalProperties.$globalConfigs = data })

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: DashboardView,
    meta: { title: 'CU | Dashboard' }
  },
  {
    path: '/mint-kingdomly',
    name: 'Mint Kingdomly',
    component: MintKingdomlyView,
    meta: { title: 'CU | Mint Kingdomly' }
  },
  {
    path: '/mint-kingdomly/settings',
    name: 'Mint Kingdomly Settings',
    component: MintKingdomlySettingsView,
    meta: { title: 'CU | Mint Kingdomly Settings' }
  },
  {
    path: '/mint-magiceden',
    name: 'Mint Magiceden',
    component: MintMagicedenView,
    meta: { title: 'CU | Mint Magiceden' }
  },
  {
    path: '/mint-magiceden/settings',
    name: 'Mint Magiceden Settings',
    component: MintMagicedenSettingsView,
    meta: { title: 'CU | Mint Magiceden Settings' }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: SettingsView,
    meta: { title: 'CU | Balances Settings' }
  },
  {
    path: '/balances',
    name: 'Balances',
    component: BalancesView,
    meta: { title: 'CU | Balances' }
  },
  {
    path: '/balances/settings',
    name: 'Balances Settings',
    component: BalancesSettingsView,
    meta: { title: 'CU | Balances Settings' }
  },
  {
    path: '/withdraw-okx',
    name: 'Withdraw OKX',
    component: WithdrawOkxView,
    meta: { title: 'CU | Withdraw OKX' }
  },
  {
    path: '/withdraw-okx/settings',
    name: 'Withdraw OKX Settings',
    component: WithdrawOkxSettingsView,
    meta: { title: 'CU | Withdraw OKX Settings' }
  },
  {
    path: '/bridge-jumper',
    name: 'Bridge Jumper',
    component: BridgeJumperView,
    meta: { title: 'CU | Bridge Jumper' }
  },
  {
    path: '/bridge-jumper/settings',
    name: 'Bridge Jumper Settings',
    component: BridgeJumperSettingsView,
    meta: { title: 'CU | Bridge Jumper Settings' }
  },
  {
    path: '/bridge-relay',
    name: 'Bridge Relay',
    component: BridgeRelayView,
    meta: { title: 'CU | Bridge Relay' }
  },
  {
    path: '/bridge-relay/settings',
    name: 'Bridge Relay Settings',
    component: BridgeRelaySettingsView,
    meta: { title: 'CU | Bridge Relay Settings' }
  },
  {
    path: '/bridge-hyperlane',
    name: 'Bridge Hyperlane',
    component: BridgeHyperlaneView,
    meta: { title: 'CU | Bridge Hyperlane' }
  },
  {
    path: '/bridge-hyperlane/settings',
    name: 'Bridge Hyperlane Settings',
    component: BridgeHyperlaneSettingsView,
    meta: { title: 'CU | Bridge Hyperlane Settings' }
  },
  {
    path: '/swap-jumper',
    name: 'Swap Jumper',
    component: SwapJumperView,
    meta: { title: 'CU | Swap Jumper' }
  },
  {
    path: '/swap-jumper/settings',
    name: 'Swap Jumper Settings',
    component: SwapJumperSettingsView,
    meta: { title: 'CU | Swap Jumper Settings' }
  },
  {
    path: '/swap-pancakeswap',
    name: 'Swap Pancakeswap',
    component: SwapPancakeswapView,
    meta: { title: 'CU | Swap Pancakeswap' }
  },
  {
    path: '/swap-pancakeswap/settings',
    name: 'Swap Pancakeswap Settings',
    component: SwapPancakeswapSettingsView,
    meta: { title: 'CU | Swap Pancakeswap Settings' }
  },
  {
    path: '/transfer',
    name: 'Transfer',
    component: TransferView,
    meta: { title: 'CU | Transfer' }
  },
  {
    path: '/transfer/settings',
    name: 'Transfer Settings',
    component: TransferSettingsView,
    meta: { title: 'CU | Transfer Settings' }
  },
  {
    path: '/yt_tokens',
    name: 'YT Tokens',
    component: YtTokensView,
    meta: { title: 'CU | YT Tokens' }
  },
  {
    path: '/yt_tokens/settings',
    name: 'YT Tokens Settings',
    component: YtTokensSettingsView,
    meta: { title: 'CU | YT Tokens Settings' }
  },
  {
    path: '/testnet-mitosis',
    name: 'Testnet Mitosis',
    component: TestnetMitosisView,
    meta: { title: 'CU | Testnet - Mitosis' }
  },
  {
    path: '/activity-treehouse_prize',
    name: 'Activity Treehouse Prize',
    component: ActivityTreehousePrizeView,
    meta: { title: 'CU | Activity - Treehouse Prize' }
  },
  {
    path: '/chore-rabby_import',
    name: 'Chore Rabby Import',
    component: ChoreRabbyImportView,
    meta: { title: 'CU | Chore - Rabby Import' }
  }
]

const router = new createRouter({
  routes: routes,
  history: createWebHashHistory(),
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title
  next()
})

app.use(router)
app.mount('#app')
