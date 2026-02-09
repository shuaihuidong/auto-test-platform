<template>
  <div class="help-center">
    <div class="page-header">
      <h2>帮助中心</h2>
      <a-input-search
        v-model:value="searchKeyword"
        placeholder="搜索帮助内容..."
        style="width: 300px;"
        @search="onSearch"
      />
    </div>

    <a-row :gutter="24">
      <a-col :span="6">
        <a-menu
          v-model:selectedKeys="selectedKeys"
          mode="inline"
          theme="dark"
          @click="handleMenuClick"
          style="border-right: none;"
        >
          <a-menu-item key="quickstart">
            <RocketOutlined /> 快速开始
          </a-menu-item>
          <a-menu-item key="executor">
            <DesktopOutlined /> 执行机安装
          </a-menu-item>
          <a-menu-item key="script">
            <CodeOutlined /> 脚本编辑
          </a-menu-item>
          <a-menu-item key="variable">
            <DatabaseOutlined /> 变量管理
          </a-menu-item>
          <a-menu-item key="plan">
            <ScheduleOutlined /> 测试计划
          </a-menu-item>
          <a-menu-item key="execution">
            <PlayCircleOutlined /> 执行测试
          </a-menu-item>
          <a-menu-item key="report">
            <BarChartOutlined /> 测试报告
          </a-menu-item>
          <a-menu-item key="faq">
            <QuestionCircleOutlined /> 常见问题
          </a-menu-item>
        </a-menu>
      </a-col>

      <a-col :span="18">
        <a-card class="content-card">
          <!-- 快速开始 -->
          <div v-if="currentSection === 'quickstart'" class="help-content">
            <h3>🚀 快速开始</h3>
            <p>欢迎使用自动化测试平台！本教程将带您快速上手平台的各项功能。</p>

            <a-timeline>
              <a-timeline-item color="green">
                <template #dot>
                  <span class="timeline-number">1</span>
                </template>
                <div class="timeline-content">
                  <h4>创建项目</h4>
                  <p>进入"项目管理"页面，点击右上角"新建项目"按钮</p>
                  <p>填写项目信息：</p>
                  <ul>
                    <li><strong>项目名称</strong>：给项目起个容易识别的名字</li>
                    <li><strong>项目类型</strong>：选择 Web自动化/移动端/API测试</li>
                    <li><strong>项目描述</strong>：简要描述项目用途（可选）</li>
                  </ul>
                </div>
              </a-timeline-item>

              <a-timeline-item>
                <template #dot>
                  <span class="timeline-number">2</span>
                </template>
                <div class="timeline-content">
                  <h4>安装执行机</h4>
                  <p>执行机是运行测试的核心组件，需要在本地机器上安装：</p>
                  <ol>
                    <li>下载执行机安装包（.exe / .dmg / .tar.gz）</li>
                    <li>双击运行安装程序</li>
                    <li>按照配置向导填写服务器地址和账号信息</li>
                    <li>点击"连接服务器"按钮</li>
                  </ol>
                  <a-alert type="info" show-icon message="详细安装教程请查看左侧「执行机安装」章节" style="margin-top: 12px;" />
                </div>
              </a-timeline-item>

              <a-timeline-item>
                <template #dot>
                  <span class="timeline-number">3</span>
                </template>
                <div class="timeline-content">
                  <h4>创建测试脚本</h4>
                  <p>进入项目详情，点击"新建脚本"开始编写测试：</p>
                  <ol>
                    <li>从左侧拖拽步骤到中间画布</li>
                    <li>点击步骤配置参数</li>
                    <li>点击"保存"按钮</li>
                  </ol>
                  <a-alert type="info" show-icon message="详细编辑教程请查看左侧「脚本编辑」章节" style="margin-top: 12px;" />
                </div>
              </a-timeline-item>

              <a-timeline-item>
                <template #dot>
                  <span class="timeline-number">4</span>
                </template>
                <div class="timeline-content">
                  <h4>运行测试</h4>
                  <p>脚本创建完成后，即可运行测试：</p>
                  <ul>
                    <li><strong>单脚本运行</strong>：在脚本列表点击"运行"</li>
                    <li><strong>计划运行</strong>：创建测试计划，批量执行</li>
                  </ul>
                </div>
              </a-timeline-item>

              <a-timeline-item color="gray">
                <template #dot>
                  <span class="timeline-number">5</span>
                </template>
                <div class="timeline-content">
                  <h4>查看报告</h4>
                  <p>执行完成后，查看详细的测试报告和统计数据</p>
                </div>
              </a-timeline-item>
            </a-timeline>
          </div>

          <!-- 执行机安装教程 -->
          <div v-if="currentSection === 'executor'" class="help-content">
            <h3>🖥️ 执行机安装教程</h3>
            <p>执行机是运行测试的核心组件，负责执行脚本并控制浏览器。本教程将指导您完成执行机的安装和配置。</p>

            <a-divider>什么是执行机</a-divider>

            <div class="info-box">
              <p><strong>执行机</strong>是运行在您本地机器上的软件程序，负责：</p>
              <ul>
                <li>📡 与平台服务器通信，接收测试任务</li>
                <li>🌐 控制 Chrome/Firefox/Edge 浏览器</li>
                <li>📸 执行测试步骤，截图记录</li>
                <li>📤 上传执行日志和结果到平台</li>
              </ul>
            </div>

            <a-divider>下载安装包</a-divider>

            <p>根据您的操作系统选择对应的安装包：</p>

            <a-row :gutter="16" style="margin-bottom: 24px;">
              <a-col :span="8">
                <a-card hoverable>
                  <template #cover>
                    <div class="os-icon windows">🪟</div>
                  </template>
                  <a-card-meta title="Windows" description="适用于 Windows 10/11" />
                  <template #actions>
                    <a-button type="primary" block>下载 .exe</a-button>
                  </template>
                </a-card>
              </a-col>
              <a-col :span="8">
                <a-card hoverable>
                  <template #cover>
                    <div class="os-icon macos">🍎</div>
                  </template>
                  <a-card-meta title="macOS" description="适用于 macOS 10.15+" />
                  <template #actions>
                    <a-button type="primary" block>下载 .dmg</a-button>
                  </template>
                </a-card>
              </a-col>
              <a-col :span="8">
                <a-card hoverable>
                  <template #cover>
                    <div class="os-icon linux">🐧</div>
                  </template>
                  <a-card-meta title="Linux" description="适用于 Ubuntu/Debian/CentOS" />
                  <template #actions>
                    <a-button type="primary" block>下载 .tar.gz</a-button>
                  </template>
                </a-card>
              </a-col>
            </a-row>

            <a-divider>安装步骤（以 Windows 为例）</a-divider>

            <a-steps direction="vertical" :current="-1">
              <a-step title="运行安装程序">
                <template #description>
                  <div class="step-detail">
                    <p>下载完成后，双击 <code>AutoTestExecutor.exe</code> 文件</p>
                    <div class="screenshot-placeholder">
                      📷 <span>截图：双击运行安装程序</span>
                    </div>
                  </div>
                </template>
              </a-step>

              <a-step title="配置向导 - 服务器设置">
                <template #description>
                  <div class="step-detail">
                    <p>首次运行会弹出配置向导，首先配置服务器信息：</p>
                    <ul>
                      <li><strong>服务器地址</strong>：输入平台服务器地址</li>
                      <li>本地开发：使用 <code>ws://localhost:8000</code></li>
                      <li>生产环境：使用服务器实际地址，如 <code>wss://your-server.com</code></li>
                    </ul>
                    <div class="screenshot-placeholder">
                      📷 <span>截图：配置向导 - 服务器设置页面</span>
                    </div>
                    <a-alert type="warning" show-icon message="注意：地址必须以 ws:// 或 wss:// 开头" style="margin-top: 12px;" />
                  </div>
                </template>
              </a-step>

              <a-step title="配置向导 - 执行机信息">
                <template #description>
                  <div class="step-detail">
                    <p>设置执行机的身份信息：</p>
                    <ul>
                      <li><strong>执行机名称</strong>：如"测试机-01"（方便识别）</li>
                      <li><strong>用户名</strong>：平台登录账号</li>
                      <li><strong>密码</strong>：平台登录密码</li>
                    </ul>
                    <div class="screenshot-placeholder">
                      📷 <span>截图：配置向导 - 执行机信息页面</span>
                    </div>
                  </div>
                </template>
              </a-step>

              <a-step title="配置向导 - 浏览器设置">
                <template #description>
                  <div class="step-detail">
                    <p>配置浏览器路径（可选）：</p>
                    <ul>
                      <li>留空则自动检测或下载驱动</li>
                      <li>如浏览器安装位置特殊，可手动指定路径</li>
                    </ul>
                    <div class="screenshot-placeholder">
                      📷 <span>截图：配置向导 - 浏览器配置页面</span>
                    </div>
                  </div>
                </template>
              </a-step>

              <a-step title="配置向导 - 高级设置">
                <template #description>
                  <div class="step-detail">
                    <p>配置执行参数（可选）：</p>
                    <ul>
                      <li><strong>最大并发</strong>：同时执行的任务数（默认3）</li>
                      <li><strong>日志保留</strong>：日志文件保留天数（默认7天）</li>
                    </ul>
                    <div class="screenshot-placeholder">
                      📷 <span>截图：配置向导 - 高级设置页面</span>
                    </div>
                  </div>
                </template>
              </a-step>

              <a-step title="连接服务器">
                <template #description>
                  <div class="step-detail">
                    <p>配置完成后，执行机主窗口会自动打开：</p>
                    <ol>
                      <li>点击"连接服务器"按钮</li>
                      <li>状态变为"在线"表示连接成功</li>
                      <li>此时执行机可以接收并执行任务</li>
                    </ol>
                    <div class="screenshot-placeholder">
                      📷 <span>截图：执行机主窗口，显示在线状态</span>
                    </div>
                  </div>
                </template>
              </a-step>
            </a-steps>

            <a-divider>常见问题</a-divider>

            <a-collapse>
              <a-collapse-panel key="1" header="连接服务器失败怎么办？">
                <p><strong>可能原因：</strong></p>
                <ul>
                  <li>服务器地址填写错误</li>
                  <li>服务器未启动</li>
                  <li>网络不通（防火墙阻止）</li>
                  <li>用户名或密码错误</li>
                </ul>
                <p><strong>解决方法：</strong></p>
                <ul>
                  <li>检查服务器地址是否正确（注意 ws:// 或 wss://）</li>
                  <li>确认平台服务器已启动</li>
                  <li>尝试在浏览器访问服务器地址测试连通性</li>
                  <li>检查用户名密码是否正确</li>
                </ul>
              </a-collapse-panel>

              <a-collapse-panel key="2" header="浏览器启动失败怎么办？">
                <p><strong>可能原因：</strong></p>
                <ul>
                  <li>未安装浏览器</li>
                  <li>浏览器版本与驱动不匹配</li>
                </ul>
                <p><strong>解决方法：</strong></p>
                <ul>
                  <li>确保已安装 Chrome/Firefox/Edge 浏览器</li>
                  <li>重新配置执行机，留空浏览器路径让系统自动检测</li>
                  <li>或手动指定正确的浏览器路径</li>
                </ul>
              </a-collapse-panel>

              <a-collapse-panel key="3" header="如何修改配置？">
                <p>已配置的执行机可以重新配置：</p>
                <ol>
                  <li>点击主窗口"重新配置"按钮</li>
                  <li>或在配置文件中直接修改：<code>~/.executor/config.json</code></li>
                  <li>修改后重启执行机生效</li>
                </ol>
              </a-collapse-panel>
            </a-collapse>
          </div>

          <!-- 脚本编辑教程 -->
          <div v-if="currentSection === 'script'" class="help-content">
            <h3>📝 脚本编辑教程</h3>
            <p>本教程将详细介绍如何使用可视化编辑器创建测试脚本。</p>

            <a-divider>编辑器界面</a-divider>

            <div class="editor-layout">
              <div class="layout-panel left">
                <div class="panel-header">步骤面板</div>
                <p>所有可用的测试步骤按类别分组</p>
              </div>
              <div class="layout-panel center">
                <div class="panel-header">画布</div>
                <p>拖拽步骤到此处，按执行顺序排列</p>
              </div>
              <div class="layout-panel right">
                <div class="panel-header">属性面板</div>
                <p>点击步骤后配置参数</p>
              </div>
            </div>

            <a-divider>基本步骤类型</a-divider>

            <a-row :gutter="16">
              <a-col :span="12">
                <a-card title="🌐 页面控制" size="small">
                  <ul class="step-list">
                    <li><strong>打开页面</strong>：导航到指定URL</li>
                    <li><strong>刷新页面</strong>：重新加载当前页</li>
                    <li><strong>后退/前进</strong>：浏览器导航</li>
                    <li><strong>滚动页面</strong>：滚动到顶部/底部/指定位置</li>
                  </ul>
                </a-card>
              </a-col>
              <a-col :span="12">
                <a-card title="🖱️ 交互操作" size="small">
                  <ul class="step-list">
                    <li><strong>点击</strong>：点击页面元素</li>
                    <li><strong>双击</strong>：双击页面元素</li>
                    <li><strong>右键点击</strong>：右键菜单</li>
                    <li><strong>输入文本</strong>：在输入框输入内容</li>
                    <li><strong>清空输入</strong>：清空输入框内容</li>
                  </ul>
                </a-card>
              </a-col>
            </a-row>

            <a-divider>创建第一个脚本</a-divider>

            <a-steps direction="vertical" :current="-1">
              <a-step title="创建脚本">
                <template #description>
                  <div class="step-detail">
                    <p>进入项目详情页，点击"新建脚本"：</p>
                    <ol>
                      <li>填写脚本名称，如"登录测试"</li>
                      <li>选择测试框架（Selenium/Playwright）</li>
                      <li>点击"确定"进入编辑器</li>
                    </ol>
                    <div class="screenshot-placeholder">
                      📷 <span>截图：新建脚本对话框</span>
                    </div>
                  </div>
                </template>
              </a-step>

              <a-step title="添加打开页面步骤">
                <template #description>
                  <div class="step-detail">
                    <p>从左侧"页面控制"分类拖拽"打开页面"到画布：</p>
                    <ol>
                      <li>点击该步骤，右侧属性面板会显示配置项</li>
                      <li>在"页面URL"输入框中填写目标网址</li>
                      <li>例如：<code>https://example.com/login</code></li>
                    </ol>
                    <div class="screenshot-placeholder">
                      📷 <span>截图：配置打开页面步骤</span>
                    </div>
                  </div>
                </template>
              </a-step>

              <a-step title="添加输入步骤">
                <template #description>
                  <div class="step-detail">
                    <p>从"交互操作"拖拽"输入文本"到画布：</p>
                    <ol>
                      <li>配置元素定位器（如何找到输入框）</li>
                      <li>选择定位类型（推荐使用 XPath 或 ID）</li>
                      <li>填写定位值，如：<code>//input[@id='username']</code></li>
                      <li>在"输入值"中填写要输入的内容</li>
                    </ol>
                    <div class="code-example">
                      <strong>示例：</strong>
                      <ul>
                        <li>定位器类型：<code>XPath</code></li>
                        <li>定位器值：<code>//input[@name='username']</code></li>
                        <li>输入值：<code>testuser</code></li>
                      </ul>
                    </div>
                    <div class="screenshot-placeholder">
                      📷 <span>截图：配置输入步骤</span>
                    </div>
                  </div>
                </template>
              </a-step>

              <a-step title="添加断言步骤">
                <template #description>
                  <div class="step-detail">
                    <p>添加验证步骤确保测试结果正确：</p>
                    <ol>
                      <li>拖拽"验证文本"到画布</li>
                      <li>配置要验证的文本内容</li>
                      <li>可选：指定在哪个元素中查找</li>
                    </ol>
                    <div class="code-example">
                      <strong>验证登录成功的示例：</strong>
                      <ul>
                        <li>验证类型：<code>验证文本</code></li>
                        <li>期望文本：<code>欢迎, testuser</code></li>
                      </ul>
                    </div>
                    <div class="screenshot-placeholder">
                      📷 <span>截图：配置断言步骤</span>
                    </div>
                  </div>
                </template>
              </a-step>

              <a-step title="保存并运行">
                <template #description>
                  <div class="step-detail">
                    <p>脚本编辑完成后：</p>
                    <ol>
                      <li>点击顶部"保存"按钮保存脚本</li>
                      <li>点击"运行"按钮开始测试</li>
                      <li>执行机会自动打开浏览器并执行步骤</li>
                      <li>执行完成后查看结果</li>
                    </ol>
                    <div class="screenshot-placeholder">
                      📷 <span>截图：脚本运行结果</span>
                    </div>
                  </div>
                </template>
              </a-step>
            </a-steps>

            <a-divider>元素定位技巧</a-divider>

            <a-card title="如何获取元素定位器" size="small">
              <p><strong>使用浏览器开发者工具：</strong></p>
              <ol>
                <li>在页面上右键点击目标元素</li>
                <li>选择"检查"或"审查元素"</li>
                <li>在开发者工具中右键点击该元素</li>
                <li>选择"Copy" → "Copy XPath"</li>
              </ol>
              <div class="screenshot-placeholder">
                📷 <span>截图：浏览器开发者工具复制 XPath</span>
              </div>

              <p style="margin-top: 16px;"><strong>定位器选择建议：</strong></p>
              <a-table :columns="locatorColumns" :data-source="locatorData" :pagination="false" size="small" />
            </a-card>

            <a-divider>使用变量</a-divider>

            <p>在脚本中可以使用变量实现参数化：</p>

            <a-steps :current="1" size="small" style="margin-bottom: 16px;">
              <a-step title="定义变量">在变量管理中创建变量</a-step>
              <a-step title="引用变量">在步骤中使用 ${变量名}</a-step>
            </a-steps>

            <div class="code-example">
              <p><strong>变量使用示例：</strong></p>
              <ul>
                <li>定义变量：<code>username</code> = <code>testuser</code></li>
                <li>在输入值中使用：<code>${username}</code></li>
                <li>执行时会自动替换为：<code>testuser</code></li>
              </ul>
            </div>

            <a-button type="link" @click="currentSection = 'variable'">查看详细的变量管理教程 →</a-button>
          </div>

          <!-- 变量管理 -->
          <div v-if="currentSection === 'variable'" class="help-content">
            <h3>🗄️ 变量管理</h3>
            <p>变量可以让您的脚本更加灵活，支持参数化测试和环境配置。</p>

            <a-divider>变量类型</a-divider>

            <a-row :gutter="16">
              <a-col :span="6">
                <a-card>
                  <a-statistic title="字符串" value="String" :value-style="{ color: '#1890ff' }">
                    <template #prefix>
                      <span style="font-size: 24px;">📝</span>
                    </template>
                  </a-statistic>
                  <p style="margin-top: 12px; font-size: 12px; color: #666;">存储文本内容</p>
                </a-card>
              </a-col>
              <a-col :span="6">
                <a-card>
                  <a-statistic title="数字" value="Number" :value-style="{ color: '#52c41a' }">
                    <template #prefix>
                      <span style="font-size: 24px;">🔢</span>
                    </template>
                  </a-statistic>
                  <p style="margin-top: 12px; font-size: 12px; color: #666;">存储数值</p>
                </a-card>
              </a-col>
              <a-col :span="6">
                <a-card>
                  <a-statistic title="布尔" value="Boolean" :value-style="{ color: '#faad14' }">
                    <template #prefix>
                      <span style="font-size: 24px;">☑️</span>
                    </template>
                  </a-statistic>
                  <p style="margin-top: 12px; font-size: 12px; color: #666;">存储 true/false</p>
                </a-card>
              </a-col>
              <a-col :span="6">
                <a-card>
                  <a-statistic title="JSON" value="JSON" :value-style="{ color: '#722ed1' }">
                    <template #prefix>
                      <span style="font-size: 24px;">📋</span>
                    </template>
                  </a-statistic>
                  <p style="margin-top: 12px; font-size: 12px; color: #666;">存储复杂数据</p>
                </a-card>
              </a-col>
            </a-row>

            <a-divider>变量作用域</a-divider>

            <div class="scope-comparison">
              <a-card title="项目变量" size="small" style="margin-bottom: 16px;">
                <ul>
                  <li>✅ 在整个项目中共享</li>
                  <li>✅ 所有脚本都可以使用</li>
                  <li>✅ 适合存储环境配置、通用参数</li>
                </ul>
                <p><strong>示例：</strong>环境URL、测试账号、超时时间</p>
              </a-card>

              <a-card title="脚本变量" size="small">
                <ul>
                  <li>✅ 只在当前脚本中有效</li>
                  <li>✅ 优先级高于项目变量</li>
                  <li>✅ 适合存储脚本特定参数</li>
                </ul>
                <p><strong>示例：</strong>测试数据、临时值</p>
              </a-card>
            </div>

            <a-divider>使用步骤</a-divider>

            <a-steps direction="vertical" :current="-1">
              <a-step title="创建变量">
                <template #description>
                  <p>进入"变量管理"页面，点击"新建变量"：</p>
                  <ol>
                    <li>选择变量作用域（项目/脚本）</li>
                    <li>填写变量名称（使用英文，如 username）</li>
                    <li>选择变量类型</li>
                    <li>填写变量值</li>
                    <li>勾选"敏感数据"可隐藏显示（如密码）</li>
                  </ol>
                </template>
              </a-step>

              <a-step title="在脚本中使用">
                <template #description>
                  <p>在脚本编辑器中使用变量：</p>
                  <ol>
                    <li>点击属性面板的"变量"按钮</li>
                    <li>选择要插入的变量</li>
                    <li>变量会以 <code>${变量名}</code> 格式插入</li>
                    <li>执行时自动替换为实际值</li>
                  </ol>
                  <div class="code-example">
                    <p><strong>示例：</strong></p>
                    <p>输入框中填写：<code>${username}</code></p>
                    <p>执行时替换为：<code>testuser</code></p>
                  </div>
                </template>
              </a-step>

              <a-step title="变量预览">
                <template #description>
                  <p>脚本编辑器会实时显示变量替换后的预览：</p>
                  <ul>
                    <li>输入 <code>Hello, ${username}</code></li>
                    <li>预览显示 <code>Hello, testuser</code></li>
                  </ul>
                </template>
              </a-step>
            </a-steps>

            <a-divider>使用场景示例</a-divider>

            <a-collapse>
              <a-collapse-panel key="1" header="场景1：环境切换">
                <p>使用变量轻松切换测试环境和生产环境：</p>
                <div class="code-example">
                  <p><strong>项目变量：</strong></p>
                  <ul>
                    <li><code>base_url</code> = <code>https://test.example.com</code></li>
                    <li><code>username</code> = <code>test_user</code></li>
                    <li><code>password</code> = <code>test_pass</code></li>
                  </ul>
                  <p><strong>脚本中使用：</strong></p>
                  <ul>
                    <li>打开页面：<code>${base_url}/login</code></li>
                    <li>输入用户名：<code>${username}</code></li>
                  </ul>
                </div>
                <p>切换环境时只需修改变量值，无需修改脚本！</p>
              </a-collapse-panel>

              <a-collapse-panel key="2" header="场景2：数据驱动测试">
                <p>结合测试数据实现参数化：</p>
                <div class="code-example">
                  <p><strong>测试数据：</strong></p>
                  <table style="width: 100%; border-collapse: collapse;">
                    <tr style="background: #f0f0f0;">
                      <th style="border: 1px solid #ddd; padding: 8px;">username</th>
                      <th style="border: 1px solid #ddd; padding: 8px;">password</th>
                      <th style="border: 1px solid #ddd; padding: 8px;">expected</th>
                    </tr>
                    <tr>
                      <td style="border: 1px solid #ddd; padding: 8px;">user1</td>
                      <td style="border: 1px solid #ddd; padding: 8px;">pass1</td>
                      <td style="border: 1px solid #ddd; padding: 8px;">成功</td>
                    </tr>
                    <tr>
                      <td style="border: 1px solid #ddd; padding: 8px;">user2</td>
                      <td style="border: 1px solid #ddd; padding: 8px;">pass2</td>
                      <td style="border: 1px solid #ddd; padding: 8px;">成功</td>
                    </tr>
                  </table>
                </div>
                <p>脚本中使用 <code>${username}</code>、<code>${password}</code>，每次执行自动替换！</p>
              </a-collapse-panel>
            </a-collapse>
          </div>

          <!-- 测试计划 -->
          <div v-if="currentSection === 'plan'" class="help-content">
            <h3>📋 测试计划</h3>
            <p>测试计划可以将多个脚本组合执行，支持定时任务和批量测试。</p>

            <a-divider>什么是测试计划</a-divider>

            <div class="info-box">
              <p><strong>测试计划</strong>是一组脚本的集合，可以：</p>
              <ul>
                <li>📦 组合多个相关脚本一起执行</li>
                <li>🔄 设置执行顺序（串行/并行）</li>
                <li>⏰ 配置定时任务（Cron 表达式）</li>
                <li>⚙️ 设置失败后是否继续</li>
              </ul>
            </div>

            <a-divider>创建测试计划</a-divider>

            <a-steps direction="vertical" :current="-1">
              <a-step title="基本信息">
                <template #description>
                  <p>填写计划的基本信息：</p>
                  <ul>
                    <li><strong>计划名称</strong>：如"冒烟测试"、"回归测试"</li>
                    <li><strong>描述</strong>：计划的用途说明</li>
                    <li><strong>所属项目</strong>：选择关联的项目</li>
                  </ul>
                </template>
              </a-step>

              <a-step title="选择脚本">
                <template #description>
                  <p>选择要包含在计划中的脚本：</p>
                  <ul>
                    <li>从脚本列表中勾选</li>
                    <li>可跨项目选择脚本</li>
                    <li>支持拖拽调整执行顺序</li>
                  </ul>
                </template>
              </a-step>

              <a-step title="执行配置">
                <template #description>
                  <p>配置执行参数：</p>
                  <ul>
                    <li><strong>执行顺序</strong>：
                      <ul>
                        <li>串行：按顺序一个一个执行</li>
                        <li>并行：同时执行所有脚本</li>
                      </ul>
                    </li>
                    <li><strong>失败后继续</strong>：某个脚本失败后是否继续执行其他脚本</li>
                    <li><strong>Cron 表达式</strong>：设置定时执行（可选）</li>
                  </ul>
                  <div class="code-example">
                    <p><strong>Cron 表达式示例：</strong></p>
                    <ul>
                      <li><code>0 0 * * *</code> - 每天凌晨0点</li>
                      <li><code>0 */6 * * *</code> - 每6小时一次</li>
                      <li><code>0 9 * * 1-5</code> - 工作日早上9点</li>
                    </ul>
                  </div>
                </template>
              </a-step>

              <a-step title="执行计划">
                <template #description>
                  <p>计划创建后即可执行：</p>
                  <ul>
                    <li>在计划列表点击"运行"按钮</li>
                    <li>系统会按配置自动执行所有脚本</li>
                    <li>可在执行记录中查看详细结果</li>
                  </ul>
                </template>
              </a-step>
            </a-steps>
          </div>

          <!-- 执行测试 -->
          <div v-if="currentSection === 'execution'" class="help-content">
            <h3>▶️ 执行测试</h3>

            <a-divider>执行方式</a-divider>

            <a-row :gutter="16">
              <a-col :span="12">
                <a-card title="单脚本执行" hoverable>
                  <p>快速执行单个脚本进行调试：</p>
                  <ol>
                    <li>进入脚本列表</li>
                    <li>点击脚本右侧的"运行"按钮</li>
                    <li>选择执行机</li>
                    <li>查看实时执行日志</li>
                  </ol>
                </a-card>
              </a-col>
              <a-col :span="12">
                <a-card title="计划执行" hoverable>
                  <p>批量执行多个脚本：</p>
                  <ol>
                    <li>进入计划管理</li>
                    <li>点击"运行"按钮</li>
                    <li>系统自动分配执行机</li>
                    <li>执行完成后查看报告</li>
                  </ol>
                </a-card>
              </a-col>
            </a-row>

            <a-divider>执行状态</a-divider>

            <a-descriptions bordered :column="1">
              <a-descriptions-item label="🟡 等待中">任务已创建，等待执行机接取</a-descriptions-item>
              <a-descriptions-item label="🔵 执行中">脚本正在执行</a-descriptions-item>
              <a-descriptions-item label="🟢 已完成">执行成功</a-descriptions-item>
              <a-descriptions-item label="🔴 已失败">执行失败，可查看错误日志</a-descriptions-item>
              <a-descriptions-item label="⚪ 已取消">任务被手动取消</a-descriptions-item>
            </a-descriptions>

            <a-divider>实时日志</a-divider>

            <p>执行过程中可以查看实时日志：</p>
            <ul>
              <li>每个步骤的执行状态</li>
              <li>页面加载时间</li>
              <li>元素定位结果</li>
              <li>错误信息和堆栈</li>
            </ul>

            <a-divider>执行选项</a-divider>

            <a-collapse>
              <a-collapse-panel key="1" header="并发执行">
                <p>同时运行多个测试用例：</p>
                <ul>
                  <li>执行机支持配置最大并发数</li>
                  <li>计划执行时可选择并行模式</li>
                  <li>充分利用执行机资源</li>
                </ul>
              </a-collapse-panel>

              <a-collapse-panel key="2" header="失败重试">
                <p>自动重试失败的步骤：</p>
                <ul>
                  <li>可配置重试次数</li>
                  <li>每次重试间隔时间</li>
                  <li>减少因偶发问题导致的失败</li>
                </ul>
              </a-collapse-panel>

              <a-collapse-panel key="3" header="条件执行">
                <p>根据上一步结果决定是否继续：</p>
                <ul>
                  <li>失败后停止执行</li>
                  <li>失败后继续执行</li>
                  <li>灵活应对不同测试场景</li>
                </ul>
              </a-collapse-panel>
            </a-collapse>
          </div>

          <!-- 测试报告 -->
          <div v-if="currentSection === 'report'" class="help-content">
            <h3>📊 测试报告</h3>

            <a-divider>报告内容</a-divider>

            <div class="report-sections">
              <a-card title="📈 测试概览" size="small" style="margin-bottom: 16px;">
                <ul>
                  <li><strong>总用例数</strong>：执行的脚本/步骤总数</li>
                  <li><strong>通过数</strong>：执行成功的数量</li>
                  <li><strong>失败数</strong>：执行失败的数量</li>
                  <li><strong>通过率</strong>：通过数 / 总数 × 100%</li>
                  <li><strong>总耗时</strong>：整个执行过程的总时间</li>
                </ul>
              </a-card>

              <a-card title="📉 执行趋势" size="small" style="margin-bottom: 16px;">
                <p>各步骤执行耗时的折线图，直观发现性能瓶颈</p>
              </a-card>

              <a-card title="🍰 失败截图" size="small" style="margin-bottom: 16px;">
                <p>失败步骤的页面截图，帮助快速定位问题</p>
              </a-card>

              <a-card title="📝 步骤详情" size="small">
                <p>每个步骤的详细执行信息：</p>
                <ul>
                  <li>步骤名称和类型</li>
                  <li>执行结果（成功/失败）</li>
                  <li>执行耗时</li>
                  <li>错误信息（如有）</li>
                </ul>
              </a-card>
            </div>

            <a-divider>报告操作</a-divider>

            <a-space>
              <a-button type="primary">📥 导出 HTML</a-button>
              <a-button>📧 分享报告</a-button>
              <a-button>🖨️ 打印报告</a-button>
            </a-space>
          </div>

          <!-- 常见问题 -->
          <div v-if="currentSection === 'faq'" class="help-content">
            <h3>❓ 常见问题</h3>

            <a-collapse accordion>
              <a-collapse-panel key="1" header="如何定位页面元素？">
                <p><strong>方法1：使用浏览器开发者工具</strong></p>
                <ol>
                  <li>在浏览器中 F12 打开开发者工具</li>
                  <li>点击元素选择器（左上角箭头图标）</li>
                  <li>点击页面上的目标元素</li>
                  <li>在 Elements 面板中右键点击该元素</li>
                  <li>选择 Copy → Copy XPath</li>
                </ol>
                <p><strong>方法2：使用浏览器插件</strong></p>
                <p>安装如 ChroPath 等插件，可直接生成多种定位器</p>
              </a-collapse-panel>

              <a-collapse-panel key="2" header="测试执行失败怎么办？">
                <p><strong>排查步骤：</strong></p>
                <ol>
                  <li>查看执行日志中的错误信息</li>
                  <li>检查失败截图中的页面状态</li>
                  <li>确认元素定位器是否正确</li>
                  <li>检查页面是否完全加载（增加等待时间）</li>
                  <li>验证执行机是否在线</li>
                </ol>
                <p><strong>常见错误：</strong></p>
                <ul>
                  <li><code>NoSuchElementException</code>：元素未找到，检查定位器</li>
                  <li><code>TimeoutException</code>：等待超时，增加等待时间</li>
                  <li><code>ElementNotInteractableException</code>：元素不可交互，可能被遮挡</li>
                </ul>
              </a-collapse-panel>

              <a-collapse-panel key="3" header="如何处理动态加载的内容？">
                <p><strong>解决方案：</strong></p>
                <ul>
                  <li>使用"等待元素"步骤，等待目标元素出现</li>
                  <li>设置合理的超时时间（默认10秒）</li>
                  <li>使用"等待文本"等待特定内容加载</li>
                  <li>添加固定等待时间作为缓冲</li>
                </ul>
              </a-collapse-panel>

              <a-collapse-panel key="4" header="如何在 iframe 中操作元素？">
                <p>使用"切换框架"步骤：</p>
                <ol>
                  <li>先添加"切换框架"步骤</li>
                  <li>填写 iframe 的 name 或 index</li>
                  <li>切换后的操作针对 iframe 内的元素</li>
                  <li>完成后使用"切换到主文档"返回主页面</li>
                </ol>
              </a-collapse-panel>

              <a-collapse-panel key="5" header="执行机显示离线怎么办？">
                <p><strong>检查清单：</strong></p>
                <ul>
                  <li>✅ 执行机程序是否正在运行</li>
                  <li>✅ 是否已点击"连接服务器"按钮</li>
                  <li>✅ 网络连接是否正常</li>
                  <li>✅ 服务器地址是否正确</li>
                  <li>✅ 用户名密码是否正确</li>
                </ul>
                <p><strong>解决方法：</strong></p>
                <ul>
                  <li>重新点击"连接服务器"</li>
                  <li>检查执行机日志窗口的错误信息</li>
                  <li>确认平台服务器已启动</li>
                </ul>
              </a-collapse-panel>

              <a-collapse-panel key="6" header="如何进行参数化测试？">
                <p>使用变量实现参数化：</p>
                <ol>
                  <li>在变量管理中创建变量</li>
                  <li>在脚本中使用 ${变量名} 引用</li>
                  <li>可以创建多个变量组合</li>
                  <li>支持敏感数据（如密码）隐藏显示</li>
                </ol>
                <p>详细教程请查看"变量管理"章节</p>
              </a-collapse-panel>

              <a-collapse-panel key="7" header="测试计划不执行怎么办？">
                <p><strong>可能原因：</strong></p>
                <ul>
                  <li>计划中没有添加脚本</li>
                  <li>没有可用的在线执行机</li>
                  <li>执行机的浏览器未配置</li>
                </ul>
                <p><strong>解决方法：</strong></p>
                <ul>
                  <li>确认计划中至少有一个脚本</li>
                  <li>检查执行机是否在线</li>
                  <li>确保执行机已配置浏览器</li>
                </ul>
              </a-collapse-panel>

              <a-collapse-panel key="8" header="如何导出测试报告？">
                <p>在测试报告页面：</p>
                <ol>
                  <li>找到对应的执行记录</li>
                  <li>点击"报告"按钮查看详情</li>
                  <li>点击"导出 HTML"按钮</li>
                  <li>选择保存位置下载报告</li>
                </ol>
                <p>导出的报告是独立的 HTML 文件，可以在浏览器中直接打开。</p>
              </a-collapse-panel>
            </a-collapse>
          </div>

          <!-- 搜索结果 -->
          <div v-if="currentSection === 'search'" class="help-content">
            <h3>🔍 搜索结果</h3>
            <p>关键词：<strong>"{{ searchKeyword }}"</strong></p>
            <a-list v-if="searchResults.length > 0" :data-source="searchResults" item-layout="horizontal">
              <template #renderItem="{ item }">
                <a-list-item>
                  <a-list-item-meta>
                    <template #title>
                      <a @click="currentSection = item.section; searchKeyword = ''">{{ item.title }}</a>
                    </template>
                    <template #description>{{ item.preview }}</template>
                  </a-list-item-meta>
                </a-list-item>
              </template>
            </a-list>
            <a-empty v-else description="未找到相关内容" />
          </div>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import {
  RocketOutlined,
  DesktopOutlined,
  CodeOutlined,
  DatabaseOutlined,
  ScheduleOutlined,
  PlayCircleOutlined,
  BarChartOutlined,
  QuestionCircleOutlined
} from '@ant-design/icons-vue'

const selectedKeys = ref(['quickstart'])
const currentSection = ref('quickstart')
const searchKeyword = ref('')

const locatorColumns = [
  { title: '定位器', dataIndex: 'locator', key: 'locator' },
  { title: '稳定性', dataIndex: 'stability', key: 'stability' },
  { title: '适用场景', dataIndex: 'usage', key: 'usage' }
]

const locatorData = [
  { key: '1', locator: 'ID', stability: '⭐⭐⭐⭐⭐', usage: '元素有唯一ID时首选' },
  { key: '2', locator: 'XPath', stability: '⭐⭐⭐⭐', usage: '灵活强大，最常用' },
  { key: '3', locator: 'CSS Selector', stability: '⭐⭐⭐⭐', usage: '简洁高效' },
  { key: '4', locator: 'Name', stability: '⭐⭐⭐', usage: '元素有name属性' },
  { key: '5', locator: 'Class', stability: '⭐⭐', usage: '不推荐（可能重复）' }
]

const searchResults = ref<Array<{section: string, title: string, preview: string}>>([])

function handleMenuClick({ key }: { key: string }) {
  currentSection.value = key
  selectedKeys.value = [key]
}

function onSearch(value: string) {
  if (!value) {
    currentSection.value = 'quickstart'
    return
  }

  // TODO: 实现搜索功能
  currentSection.value = 'search'
  searchResults.value = []
}
</script>

<style scoped>
.help-center {
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

.content-card {
  min-height: 600px;
}

.help-content h3 {
  margin-bottom: 24px;
  font-size: 20px;
}

.help-content h4 {
  margin: 12px 0;
  font-size: 16px;
}

.help-content p {
  margin: 8px 0;
  color: #333;
}

.help-content ul,
.help-content ol {
  margin: 12px 0;
  padding-left: 24px;
}

.help-content li {
  margin: 8px 0;
  color: #555;
}

.help-content code {
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Consolas', monospace;
  color: #c7254e;
}

.info-box {
  background: #e6f7ff;
  border: 1px solid #91d5ff;
  border-radius: 8px;
  padding: 16px;
  margin: 16px 0;
}

.info-box ul {
  margin-bottom: 0;
}

/* OS Icon */
.os-icon {
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
}

.os-icon.windows { background: #f0f0f0; }
.os-icon.macos { background: #f5f5f5; }
.os-icon.linux { background: #fafafa; }

/* Screenshot placeholder */
.screenshot-placeholder {
  background: #fafafa;
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  padding: 40px;
  text-align: center;
  margin: 16px 0;
  color: #999;
}

/* Step detail */
.step-detail {
  padding: 8px 0;
}

.step-detail ol,
.step-detail ul {
  padding-left: 20px;
}

.step-detail li {
  margin: 8px 0;
}

/* Code example */
.code-example {
  background: #f6f8fa;
  border-left: 3px solid #1890ff;
  padding: 12px 16px;
  margin: 16px 0;
  border-radius: 4px;
}

.code-example ul {
  margin: 8px 0 0 0;
  padding-left: 20px;
}

.code-example li {
  margin: 4px 0;
  font-family: 'Consolas', monospace;
  font-size: 13px;
}

/* Editor layout */
.editor-layout {
  display: flex;
  gap: 16px;
  margin: 16px 0;
}

.layout-panel {
  flex: 1;
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  padding: 16px;
  text-align: center;
}

.layout-panel .panel-header {
  font-weight: bold;
  margin-bottom: 12px;
  color: #1890ff;
}

.layout-panel.left { flex: 1; }
.layout-panel.center { flex: 2; }
.layout-panel.right { flex: 1.5; }

/* Step list */
.step-list {
  margin: 0;
  padding-left: 20px;
}

.step-list li {
  margin: 8px 0;
}

/* Scope comparison */
.scope-comparison {
  display: flex;
  gap: 16px;
  margin: 16px 0;
}

.scope-comparison > * {
  flex: 1;
}

/* Report sections */
.report-sections {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.report-sections ul {
  margin: 0;
  padding-left: 20px;
}

.report-sections li {
  margin: 4px 0;
}

/* Timeline */
.timeline-number {
  display: inline-block;
  width: 24px;
  height: 24px;
  line-height: 24px;
  text-align: center;
  background: #1890ff;
  color: white;
  border-radius: 50%;
  font-weight: bold;
}

.timeline-content {
  padding: 8px 0;
}

.timeline-content h4 {
  margin-bottom: 8px;
}

.timeline-content ul,
.timeline-content ol {
  padding-left: 20px;
}

.timeline-content li {
  margin: 6px 0;
}
</style>
