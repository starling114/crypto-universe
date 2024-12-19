export const loadModuleData = async (proxy, module, type, moduleType, callback, logs) => {
  try {
    await proxy.$axios.get('/api/module_data', {
      params: { module, type, module_type: moduleType }
    }).then((response) => {
      if (response.data) callback(response.data)
    })
  } catch (error) {
    if (logs) {
      logs.value.push('Error: ' + error.toString())
    } else {
      throw error
    }
  }
}

export const loadAdsProfiles = async (proxy, callback, logs) => {
  await proxy.$axios.get('/api/ads_profiles').then((response) => {
    if (response.data && response.data.profiles) callback(response.data.profiles)
  }).catch((error) => {
    if (logs) {
      logs.value.push(error.response.data.error)
    } else {
      throw error
    }
  })
}

export const updateModuleData = async (proxy, module, type, moduleType, data, logs) => {
  try {
    await proxy.$axios.post('/api/module_data/update', {
      module: module, type: type, module_type: moduleType, ...data
    })
  } catch (error) {
    if (logs) {
      logs.value.push('Error: ' + error.toString())
    } else {
      throw error
    }
  }
}

export const startModule = async (proxy, module, logs) => {
  try {
    await proxy.$axios.post('/api/start_module', { module: module })
  } catch (error) {
    if (logs) {
      logs.value.push('Error: ' + error.toString())
    } else {
      throw error
    }
  }
}

export const stopModule = async (proxy, module, logs) => {
  try {
    await proxy.$axios.post('/api/stop_module', { module: module })
  } catch (error) {
    if (logs) {
      logs.value.push('Error: ' + error.toString())
    } else {
      throw error
    }
  }
}

export const beforeUnloadModule = (moduleRunning) => (event) => {
  if (moduleRunning.value) {
    event.preventDefault()
    event.returnValue = ''
  }
}

export const beforeRouteLeaveModule = (moduleRunning, callback) => {
  return async (to, from, next) => {
    if (moduleRunning.value) {
      const answer = confirm('Module might be running. Do you really want to leave?')
      if (answer) {
        await callback()
        next()
      } else {
        next(false)
      }
    } else {
      next()
    }
  }
}