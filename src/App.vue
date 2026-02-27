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
const chartRef = ref(null)
let chartInstance = null

const defaultParams = {
  "inRadius": "15",
  "leftTensionPos": "-0.07",
  "rightTensionPos": "2.79",
  "normalStiffness": "100000",
  "vel": "-0.681462",
  "box_n": "1.0",
  "damping": "0.4",
  "alpha": "1e4",
  "gravity": "0,0,0",
  "iterPeriod": "10",
  "interactionDetectionFactor": "1",
  "aabbEnlargeFactor": "1",
  "young1": "1e9",
  "poisson1": ".4",
  "frictionAngle1_radians": "40",
  "density1": "2650",
  "young2": "1e9",
  "poisson2": "0.4",                                            
  "frictionAngle2": "0",
  "density2": "2600",
  "geom.facetBox1_1_1": ".5",
  "geom.facetBox1_1_2": ".5",
  "geom.facetBox1_1_3": "0.6124/2+0.05",
  "geom.facetBox1_2_1": ".5",
  "geom.facetBox1_2_2": ".5",
  "geom.facetBox1_2_3": "0.6124/2+0.05",
  "geom.facetBox2_1_1": ".5",
  "geom.facetBox2_1_2": ".5",
  "geom.facetBox2_1_3": "-0.6124/2-0.005",
  "geom.facetBox2_2_1": ".5",
  "geom.facetBox2_2_2": ".5",
  "geom.facetBox2_2_3": "0.6124/2",
  "mass": "1000000",
  "dt": ".5",
  "setPermF1": "0",
  "setPermF2": "0",
  "setPermF3": "-1",
  "O.iter1": "50000",
  "O.iter2": "% 100000",
  "dspl": "0.01"
}

const formData = reactive({ ...defaultParams })

// Mock API Functions
const mockGetLastParams = () => {
    return new Promise((resolve) => {
        setTimeout(() => {
            // Check localStorage
            const saved = localStorage.getItem('lastParams')
            if (saved) {
                resolve({ data: { ...defaultParams, ...JSON.parse(saved) } })
            } else {
                // Return default empty map or some defaults
                resolve({ data: { ...defaultParams } })
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
            // 使用 inRadius 参数作为乘数来影响生成的颗粒数量或大小
            const multiplier = Number(params.inRadius) || 15;
            const particleCount = 20 * multiplier;
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
            backgroundColor: 'rgba(255, 255, 255, 0.9)',
            borderColor: '#e4e7ed',
            textStyle: {
                color: '#303133'
            },
            formatter: function (params) {
                return `X: ${params.data[0].toFixed(2)}<br/>
                        Y: ${params.data[1].toFixed(2)}<br/>
                        半径: ${params.data[2].toFixed(2)}<br/>
                        受力: ${params.data[3].toFixed(2)}`;
            }
        },
        grid: {
            top: 40,
            bottom: 40,
            left: 60,
            right: 100,
            containLabel: true
        },
        xAxis: {
            type: 'value',
            name: 'X 坐标 (mm)',
            nameLocation: 'middle',
            nameGap: 30,
            nameTextStyle: {
                color: '#606266'
            },
            axisLabel: {
                color: '#606266'
            },
            splitLine: {
                lineStyle: {
                    type: 'dashed',
                    color: '#ebeef5'
                }
            }
        },
        yAxis: {
            type: 'value',
            name: 'Y 坐标 (mm)',
            nameLocation: 'middle',
            nameGap: 40,
            nameTextStyle: {
                color: '#606266'
            },
            axisLabel: {
                color: '#606266'
            },
            splitLine: {
                lineStyle: {
                    type: 'dashed',
                    color: '#ebeef5'
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
                color: '#606266'
            },
            calculable: true,
            inRange: {
                // 经典的工程软件热力图配色：蓝-青-绿-黄-红
                color: ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
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
                    shadowBlur: 5,
                    shadowColor: 'rgba(0, 0, 0, 0.1)',
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
    background: #ffffff;
    width: 100%;
    height: 100%;
}

.result-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 24px;
    border-bottom: 1px solid #ebeef5;
    background-color: #fff;
    z-index: 5;
    box-shadow: 0 2px 8px rgba(0,0,0,0.02);
}

.result-header h3 {
    margin: 0;
    color: #303133;
    font-size: 16px;
    font-weight: 600;
    display: flex;
    align-items: center;
}

.result-header h3::before {
    content: '';
    display: inline-block;
    width: 4px;
    height: 16px;
    background: #409eff;
    margin-right: 8px;
    border-radius: 2px;
}

:deep(.el-tag--success) {
    background-color: #f0f9eb;
    border-color: #e1f3d8;
    color: #67c23a;
}

.chart-container {
    flex: 1;
    width: 100%;
    height: 100%;
    background-color: #fafafa;
    position: relative;
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
