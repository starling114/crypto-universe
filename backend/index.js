import { exec } from "child_process"

function startExpressServer() {
  const expressServer = exec('node ./backend/server.js', (error, stdout, _stderr) => {
    if (error) {
      console.error(`${error}`)
    }
    console.log(`${stdout}`)
  })

  expressServer.stdout.on('data', (data) => {
    console.log(`${data}`)
  })

  expressServer.stderr.on('data', (data) => {
    console.error(`${data}`)
  })
}

startExpressServer()
