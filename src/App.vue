<template>
  <div class="app">
    <header class="app-header">
      <h1>YADE 仿真参数配置</h1>
    </header>

    <main class="app-main">
      <!-- 脚本来源选择 -->
      <section class="section">
        <h2>Python 脚本</h2>
        <div class="script-source">
          <label class="radio-label">
            <input type="radio" v-model="scriptSource" value="builtin" />
            使用内置脚本
          </label>
          <label class="radio-label">
            <input type="radio" v-model="scriptSource" value="custom" />
            选择外部脚本
          </label>
        </div>

        <div v-if="scriptSource === 'builtin'" class="field">
          <label>选择内置脚本：</label>
          <select v-model="selectedBuiltinScript" class="input">
            <option value="" disabled>请选择...</option>
            <option v-for="f in builtinScripts" :key="f" :value="f">{{ f }}</option>
          </select>
          <p v-if="builtinScripts.length === 0" class="hint">
            未找到内置脚本，请将 .py 文件放入 scripts/ 目录
          </p>
        </div>

        <div v-if="scriptSource === 'custom'" class="field">
          <label>脚本路径：</label>
          <div class="file-picker">
            <input type="text" v-model="customScriptPath" class="input" readonly placeholder="点击右侧按钮选择文件..." />
            <button class="btn btn-secondary" @click="selectScript">浏览...</button>
          </div>
        </div>
      </section>

      <!-- 全局参数 -->
      <section class="section">
        <h2>全局参数</h2>
        <div class="field-grid">
          <div class="field">
            <label>in_radius <span class="hint-inline">球体半径</span></label>
            <input type="text" v-model="form.in_radius" class="input" />
          </div>
          <div class="field">
            <label>vel <span class="hint-inline">速度</span></label>
            <input type="text" v-model="form.vel" class="input" />
          </div>
          <div class="field">
            <label>gravity <span class="hint-inline">重力 (x,y,z)</span></label>
            <input type="text" v-model="form.gravity" class="input" />
          </div>
          <div class="field">
            <label>damping <span class="hint-inline">阻尼</span></label>
            <input type="text" v-model="form.damping" class="input" />
          </div>
          <div class="field">
            <label>alpha</label>
            <input type="text" v-model="form.alpha" class="input" />
          </div>
          <div class="field">
            <label>normal_stiffness <span class="hint-inline">法向刚度</span></label>
            <input type="text" v-model="form.normal_stiffness" class="input" />
          </div>
          <div class="field">
            <label>box_n</label>
            <input type="text" v-model="form.box_n" class="input" />
          </div>
          <div class="field">
            <label>mass <span class="hint-inline">质量</span></label>
            <input type="text" v-model="form.mass" class="input" />
          </div>
          <div class="field">
            <label>dt <span class="hint-inline">时间步长</span></label>
            <input type="text" v-model="form.dt" class="input" />
          </div>
          <div class="field">
            <label>dspl <span class="hint-inline">位移</span></label>
            <input type="text" v-model="form.dspl" class="input" />
          </div>
        </div>
      </section>

      <!-- 张拉位置 -->
      <section class="section">
        <h2>张拉位置</h2>
        <div class="field-grid">
          <div class="field">
            <label>left_tension_pos <span class="hint-inline">左侧</span></label>
            <input type="text" v-model="form.left_tension_pos" class="input" />
          </div>
          <div class="field">
            <label>right_tension_pos <span class="hint-inline">右侧</span></label>
            <input type="text" v-model="form.right_tension_pos" class="input" />
          </div>
        </div>
      </section>

      <!-- 检测因子 -->
      <section class="section">
        <h2>检测因子</h2>
        <div class="field-grid">
          <div class="field">
            <label>iter_period <span class="hint-inline">迭代周期</span></label>
            <input type="text" v-model="form.iter_period" class="input" />
          </div>
          <div class="field">
            <label>interaction_detection_factor</label>
            <input type="text" v-model="form.interaction_detection_factor" class="input" />
          </div>
          <div class="field">
            <label>aabb_enlarge_factor</label>
            <input type="text" v-model="form.aabb_enlarge_factor" class="input" />
          </div>
        </div>
      </section>

      <!-- 材料 1 -->
      <section class="section">
        <h2>材料 1</h2>
        <div class="field-grid">
          <div class="field">
            <label>young1 <span class="hint-inline">杨氏模量</span></label>
            <input type="text" v-model="form.young1" class="input" />
          </div>
          <div class="field">
            <label>poisson1 <span class="hint-inline">泊松比</span></label>
            <input type="text" v-model="form.poisson1" class="input" />
          </div>
          <div class="field">
            <label>friction_angle1_radians <span class="hint-inline">摩擦角</span></label>
            <input type="text" v-model="form.friction_angle1_radians" class="input" />
          </div>
          <div class="field">
            <label>density1 <span class="hint-inline">密度</span></label>
            <input type="text" v-model="form.density1" class="input" />
          </div>
        </div>
      </section>

      <!-- 材料 2 -->
      <section class="section">
        <h2>材料 2</h2>
        <div class="field-grid">
          <div class="field">
            <label>young2 <span class="hint-inline">杨氏模量</span></label>
            <input type="text" v-model="form.young2" class="input" />
          </div>
          <div class="field">
            <label>poisson2 <span class="hint-inline">泊松比</span></label>
            <input type="text" v-model="form.poisson2" class="input" />
          </div>
          <div class="field">
            <label>friction_angle2 <span class="hint-inline">摩擦角</span></label>
            <input type="text" v-model="form.friction_angle2" class="input" />
          </div>
          <div class="field">
            <label>density2 <span class="hint-inline">密度</span></label>
            <input type="text" v-model="form.density2" class="input" />
          </div>
        </div>
      </section>

      <!-- 几何 Facet Box 1 -->
      <section class="section">
        <h2>几何 Facet Box 1</h2>
        <div class="field-grid">
          <div class="field">
            <label>box1_1_1</label>
            <input type="text" v-model="form.geom_facet_box1_1_1" class="input" />
          </div>
          <div class="field">
            <label>box1_1_2</label>
            <input type="text" v-model="form.geom_facet_box1_1_2" class="input" />
          </div>
          <div class="field">
            <label>box1_1_3</label>
            <input type="text" v-model="form.geom_facet_box1_1_3" class="input" />
          </div>
          <div class="field">
            <label>box1_2_1</label>
            <input type="text" v-model="form.geom_facet_box1_2_1" class="input" />
          </div>
          <div class="field">
            <label>box1_2_2</label>
            <input type="text" v-model="form.geom_facet_box1_2_2" class="input" />
          </div>
          <div class="field">
            <label>box1_2_3</label>
            <input type="text" v-model="form.geom_facet_box1_2_3" class="input" />
          </div>
        </div>
      </section>

      <!-- 几何 Facet Box 2 -->
      <section class="section">
        <h2>几何 Facet Box 2</h2>
        <div class="field-grid">
          <div class="field">
            <label>box2_1_1</label>
            <input type="text" v-model="form.geom_facet_box2_1_1" class="input" />
          </div>
          <div class="field">
            <label>box2_1_2</label>
            <input type="text" v-model="form.geom_facet_box2_1_2" class="input" />
          </div>
          <div class="field">
            <label>box2_1_3</label>
            <input type="text" v-model="form.geom_facet_box2_1_3" class="input" />
          </div>
          <div class="field">
            <label>box2_2_1</label>
            <input type="text" v-model="form.geom_facet_box2_2_1" class="input" />
          </div>
          <div class="field">
            <label>box2_2_2</label>
            <input type="text" v-model="form.geom_facet_box2_2_2" class="input" />
          </div>
          <div class="field">
            <label>box2_2_3</label>
            <input type="text" v-model="form.geom_facet_box2_2_3" class="input" />
          </div>
        </div>
      </section>

      <!-- 永久力 & 迭代控制 -->
      <section class="section">
        <h2>永久力 & 迭代控制</h2>
        <div class="field-grid">
          <div class="field">
            <label>set_perm_f1</label>
            <input type="text" v-model="form.set_perm_f1" class="input" />
          </div>
          <div class="field">
            <label>set_perm_f2</label>
            <input type="text" v-model="form.set_perm_f2" class="input" />
          </div>
          <div class="field">
            <label>set_perm_f3</label>
            <input type="text" v-model="form.set_perm_f3" class="input" />
          </div>
          <div class="field">
            <label>o_iter1 <span class="hint-inline">迭代次数1</span></label>
            <input type="text" v-model="form.o_iter1" class="input" />
          </div>
          <div class="field">
            <label>o_iter2 <span class="hint-inline">迭代次数2</span></label>
            <input type="text" v-model="form.o_iter2" class="input" />
          </div>
        </div>
      </section>
    </main>

    <footer class="app-footer">
      <div class="footer-left">
        <button class="btn btn-secondary" @click="resetForm">恢复默认</button>
      </div>
      <button class="btn btn-primary" @click="runScript" :disabled="running">
        {{ running ? '运行中...' : '运行仿真' }}
      </button>
    </footer>

    <div v-if="message" :class="['toast', messageType]">
      {{ message }}
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'

const scriptSource = ref('builtin')
const selectedBuiltinScript = ref('')
const customScriptPath = ref('')
const builtinScripts = ref([])
const builtinScriptsDir = ref('')
const running = ref(false)
const message = ref('')
const messageType = ref('success')

const defaultParams = {
  in_radius: "15",
  left_tension_pos: "-0.07",
  right_tension_pos: "2.79",
  normal_stiffness: "100000",
  vel: "-0.681462",
  box_n: "1.0",
  damping: "0.4",
  alpha: "1e4",
  gravity: "0,0,0",
  iter_period: "10",
  interaction_detection_factor: "1",
  aabb_enlarge_factor: "1",
  young1: "1e9",
  poisson1: ".4",
  friction_angle1_radians: "40",
  density1: "2650",
  young2: "1e9",
  poisson2: "0.4",
  friction_angle2: "0",
  density2: "2600",
  geom_facet_box1_1_1: ".5",
  geom_facet_box1_1_2: ".5",
  geom_facet_box1_1_3: "0.6124/2+0.05",
  geom_facet_box1_2_1: ".5",
  geom_facet_box1_2_2: ".5",
  geom_facet_box1_2_3: "0.6124/2+0.05",
  geom_facet_box2_1_1: ".5",
  geom_facet_box2_1_2: ".5",
  geom_facet_box2_1_3: "-0.6124/2-0.005",
  geom_facet_box2_2_1: ".5",
  geom_facet_box2_2_2: ".5",
  geom_facet_box2_2_3: "0.6124/2",
  mass: "1000000",
  dt: ".5",
  set_perm_f1: "0",
  set_perm_f2: "0",
  set_perm_f3: "-1",
  o_iter1: "50000",
  o_iter2: "% 100000",
  dspl: "0.01",
}

const form = reactive({ ...defaultParams })

function resetForm() {
  Object.assign(form, defaultParams)
  showMessage('已恢复默认参数')
}

let messageTimer = null

function showMessage(text, type = 'success') {
  message.value = text
  messageType.value = type
  clearTimeout(messageTimer)
  messageTimer = setTimeout(() => {
    message.value = ''
  }, 3000)
}

async function loadBuiltinScripts() {
  const result = await window.electronAPI.getBuiltinScriptPath()
  if (result.success) {
    builtinScripts.value = result.files
    builtinScriptsDir.value = result.scriptsDir
    if (result.files.length > 0) {
      selectedBuiltinScript.value = result.files[0]
    }
  }
}

async function selectScript() {
  const result = await window.electronAPI.selectFile()
  if (result.success) {
    customScriptPath.value = result.filePath
  }
}

async function saveConfig() {
  const config = {
    scriptSource: scriptSource.value,
    selectedBuiltinScript: selectedBuiltinScript.value,
    customScriptPath: customScriptPath.value,
    form: { ...form },
  }
  const result = await window.electronAPI.saveConfig(config)
  if (result.success) {
    showMessage('配置已保存')
  } else {
    showMessage('保存失败: ' + result.error, 'error')
  }
}

async function loadConfig() {
  const result = await window.electronAPI.loadConfig()
  if (result.success && result.data) {
    const data = result.data
    scriptSource.value = data.scriptSource || 'builtin'
    selectedBuiltinScript.value = data.selectedBuiltinScript || ''
    customScriptPath.value = data.customScriptPath || ''
    if (data.form) {
      Object.assign(form, data.form)
    }
    showMessage('配置已加载')
  } else if (result.success) {
    showMessage('暂无保存的配置', 'warning')
  } else {
    showMessage('加载失败: ' + result.error, 'error')
  }
}

async function runScript() {
  let scriptPath = ''
  if (scriptSource.value === 'builtin') {
    if (!selectedBuiltinScript.value) {
      showMessage('请选择一个内置脚本', 'error')
      return
    }
    scriptPath = builtinScriptsDir.value + '/' + selectedBuiltinScript.value
  } else {
    if (!customScriptPath.value) {
      showMessage('请选择一个 Python 脚本文件', 'error')
      return
    }
    scriptPath = customScriptPath.value
  }

  running.value = true
  await saveConfig()

  const result = await window.electronAPI.runPython(scriptPath, { ...form })
  running.value = false

  if (result.success) {
    showMessage(`脚本已启动 (PID: ${result.pid})，后台运行中`)
  } else {
    showMessage('启动失败: ' + result.error, 'error')
  }
}

onMounted(() => {
  loadBuiltinScripts()
  loadConfig()
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Ubuntu', 'Noto Sans SC', sans-serif;
  background: #f5f5f5;
  color: #333;
}

.app {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.app-header {
  background: linear-gradient(135deg, #1a3a5c, #1e5080);
  color: white;
  padding: 16px 24px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.15);
}

.app-header h1 {
  font-size: 20px;
  font-weight: 500;
}

.app-main {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}

.section h2 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  color: #1a3a5c;
  border-bottom: 2px solid #e8edf2;
  padding-bottom: 8px;
}

.script-source {
  display: flex;
  gap: 24px;
  margin-bottom: 12px;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  font-size: 14px;
}

.field-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px 20px;
}

.field {
  margin-bottom: 2px;
}

.field > label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #444;
  margin-bottom: 4px;
  font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
}

.hint-inline {
  font-family: 'Ubuntu', 'Noto Sans SC', sans-serif;
  font-weight: 400;
  color: #999;
  font-size: 12px;
}

.input {
  width: 100%;
  padding: 7px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
  transition: border-color 0.2s;
  background: white;
}

.input:focus {
  outline: none;
  border-color: #2b6cb0;
  box-shadow: 0 0 0 2px rgba(43, 108, 176, 0.15);
}

.file-picker {
  display: flex;
  gap: 8px;
}

.file-picker .input {
  flex: 1;
  font-family: 'Ubuntu', 'Noto Sans SC', sans-serif;
}

.hint {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.app-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: white;
  border-top: 1px solid #eee;
}

.footer-left {
  display: flex;
  gap: 8px;
}

.btn {
  padding: 8px 20px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn:hover {
  opacity: 0.85;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(135deg, #2b6cb0, #2c5282);
  color: white;
  font-weight: 600;
  padding: 10px 32px;
  font-size: 15px;
}

.btn-secondary {
  background: #e8edf2;
  color: #2c5282;
  border: 1px solid #cbd5e0;
}

.toast {
  position: fixed;
  bottom: 80px;
  left: 50%;
  transform: translateX(-50%);
  padding: 10px 24px;
  border-radius: 4px;
  font-size: 14px;
  color: white;
  z-index: 1000;
  animation: fadeIn 0.2s;
}

.toast.success {
  background: #38b44a;
}

.toast.error {
  background: #e74c3c;
}

.toast.warning {
  background: #f39c12;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateX(-50%) translateY(10px); }
  to { opacity: 1; transform: translateX(-50%) translateY(0); }
}
</style>
