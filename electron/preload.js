// Preload script: expose safe IPC bridges to the renderer process.
// https://www.electronjs.org/docs/latest/tutorial/process-model#preload-scripts

const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
  /**
   * Run the Yade DEM simulation with the given parameters.
   * @param {Object} params – form parameter key/value pairs
   * @returns {Promise<{success: boolean, data: object}>}
   */
  runSimulation: (params) => ipcRenderer.invoke('run-simulation', params),

  /**
   * Listen for log/progress lines forwarded from the Yade process.
   * @param {(message: string) => void} callback
   */
  onSimulationLog: (callback) => {
    ipcRenderer.on('simulation-log', (_event, message) => callback(message))
  },
})

