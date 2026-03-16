const { app, BrowserWindow, ipcMain } = require('electron')
const path = require('path')
const { spawn } = require('child_process')
const fs = require('fs')
const os = require('os')

process.env.DIST = path.join(__dirname, '../dist')
process.env.VITE_PUBLIC = app.isPackaged ? process.env.DIST : path.join(__dirname, '../public')

let win = null

function createWindow() {
  win = new BrowserWindow({
    icon: path.join(process.env.VITE_PUBLIC, 'electron-vite.svg'),
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
    },
    width: 1200,
    height: 800,
    autoHideMenuBar: true, // 隐藏菜单栏
  })

  // Test active push message to Renderer-process.
  win.webContents.on('did-finish-load', () => {
    win?.webContents.send('main-process-message', (new Date).toLocaleString())
  })

  if (process.env.VITE_DEV_SERVER_URL) {
    win.loadURL(process.env.VITE_DEV_SERVER_URL)
    win.webContents.openDevTools() // 本地运行自动打开调试工具
  } else {
    // win.loadFile('dist/index.html')
    win.loadFile(path.join(process.env.DIST, 'index.html'))
  }
}

app.on('window-all-closed', () => {
  win = null
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('second-instance', () => {
  if (win) {
    // Focus on the main window if the user tried to open another
    if (win.isMinimized()) win.restore()
    win.focus()
  }
})

app.on('activate', () => {
  const allWindows = BrowserWindow.getAllWindows()
  if (allWindows.length) {
    allWindows[0].focus()
  } else {
    createWindow()
  }
})

app.whenReady().then(createWindow)

// ── IPC: run Yade simulation ─────────────────────────────────────────────────
ipcMain.handle('run-simulation', async (event, params) => {
  // Write parameters to a temporary JSON file
  const tempFile = path.join(os.tmpdir(), `yade_params_${Date.now()}.json`)
  try {
    fs.writeFileSync(tempFile, JSON.stringify(params), 'utf8')
  } catch (err) {
    throw new Error('Failed to write params file: ' + err.message)
  }

  // Resolve the Python script path (dev vs packaged)
  const scriptPath = app.isPackaged
    ? path.join(process.resourcesPath, 'python', 'yade_simulation.py')
    : path.join(__dirname, '..', 'python', 'yade_simulation.py')

  return new Promise((resolve, reject) => {
    const cleanup = () => { try { fs.unlinkSync(tempFile) } catch (_) {} }

    const proc = spawn('yade', ['-x', scriptPath, tempFile], {
      env: { ...process.env, PYTHONUNBUFFERED: '1' },
    })

    let stdout = ''
    let stderr = ''

    proc.stdout.on('data', (chunk) => {
      const text = chunk.toString()
      stdout += text
      // Forward progress lines to the renderer
      text.split('\n').forEach((line) => {
        const trimmed = line.trim()
        if (trimmed) event.sender.send('simulation-log', trimmed)
      })
    })

    proc.stderr.on('data', (chunk) => {
      const text = chunk.toString()
      stderr += text
      // Forward Yade/Python log output to the renderer
      text.split('\n').forEach((line) => {
        const trimmed = line.trim()
        if (trimmed) event.sender.send('simulation-log', trimmed)
      })
    })

    proc.on('error', (err) => {
      cleanup()
      if (err.code === 'ENOENT') {
        reject(new Error('Yade 未找到，请确认 Yade 已安装并在系统 PATH 中。'))
      } else {
        reject(new Error('无法启动 Yade：' + err.message))
      }
    })

    proc.on('close', (code) => {
      cleanup()

      // Extract the RESULT_JSON line from stdout
      const match = stdout.match(/RESULT_JSON:(.+)/)
      if (match) {
        try {
          const data = JSON.parse(match[1])
          if (data.error) {
            reject(new Error('仿真脚本错误：' + data.error))
          } else {
            resolve({ success: true, data })
          }
        } catch (e) {
          reject(new Error('解析仿真结果失败：' + e.message))
        }
        return
      }

      if (code !== 0) {
        const errMsg = stderr.slice(-1000) || stdout.slice(-500)
        reject(new Error(`Yade 进程退出 (code ${code})：${errMsg}`))
      } else {
        reject(new Error('仿真未输出结果数据。stderr: ' + stderr.slice(-500)))
      }
    })
  })
})
