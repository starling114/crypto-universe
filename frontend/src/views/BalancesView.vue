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
              <a :href="`https://debank.com/profile/${item.wallet}/history`">
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
          <cu-table-cell>{{ formatAmount(totalRowData.native) }} {{ totalRowData.nativeName }}</cu-table-cell>
          <cu-table-cell>${{ formatAmount(totalRowData.nativeInUsd, 2) }}</cu-table-cell>
        </cu-table-row>
      </cu-table-foot>
    </cu-table>

    <cu-pagination :current-page="currentPage" :total-items="totalItems" :items-per-page="itemsPerPage"
      @update:currentPage="handlePageChange" @update:itemsPerPage="handleItemsPerPageChange" />
  </cu-spinner>
</template>


<script setup>
import { ref, computed, onMounted, getCurrentInstance, watch } from 'vue'
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

const activeNetwork = ref(localStorage.getItem('activeNetwork') || null)
const isDataLoaded = ref(false)
const data = ref([])
const dataCount = ref(0)
const currentPage = ref(parseInt(localStorage.getItem('currentPage')) || 1)
const itemsPerPage = ref(parseInt(localStorage.getItem('itemsPerPage')) || 5)

const configs = ref({})

const module = ref('balances')

const { proxy } = getCurrentInstance()

const loadDefaults = async () => {
  await loadModuleData(proxy, '', 'configs', 'global', (data) => {
    configs.value = data ?? configs.value
  })

  await loadModuleData(proxy, module.value, 'instructions', 'js', (data) => {
    if (!Object.hasOwn(data, 'addresses')) return

    minBalanceHighlight.value = parseFloat(data.min_balance_highlight)
    networks.value = data.networks ?? networks.value
    totalRow.value = data.total_row ?? totalRow.value
  })

  await loadModuleData(proxy, module.value, 'configs', 'js', (data) => {
    if (!Object.hasOwn(data, 'networks')) return

    availableNetworks.value = data.networks ?? availableNetworks.value
  })

  activeNetwork.value = activeNetwork.value || enabledNetworks.value[0]
}

const enabledNetworks = computed(() => {
  return availableNetworks.value
    .filter((network) => networks.value[network] ? networks.value[network].enabled : false)
})

const showTotalRow = computed(() => {
  return paginatedData.value.length != 0 && totalRow.value
})

const formatAmount = (value, decimals = 5) => {
  let float = parseFloat(value)

  return float > 0 ? parseFloat(float.toFixed(decimals)) : parseFloat(float.toFixed(1))
}

const totalRowData = computed(() => {
  let totalRowData = { transactionsCount: 0, native: 0, nativeInUsd: 0 }

  paginatedData.value.forEach(data => {
    totalRowData.transactionsCount += data.transactionsCount
    totalRowData.native += data.native
    totalRowData.nativeInUsd += data.nativeInUsd
    totalRowData.nativeName = data.nativeName
  })

  return totalRowData
})

watch(itemsPerPage, (newVal) => {
  localStorage.setItem('itemsPerPage', newVal)
})

watch(currentPage, (newVal) => {
  localStorage.setItem('currentPage', newVal)
})

watch(activeNetwork, (newVal) => {
  localStorage.setItem('activeNetwork', newVal)
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
