import {
  getNativeToken,
  random,
  multicallAbi,
  multicallAddress,
  formatAmount,
  getNativeTokenPriceInUsd,
  getRps,
  readJson
} from "../../utils.js"
import { createPublicClient, http, formatEther } from 'viem'
import { mainnet, arbitrum, base, optimism, scroll, blast, bsc, polygon } from "viem/chains"

const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
const viem_chains = {
  'ethereum': mainnet,
  'arbitrum': arbitrum,
  'base': base,
  'optimism': optimism,
  'scroll': scroll,
  'blast': blast,
  'polygon': polygon,
  'bsc': bsc
}

let walletsData = []

async function fetchWallets(network) {
  walletsData = []
  let instructions = readJson('./backend/modules/balances/instructions.json')
  let wallets = instructions.addresses ? instructions.addresses : []

  let transactionCounts
  let balanceResults

  let isSuccess = false, retry = 0

  while (!isSuccess) {
    const rpc = getRps(network)
    const client = createPublicClient({ chain: viem_chains[network], transport: http(rpc), batch: { multicall: true } })

    try {
      const promises = wallets.map(wallet => client.getTransactionCount({ address: wallet }))

      await Promise.all(promises).then(results => {
        transactionCounts = results.map((count, index) => ({ address: wallets[index], count }))
      })

      const balanceMulticall = wallets.map(wallet => {
        return {
          address: multicallAddress,
          abi: multicallAbi,
          functionName: 'getEthBalance',
          args: [wallet]
        }
      })

      balanceResults = await client.multicall({
        contracts: balanceMulticall,
        multicallAddress: multicallAddress
      })

      isSuccess = true
    } catch (e) {
      retry++

      if (retry > 3) {
        isSuccess = true
      }
    }
  }

  const nativeName = getNativeToken(network)
  const nativePrice = getNativeTokenPriceInUsd(network)

  walletsData = wallets.map((wallet, index) => {
    let eth = 0
    let formattedIndex = index + 1

    if (balanceResults) {
      eth = formatEther(balanceResults[index].result || 0)
    } else {
      eth = 0
    }

    switch (instructions.naming_strategy) {
      case 'alphabet_batches':
        let letter = alphabet[Math.floor(index / 5)];
        let batchIndex = (index % 5) + 1;
        formattedIndex = letter + batchIndex
        break
    }

    return {
      index: formattedIndex,
      wallet: wallet,
      transactionsCount: transactionCounts ? transactionCounts[index].count : 0,
      native: formatAmount(eth),
      nativeName: nativeName,
      nativeInUsd: formatAmount(eth * nativePrice, 2)
    }
  })
}

export async function balancesData(network) {
  await fetchWallets(network)

  return walletsData.sort((a, b) => a.index - b.index)
}