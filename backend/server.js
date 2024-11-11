import express from 'express'
import cors from 'cors'
import { balancesData } from "./modules/balances/balances.js"
import { readJson, writeJson, parseLogs, moduleDataFilepath } from "./utils.js"
import { spawn } from 'child_process'
import { EventEmitter } from 'events'
import AnsiToHtml from 'ansi-to-html'

const app = express()
const port = 3000
const apiRoutes = express.Router()

const logEmitter = new EventEmitter()
const ansiToHtml = new AnsiToHtml()

let pythonProcesses = {}

app.use(cors())
app.use(express.json())
app.use('/api', apiRoutes)

app.use(express.static('./frontend/dist'))

app.get('*', (req, res) => {
  res.sendFile('./frontend/dist/index.html')
})

apiRoutes.get('/balances', async (req, res) => {
  const responseData = await balancesData(req.query.network)
  res.json(responseData)
})

apiRoutes.get('/module_data', async (req, res) => {
  const { module, type, module_type } = req.query

  try {
    const json = readJson(moduleDataFilepath(module, type, module_type))

    return res.json(json)
  } catch (error) {
    if (error.code === 'ENOENT') {
      return res.json({})
    } else {
      logEmitter.emit('log', `Error reading module ${type}: ${error}`, module)
      return res.json(false)
    }
  }
})

apiRoutes.post('/module_data/update', async (req, res) => {
  const { module, type, module_type, ...jsonData } = req.body

  try {
    writeJson(moduleDataFilepath(module, type, module_type), jsonData)
    logEmitter.emit('log', `Module '${module}' ${type} were updated`, module)
    return res.json(true)
  } catch (error) {
    logEmitter.emit('log', `Error updating module instructions: ${error}`, module)
    return res.json(false)
  }
})

apiRoutes.post('/stop_module', (req, res) => {
  const { module } = req.body

  if (pythonProcesses[module]) {
    logEmitter.emit('log', `Stopping ${module} module...`, module)
    pythonProcesses[module].kill()
    delete pythonProcesses[module]
    res.json(true)
    logEmitter.emit('log', `Module ${module} was successfuly stopped`, module)
  } else {
    logEmitter.emit('log', 'No module running', module)
    res.json(false)
  }
})

apiRoutes.post('/start_module', (req, res) => {
  const { module } = req.body

  if (pythonProcesses[module]) {
    logEmitter.emit('log', `Module ${module} is running`, module)
    res.json(false)
  } else {
    try {
      logEmitter.emit('log', `Starting ${module} module...`, module)
      pythonProcesses[module] = spawn(`myenv/bin/python`, ['main.py', module], { cwd: 'scripts' })

      res.json(true)

      pythonProcesses[module].stdout.on('data', (data) => {
        parseLogs(data.toString()).forEach(log => {
          logEmitter.emit('log', ansiToHtml.toHtml(log), module)
        })
      })

      pythonProcesses[module].stderr.on('data', (data) => {
        parseLogs(data.toString()).forEach(log => {
          logEmitter.emit('log', ansiToHtml.toHtml(log), module)
        })
      })

      pythonProcesses[module].on('close', (code) => {
        logEmitter.emit('log', `Module ${module} finished with exit code ${code}`, module)
        delete pythonProcesses[module]
      })
    } catch (error) {
      logEmitter.emit('log', `Error starting ${module} module: ${error}`, module)
      res.json(false)
    }
  }
})

apiRoutes.get('/logs', (req, res) => {
  res.setHeader('Content-Type', 'text/event-stream')
  res.setHeader('Cache-Control', 'no-cache')
  res.setHeader('Connection', 'keep-alive')

  const requestedModule = req.query.module

  const onLog = (logMessage, module) => {
    if (requestedModule && requestedModule === module) {
      res.write(`data: ${logMessage}\n\n`)
    }
  }

  logEmitter.on('log', onLog)

  req.on('close', () => {
    logEmitter.removeListener('log', onLog)
    res.end()
  })
})

app.listen(port, () => {
  console.log(`Crypto Universe started: http://localhost:${port}`)
})