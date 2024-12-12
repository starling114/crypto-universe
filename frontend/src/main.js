import { createApp } from 'vue'
import App from './App.vue'

import { createRouter, createWebHashHistory } from 'vue-router'
import axios from 'axios'
import './assets/tailwind.css'
import DashboardView from "@/views/DashboardView"
import SettingsView from '@/views/settings/SettingsView.vue'
import BalancesView from "@/views/BalancesView"
import BalancesSettingsView from '@/views/settings/BalancesSettingsView.vue'
import WithdrawOkxView from '@/views/WithdrawOkxView.vue'
import WithdrawOkxSettingsView from '@/views/settings/WithdrawOkxSettingsView.vue'
import BridgeRelayView from '@/views/BridgeRelayView.vue'
import BridgeRelaySettingsView from '@/views/settings/BridgeRelaySettingsView.vue'
import BridgeHyperlaneView from '@/views/BridgeHyperlaneView.vue'
import BridgeHyperlaneSettingsView from '@/views/settings/BridgeHyperlaneSettingsView.vue'
import TransferView from '@/views/TransferView.vue'
import TransferSettingsView from '@/views/settings/TransferSettingsView.vue'
import TestnetMitosisView from '@/views/TestnetMitosisView.vue'

const app = createApp(App)

app.config.globalProperties.$axios = axios.create({
  // baseURL: 'http://' + window.location.host,
  baseURL: 'http://localhost:3000',
})

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: DashboardView,
    meta: { title: 'CU | Dashboard' }
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
    path: '/testnet-mitosis',
    name: 'Testnet Mitosis',
    component: TestnetMitosisView,
    meta: { title: 'CU | Testnet Mitosis' }
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
