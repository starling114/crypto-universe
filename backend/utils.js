import fs from 'fs'
import axios from 'axios'
import path from 'path'

export const wait = ms => new Promise(r => setTimeout(r, ms))
export const sleep = async (millis) => new Promise(resolve => setTimeout(resolve, millis))
export const configs = readJson('./configs.json')

const prices = await getTokensPrice('ETH,MATIC,BNB')

export function random(min, max) {
  min = Math.ceil(min)
  max = Math.floor(max)
  return Math.floor(Math.random() * (max - min + 1) + min)
}

export function formatAmount(value, decimals = 5) {
  let float = parseFloat(value)

  return float > 0 ? parseFloat(float.toFixed(decimals)) : parseFloat(float.toFixed(1))
}

export function readJson(filePath) {
  try {
    const fileContent = fs.readFileSync(filePath, 'utf-8')
    return JSON.parse(fileContent)
  } catch {
    return {}
  }
}

export function writeJson(filePath, jsonData) {
  fs.writeFileSync(filePath, JSON.stringify(jsonData, null, 2), 'utf-8')
}

export function parseLogs(log) {
  return log.split('\n').filter(line => line.trim() !== '')
}

export function moduleDataFilepath(module, type, script_type) {
  let folder = ''

  switch (script_type) {
    case 'js':
      folder = `backend/modules/${module}/`
      break
    case 'python':
      const module_location = module.split('-').join('/')
      folder = `scripts/modules/${module_location}/`
      break
  }

  return path.resolve(`${folder}${type}.json`)
}

export function getRps(chain) {
  const rpcs = configs.chains[chain].rpcs

  return rpcs[random(0, rpcs.length - 1)]
}

export function getNativeToken(chain) {
  return configs.chains[chain].native_token
}

export function getNativeTokenPriceInUsd(chain) {
  const nativeToken = getNativeToken(chain)

  return prices[nativeToken] ? prices[nativeToken].USD : 0
}

export async function getTokensPrice(tokens) {
  let prices = {}
  let isFetched = false
  let retry = 0

  while (!isFetched) {
    await axios.get(`https://min-api.cryptocompare.com/data/pricemulti?fsyms=${tokens}&tsyms=USD`).then(response => {
      prices = response.data
      isFetched = true
    }).catch(e => {
      retry++

      if (retry > 3) {
        isFetched = true
      }
    })
  }

  return prices
}

export const multicallAddress = '0xca11bde05977b3631167028862be2a173976ca11'
export const multicallAbi = [
  {
    "constant": true,
    "inputs": [],
    "name": "getCurrentBlockTimestamp",
    "outputs": [{ "name": "timestamp", "type": "uint256" }],
    "payable": false,
    "stateMutability": "view",
    "type": "function"
  },
  {
    "constant": false,
    "inputs": [
      {
        "components": [
          { "name": "target", "type": "address" },
          { "name": "callData", "type": "bytes" }
        ],
        "name": "calls",
        "type": "tuple[]"
      }
    ],
    "name": "aggregate",
    "outputs": [
      { "name": "blockNumber", "type": "uint256" },
      { "name": "returnData", "type": "bytes[]" }
    ],
    "payable": false,
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "constant": true,
    "inputs": [],
    "name": "getLastBlockHash",
    "outputs": [{ "name": "blockHash", "type": "bytes32" }],
    "payable": false,
    "stateMutability": "view",
    "type": "function"
  },
  {
    "constant": true,
    "inputs": [{ "name": "addr", "type": "address" }],
    "name": "getEthBalance",
    "outputs": [{ "name": "balance", "type": "uint256" }],
    "payable": false,
    "stateMutability": "view",
    "type": "function"
  },
  {
    "constant": true,
    "inputs": [],
    "name": "getCurrentBlockDifficulty",
    "outputs": [{ "name": "difficulty", "type": "uint256" }],
    "payable": false,
    "stateMutability": "view",
    "type": "function"
  },
  {
    "constant": true,
    "inputs": [],
    "name": "getCurrentBlockGasLimit",
    "outputs": [{ "name": "gaslimit", "type": "uint256" }],
    "payable": false,
    "stateMutability": "view",
    "type": "function"
  },
  {
    "constant": true,
    "inputs": [],
    "name": "getCurrentBlockCoinbase",
    "outputs": [{ "name": "coinbase", "type": "address" }],
    "payable": false,
    "stateMutability": "view",
    "type": "function"
  },
  {
    "constant": true,
    "inputs": [{ "name": "blockNumber", "type": "uint256" }],
    "name": "getBlockHash",
    "outputs": [{ "name": "blockHash", "type": "bytes32" }],
    "payable": false,
    "stateMutability": "view",
    "type": "function"
  }
]