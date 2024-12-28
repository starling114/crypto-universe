import fs from 'fs'
import os from 'os'
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
  const dir = path.dirname(filePath)

  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true })
  }

  fs.writeFileSync(filePath, JSON.stringify(jsonData, null, 2), 'utf-8')
}

export function parseLogs(log) {
  return log.split('\n').filter(line => line.trim() !== '')
}

export function compareVersions(version1, version2) {
  const v1Parts = version1.split('.').map(Number)
  const v2Parts = version2.split('.').map(Number)
  const maxLength = Math.max(v1Parts.length, v2Parts.length)

  for (let i = 0; i < maxLength; i++) {
    const part1 = v1Parts[i] || 0
    const part2 = v2Parts[i] || 0

    if (part1 < part2) return false
  }

  return true
}

export function debugMode() {
  return process.env.DEBUG === "true"
}

export function runAuthentication() {
  return process.env.BASIC_AUTH === "true"
}

async function fetchRemoteVersion(localVersion) {
  try {
    const response = await axios.get(`https://crypto-universe.starling114.workers.dev?version=${localVersion}`)
    return response.data
  } catch {
    return false
  }
}

export async function checkVersion() {
  if (debugMode()) return true

  const localVersion = readJson('./package.json').version

  if (!localVersion) return true

  let latestVersion = await fetchRemoteVersion(localVersion)
  latestVersion ||= await fetchVersion()

  if (!latestVersion) return true

  const upToDate = compareVersions(localVersion, latestVersion)

  if (!upToDate) {
    console.log('\x1b[31m', 'Crypto Universe is out of date, please update it running `git pull`')
    console.log('\x1b[31m', `Latest available version: ${latestVersion}, Local version: ${localVersion}`)
    console.log('\x1b[0m')
  }

  return upToDate
}

async function fetchVersion() {
  try {
    const response = await axios.get('https://raw.githubusercontent.com/starling114/crypto-universe/refs/heads/main/package.json')
    return response.data.version
  } catch {
    return false
  }
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
  const apiUrl = 'http://local.adspower.net:50325/api/v1/user/list';
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

export function premiumMode() {
  const instructions = readJson('./backend/modules/crypto_universe/instructions.json')

  return !!instructions.lisence_key
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