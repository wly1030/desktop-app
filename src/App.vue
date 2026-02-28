<template>
  <div class="common-layout">
    <el-container class="main-container">
      <el-header class="app-header">
        <div class="header-content">
          <el-icon class="header-icon"><DataAnalysis /></el-icon>
          <h1>数据分析图</h1>
        </div>
        <div class="header-actions">
            <el-button type="primary" @click="openEditDialog" class="action-btn" :icon="DataAnalysis">
              {{ hasData ? '重新编辑参数' : '编辑参数生成图表' }}
            </el-button>
        </div>
      </el-header>
      
      <el-main v-loading="loading" element-loading-text="正在加载数据..." element-loading-background="rgba(255, 255, 255, 0.8)">
        <div class="content-wrapper">
          <div v-if="hasData" class="result-area">
            <div class="chart-section">
              <h3 class="chart-title">收敛监控 (Iteration vs Unbalanced Force / Top Position)</h3>
              <div class="chart-container" ref="chart1Ref"></div>
            </div>
            <div class="chart-section">
              <h3 class="chart-title">剪切应力-位移曲线 (Displacement vs Shear Stress)</h3>
              <div class="chart-container" ref="chart2Ref"></div>
            </div>
          </div>
          <div v-else class="empty-state">
             <el-empty description="暂无生成结果，请编辑参数进行生成" :image-size="200">
               <template #image>
                 <el-icon :size="100" color="#c0c4cc"><DataAnalysis /></el-icon>
               </template>
             </el-empty>
          </div>
        </div>
      </el-main>
    </el-container>

    <!-- Dialog -->
    <el-dialog
      v-model="dialogVisible"
      title="配置参数"
      width="70%"
      :close-on-click-modal="false"
    >
      <el-form :model="formData" label-width="180px" class="param-form">
        <el-row :gutter="20">
            <el-col :span="12" v-for="(value, key) in defaultParams" :key="key">
                <el-form-item :label="key">
                    <el-input v-model="formData[key]" placeholder="请输入值" />
                </el-form-item>
            </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm" :loading="submitLoading">
            生成图表
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { DataAnalysis } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import * as echarts from 'echarts'

// State
const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const hasData = ref(false)
const chart1Ref = ref(null)
const chart2Ref = ref(null)
let chart1Instance = null
let chart2Instance = null

const defaultParams = {
  "in_radius": "15",
  "left_tension_pos": "-0.07",
  "right_tension_pos": "2.79",
  "normal_stiffness": "100000",
  "vel": "-0.681462",
  "box_n": "1.0",
  "damping": "0.4",
  "alpha": "1e4",
  "gravity": "0,0,0",
  "iter_period": "10",
  "interaction_detection_factor": "1",
  "aabb_enlarge_factor": "1",
  "young1": "1e9",
  "poisson1": ".4",
  "friction_angle1_radians": "40",
  "density1": "2650",
  "young2": "1e9",
  "poisson2": "0.4",
  "friction_angle2": "0",
  "density2": "2600",
  "geom_facet_box1_1_1": ".5",
  "geom_facet_box1_1_2": ".5",
  "geom_facet_box1_1_3": "0.6124/2+0.05",
  "geom_facet_box1_2_1": ".5",
  "geom_facet_box1_2_2": ".5",
  "geom_facet_box1_2_3": "0.6124/2+0.05",
  "geom_facet_box2_1_1": ".5",
  "geom_facet_box2_1_2": ".5",
  "geom_facet_box2_1_3": "-0.6124/2-0.005",
  "geom_facet_box2_2_1": ".5",
  "geom_facet_box2_2_2": ".5",
  "geom_facet_box2_2_3": "0.6124/2",
  "mass": "1000000",
  "dt": ".5",
  "set_perm_f1": "0",
  "set_perm_f2": "0",
  "set_perm_f3": "-1",
  "o_iter1": "50000",
  "o_iter2": "% 100000",
  "dspl": "0.01"
}

const formData = reactive({ ...defaultParams })

const API_BASE = 'http://localhost:8000'

// 从 localStorage 恢复上次的参数
const loadLastParams = () => {
    const saved = localStorage.getItem('lastParams')
    if (saved) {
        return { ...defaultParams, ...JSON.parse(saved) }
    }
    return { ...defaultParams }
}

// 调用后端 API 运行脚本并获取数据
const fetchChartData = async (params) => {
    localStorage.setItem('lastParams', JSON.stringify(params))
    const res = await axios.post(`${API_BASE}/api/run`, {
        script_name: 'mock_simulation.py',
        params: params,
        timeout: 600
    })
    if (!res.data.success) {
        throw new Error(res.data.error || '脚本执行失败')
    }
    // 从 data 中提取 result.json 的内容
    const resultData = res.data.data?.['result.json']
    if (!resultData) {
        throw new Error('未获取到输出数据')
    }
    return { data: resultData }
}

const renderCharts = (data) => {
    // ====== 图1: 收敛监控 (双Y轴) ======
    if (chart1Ref.value) {
        if (!chart1Instance) {
            chart1Instance = echarts.init(chart1Ref.value)
        }
        chart1Instance.setOption({
            backgroundColor: 'transparent',
            tooltip: {
                trigger: 'axis',
                backgroundColor: 'rgba(255,255,255,0.95)',
                borderColor: '#e4e7ed',
                textStyle: { color: '#303133' }
            },
            legend: {
                data: ['Unbalanced Force', 'Top Position'],
                top: 4,
                textStyle: { color: '#606266' }
            },
            grid: { top: 36, bottom: 40, left: 20, right: 20, containLabel: true },
            xAxis: {
                type: 'category',
                name: 'Iteration',
                nameLocation: 'middle',
                nameGap: 24,
                nameTextStyle: { color: '#606266' },
                axisLabel: { color: '#606266' },
                data: data.i,
                splitLine: { show: false }
            },
            yAxis: [
                {
                    type: 'value',
                    name: 'Unbalanced',
                    nameTextStyle: { color: '#409eff' },
                    axisLabel: { color: '#409eff' },
                    splitLine: { lineStyle: { type: 'dashed', color: '#ebeef5' } }
                },
                {
                    type: 'value',
                    name: 'Top Y (m)',
                    nameTextStyle: { color: '#e6a23c' },
                    axisLabel: { color: '#e6a23c' },
                    splitLine: { show: false }
                }
            ],
            series: [
                {
                    name: 'Unbalanced Force',
                    type: 'line',
                    yAxisIndex: 0,
                    data: data.unbalanced,
                    showSymbol: false,
                    lineStyle: { width: 2, color: '#409eff' },
                    itemStyle: { color: '#409eff' }
                },
                {
                    name: 'Top Position',
                    type: 'line',
                    yAxisIndex: 1,
                    data: data.top_y,
                    showSymbol: false,
                    lineStyle: { width: 2, color: '#e6a23c' },
                    itemStyle: { color: '#e6a23c' }
                }
            ]
        })
    }

    // ====== 图2: 剪切应力-位移曲线 ======
    if (chart2Ref.value) {
        if (!chart2Instance) {
            chart2Instance = echarts.init(chart2Ref.value)
        }
        chart2Instance.setOption({
            backgroundColor: 'transparent',
            tooltip: {
                trigger: 'axis',
                backgroundColor: 'rgba(255,255,255,0.95)',
                borderColor: '#e4e7ed',
                textStyle: { color: '#303133' },
                formatter: function (params) {
                    const p = params[0]
                    return `Displacement: ${p.axisValue}<br/>Shear Stress: ${p.data} kPa`
                }
            },
            grid: { top: 16, bottom: 40, left: 20, right: 20, containLabel: true },
            xAxis: {
                type: 'category',
                name: 'Displacement (m)',
                nameLocation: 'middle',
                nameGap: 24,
                nameTextStyle: { color: '#606266' },
                axisLabel: { color: '#606266' },
                data: data.dspl,
                splitLine: { show: false }
            },
            yAxis: {
                type: 'value',
                name: 'Shear Stress (kPa)',
                nameTextStyle: { color: '#606266' },
                axisLabel: { color: '#606266' },
                splitLine: { lineStyle: { type: 'dashed', color: '#ebeef5' } }
            },
            series: [
                {
                    name: 'Shear Stress',
                    type: 'line',
                    data: data.shearStress,
                    showSymbol: false,
                    lineStyle: { width: 2.5, color: '#f56c6c' },
                    itemStyle: { color: '#f56c6c' },
                    areaStyle: {
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                            { offset: 0, color: 'rgba(245,108,108,0.25)' },
                            { offset: 1, color: 'rgba(245,108,108,0.02)' }
                        ])
                    }
                }
            ]
        })
    }
}

// Logic
const initData = async () => {
    loading.value = true
    try {
        // 1. 从 localStorage 恢复参数
        const lastParams = loadLastParams()
        Object.assign(formData, lastParams)

        // 2. 调用后端 API 获取数据
        const resData = await fetchChartData(formData)
        hasData.value = true

        // 3. Render chart
        await nextTick()
        renderCharts(resData.data)

    } catch (error) {
        console.error(error)
        // 首次加载失败不弹错误提示，只显示空状态
        hasData.value = false
    } finally {
        loading.value = false
    }
}

const openEditDialog = () => {
    dialogVisible.value = true
}

const submitForm = async () => {
    submitLoading.value = true
    try {
        const resData = await fetchChartData(formData)
        hasData.value = true
        dialogVisible.value = false
        ElMessage.success('生成成功')
        
        await nextTick()
        renderCharts(resData.data)
    } catch (error) {
        ElMessage.error('生成失败')
    } finally {
        submitLoading.value = false
    }
}

onMounted(() => {
    initData()
    
    // 监听窗口大小变化，自适应图表
    window.addEventListener('resize', () => {
        chart1Instance?.resize()
        chart2Instance?.resize()
    })
})

</script>

<style scoped>
.main-container {
    height: 100vh;
    background-color: #f4f7f9; /* 柔和的浅灰蓝背景 */
    font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
    color: #333;
    display: flex;
    flex-direction: column;
}

.app-header {
    background: #ffffff;
    border-bottom: 1px solid #e4e7ed;
    color: #2c3e50;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 24px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    height: 64px !important;
    z-index: 10;
    flex-shrink: 0;
}

.header-content {
    display: flex;
    align-items: center;
    gap: 12px;
}

.header-icon {
    font-size: 26px;
    color: #409eff;
}

.app-header h1 {
    margin: 0;
    font-size: 20px;
    font-weight: 600;
    letter-spacing: 1px;
}

.header-actions {
    display: flex;
    align-items: center;
}

.el-main {
    padding: 0;
    overflow: hidden; /* 隐藏默认滚动条，由内部控制 */
    display: flex;
    flex-direction: column;
}

.content-wrapper {
    display: flex;
    flex-direction: column;
    height: 100%;
    width: 100%;
    box-sizing: border-box;
    position: relative;
}

.result-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    background: #f4f7f9;
    width: 100%;
    height: 100%;
    overflow-y: auto;
    padding: 16px;
    gap: 16px;
    box-sizing: border-box;
}

.chart-section {
    flex: 1;
    min-height: 0;
    background: #ffffff;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.chart-title {
    margin: 0;
    padding: 12px 20px;
    font-size: 15px;
    font-weight: 600;
    color: #303133;
    border-bottom: 1px solid #ebeef5;
    display: flex;
    align-items: center;
    flex-shrink: 0;
}

.chart-title::before {
    content: '';
    display: inline-block;
    width: 4px;
    height: 16px;
    background: #409eff;
    margin-right: 10px;
    border-radius: 2px;
}

.chart-container {
    flex: 1;
    width: 100%;
    min-height: 280px;
}

.empty-state {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #ffffff;
}

.actions {
    position: absolute;
    bottom: 30px;
    right: 30px;
    z-index: 100;
}

.action-btn {
    padding: 12px 24px;
    font-size: 15px;
    border-radius: 8px;
    box-shadow: 0 4px 16px rgba(64, 158, 255, 0.3);
    transition: all 0.3s ease;
}

.action-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(64, 158, 255, 0.4);
}

.param-form {
    padding: 10px 20px;
}

/* 弹窗风格定制 */
:deep(.el-dialog) {
    border-radius: 8px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

:deep(.el-dialog__header) {
    margin-right: 0;
    padding: 20px 24px;
    border-bottom: 1px solid #ebeef5;
}

:deep(.el-dialog__title) {
    font-weight: 600;
    color: #303133;
}

:deep(.el-dialog__footer) {
    border-top: 1px solid #ebeef5;
    padding: 16px 24px;
}

/* Loading 遮罩层 */
:deep(.el-loading-mask) {
    background-color: rgba(255, 255, 255, 0.9) !important;
}
</style>
