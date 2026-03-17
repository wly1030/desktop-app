const { app, BrowserWindow, ipcMain, dialog } = require('electron')
const path = require('path')
const fs = require('fs')
const { spawn } = require('child_process')

// 本地配置文件路径
const userDataPath = app.getPath('userData')
const configPath = path.join(userDataPath, 'form-config.json')

let mainWindow

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 900,
    height: 750,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  })

  // 隐藏顶部默认菜单
  mainWindow.setMenu(null)

  // 默认打开控制台（DevTools）
  mainWindow.webContents.openDevTools()

  // 开发环境加载 vite dev server，生产环境加载打包后的文件
  if (process.env.NODE_ENV === 'development' || !app.isPackaged) {
    const url = process.argv.find(arg => arg.startsWith('http'))
    mainWindow.loadURL(url || 'http://localhost:5173')
  } else {
    mainWindow.loadFile(path.join(__dirname, '..', 'dist', 'index.html'))
  }
}

app.whenReady().then(createWindow)

app.on('window-all-closed', () => {
  app.quit()
})

// ===== IPC 处理 =====

// 保存表单配置到本地
ipcMain.handle('save-config', async (_event, config) => {
  try {
    fs.writeFileSync(configPath, JSON.stringify(config, null, 2), 'utf-8')
    return { success: true }
  } catch (err) {
    return { success: false, error: err.message }
  }
})

// 读取本地表单配置
ipcMain.handle('load-config', async () => {
  try {
    if (fs.existsSync(configPath)) {
      const data = fs.readFileSync(configPath, 'utf-8')
      return { success: true, data: JSON.parse(data) }
    }
    return { success: true, data: null }
  } catch (err) {
    return { success: false, error: err.message }
  }
})

// 打开文件选择对话框（选择 Python 脚本）
ipcMain.handle('select-file', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    title: '选择 Python 脚本',
    filters: [
      { name: 'Python 文件', extensions: ['py'] },
      { name: '所有文件', extensions: ['*'] },
    ],
    properties: ['openFile'],
  })
  if (result.canceled) {
    return { success: false, canceled: true }
  }
  return { success: true, filePath: result.filePaths[0] }
})

// 获取内置脚本路径
ipcMain.handle('get-builtin-script-path', async () => {
  // 打包后在 resources/scripts 目录，开发时在项目的 scripts 目录
  let scriptsDir
  if (app.isPackaged) {
    scriptsDir = path.join(process.resourcesPath, 'scripts')
  } else {
    scriptsDir = path.join(__dirname, '..', 'scripts')
  }

  try {
    const files = fs.readdirSync(scriptsDir).filter(f => f.endsWith('.py'))
    return { success: true, scriptsDir, files }
  } catch (err) {
    return { success: false, error: err.message }
  }
})

// 运行 Python 脚本
ipcMain.handle('run-python', async (_event, { scriptPath, params }) => {
  return new Promise((resolve) => {
    // 将参数转为 JSON 字符串，通过命令行参数传递给 Python 脚本
    const paramsJson = JSON.stringify(params)
    const pythonCmd = process.platform === 'win32' ? 'python' : 'python3'

    const child = spawn(pythonCmd, [scriptPath, paramsJson], {
      detached: false,
    })

    // 不做 unref 并且处理标准输出，让其能在主进程控制台打印出来
    child.stdout.on('data', (data) => {
      console.log(`[Python Output]: ${data}`)
    })

    child.stderr.on('data', (data) => {
      console.error(`[Python Error]: ${data}`)
    })

    child.on('error', (err) => {
      resolve({ success: false, error: `无法启动 Python: ${err.message}` })
    })

    child.on('close', (code) => {
      console.log(`[Python] 进程退出，退出码: ${code}`)
    })

    // 确认进程启动成功
    setTimeout(() => {
      resolve({ success: true, pid: child.pid })
    }, 500)
  })
})
