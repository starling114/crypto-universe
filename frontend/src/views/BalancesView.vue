<template>
  <nav class="mt-4 mb-4 flex justify-center">
    <cu-button v-for="network in enabledNetworks" :key="network" @click="loadNetwork(network)"
      :color="network == activeNetwork ? 'orange' : 'default'" :label="network" size="small" class="ml-3 w-1/6">
    </cu-button>
  </nav>

  <cu-spinner :show="!isDataLoaded">
    <cu-table>
      <cu-table-head>
        <cu-table-head-cell>#</cu-table-head-cell>
        <cu-table-head-cell>Wallet</cu-table-head-cell>
        <cu-table-head-cell># txs</cu-table-head-cell>
        <cu-table-head-cell>{{ data[0] ? data[0].nativeName : 'Native' }}</cu-table-head-cell>
        <cu-table-head-cell>{{ data[0] ? data[0].nativeName : 'Native' }} in USD</cu-table-head-cell>
      </cu-table-head>
      <cu-table-body>
        <cu-table-row v-for="(item, index) in paginatedData" :key="index">
          <cu-table-cell>{{ item.index }}</cu-table-cell>
          <cu-table-cell>
            {{ item.wallet }}
            <div class="float-right">
              <a :href="'https://debank.com/profile/' + item.wallet">
                <img src="debank.png" class="inline-block h-4 w-4" />
              </a>
              <a :href="`${configs.chains[activeNetwork].scan}/address/${item.wallet}`" class="ml-2">
                <img :src="`${activeNetwork}_scan.png`" class="inline-block h-4 w-4" />
              </a>
            </div>
          </cu-table-cell>
          <cu-table-cell>{{ item.transactionsCount }}</cu-table-cell>
          <cu-table-cell>
            <span :class="item.native < minBalanceHighlight ? 'text-red-500' : ''">
              {{ item.native }} {{ item.nativeName }}
            </span>
          </cu-table-cell>
          <cu-table-cell>${{ item.nativeInUsd }}</cu-table-cell>
        </cu-table-row>
      </cu-table-body>
      <cu-table-foot v-if="showTotalRow">
        <cu-table-row>
          <cu-table-cell></cu-table-cell>
          <cu-table-cell class="text-right">Total:</cu-table-cell>
          <cu-table-cell>{{ totalRowData.transactionsCount }}</cu-table-cell>
          <cu-table-cell>{{ totalRowData.native }} {{ totalRowData.nativeName }}</cu-table-cell>
          <cu-table-cell>${{ totalRowData.nativeInUsd }}</cu-table-cell>
        </cu-table-row>
      </cu-table-foot>
    </cu-table>

    <cu-pagination :current-page="currentPage" :total-items="totalItems" :items-per-page="itemsPerPage"
      @update:currentPage="handlePageChange" @update:itemsPerPage="handleItemsPerPageChange" />
  </cu-spinner>
</template>


<script setup>
import { ref, computed, onMounted, getCurrentInstance } from 'vue'
import { loadModuleData } from '@/utils'
import { initFlowbite } from 'flowbite'
import {
  CuTable,
  CuTableHead,
  CuTableHeadCell,
  CuTableBody,
  CuTableRow,
  CuTableCell,
  CuTableFoot,
  CuButton,
  CuSpinner,
  CuPagination
} from '@/components/cu'

const minBalanceHighlight = ref(0.00001)
const availableNetworks = ref([])
const networks = ref({})
const totalRow = ref(false)

const activeNetwork = ref()
const isDataLoaded = ref(false)
const data = ref([])
const dataCount = ref(0)
const currentPage = ref(1)
const itemsPerPage = ref(5)

const configs = ref({})

const module = ref('balances')

const { proxy } = getCurrentInstance()

const loadDefaults = async () => {
  await loadModuleData(proxy, '', 'configs', 'global', (data) => {
    configs.value = data
  })

  await loadModuleData(proxy, module.value, 'instructions', 'js', (data) => {
    if (!Object.hasOwn(data, 'addresses')) return

    minBalanceHighlight.value = parseFloat(data.min_balance_highlight)
    networks.value = data.networks
    totalRow.value = data.total_row
  })

  await loadModuleData(proxy, module.value, 'configs', 'js', (data) => {
    if (!Object.hasOwn(data, 'available_networks')) return

    availableNetworks.value = data.available_networks
  })

  activeNetwork.value = enabledNetworks.value[0]
}

const enabledNetworks = computed(() => {
  return availableNetworks.value
    .filter((network) => networks.value[network] ? networks.value[network].enabled : false)
})

const showTotalRow = computed(() => {
  return paginatedData.value.length != 0 && totalRow.value
})

const totalRowData = computed(() => {
  let totalRowData = { transactionsCount: 0, native: 0, nativeInUsd: 0 }

  paginatedData.value.forEach(data => {
    totalRowData.transactionsCount += data.transactionsCount
    totalRowData.native += data.native
    totalRowData.nativeInUsd += data.nativeInUsd
    totalRowData.nativeName = data.nativeName
  })
  totalRowData.native = totalRowData.native.toFixed(5)
  totalRowData.nativeInUsd = totalRowData.nativeInUsd.toFixed(2)

  return totalRowData
})

const totalItems = computed(() => {
  return dataCount.value
})

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  return data.value.slice(start, start + itemsPerPage.value)
})

const loadNetwork = (network) => {
  isDataLoaded.value = false
  activeNetwork.value = network

  proxy.$axios.get('/api/balances', {
    params: { network: network }
  }).then((response) => {
    data.value = response.data
    dataCount.value = response.data.length
    isDataLoaded.value = true
  })
}

const handlePageChange = (newPage) => {
  currentPage.value = newPage
}

const handleItemsPerPageChange = (newItemsPerPage) => {
  itemsPerPage.value = newItemsPerPage
}

onMounted(async () => {
  initFlowbite()
  await loadDefaults()

  if (activeNetwork.value) {
    loadNetwork(activeNetwork.value)
  } else {
    isDataLoaded.value = true
  }
})
</script>
