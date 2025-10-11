import fs from 'fs'
import os from 'os'
import axios from 'axios'
import path from 'path'

export const wait = ms => new Promise(r => setTimeout(r, ms))
export const sleep = async (millis) => new Promise(resolve => setTimeout(resolve, millis))
export const configs = readJson('./configs.json')

const prices = await getTokensPrice()

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
  const dir = path.dirname(filePath)

  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true })
  }

  fs.writeFileSync(filePath, JSON.stringify(jsonData, null, 2), 'utf-8')
}

export function parseLogs(log) {
  return log.split('\n').filter(line => line.trim() !== '')
}

export function debugMode() {
  const instructions = readJson('./backend/modules/crypto_universe/instructions.json')

  return !!instructions.debug_mode
}

export function runAuthentication() {
  return process.env.BASIC_AUTH === "true"
}

export function pythonExecutable() {
  return os.platform() === 'win32' ? 'myenv\\Scripts\\python.exe' : 'myenv/bin/python'
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

export async function adsProfiles() {
  const apiUrl = (process.env.ADSPOWER_URL || 'http://local.adspower.net:50325/api/v1') + '/user/list';
  const pageSize = 100;
  let allProfiles = [];
  let page = 1;

  while (true) {
    const { data: { code, data } } = await axios.get(apiUrl, {
      params: { page_size: pageSize, page }
    });

    if (code !== 0 || !data?.list?.length) break;

    allProfiles.push(...data.list.map(profile => ({
      serial_number: profile.serial_number,
      name: profile.name
    })));

    page++;
  }

  return allProfiles.sort((a, b) => a.serial_number - b.serial_number);
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

export async function getTokensPrice() {
  const nativeTokens = new Set()
  for (const chain in configs.chains) {
    nativeTokens.add(configs.chains[chain].native_token)
  }

  let tokens = Array.from(nativeTokens).join(',')
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

export function premiumMode() {
  const instructions = readJson('./backend/modules/crypto_universe/instructions.json')

  return !!instructions.license_key
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
