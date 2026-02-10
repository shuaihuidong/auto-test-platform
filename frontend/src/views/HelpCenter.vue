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
                <li>📡 通过 RabbitMQ 消息队列接收测试任务</li>
                <li>🌐 控制 Chrome/Firefox/Edge 浏览器</li>
                <li>📸 执行测试步骤，截图记录</li>
                <li>📤 通过 HTTP API 上报执行结果</li>
                <li>💓 定时发送心跳保持在线状态</li>
                <li>⚡ 支持并发执行（默认同时3个任务）</li>
              </ul>
            </div>

            <a-divider>系统架构说明</a-divider>

            <div class="info-box" style="background: #f6f8fa; border-color: #d9d9d9;">
              <p><strong>通信架构：</strong></p>
              <ul>
                <li><strong>任务接收</strong>：RabbitMQ 消息队列（可靠传递）</li>
                <li><strong>结果上报</strong>：HTTP REST API</li>
                <li><strong>心跳维持</strong>：HTTP POST 每30秒一次</li>
              </ul>
              <p><strong>优势：</strong></p>
              <ul>
                <li>✅ 消息不丢失（RabbitMQ 持久化）</li>
                <li>✅ 支持多执行机负载均衡</li>
                <li>✅ 执行机可离线，恢复后自动接收任务</li>
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

            <a-divider>环境要求</a-divider>

            <a-card title="必需组件" size="small">
              <a-row :gutter="16}">
                <a-col :span="12">
                  <h4>🐍 Python 环境</h4>
                  <p>Python 3.8 或更高版本</p>
                  <p class="text-gray">下载：<a href="https://www.python.org/downloads/" target="_blank">python.org</a></p>
                </a-col>
                <a-col :span="12">
                  <h4>🐰 RabbitMQ 服务</h4>
                  <p>3.12 或更高版本</p>
                  <p class="text-gray">用于消息队列，必须先启动</p>
                </a-col>
              </a-row>
            </a-card>

            <a-divider>安装步骤（以 Windows 为例）</a-divider>

            <a-steps direction="vertical" :current="-1}">
              <a-step title="步骤1：安装 RabbitMQ">
                <template #description>
                  <div class="step-detail">
                    <p>执行机依赖 RabbitMQ 消息队列，需要先安装：</p>
                    <ol>
                      <li>下载 Erlang/OTP（RabbitMQ 依赖）</li>
                      <li>下载 RabbitMQ Server</li>
                      <li>安装完成后启动服务：<code>rabbitmq-service start</code></li>
                      <li>启用管理插件：<code>rabbitmq-plugins enable rabbitmq_management</code></li>
                    </ol>
                    <p>验证安装：访问 <a href="http://localhost:15672" target="_blank">http://localhost:15672</a> (guest/guest)</p>
                    <a-alert type="info" show-icon message="提示：平台根目录提供了 setup_rabbitmq.ps1 脚本可快速安装" style="margin-top: 12px;" />
                  </div>
                </template>
              </a-step>

              <a-step title="步骤2：运行安装程序">
                <template #description>
                  <div class="step-detail">
                    <p>下载完成后，双击 <code>AutoTestExecutor-Setup-v1.0.0.exe</code> 文件</p>
                    <p>按照安装向导完成安装</p>
                  </div>
                </template>
              </a-step>

              <a-step title="步骤3：配置向导 - 服务器设置">
                <template #description>
                  <div class="step-detail">
                    <p>首次运行会弹出配置向导，首先配置服务器信息：</p>
                    <ul>
                      <li><strong>服务器地址</strong>：平台 API 地址</li>
                      <li>本地开发：使用 <code>http://127.0.0.1:8000</code></li>
                      <li>生产环境：使用服务器实际地址，如 <code>https://your-server.com</code></li>
                    </ul>
                    <a-alert type="warning" show-icon message="注意：使用 HTTP 协议，不是 ws:// 或 wss://" style="margin-top: 12px;" />
                  </div>
                </template>
              </a-step>

              <a-step title="步骤4：配置向导 - RabbitMQ 设置">
                <template #description>
                  <div class="step-detail">
                    <p>配置 RabbitMQ 连接信息：</p>
                    <ul>
                      <li><strong>主机地址</strong>：默认 <code>127.0.0.1</code></li>
                      <li><strong>端口</strong>：默认 <code>5672</code>（注意不是管理端口 15672）</li>
                      <li><strong>用户名</strong>：默认 <code>guest</code></li>
                      <li><strong>密码</strong>：默认 <code>guest</code></li>
                    </ul>
                  </div>
                </template>
              </a-step>

              <a-step title="步骤5：配置向导 - 执行机信息">
                <template #description>
                  <div class="step-detail">
                    <p>设置执行机的身份信息：</p>
                    <ul>
                      <li><strong>执行机名称</strong>：如"测试机-01"（方便识别）</li>
                      <li><strong>用户名</strong>：平台登录账号</li>
                      <li><strong>密码</strong>：平台登录密码</li>
                    </ul>
                  </div>
                </template>
              </a-step>

              <a-step title="步骤6：配置向导 - 浏览器设置">
                <template #description>
                  <div class="step-detail">
                    <p>配置浏览器路径（可选）：</p>
                    <ul>
                      <li>留空则自动检测系统浏览器</li>
                      <li>支持 Chrome、Firefox、Edge</li>
                      <li>如浏览器安装位置特殊，可手动指定路径</li>
                    </ul>
                  </div>
                </template>
              </a-step>

              <a-step title="步骤7：连接服务器">
                <template #description>
                  <div class="step-detail">
                    <p>配置完成后，执行机主窗口会自动打开：</p>
                    <ol>
                      <li>确认 RabbitMQ 服务已启动</li>
                      <li>确认平台后端服务已启动</li>
                      <li>点击"连接服务器"按钮</li>
                      <li>状态变为"在线"表示连接成功</li>
                    </ol>
                    <a-alert type="success" show-icon message="连接成功后，执行机会自动创建专属队列并开始接收任务" style="margin-top: 12px;" />
                  </div>
                </template>
              </a-step>
            </a-steps>

            <a-divider>执行模式说明</a-divider>

            <a-card title="支持的任务执行模式" size="small">
              <a-row :gutter="16}">
                <a-col :span="12">
                  <h4>🔄 并发执行</h4>
                  <p>多个任务同时执行</p>
                  <ul>
                    <li>默认最大并发数：3</li>
                    <li>可配置调整</li>
                    <li>充分利用系统资源</li>
                  </ul>
                </a-col>
                <a-col :span="12">
                  <h4>📋 顺序执行</h4>
                  <p>按顺序一个一个执行</p>
                  <ul>
                    <li>前一个完成后执行下一个</li>
                    <li>适用于有依赖关系的脚本</li>
                    <li>在测试计划中配置</li>
                  </ul>
                </a-col>
              </a-row>
            </a-card>

            <a-divider>常见问题</a-divider>

            <a-collapse>
              <a-collapse-panel key="1" header="连接服务器失败怎么办？">
                <p><strong>可能原因：</strong></p>
                <ul>
                  <li>服务器地址填写错误</li>
                  <li>平台后端服务未启动</li>
                  <li>网络不通（防火墙阻止）</li>
                  <li>用户名或密码错误</li>
                </ul>
                <p><strong>解决方法：</strong></p>
                <ul>
                  <li>检查服务器地址是否正确（使用 http:// 或 https://）</li>
                  <li>确认平台后端服务已启动（访问 API 地址测试）</li>
                  <li>检查防火墙设置</li>
                  <li>检查用户名密码是否正确</li>
                </ul>
              </a-collapse-panel>

              <a-collapse-panel key="2" header="RabbitMQ 连接失败怎么办？">
                <p><strong>可能原因：</strong></p>
                <ul>
                  <li>RabbitMQ 服务未启动</li>
                  <li>地址或端口配置错误</li>
                  <li>用户名密码错误</li>
                </ul>
                <p><strong>解决方法：</strong></p>
                <ul>
                  <li>检查 RabbitMQ 服务状态：<code>rabbitmq-service status</code></li>
                  <li>确认端口是 5672（不是 15672）</li>
                  <li>访问管理界面验证：<code>http://localhost:15672</code></li>
                  <li>检查用户名密码是否为 guest/guest</li>
                </ul>
              </a-collapse-panel>

              <a-collapse-panel key="3" header="浏览器启动失败怎么办？">
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

              <a-collapse-panel key="4" header="如何修改配置？">
                <p>已配置的执行机可以重新配置：</p>
                <ol>
                  <li>点击主窗口"重新配置"按钮</li>
                  <li>或在配置文件中直接修改：<code>~/.executor/config.json</code></li>
                  <li>修改后重启执行机生效</li>
                </ol>
              </a-collapse-panel>

              <a-collapse-panel key="5" header="执行机显示离线怎么办？">
                <p><strong>检查清单：</strong></p>
                <ul>
                  <li>✅ 执行机程序是否正在运行</li>
                  <li>✅ 是否已点击"连接服务器"按钮</li>
                  <li>✅ RabbitMQ 服务是否已启动</li>
                  <li>✅ 网络连接是否正常</li>
                  <li>✅ 服务器地址是否正确</li>
                  <li>✅ 用户名密码是否正确</li>
                </ul>
                <p><strong>解决方法：</strong></p>
                <ul>
                  <li>确认 RabbitMQ 已启动（访问管理界面）</li>
                  <li>确认平台后端已启动</li>
                  <li>重新点击"连接服务器"</li>
                  <li>检查执行机日志窗口的错误信息</li>
                </ul>
              </a-collapse-panel>

              <a-collapse-panel key="6" header="任务堆积不执行怎么办？">
                <p><strong>可能原因：</strong></p>
                <ul>
                  <li>执行机已达到最大并发数</li>
                  <li>执行机未正确连接到消息队列</li>
                  <li>任务被停止或取消</li>
                </ul>
                <p><strong>解决方法：</strong></p>
                <ul>
                  <li>查看执行机当前运行任务数</li>
                  <li>检查 RabbitMQ 队列状态</li>
                  <li>在执行记录中查看任务状态</li>
                </ul>
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
                    <li><strong>执行模式</strong>：
                      <ul>
                        <li><strong>并行执行</strong>：所有脚本同时执行（充分利用多执行机资源）</li>
                        <li><strong>顺序执行</strong>：按脚本列表顺序一个一个执行（适用于有依赖关系的测试）</li>
                      </ul>
                    </li>
                    <li><strong>失败后继续</strong>：某个脚本失败后是否继续执行其他脚本</li>
                    <li><strong>Cron 表达式</strong>：设置定时执行（可选）</li>
                  </ul>
                  <a-card title="执行模式对比" size="small" style="margin-top: 12px;">
                    <a-row :gutter="16}">
                      <a-col :span="12">
                        <h4>🔄 并行执行</h4>
                        <ul>
                          <li>所有脚本同时开始执行</li>
                          <li>充分利用多执行机并发能力</li>
                          <li>执行时间 = 最慢脚本的时间</li>
                          <li>适用于无依赖关系的独立测试</li>
                        </ul>
                      </a-col>
                      <a-col :span="12">
                        <h4>📋 顺序执行</h4>
                        <ul>
                          <li>按顺序执行，前一个完成后才执行下一个</li>
                          <li>确保执行顺序</li>
                          <li>执行时间 = 所有脚本时间之和</li>
                          <li>适用于有依赖关系的测试场景</li>
                        </ul>
                      </a-col>
                    </a-row>
                  </a-card>
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
                    <li>选择执行机（可选）</li>
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
              <a-descriptions-item label="⚫ 已停止">任务被手动停止</a-descriptions-item>
            </a-descriptions>

            <a-divider>执行控制</a-divider>

            <a-card title="支持的操作" size="small">
              <a-row :gutter="16}">
                <a-col :span="8">
                  <div class="action-item">
                    <h4>⏹️ 停止执行</h4>
                    <p>手动停止正在执行的任务</p>
                    <ul>
                      <li>单脚本：直接停止</li>
                      <li>计划执行：停止所有子任务</li>
                      <li>支持停止等待中的任务</li>
                    </ul>
                  </div>
                </a-col>
                <a-col :span="8">
                  <div class="action-item">
                    <h4>🔄 重新执行</h4>
                    <p>再次执行失败的脚本</p>
                    <ul>
                      <li>一键重新执行</li>
                      <li>保留原始参数</li>
                      <li>生成新的执行记录</li>
                    </ul>
                  </div>
                </a-col>
                <a-col :span="8">
                  <div class="action-item">
                    <h4>📋 查看日志</h4>
                    <p>查看详细执行日志</p>
                    <ul>
                      <li>实时日志推送</li>
                      <li>步骤执行详情</li>
                      <li>错误堆栈信息</li>
                    </ul>
                  </div>
                </a-col>
              </a-row>
            </a-card>

            <a-divider>实时日志</a-divider>

            <p>执行过程中可以查看实时日志：</p>
            <ul>
              <li>每个步骤的执行状态</li>
              <li>页面加载时间</li>
              <li>元素定位结果</li>
              <li>错误信息和堆栈</li>
              <li>失败步骤的截图</li>
            </ul>

            <a-divider>执行选项</a-divider>

            <a-collapse>
              <a-collapse-panel key="1" header="并发执行模式">
                <p>同时运行多个测试用例：</p>
                <ul>
                  <li>执行机默认最大并发数：3</li>
                  <li>可在执行机配置中调整</li>
                  <li>计划执行时选择"并行"模式</li>
                  <li>充分利用执行机资源提高效率</li>
                </ul>
                <a-alert type="info" show-icon message="提示：达到最大并发后，新任务会等待直到有可用槽位" style="margin-top: 8px;" />
              </a-collapse-panel>

              <a-collapse-panel key="2" header="顺序执行模式">
                <p>按顺序一个一个执行脚本：</p>
                <ul>
                  <li>计划执行时选择"顺序"模式</li>
                  <li>前一个脚本完成后才执行下一个</li>
                  <li>适用于有依赖关系的测试场景</li>
                  <li>中间某个脚本失败不会影响后续脚本</li>
                </ul>
              </a-collapse-panel>

              <a-collapse-panel key="3" header="选择执行机">
                <p>手动指定或自动分配执行机：</p>
                <ul>
                  <li><strong>自动分配</strong>：系统选择可用执行机</li>
                  <li><strong>手动指定</strong>：选择特定执行机执行</li>
                  <li>支持按项目分组配置专属执行机</li>
                  <li>离线执行机不会被分配任务</li>
                </ul>
              </a-collapse-panel>

              <a-collapse-panel key="4" header="调试模式">
                <p>单步调试脚本：</p>
                <ul>
                  <li>在脚本编辑器中启用调试</li>
                  <li>支持设置断点</li>
                  <li>单步执行每个步骤</li>
                  <li>查看变量值变化</li>
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
