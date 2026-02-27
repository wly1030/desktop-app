<template>
  <div class="common-layout">
    <el-container class="main-container">
      <el-header class="app-header">
        <div class="header-content">
          <el-icon class="header-icon"><DataAnalysis /></el-icon>
          <h1>数据分析图</h1>
        </div>
      </el-header>
      
      <el-main v-loading="loading" element-loading-text="正在加载数据..." element-loading-background="rgba(10, 15, 28, 0.8)">
        <div class="content-wrapper">
          <div v-if="hasData" class="result-area">
            <!-- <div class="result-header">
              <h3>数据分析图预览</h3>
              <el-tag type="success" effect="dark">Yade 仿生图</el-tag>
            </div> -->
            <div class="chart-container" ref="chartRef"></div>
          </div>
          <div v-else class="empty-state">
             <el-empty description="暂无生成结果，请编辑参数进行生成" :image-size="200">
               <template #image>
                 <el-icon :size="100" color="#c0c4cc"><DataAnalysis /></el-icon>
               </template>
             </el-empty>
          </div>

          <div class="actions">
            <el-button type="primary" size="large" @click="openEditDialog" class="action-btn" :icon="DataAnalysis">
              {{ hasData ? '重新编辑参数' : '编辑参数生成图表' }}
            </el-button>
          </div>
        </div>
      </el-main>
    </el-container>

    <!-- Dialog -->
    <el-dialog
      v-model="dialogVisible"
      title="配置参数"
      width="60%"
      :close-on-click-modal="false"
    >
      <el-form :model="formData" label-width="120px" class="param-form">
        <el-row :gutter="20">
            <!-- Generating 15 mock inputs -->
            <el-col :span="12" v-for="i in 15" :key="i">
                <el-form-item :label="`参数 Config ${i}`">
                    <el-input v-model="formData[`param${i}`]" placeholder="请输入值" />
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
const chartRef = ref(null)
let chartInstance = null

const formData = reactive({})

// Mock API Functions
const mockGetLastParams = () => {
    return new Promise((resolve) => {
        setTimeout(() => {
            // Check localStorage
            const saved = localStorage.getItem('lastParams')
            if (saved) {
                resolve({ data: JSON.parse(saved) })
            } else {
                // Return default empty map or some defaults
                const defaults = {}
                for(let i=1; i<=15; i++) defaults[`param${i}`] = ''
                resolve({ data: defaults })
            }
        }, 800)
    })
}

// 模拟接口调用，实际项目中应替换为真实的 axios 请求
const fetchChartData = async (params) => {
    return new Promise((resolve) => {
        setTimeout(() => {
            localStorage.setItem('lastParams', JSON.stringify(params))
            
            // 模拟 Yade 仿生图数据 (散点图/气泡图模拟颗粒分布)
            const multiplier = Number(params.param1) || 1;
            const particleCount = 200 * multiplier;
            const data = [];
            
            for (let i = 0; i < particleCount; i++) {
                // 随机生成颗粒的 x, y 坐标和半径大小
                const x = Math.random() * 100;
                const y = Math.random() * 100;
                const radius = Math.random() * 5 + 1; // 半径 1-6
                // 模拟不同材质或受力状态的颜色映射值
                const stress = Math.random() * 100; 
                data.push([x, y, radius, stress]);
            }

            resolve({ 
                data: {
                    particles: data
                } 
            })
        }, 1000)
    })
}

const renderChart = (data) => {
    if (!chartRef.value) return
    if (!chartInstance) {
        chartInstance = echarts.init(chartRef.value)
    }
    
    const option = {
        title: {
        },
        backgroundColor: 'transparent',
        tooltip: {
            trigger: 'item',
            backgroundColor: 'rgba(16, 24, 43, 0.9)',
            borderColor: '#14ffec',
            textStyle: {
                color: '#e0e6ed'
            },
            formatter: function (params) {
                return `X: ${params.data[0].toFixed(2)}<br/>
                        Y: ${params.data[1].toFixed(2)}<br/>
                        半径: ${params.data[2].toFixed(2)}<br/>
                        受力: ${params.data[3].toFixed(2)}`;
            }
        },
        xAxis: {
            type: 'value',
            name: 'X 坐标 (mm)',
            nameLocation: 'middle',
            nameGap: 30,
            nameTextStyle: {
                color: '#8b9bb4'
            },
            axisLabel: {
                color: '#8b9bb4'
            },
            splitLine: {
                lineStyle: {
                    type: 'dashed',
                    color: 'rgba(255, 255, 255, 0.1)'
                }
            }
        },
        yAxis: {
            type: 'value',
            name: 'Y 坐标 (mm)',
            nameLocation: 'middle',
            nameGap: 40,
            nameTextStyle: {
                color: '#8b9bb4'
            },
            axisLabel: {
                color: '#8b9bb4'
            },
            splitLine: {
                lineStyle: {
                    type: 'dashed',
                    color: 'rgba(255, 255, 255, 0.1)'
                }
            }
        },
        visualMap: {
            min: 0,
            max: 100,
            dimension: 3,
            orient: 'vertical',
            right: 10,
            top: 'center',
            text: ['高受力', '低受力'],
            textStyle: {
                color: '#8b9bb4'
            },
            calculable: true,
            inRange: {
                // 赛博朋克风格的渐变色：从深紫到亮青再到亮粉
                color: ['#2b00ff', '#00d4ff', '#14ffec', '#ff00e4', '#ff0055']
            }
        },
        series: [
            {
                name: '颗粒',
                type: 'scatter',
                symbolSize: function (data) {
                    return data[2] * 3; // 放大半径以便显示
                },
                data: data.particles,
                itemStyle: {
                    shadowBlur: 15,
                    shadowColor: 'rgba(255, 255, 255, 0.5)',
                    opacity: 0.85
                }
            }
        ]
    }
    
    chartInstance.setOption(option)
}

// Logic
const initData = async () => {
    loading.value = true
    try {
        // 1. Get last params
        const resParams = await mockGetLastParams()
        Object.assign(formData, resParams.data)
        
        // 2. Fetch chart data
        const resData = await fetchChartData(formData)
        hasData.value = true
        
        // 3. Render chart
        await nextTick()
        renderChart(resData.data)
        
    } catch (error) {
        console.error(error)
        ElMessage.error('初始化数据失败')
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
        renderChart(resData.data)
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
        if (chartInstance) {
            chartInstance.resize()
        }
    })
})

</script>

<style scoped>
.main-container {
    height: 100vh;
    background-color: #0a0f1c; /* 深邃的宇宙蓝黑背景 */
    background-image: 
        radial-gradient(circle at 15% 50%, rgba(20, 255, 236, 0.08), transparent 25%),
        radial-gradient(circle at 85% 30%, rgba(255, 0, 255, 0.08), transparent 25%);
    font-family: 'Orbitron', 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
    color: #e0e6ed;
}

.app-header {
    background: rgba(10, 15, 28, 0.8);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(20, 255, 236, 0.2);
    color: #14ffec; /* 赛博朋克青色 */
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 20px rgba(20, 255, 236, 0.1);
    height: 70px !important;
    z-index: 10;
}

.header-content {
    display: flex;
    align-items: center;
    gap: 15px;
}

.header-icon {
    font-size: 28px;
    filter: drop-shadow(0 0 8px rgba(20, 255, 236, 0.8));
}

.app-header h1 {
    margin: 0;
    font-size: 24px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    text-shadow: 0 0 10px rgba(20, 255, 236, 0.5);
}

.content-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    height: 100%;
    padding: 30px 20px;
    overflow-y: auto;
    box-sizing: border-box;
}

/* 自定义滚动条 */
.content-wrapper::-webkit-scrollbar {
    width: 8px;
}
.content-wrapper::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
}
.content-wrapper::-webkit-scrollbar-thumb {
    background: rgba(20, 255, 236, 0.3);
    border-radius: 4px;
}
.content-wrapper::-webkit-scrollbar-thumb:hover {
    background: rgba(20, 255, 236, 0.6);
}

.result-area {
    width: 95%;
    max-width: 1400px;
    background: rgba(16, 24, 43, 0.7);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(20, 255, 236, 0.15);
    border-radius: 16px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5), inset 0 0 20px rgba(20, 255, 236, 0.05);
    padding: 25px;
    margin-bottom: 30px;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.result-area:hover {
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.6), inset 0 0 30px rgba(20, 255, 236, 0.1);
    border-color: rgba(20, 255, 236, 0.3);
    transform: translateY(-2px);
}

.result-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 1px solid rgba(20, 255, 236, 0.1);
}

.result-header h3 {
    margin: 0;
    color: #e0e6ed;
    font-size: 20px;
    font-weight: 600;
    letter-spacing: 1px;
    display: flex;
    align-items: center;
}

.result-header h3::before {
    content: '';
    display: inline-block;
    width: 4px;
    height: 18px;
    background: #14ffec;
    margin-right: 10px;
    border-radius: 2px;
    box-shadow: 0 0 8px #14ffec;
}

:deep(.el-tag--success) {
    background-color: rgba(20, 255, 236, 0.1);
    border-color: rgba(20, 255, 236, 0.3);
    color: #14ffec;
    box-shadow: 0 0 10px rgba(20, 255, 236, 0.2);
}

.chart-container {
    width: 100%;
    height: calc(100vh - 350px);
    min-height: 500px;
    border-radius: 12px;
    overflow: hidden;
    background-color: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.05);
    position: relative;
}

/* 图表容器的科幻边角装饰 */
.chart-container::before, .chart-container::after {
    content: '';
    position: absolute;
    width: 20px;
    height: 20px;
    border: 2px solid #14ffec;
    pointer-events: none;
    z-index: 10;
}
.chart-container::before {
    top: 0;
    left: 0;
    border-right: none;
    border-bottom: none;
    border-top-left-radius: 12px;
}
.chart-container::after {
    bottom: 0;
    right: 0;
    border-left: none;
    border-top: none;
    border-bottom-right-radius: 12px;
}

.empty-state {
    margin: 60px 0;
    background: rgba(16, 24, 43, 0.6);
    backdrop-filter: blur(10px);
    border: 1px dashed rgba(255, 255, 255, 0.1);
    padding: 40px;
    border-radius: 16px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    width: 80%;
    max-width: 800px;
}

:deep(.el-empty__description p) {
    color: #8b9bb4;
    font-size: 16px;
    letter-spacing: 1px;
}

.actions {
    text-align: center;
    margin-top: 10px;
}

.action-btn {
    background: linear-gradient(45deg, #0f3443, #34e89e);
    border: none;
    color: #fff;
    padding: 12px 35px;
    font-size: 16px;
    font-weight: bold;
    letter-spacing: 1px;
    border-radius: 30px;
    box-shadow: 0 4px 15px rgba(52, 232, 158, 0.4);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.action-btn::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    transition: all 0.5s ease;
}

.action-btn:hover {
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 8px 25px rgba(52, 232, 158, 0.6);
}

.action-btn:hover::before {
    left: 100%;
}

.param-form {
    padding: 10px 20px;
}

/* 弹窗科幻风格定制 */
:deep(.el-dialog) {
    background: rgba(16, 24, 43, 0.95);
    backdrop-filter: blur(15px);
    border: 1px solid rgba(20, 255, 236, 0.3);
    border-radius: 16px;
    box-shadow: 0 15px 50px rgba(0, 0, 0, 0.8), 0 0 20px rgba(20, 255, 236, 0.1);
}

:deep(.el-dialog__header) {
    background-color: transparent;
    margin-right: 0;
    padding: 20px 25px;
    border-bottom: 1px solid rgba(20, 255, 236, 0.15);
}

:deep(.el-dialog__title) {
    font-weight: 600;
    color: #14ffec;
    letter-spacing: 1px;
    text-shadow: 0 0 8px rgba(20, 255, 236, 0.4);
}

:deep(.el-dialog__body) {
    color: #e0e6ed;
}

:deep(.el-form-item__label) {
    color: #8b9bb4;
}

:deep(.el-input__wrapper) {
    background-color: rgba(0, 0, 0, 0.3);
    box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.1) inset;
}

:deep(.el-input__wrapper:hover), :deep(.el-input__wrapper.is-focus) {
    box-shadow: 0 0 0 1px #14ffec inset !important;
}

:deep(.el-input__inner) {
    color: #e0e6ed;
}

:deep(.el-dialog__footer) {
    border-top: 1px solid rgba(20, 255, 236, 0.15);
    padding: 15px 25px;
    background-color: transparent;
}

:deep(.el-button--default) {
    background: transparent;
    border-color: rgba(255, 255, 255, 0.2);
    color: #e0e6ed;
}

:deep(.el-button--default:hover) {
    border-color: #14ffec;
    color: #14ffec;
    background: rgba(20, 255, 236, 0.05);
}

/* Loading 遮罩层科幻化 */
:deep(.el-loading-mask) {
    background-color: rgba(10, 15, 28, 0.8) !important;
    backdrop-filter: blur(5px);
}

:deep(.el-loading-spinner .path) {
    stroke: #14ffec;
}

:deep(.el-loading-spinner .el-loading-text) {
    color: #14ffec;
    letter-spacing: 2px;
}
</style>
