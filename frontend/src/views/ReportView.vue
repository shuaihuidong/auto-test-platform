<template>
  <div class="report-view">
    <div class="page-header">
      <a-space>
        <a-button @click="goBack">
          <ArrowLeftOutlined /> 返回
        </a-button>
        <h2>{{ pageTitle }}</h2>
      </a-space>
      <a-space>
        <a-button @click="refreshReport">
          <ReloadOutlined /> 刷新
        </a-button>
        <a-button type="primary" @click="downloadReport">
          <DownloadOutlined /> 下载HTML
        </a-button>
      </a-space>
    </div>

    <a-spin :spinning="loading">
      <!-- 计划执行报告 -->
      <div v-if="report && isPlanReport" class="report-content">
        <!-- 概览卡片 -->
        <a-row :gutter="16" class="summary-cards">
          <a-col :span="5">
            <a-card>
              <a-statistic title="脚本总数" :value="report.summary.total_scripts || 0" />
            </a-card>
          </a-col>
          <a-col :span="5">
            <a-card>
              <a-statistic title="已完成" :value="report.summary.script_status?.completed || 0" :value-style="{ color: '#52c41a' }" />
            </a-card>
          </a-col>
          <a-col :span="5">
            <a-card>
              <a-statistic title="失败" :value="report.summary.script_status?.failed || 0" :value-style="{ color: '#f5222d' }" />
            </a-card>
          </a-col>
          <a-col :span="5">
            <a-card>
              <a-statistic title="待执行" :value="(report.summary.script_status?.pending || 0) + (report.summary.script_status?.running || 0)" :value-style="{ color: '#1890ff' }" />
            </a-card>
          </a-col>
          <a-col :span="4">
            <a-card>
              <a-statistic
                title="总耗时"
                :value="report.summary.total_duration"
                suffix="秒"
              />
            </a-card>
          </a-col>
        </a-row>

        <!-- 状态分布图表 -->
        <a-row :gutter="16" class="charts-section">
          <a-col :span="12">
            <a-card title="脚本状态分布" :body-style="{ height: '350px' }">
              <div ref="statusChartRef" class="chart"></div>
            </a-card>
          </a-col>
          <a-col :span="12">
            <a-card title="问题分析与建议" :body-style="{ height: '350px', padding: '20px' }">
              <!-- 失败原因分析 -->
              <div class="failure-analysis">
                <div class="analysis-title">
                  <ExperimentOutlined style="margin-right: 6px; color: #1890ff;" />
                  失败原因分析
                </div>
                <div v-if="getFailureReasons().length > 0" class="failure-reasons">
                  <div v-for="(reason, index) in getFailureReasons()" :key="index" class="failure-reason-item">
                    <span class="reason-name">{{ reason.name }}</span>
                    <span class="reason-count">{{ reason.count }} 次</span>
                  </div>
                </div>
                <div v-else class="no-failure">
                  <div class="no-failure-content">
                    <CheckCircleOutlined style="font-size: 48px; color: #52c41a; margin-bottom: 8px;" />
                    <div class="no-failure-text">暂无失败</div>
                    <div class="no-failure-sub">所有脚本均通过</div>
                  </div>
                </div>
              </div>

              <!-- 改进建议 -->
              <div v-if="getSuggestions().length > 0" class="suggestions">
                <div class="suggestions-title">
                  <BulbOutlined style="color: #faad14; margin-right: 6px;" />
                  改进建议
                </div>
                <div v-for="(suggestion, index) in getSuggestions()" :key="index" class="suggestion-item">
                  {{ suggestion }}
                </div>
              </div>
            </a-card>
          </a-col>
        </a-row>

        <!-- 脚本执行详情 -->
        <a-card title="脚本执行详情" class="steps-section">
          <a-table
            :columns="scriptColumns"
            :data-source="scripts"
            :pagination="{ pageSize: 20 }"
            row-key="id"
            size="small"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'status'">
                <a-tag :color="getStatusTagColor(record.status)">
                  {{ getStatusText(record.status) }}
                </a-tag>
              </template>
              <template v-else-if="column.key === 'error_reason'">
                <span v-if="record.error_reason" class="error-text">{{ record.error_reason }}</span>
                <span v-else>-</span>
              </template>
            </template>
          </a-table>
        </a-card>
      </div>

      <!-- 脚本执行报告 -->
      <div v-else-if="report" class="report-content">
        <!-- 概览卡片 -->
        <a-row :gutter="16" class="summary-cards">
          <a-col :span="4">
            <a-card>
              <a-statistic title="步骤总数" :value="report.summary.total || 0" />
            </a-card>
          </a-col>
          <a-col :span="4">
            <a-card>
              <a-statistic title="通过步骤" :value="report.summary.passed || 0" :value-style="{ color: '#52c41a' }" />
            </a-card>
          </a-col>
          <a-col :span="4">
            <a-card>
              <a-statistic title="失败步骤" :value="report.summary.failed || 0" :value-style="{ color: '#f5222d' }" />
            </a-card>
          </a-col>
          <a-col :span="4">
            <a-card>
              <a-statistic
                title="通过率"
                :value="report.summary.pass_rate || 0"
                suffix="%"
                :value-style="{ color: (report.summary.pass_rate || 0) >= 80 ? '#52c41a' : '#f5222d' }"
              />
            </a-card>
          </a-col>
          <a-col :span="4">
            <a-card>
              <a-statistic
                title="总耗时"
                :value="report.summary.total_duration || 0"
                suffix="秒"
              />
            </a-card>
          </a-col>
          <a-col :span="4">
            <a-card>
              <a-statistic
                title="执行状态"
                :value-style="{ color: getStatusColor(report.execution_status) }"
              >
                <template #formatter>
                  {{ getStatusText(report.execution_status) }}
                </template>
              </a-statistic>
            </a-card>
          </a-col>
        </a-row>

        <!-- 图表区域 -->
        <a-row :gutter="16" class="charts-section">
          <a-col :span="12">
            <a-card title="执行趋势" :body-style="{ height: '350px' }">
              <div ref="trendChartRef" class="chart"></div>
            </a-card>
          </a-col>
          <a-col :span="12">
            <a-card title="问题分析与建议" :body-style="{ height: '350px', padding: '20px' }">
              <!-- 失败原因分析 -->
              <div class="failure-analysis">
                <div class="analysis-title">
                  <ExperimentOutlined style="margin-right: 6px; color: #1890ff;" />
                  失败步骤分析
                </div>
                <div v-if="getStepFailureReasons().length > 0" class="failure-reasons">
                  <div v-for="(reason, index) in getStepFailureReasons()" :key="index" class="failure-reason-item">
                    <span class="reason-name">{{ reason.name }}</span>
                    <span class="reason-count">{{ reason.count }} 次</span>
                  </div>
                </div>
                <div v-else class="no-failure">
                  <div class="no-failure-content">
                    <CheckCircleOutlined style="font-size: 48px; color: #52c41a; margin-bottom: 8px;" />
                    <div class="no-failure-text">暂无失败</div>
                    <div class="no-failure-sub">所有步骤均通过</div>
                  </div>
                </div>
              </div>

              <!-- 改进建议 -->
              <div v-if="getStepSuggestions().length > 0" class="suggestions">
                <div class="suggestions-title">
                  <BulbOutlined style="color: #faad14; margin-right: 6px;" />
                  改进建议
                </div>
                <div v-for="(suggestion, index) in getStepSuggestions()" :key="index" class="suggestion-item">
                  {{ suggestion }}
                </div>
              </div>
            </a-card>
          </a-col>
        </a-row>

        <!-- 步骤详情 -->
        <a-card title="步骤详情" class="steps-section">
          <template v-if="getRemainingStepsCount() > 0" #extra>
            <a-tag color="warning" style="margin-right: 8px;">
              <WarningOutlined style="margin-right: 4px;" />
              脚本中途失败，还有 {{ getRemainingStepsCount() }} 个步骤未执行
            </a-tag>
          </template>
          <a-table
            :columns="stepColumns"
            :data-source="steps"
            :pagination="{ pageSize: 20 }"
            row-key="index"
            size="small"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'success'">
                <a-tag :color="record.success ? 'success' : 'error'">
                  {{ record.success ? '通过' : '失败' }}
                </a-tag>
              </template>
              <template v-else-if="column.key === 'duration'">
                {{ record.duration }}ms
              </template>
              <template v-else-if="column.key === 'error'">
                <span v-if="record.error" class="error-text">{{ record.error }}</span>
                <span v-else>-</span>
              </template>
            </template>
          </a-table>
        </a-card>
      </div>

      <a-empty v-else description="暂无报告数据" />
    </a-spin>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { message, Result as AResult } from 'ant-design-vue'
import * as echarts from 'echarts'
import type { EChartsOption } from 'echarts'
import {
  ArrowLeftOutlined,
  ReloadOutlined,
  DownloadOutlined,
  CheckCircleOutlined,
  BulbOutlined,
  ExperimentOutlined,
  WarningOutlined
} from '@ant-design/icons-vue'
import { getReport, downloadHtmlReport, generateReport } from '@/api/report'
import type { Report } from '@/api/report'

const router = useRouter()
const route = useRoute()
const executionId = parseInt(route.params.executionId as string)

const loading = ref(false)
const report = ref<Report | null>(null)

const trendChartRef = ref<HTMLElement>()
const statusChartRef = ref<HTMLElement>()

let trendChart: echarts.ECharts | null = null
let statusChart: echarts.ECharts | null = null

// 是否为计划报告
const isPlanReport = computed(() => {
  if (!report.value) return false
  // 优先从 execution_type 字段获取，如果没有则从 summary.execution_type 获取
  const type = report.value.execution_type || report.value.summary?.execution_type
  return type === 'plan'
})

// 页面标题
const pageTitle = computed(() => isPlanReport.value ? '测试计划报告' : '测试报告')

// 脚本执行报告的步骤列
const stepColumns = [
  { title: '序号', key: 'index', dataIndex: 'index', width: 80 },
  { title: '步骤名称', key: 'name', dataIndex: 'name', width: 200 },
  { title: '类型', key: 'type', dataIndex: 'type', width: 120 },
  { title: '状态', key: 'success', width: 100 },
  { title: '耗时', key: 'duration', width: 100 },
  { title: '信息', key: 'message', dataIndex: 'message' },
  { title: '错误', key: 'error', width: 300 }
]

// 计划报告的脚本列
const scriptColumns = [
  { title: 'ID', key: 'id', dataIndex: 'id', width: 80 },
  { title: '脚本名称', key: 'name', dataIndex: 'name', width: 300 },
  { title: '状态', key: 'status', width: 100 },
  { title: '耗时(秒)', key: 'duration', dataIndex: 'duration', width: 100 },
  { title: '失败原因', key: 'error_reason', width: 300 }
]

const steps = ref<any[]>([])
const scripts = ref<any[]>([])

async function loadReport() {
  loading.value = true
  try {
    let reports = await getReport(executionId)

    // 如果报告不存在，自动生成
    if (!reports.results || reports.results.length === 0) {
      await generateReport(executionId)
      reports = await getReport(executionId)
    }

    if (reports.results?.length > 0) {
      report.value = reports.results[0]

      // 调试日志
      console.log('报告数据:', report.value)
      console.log('execution_type:', report.value.execution_type)
      console.log('summary.execution_type:', report.value.summary?.execution_type)
      console.log('charts_data:', report.value.charts_data)

      // 如果是计划报告，处理脚本数据
      if (isPlanReport.value && report.value.charts_data?.scripts) {
        scripts.value = report.value.charts_data.scripts.map((script: any) => ({
          ...script,
          error_reason: script.error_reason || (script.status === 'failed' ? '执行失败' : '')
        }))
        console.log('脚本数据:', scripts.value)
      } else {
        // 脚本报告，处理步骤数据
        if (report.value.charts_data?.trend) {
          steps.value = report.value.charts_data.trend.map((item: any, index: number) => ({
            index: index + 1,
            name: item.name || `步骤${index + 1}`,
            type: item.type || 'unknown',
            success: item.success,
            duration: item.duration || 0,
            message: item.message || (item.success ? '执行成功' : '执行失败'),
            error: item.success ? '' : (item.error || item.message || '执行失败')
          }))
        }
        console.log('步骤数据:', steps.value)
      }

      await nextTick()
      renderCharts()
    }
  } catch (error) {
    // 错误已由拦截器处理
  } finally {
    loading.value = false
  }
}

async function refreshReport() {
  await generateReport(executionId)
  await loadReport()
  message.success('报告已刷新')
}

async function downloadReport() {
  if (!report.value) return
  try {
    const blob = await downloadHtmlReport(report.value.id)
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `report_${executionId}.html`
    a.click()
    window.URL.revokeObjectURL(url)
    message.success('下载成功')
  } catch (error) {
    message.error('下载失败')
  }
}

function goBack() {
  // 根据报告类型返回到对应的 tab
  if (isPlanReport.value) {
    router.push({ path: '/executions', query: { tab: 'plan' } })
  } else {
    router.push({ path: '/executions', query: { tab: 'script' } })
  }
}

function renderCharts() {
  if (!report.value) return

  // 如果是计划报告，渲染状态分布图
  if (isPlanReport.value) {
    if (statusChartRef.value) {
      statusChart = echarts.init(statusChartRef.value)

      // 定义状态颜色映射
      const statusColors: Record<string, string> = {
        '已完成': '#52c41a',  // 绿色
        '失败': '#f5222d',    // 红色
        '等待中': '#faad14',  // 黄色
        '执行中': '#faad14',  // 黄色
        '已停止': '#d9d9d9'   // 灰色
      }

      // 只显示有数据的状态
      const filteredData = report.value.charts_data.status_distribution
        .filter((item: any) => item.count > 0)
        .map((item: any) => ({
          name: item.status === 'running' ? '执行中' :
                 item.status === 'pending' ? '待执行' :
                 item.status === 'stopped' ? '已停止' :
                 getStatusText(item.status),
          value: item.count,
          itemStyle: {
            color: statusColors[
              item.status === 'running' ? '执行中' :
              item.status === 'pending' ? '待执行' :
              item.status === 'stopped' ? '已停止' :
              getStatusText(item.status)
            ] || '#d9d9d9'
          }
        }))

      const statusOption: EChartsOption = {
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          right: 10,
          top: 'center'
        },
        series: [{
          name: '脚本状态',
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['40%', '50%'],
          data: filteredData,
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          },
          label: {
            formatter: '{b}: {c}'
          }
        }]
      }
      statusChart.setOption(statusOption)
    }
    return
  }

  // 脚本报告：渲染趋势图
  if (trendChartRef.value) {
    trendChart = echarts.init(trendChartRef.value)
    const trendOption: EChartsOption = {
      tooltip: {
        trigger: 'axis',
        formatter: (params: any) => {
          const param = params[0]
          const item = report.value.charts_data.trend[param.dataIndex]
          return `${param.name}<br/>耗时: ${item.duration}ms<br/>状态: ${item.success ? '成功' : '失败'}`
        }
      },
      xAxis: {
        type: 'category',
        data: report.value.charts_data.trend.map((item: any) => `步骤${item.index}`),
        axisLabel: { rotate: 45 }
      },
      yAxis: { type: 'value', name: '耗时(ms)' },
      series: [{
        type: 'line',
        smooth: true,
        data: report.value.charts_data.trend.map((item: any) => ({
          value: item.duration,
          itemStyle: { color: item.success ? '#52c41a' : '#f5222d' }
        })),
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(82, 196, 26, 0.3)' },
              { offset: 1, color: 'rgba(82, 196, 26, 0.05)' }
            ]
          }
        }
      }]
    }
    trendChart.setOption(trendOption)
  }
}

function getStatusColor(status: string) {
  const colors: Record<string, string> = {
    completed: '#52c41a',
    failed: '#f5222d',
    running: '#1890ff',
    pending: '#999',
    stopped: '#faad14'
  }
  return colors[status] || '#999'
}

function getStatusTagColor(status: string) {
  const colors: Record<string, string> = {
    completed: 'success',
    failed: 'error',
    running: 'processing',
    pending: 'default',
    stopped: 'warning'
  }
  return colors[status] || 'default'
}

function getStatusText(status: string) {
  const texts: Record<string, string> = {
    completed: '已完成',
    failed: '失败',
    running: '执行中',
    pending: '等待中',
    stopped: '已停止'
  }
  return texts[status] || status
}

// 获取失败原因分析
function getFailureReasons() {
  if (!report.value || !report.value.charts_data?.scripts) return []

  // 统计失败原因（从脚本维度）
  const reasonMap = new Map<string, number>()
  const failedScripts = report.value.charts_data.scripts.filter((s: any) => s.status === 'failed' && s.error_reason)

  failedScripts.forEach((script: any) => {
    const reason = classifyFailureReason(script.error_reason)
    reasonMap.set(reason, (reasonMap.get(reason) || 0) + 1)
  })

  // 如果没有失败原因但有失败的脚本，返回通用原因
  if (reasonMap.size === 0) {
    const failedCount = report.value.charts_data.scripts.filter((s: any) => s.status === 'failed').length
    if (failedCount > 0) {
      return [{ name: '脚本执行失败', count: failedCount }]
    }
  }

  // 转换为数组并排序
  return Array.from(reasonMap.entries())
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 3) // 只显示前3个
}

// 分类失败原因（脚本级别）
function classifyFailureReason(errorMsg: string): string {
  if (!errorMsg) return '未知错误'

  const lowerMsg = errorMsg.toLowerCase()

  // 超时相关
  if (lowerMsg.includes('timeout') || lowerMsg.includes('超时') || lowerMsg.includes('timed out')) {
    return '执行超时'
  }

  // 元素定位相关
  if (lowerMsg.includes('element') || lowerMsg.includes('元素') ||
      lowerMsg.includes('locator') || lowerMsg.includes('定位') ||
      lowerMsg.includes('not found') || lowerMsg.includes('找不到') ||
      lowerMsg.includes('no such')) {
    return '元素定位失败'
  }

  // 网络相关
  if (lowerMsg.includes('network') || lowerMsg.includes('网络') ||
      lowerMsg.includes('connection') || lowerMsg.includes('连接') ||
      lowerMsg.includes('unreachable') || lowerMsg.includes('无法访问')) {
    return '网络连接问题'
  }

  // 断言相关
  if (lowerMsg.includes('assert') || lowerMsg.includes('断言') ||
      lowerMsg.includes('expected') || lowerMsg.includes('期望') ||
      lowerMsg.includes('match') || lowerMsg.includes('匹配')) {
    return '断言验证失败'
  }

  // 浏览器相关
  if (lowerMsg.includes('browser') || lowerMsg.includes('浏览器') ||
      lowerMsg.includes('driver') || lowerMsg.includes('驱动') ||
      lowerMsg.includes('chrome') || lowerMsg.includes('firefox')) {
    return '浏览器相关问题'
  }

  // JavaScript错误
  if (lowerMsg.includes('javascript') || lowerMsg.includes('js error') ||
      lowerMsg.includes('script error') || lowerMsg.includes('语法')) {
    return 'JavaScript错误'
  }

  // 权限相关
  if (lowerMsg.includes('permission') || lowerMsg.includes('权限') ||
      lowerMsg.includes('access') || lowerMsg.includes('访问') ||
      lowerMsg.includes('unauthorized') || lowerMsg.includes('未授权')) {
    return '权限问题'
  }

  // 数据相关
  if (lowerMsg.includes('data') || lowerMsg.includes('数据') ||
      lowerMsg.includes('null') || lowerMsg.includes('undefined') ||
      lowerMsg.includes('空值')) {
    return '数据异常'
  }

  return '其他错误'
}

// 获取改进建议
function getSuggestions() {
  const failureReasons = getFailureReasons()
  const suggestions: string[] = []

  failureReasons.forEach(reason => {
    switch (reason.name) {
      case '执行超时':
        suggestions.push('增加脚本执行超时时间，或检查页面加载速度')
        suggestions.push('优化等待策略，使用显式等待而非固定等待')
        break
      case '元素定位失败':
        suggestions.push('检查元素选择器是否正确，元素是否在iframe中')
        suggestions.push('确保页面完全加载后再进行元素操作')
        break
      case '网络连接问题':
        suggestions.push('检查网络连接和服务器状态')
        suggestions.push('增加重试机制处理网络波动')
        break
      case '断言验证失败':
        suggestions.push('检查断言条件和测试数据是否匹配')
        suggestions.push('验证页面结构是否发生变化')
        break
      case '浏览器相关问题':
        suggestions.push('检查浏览器驱动版本是否匹配')
        suggestions.push('尝试使用不同的浏览器或浏览器版本')
        break
      case 'JavaScript错误':
        suggestions.push('检查页面控制台是否有JS错误')
        suggestions.push('验证页面脚本是否正常加载')
        break
      case '权限问题':
        suggestions.push('检查用户权限和访问控制配置')
        suggestions.push('确保测试账号有足够的操作权限')
        break
      case '数据异常':
        suggestions.push('检查测试数据是否正确配置')
        suggestions.push('验证数据源是否可用')
        break
      default:
        suggestions.push('检查测试环境配置和脚本逻辑')
        suggestions.push('查看详细日志定位具体问题')
    }
  })

  // 如果没有失败原因，提供通用的建议
  if (suggestions.length === 0) {
    suggestions.push('定期维护测试用例，保持测试数据更新')
    suggestions.push('监控测试执行环境，确保资源充足')
  }

  // 去重并限制数量
  return Array.from(new Set(suggestions)).slice(0, 3)
}

// 获取步骤失败原因分析
function getStepFailureReasons() {
  if (!report.value || !report.value.charts_data?.trend) return []

  // 统计失败原因（从步骤维度）
  const reasonMap = new Map<string, number>()
  const failedSteps = report.value.charts_data.trend.filter((s: any) => !s.success && (s.error || s.message))

  failedSteps.forEach((step: any) => {
    const errorMsg = step.error || step.message || '未知错误'
    const reason = classifyStepFailureReason(errorMsg)
    reasonMap.set(reason, (reasonMap.get(reason) || 0) + 1)
  })

  // 如果没有失败原因但有失败的步骤，返回通用原因
  if (reasonMap.size === 0) {
    const failedCount = report.value.charts_data.trend.filter((s: any) => !s.success).length
    if (failedCount > 0) {
      return [{ name: '步骤执行失败', count: failedCount }]
    }
  }

  // 转换为数组并排序
  return Array.from(reasonMap.entries())
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 3)
}

// 分类步骤失败原因
function classifyStepFailureReason(errorMsg: string): string {
  if (!errorMsg) return '未知错误'

  const lowerMsg = errorMsg.toLowerCase()

  // 超时相关
  if (lowerMsg.includes('timeout') || lowerMsg.includes('超时') || lowerMsg.includes('timed out')) {
    return '步骤超时'
  }

  // 元素定位相关
  if (lowerMsg.includes('element') || lowerMsg.includes('元素') ||
      lowerMsg.includes('locator') || lowerMsg.includes('定位') ||
      lowerMsg.includes('not found') || lowerMsg.includes('找不到') ||
      lowerMsg.includes('no such')) {
    return '元素定位失败'
  }

  // 网络相关
  if (lowerMsg.includes('network') || lowerMsg.includes('网络') ||
      lowerMsg.includes('connection') || lowerMsg.includes('连接')) {
    return '网络连接问题'
  }

  // 断言相关
  if (lowerMsg.includes('assert') || lowerMsg.includes('断言') ||
      lowerMsg.includes('expected') || lowerMsg.includes('期望')) {
    return '断言验证失败'
  }

  // JavaScript错误
  if (lowerMsg.includes('javascript') || lowerMsg.includes('js error')) {
    return 'JavaScript错误'
  }

  return '其他错误'
}

// 获取步骤改进建议
function getStepSuggestions() {
  if (!report.value || !report.value.charts_data?.trend) return []

  const failureReasons = getStepFailureReasons()
  const suggestions: string[] = []
  const steps = report.value.charts_data.trend

  // 检查脚本是否从中间失败（有未执行的步骤）
  const totalSteps = report.value.summary.total || 0
  const executedSteps = steps.length
  const failedStep = steps.find((s: any) => !s.success)

  // 如果脚本从中间失败
  if (failedStep && executedSteps < totalSteps) {
    const remainingSteps = totalSteps - executedSteps
    suggestions.push(`脚本在步骤${failedStep.index || executedSteps}失败，还有${remainingSteps}个步骤未执行`)

    // 根据失败原因给出针对性建议
    const errorMsg = failedStep.error || failedStep.message || ''
    if (errorMsg.toLowerCase().includes('timeout') || errorMsg.includes('超时')) {
      suggestions.push('该步骤超时导致脚本中断，建议增加超时时间或优化页面加载')
    } else if (errorMsg.toLowerCase().includes('element') || errorMsg.includes('元素') || errorMsg.includes('定位')) {
      suggestions.push('元素定位失败导致脚本中断，建议检查页面结构和元素选择器')
    } else {
      suggestions.push('步骤失败导致脚本中断，建议查看详细错误日志并修复问题步骤')
    }

    suggestions.push('考虑在脚本中添加异常处理，提高脚本健壮性')
  } else if (failureReasons.length > 0) {
    // 正常失败处理
    failureReasons.forEach(reason => {
      switch (reason.name) {
        case '步骤超时':
          suggestions.push('增加该步骤的等待时间')
          suggestions.push('检查页面加载速度')
          break
        case '元素定位失败':
          suggestions.push('检查元素定位器是否正确')
          suggestions.push('确保元素已加载完成')
          break
        case '网络连接问题':
          suggestions.push('检查网络连接稳定性')
          break
        case '断言验证失败':
          suggestions.push('检查断言条件和测试数据')
          break
        case 'JavaScript错误':
          suggestions.push('检查页面是否有JavaScript错误')
          break
        default:
          suggestions.push('查看详细日志定位问题')
      }
    })
  }

  // 如果没有失败原因，提供通用的建议
  if (suggestions.length === 0) {
    suggestions.push('定期维护测试用例，保持测试数据更新')
    suggestions.push('优化等待策略，提高脚本稳定性')
  }

  // 去重并限制数量
  return Array.from(new Set(suggestions)).slice(0, 4)
}

// 获取未执行的步骤数
function getRemainingStepsCount() {
  if (!report.value || !report.value.charts_data?.trend) return 0

  const totalSteps = report.value.summary.total || 0
  const executedSteps = report.value.charts_data.trend.length

  // 如果已执行步骤数小于总步骤数，说明有未执行的步骤
  if (executedSteps < totalSteps) {
    return totalSteps - executedSteps
  }

  return 0
}

onMounted(() => {
  loadReport()
})
</script>

<style scoped>
.report-view {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0;
  color: rgba(255, 255, 255, 0.9);
}

.summary-cards {
  margin-bottom: 16px;
}

.charts-section {
  margin-bottom: 16px;
}

.chart {
  width: 100%;
  height: 300px;
}

.steps-section {
  margin-top: 16px;
}

.error-text {
  color: #f5222d;
}

.failure-analysis {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.analysis-title {
  font-size: 14px;
  font-weight: 500;
  color: rgba(0, 0, 0, 0.85);
  margin-bottom: 16px;
  display: flex;
  align-items: center;
}

.failure-reasons {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.failure-reason-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  background: rgba(245, 34, 45, 0.06);
  border-radius: 6px;
  border-left: 3px solid #f5222d;
  transition: all 0.2s;
}

.failure-reason-item:hover {
  background: rgba(245, 34, 45, 0.1);
  transform: translateX(2px);
}

.reason-name {
  font-size: 14px;
  color: rgba(0, 0, 0, 0.75);
  font-weight: 400;
}

.reason-count {
  font-size: 15px;
  font-weight: 500;
  color: #f5222d;
}

.no-failure {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.no-failure-content {
  text-align: center;
}

.no-failure-text {
  font-size: 16px;
  font-weight: 500;
  color: rgba(0, 0, 0, 0.85);
  margin-bottom: 4px;
}

.no-failure-sub {
  font-size: 13px;
  color: rgba(0, 0, 0, 0.45);
}

.suggestions {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

.suggestions-title {
  font-size: 14px;
  font-weight: 500;
  color: rgba(0, 0, 0, 0.85);
  margin-bottom: 12px;
  display: flex;
  align-items: center;
}

.suggestion-item {
  font-size: 13px;
  color: rgba(0, 0, 0, 0.65);
  padding: 10px 14px;
  background: rgba(250, 173, 20, 0.08);
  border-radius: 6px;
  margin-bottom: 8px;
  line-height: 1.6;
  border-left: 3px solid #faad14;
}

.suggestion-item:last-child {
  margin-bottom: 0;
}
</style>
