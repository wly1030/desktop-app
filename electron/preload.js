const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
  // 配置持久化
  saveConfig: (config) => ipcRenderer.invoke('save-config', config),
  loadConfig: () => ipcRenderer.invoke('load-config'),

  // 文件选择
  selectFile: () => ipcRenderer.invoke('select-file'),

  // 获取内置脚本列表
  getBuiltinScriptPath: () => ipcRenderer.invoke('get-builtin-script-path'),

  // 运行 Python 脚本
  runPython: (scriptPath, params) =>
    ipcRenderer.invoke('run-python', { scriptPath, params }),
})
