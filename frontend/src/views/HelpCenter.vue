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
            <RocketOutlined /> 新手入门
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
          <!-- 新手入门 -->
          <div v-if="currentSection === 'quickstart'" class="help-content">
            <h3>🚀 新手入门</h3>
            <p>欢迎使用自动化测试平台！跟着下面5步，快速上手。</p>

            <a-timeline>
              <a-timeline-item color="green">
                <template #dot>
                  <span class="timeline-number">1</span>
                </template>
                <div class="timeline-content">
                  <h4>创建项目</h4>
                  <p>进入"项目管理"页面，点击"新建项目"按钮</p>
                  <a-descriptions :column="1" size="small" bordered style="margin-top: 12px;">
                    <a-descriptions-item label="项目名称">比如：电商网站测试</a-descriptions-item>
                    <a-descriptions-item label="项目类型">Web自动化 / 移动端 / API测试</a-descriptions-item>
                    <a-descriptions-item label="描述">选填，方便记录项目用途</a-descriptions-item>
                  </a-descriptions>
                </div>
              </a-timeline-item>

              <a-timeline-item>
                <template #dot>
                  <span class="timeline-number">2</span>
                </template>
                <div class="timeline-content">
                  <h4>安装执行机</h4>
                  <p>执行机是运行测试的小助手，需要安装在你的电脑上：</p>
                  <ol>
                    <li>向管理员获取 <code>executor-setup.exe</code> 安装包</li>
                    <li>双击运行安装程序</li>
                    <li>按照提示完成安装配置</li>
                    <li>启动后会自动连接服务器</li>
                  </ol>
                  <a-alert type="info" show-icon message="详细安装教程请点击左侧「执行机安装」" style="margin-top: 12px;" />
                </div>
              </a-timeline-item>

              <a-timeline-item>
                <template #dot>
                  <span class="timeline-number">3</span>
                </template>
                <div class="timeline-content">
                  <h4>创建测试脚本</h4>
                  <p>进入项目详情，点击"新建脚本"：</p>
                  <ol>
                    <li>给脚本起个名字，比如"登录功能测试"</li>
                    <li>从左侧拖拽步骤到中间</li>
                    <li>点击步骤配置参数</li>
                    <li>点击"保存"完成</li>
                  </ol>
                </div>
              </a-timeline-item>

              <a-timeline-item>
                <template #dot>
                  <span class="timeline-number">4</span>
                </template>
                <div class="timeline-content">
                  <h4>运行测试</h4>
                  <p>脚本创建完成后，点击"运行"按钮即可开始测试。</p>
                  <p>执行机会自动打开浏览器，按步骤执行你的测试。</p>
                </div>
              </a-timeline-item>

              <a-timeline-item color="gray">
                <template #dot>
                  <span class="timeline-number">5</span>
                </template>
                <div class="timeline-content">
                  <h4>查看结果</h4>
                  <p>执行完成后，可以查看：</p>
                  <ul>
                    <li>✅ 哪些步骤成功了</li>
                    <li>❌ 哪些步骤失败了</li>
                    <li>📸 失败时的截图</li>
                    <li>📊 测试统计数据</li>
                  </ul>
                </div>
              </a-timeline-item>
            </a-timeline>
          </div>

          <!-- 执行机安装教程 -->
          <div v-if="currentSection === 'executor'" class="help-content">
            <h3>🖥️ 执行机安装指南</h3>
            <p>执行机是运行测试的必备工具，安装在你的电脑上，负责打开浏览器并执行测试步骤。</p>

            <a-divider>什么是执行机</a-divider>

            <div class="info-box">
              <p><strong>简单来说：</strong>执行机就是一个能听懂平台指令的小助手，它会：</p>
              <ul>
                <li>📡 接收平台下发的测试任务</li>
                <li>🌐 自动打开 Chrome/Firefox/Edge 浏览器</li>
                <li>🤖 按照你的脚本步骤操作网页</li>
                <li>📸 遇到问题自动截图</li>
                <li>📤 把执行结果告诉平台</li>
              </ul>
            </div>

            <a-divider>开始安装</a-divider>

            <a-card title="第一步：获取安装包" size="small" style="margin-bottom: 16px;">
              <p>向管理员获取执行机安装包：<code>executor-setup-x.x.x.exe</code></p>
              <a-alert type="warning" show-icon message="注意：请从管理员处获取，不要自行下载！" style="margin-top: 8px;" />
            </a-card>

            <a-card title="第二步：运行安装程序" size="small" style="margin-bottom: 16px;">
              <ol>
                <li>双击运行 <code>executor-setup.exe</code></li>
                <li>选择安装位置（默认即可）</li>
                <li>等待安装完成</li>
                <li>安装完成后会自动启动配置向导</li>
              </ol>
            </a-card>

            <a-divider>配置向导</a-divider>

            <a-steps direction="vertical" :current="-1">
              <a-step title="步骤1：服务器设置">
                <template #description>
                  <div class="step-detail">
                    <p>填写平台服务器的地址：</p>
                    <a-card size="small" style="margin-top: 8px; background: #f5f5f5;">
                      <p><strong>服务器地址：</strong></p>
                      <ul>
                        <li>如果服务器和你的电脑在同一台电脑上，填写：<code>http://127.0.0.1:8000</code></li>
                        <li>如果服务器在局域网其他电脑上，填写：<code>http://192.168.x.x:8000</code>（具体IP问管理员）</li>
                        <li>如果是互联网服务器，填写管理员给的域名或IP</li>
                      </ul>
                    </a-card>
                    <a-alert type="warning" show-icon message="注意：必须是 http:// 开头，端口是 8000" style="margin-top: 8px;" />
                  </div>
                </template>
              </a-step>

              <a-step title="步骤2：RabbitMQ 设置">
                <template #description>
                  <div class="step-detail">
                    <p>RabbitMQ 是执行机和服务器之间的通信桥梁：</p>
                    <a-card size="small" style="margin-top: 8px; background: #f5f5f5;">
                      <p><strong>RabbitMQ 地址：</strong></p>
                      <ul>
                        <li><strong>同电脑安装</strong>：填写 <code>127.0.0.1</code></li>
                        <li><strong>局域网安装</strong>：填写服务器的实际 IP 地址（如 <code>192.168.1.100</code>）</li>
                        <li><strong>端口</strong>：保持默认 <code>5672</code></li>
                      </ul>
                    </a-card>

                    <p style="margin-top: 16px;"><strong>账号设置：</strong></p>
                    <a-alert type="warning" show-icon>
                      <template #message>
                        <span>远程执行机需要使用专用账号</span>
                      </template>
                      <template #description>
                        <p>执行机和服务器在不同电脑上，需要使用专用 RabbitMQ 账号：</p>
                        <ol style="margin-bottom: 0;">
                          <li>联系超级管理员在平台中创建账号</li>
                          <li>管理员登录平台 → 账号角色管理 → 角色管理</li>
                          <li>在「RabbitMQ 用户管理」区域创建用户</li>
                          <li>管理员会提供用户名和密码给你</li>
                          <li>使用创建的用户名和密码配置执行机</li>
                        </ol>
                      </template>
                    </a-alert>
                  </div>
                </template>
              </a-step>

              <a-step title="步骤3：执行机信息">
                <template #description>
                  <div class="step-detail">
                    <p>填写你的执行机信息：</p>
                    <a-descriptions :column="1" size="small" bordered>
                      <a-descriptions-item label="执行机名称">给执行机起个名字，方便区分，如"测试机-张三"</a-descriptions-item>
                      <a-descriptions-item label="平台用户名">你登录平台的账号</a-descriptions-item>
                      <a-descriptions-item label="平台密码">你登录平台的密码</a-descriptions-item>
                    </a-descriptions>
                  </div>
                </template>
              </a-step>

              <a-step title="步骤4：浏览器设置">
                <template #description>
                  <div class="step-detail">
                    <p>选择要使用的浏览器：</p>
                    <ul>
                      <li><strong>推荐使用 Chrome</strong>（最稳定）</li>
                      <li>也可以选择 Firefox 或 Edge</li>
                      <li>留空则自动检测系统已安装的浏览器</li>
                    </ul>
                    <a-alert type="info" show-icon message="如果没有安装浏览器，请先安装 Chrome 浏览器" style="margin-top: 8px;" />
                  </div>
                </template>
              </a-step>

              <a-step title="步骤5：完成配置">
                <template #description>
                  <div class="step-detail">
                    <p>配置完成后，执行机主窗口会自动打开：</p>
                    <ol>
                      <li>确认服务器已启动</li>
                      <li>点击"连接服务器"按钮</li>
                      <li>看到状态变为"🟢 在线"表示连接成功</li>
                    </ol>
                    <a-alert type="success" show-icon message="🎉 恭喜！执行机已配置完成，可以开始运行测试了！" style="margin-top: 12px;" />
                  </div>
                </template>
              </a-step>
            </a-steps>

            <a-divider>日常使用</a-divider>

            <a-row :gutter="16">
              <a-col :span="12">
                <a-card title="启动执行机" size="small">
                  <p>安装完成后，以后启动很简单：</p>
                  <ol>
                    <li>双击桌面快捷方式"自动化测试执行机"</li>
                    <li>或从开始菜单找到程序并点击</li>
                    <li>程序会自动连接服务器</li>
                  </ol>
                </a-card>
              </a-col>
              <a-col :span="12">
                <a-card title="查看状态" size="small">
                  <p>执行机窗口会显示：</p>
                  <ul>
                    <li>当前连接状态（在线/离线）</li>
                    <li>正在执行的任务</li>
                    <li>执行统计（成功/失败数）</li>
                    <li>实时日志输出</li>
                  </ul>
                </a-card>
              </a-col>
            </a-row>

            <a-divider>常见问题</a-divider>

            <a-collapse>
              <a-collapse-panel key="1" header="连接服务器失败怎么办？">
                <p><strong>请按以下步骤检查：</strong></p>
                <ol>
                  <li>确认服务器地址是否正确（注意 http:// 和端口号 8000）</li>
                  <li>在浏览器中访问服务器地址，看是否能打开</li>
                  <li>检查网络连接是否正常</li>
                  <li>确认服务器已经启动（联系管理员确认）</li>
                </ol>
              </a-collapse-panel>

              <a-collapse-panel key="2" header="RabbitMQ 连接失败？">
                <p><strong>请按以下步骤检查：</strong></p>
                <ol>
                  <li>确认 RabbitMQ 地址填写正确</li>
                  <li>如果在不同电脑上，确认填写的是服务器的 IP（不是 127.0.0.1）</li>
                  <li><strong>远程执行机必须使用专用账号</strong>，不能用 guest</li>
                  <li>联系超级管理员在平台中创建 RabbitMQ 用户</li>
                </ol>
              </a-collapse-panel>

              <a-collapse-panel key="3" header="浏览器启动失败？">
                <p><strong>解决方法：</strong></p>
                <ul>
                  <li>确认已安装 Chrome 浏览器</li>
                  <li>点击"重新配置"按钮，选择正确的浏览器路径</li>
                  <li>或者留空让系统自动检测</li>
                </ul>
              </a-collapse-panel>

              <a-collapse-panel key="4" header="如何修改配置？">
                <p>配置完成后如果需要修改：</p>
                <ul>
                  <li>点击执行机主窗口的"重新配置"按钮</li>
                  <li>按照向导重新填写配置信息</li>
                  <li>完成后会自动重新连接</li>
                </ul>
              </a-collapse-panel>

              <a-collapse-panel key="5" header="执行机显示离线？">
                <p><strong>请按以下步骤检查：</strong></p>
                <ol>
                  <li>确认执行机程序正在运行</li>
                  <li>检查是否已点击"连接服务器"按钮</li>
                  <li>查看日志窗口的错误信息</li>
                  <li>确认网络连接正常</li>
                  <li>确认服务器已启动</li>
                </ol>
              </a-collapse-panel>
            </a-collapse>
          </div>

          <!-- 脚本编辑教程 -->
          <div v-if="currentSection === 'script'" class="help-content">
            <h3>📝 脚本编辑教程</h3>
            <p>通过拖拽的方式创建测试脚本，无需编程基础！</p>

            <a-divider>认识编辑器</a-divider>

            <div class="editor-layout">
              <div class="layout-panel left">
                <div class="panel-header">📦 步骤面板</div>
                <p>左侧：各种可用的测试步骤，分类清晰</p>
              </div>
              <div class="layout-panel center">
                <div class="panel-header">🎨 画布</div>
                <p>中间：把步骤拖到这里，按执行顺序排列</p>
              </div>
              <div class="layout-panel right">
                <div class="panel-header">⚙️ 属性面板</div>
                <p>右侧：点击步骤后配置具体参数</p>
              </div>
            </div>

            <a-divider>常用步骤说明</a-divider>

            <a-card title="最常用的几类步骤" size="small" style="margin-bottom: 16px;">
              <a-row :gutter="16">
                <a-col :span="8">
                  <h4>🌐 页面操作</h4>
                  <ul class="step-list">
                    <li><strong>打开页面</strong> - 访问一个网址</li>
                    <li><strong>刷新页面</strong> - 重新加载</li>
                    <li><strong>后退/前进</strong> - 浏览器导航</li>
                  </ul>
                </a-col>
                <a-col :span="8">
                  <h4>🖱️ 鼠标操作</h4>
                  <ul class="step-list">
                    <li><strong>点击</strong> - 点击按钮/链接</li>
                    <li><strong>输入文本</strong> - 填写表单</li>
                    <li><strong>清空</strong> - 清空输入框</li>
                  </ul>
                </a-col>
                <a-col :span="8">
                  <h4>✅ 验证步骤</h4>
                  <ul class="step-list">
                    <li><strong>验证文本</strong> - 检查页面文字</li>
                    <li><strong>验证元素</strong> - 检查元素存在</li>
                    <li><strong>验证标题</strong> - 检查页面标题</li>
                  </ul>
                </a-col>
              </a-row>
            </a-card>

            <a-divider>创建你的第一个脚本</a-divider>

            <a-steps direction="vertical" :current="-1">
              <a-step title="步骤1：打开网页">
                <template #description>
                  <div class="step-detail">
                    <p>比如要测试登录功能，首先需要打开登录页面：</p>
                    <ol>
                      <li>从左侧拖拽"打开页面"到画布</li>
                      <li>点击这个步骤，右侧会显示配置框</li>
                      <li>在"页面URL"中填写网址，比如：<code>https://example.com/login</code></li>
                    </ol>
                  </div>
                </template>
              </a-step>

              <a-step title="步骤2：输入用户名">
                <template #description>
                  <div class="step-detail">
                    <p>在登录页面输入用户名：</p>
                    <ol>
                      <li>拖拽"输入文本"到画布</li>
                      <li>需要告诉执行机"在哪里输入"和"输入什么"</li>
                      <li><strong>元素定位器</strong>：如何找到输入框</li>
                      <li><strong>输入值</strong>：要输入的内容</li>
                    </ol>
                    <a-card size="small" style="margin-top: 8px; background: #f0f7ff;">
                      <p><strong>💡 如何获取元素定位器：</strong></p>
                      <ol>
                        <li>在网页上右键点击输入框</li>
                        <li>选择"检查"或"审查元素"</li>
                        <li>在代码中右键点击高亮的那一行</li>
                        <li>选择 Copy → Copy XPath</li>
                      </ol>
                    </a-card>
                  </div>
                </template>
              </a-step>

              <a-step title="步骤3：输入密码并点击登录">
                <template #description>
                  <div class="step-detail">
                    <p>同样的方式添加密码输入和点击登录按钮：</p>
                    <ul>
                      <li>拖入"输入文本"，填写密码框的定位器和密码</li>
                      <li>拖入"点击"，填写登录按钮的定位器</li>
                    </ul>
                  </div>
                </template>
              </a-step>

              <a-step title="步骤4：验证登录成功">
                <template #description>
                  <div class="step-detail">
                    <p>添加验证步骤确保登录成功：</p>
                    <ul>
                      <li>拖入"验证文本"</li>
                      <li>在"期望文本"中填写登录成功后应该出现的文字</li>
                      <li>比如："欢迎，张三" 或 "用户中心"</li>
                    </ul>
                  </div>
                </template>
              </a-step>

              <a-step title="步骤5：保存并运行">
                <template #description>
                  <div class="step-detail">
                    <p>脚本创建完成！</p>
                    <ol>
                      <li>点击右上角"保存"按钮</li>
                      <li>点击"运行"按钮</li>
                      <li>执行机会自动打开浏览器，按你的步骤操作</li>
                      <li>完成后查看结果</li>
                    </ol>
                  </div>
                </template>
              </a-step>
            </a-steps>

            <a-divider>定位器选择建议</a-divider>

            <a-card title="不同定位器的特点" size="small">
              <a-table :columns="locatorColumns" :data-source="locatorData" :pagination="false" size="small" />
            </a-card>

            <a-divider>小技巧</a-divider>

            <a-collapse>
              <a-collapse-panel key="1" header="💡 如何找到正确的元素定位器？">
                <p><strong>使用浏览器开发者工具：</strong></p>
                <ol>
                  <li>按 F12 打开开发者工具</li>
                  <li>点击左上角的小箭头图标</li>
                  <li>点击网页上的目标元素</li>
                  <li>代码会自动定位到对应位置</li>
                  <li>右键点击该行代码 → Copy → Copy XPath</li>
                </ol>
              </a-collapse-panel>

              <a-collapse-panel key="2" header="💡 页面加载慢怎么办？">
                <p>添加"等待元素"步骤：</p>
                <ul>
                  <li>在操作前拖入"等待元素"</li>
                  <li>填写要等待的元素定位器</li>
                  <li>执行机会等待元素出现后再继续</li>
                </ul>
              </a-collapse-panel>

              <a-collapse-panel key="3" header="💡 如何在多步骤中使用同一个值？">
                <p>使用变量功能：</p>
                <ul>
                  <li>在"变量管理"中创建变量</li>
                  <li>在步骤中使用 <code>${变量名}</code></li>
                  <li>详细教程请点击左侧"变量管理"</li>
                </ul>
              </a-collapse-panel>
            </a-collapse>
          </div>

          <!-- 变量管理 -->
          <div v-if="currentSection === 'variable'" class="help-content">
            <h3>🗄️ 变量管理</h3>
            <p>变量让你的脚本更灵活，修改一处，处处生效！</p>

            <a-divider>什么是变量</a-divider>

            <div class="info-box">
              <p><strong>简单理解：</strong>变量就是一个"占位符"，你在脚本中用 <code>${变量名}</code> 表示，实际执行时会替换成具体的值。</p>
              <p><strong>举个例子：</strong></p>
              <ul>
                <li>定义变量：<code>username</code> = <code>张三</code></li>
                <li>脚本中使用：<code>${username}</code></li>
                <li>执行时变成：<code>张三</code></li>
              </ul>
            </div>

            <a-divider>变量的好处</a-divider>

            <a-row :gutter="16">
              <a-col :span="12">
                <a-card title="✅ 一次修改，全局生效" size="small">
                  <p>比如测试环境的网址是 <code>http://test.com</code>，后来换成了 <code>http://newtest.com</code>：</p>
                  <ul>
                    <li><strong>不用变量</strong>：要修改每个脚本中的网址</li>
                    <li><strong>用变量</strong>：只修改变量值，所有脚本自动更新</li>
                  </ul>
                </a-card>
              </a-col>
              <a-col :span="12">
                <a-card title="✅ 环境切换超方便" size="small">
                  <p>测试环境和生产环境切换：</p>
                  <ul>
                    <li>定义变量 <code>env</code> = <code>test</code></li>
                    <li>URL 写成：<code>https://${env}.example.com</code></li>
                    <li>切换环境只需改一个变量值！</li>
                  </ul>
                </a-card>
              </a-col>
            </a-row>

            <a-divider>变量类型</a-divider>

            <a-row :gutter="16">
              <a-col :span="12">
                <a-card title="📦 项目变量" size="small">
                  <p><strong>在整个项目中共享</strong></p>
                  <ul>
                    <li>✅ 项目下所有脚本都能用</li>
                    <li>✅ 适合存环境配置、通用参数</li>
                    <li>✅ 示例：环境URL、测试账号</li>
                  </ul>
                </a-card>
              </a-col>
              <a-col :span="12">
                <a-card title="📄 脚本变量" size="small">
                  <p><strong>只在当前脚本中有效</strong></p>
                  <ul>
                    <li>✅ 只在当前脚本能用</li>
                    <li>✅ 优先级高于项目变量</li>
                    <li>✅ 适合存脚本特定数据</li>
                  </ul>
                </a-card>
              </a-col>
            </a-row>

            <a-divider>使用步骤</a-divider>

            <a-steps direction="vertical" :current="-1">
              <a-step title="第一步：创建变量">
                <template #description>
                  <div class="step-detail">
                    <p>进入"变量管理"页面：</p>
                    <ol>
                      <li>点击"新建变量"按钮</li>
                      <li>选择作用域（项目/脚本）</li>
                      <li>填写变量名（用英文，如 username）</li>
                      <li>选择类型（字符串/数字/布尔）</li>
                      <li>填写变量值</li>
                      <li>如果是密码等敏感信息，勾选"敏感数据"</li>
                    </ol>
                  </div>
                </template>
              </a-step>

              <a-step title="第二步：在脚本中使用">
                <template #description>
                  <div class="step-detail">
                    <p>在脚本编辑器中使用变量：</p>
                    <ol>
                      <li>点击步骤的输入框</li>
                      <li>输入 <code>$</code> 符号会自动提示可用变量</li>
                      <li>选择变量后自动插入 <code>${变量名}</code></li>
                      <li>或者直接手动输入 <code>${变量名}</code></li>
                    </ol>
                    <a-card size="small" style="margin-top: 8px; background: #f0f7ff;">
                      <p><strong>示例：</strong></p>
                      <p>输入框中填写：<code>Hello, ${username}</code></p>
                      <p>执行时自动替换为：<code>Hello, 张三</code></p>
                    </a-card>
                  </div>
                </template>
              </a-step>

              <a-step title="第三步：保存并运行">
                <template #description>
                  <div class="step-detail">
                    <p>保存脚本后运行，系统会自动把变量替换成实际值。</p>
                    <p>修改变量值后，再次运行会使用新值，无需修改脚本！</p>
                  </div>
                </template>
              </a-step>
            </a-steps>

            <a-divider>实际应用示例</a-divider>

            <a-collapse>
              <a-collapse-panel key="1" header="示例1：测试环境切换">
                <a-card size="small" style="background: #f9f9f9;">
                  <p><strong>定义的变量：</strong></p>
                  <ul>
                    <li>base_url = <code>http://test.example.com</code></li>
                    <li>username = <code>test_user</code></li>
                    <li>password = <code>test_pass</code></li>
                  </ul>
                  <p><strong>脚本中使用：</strong></p>
                  <ul>
                    <li>打开页面：<code>${base_url}/login</code> → <code>http://test.example.com/login</code></li>
                    <li>输入用户名：<code>${username}</code> → <code>test_user</code></li>
                  </ul>
                  <p><strong>切换环境：</strong></p>
                  <p>只需把 base_url 改成 <code>http://prod.example.com</code>，所有脚本自动指向生产环境！</p>
                </a-card>
              </a-collapse-panel>

              <a-collapse-panel key="2" header="示例2：多账号测试">
                <p>同一个脚本，测试不同用户登录：</p>
                <ul>
                  <li>定义变量 test_user = <code>user1</code></li>
                  <li>运行脚本测试 user1</li>
                  <li>修改变量 test_user = <code>user2</code></li>
                  <li>再次运行脚本测试 user2</li>
                </ul>
              </a-collapse-panel>
            </a-collapse>
          </div>

          <!-- 测试计划 -->
          <div v-if="currentSection === 'plan'" class="help-content">
            <h3>📋 测试计划</h3>
            <p>测试计划可以把多个脚本组合起来，一键批量执行！</p>

            <a-divider>什么是测试计划</a-divider>

            <div class="info-box">
              <p><strong>简单来说：</strong>测试计划就是一组脚本的"打包执行"，可以：</p>
              <ul>
                <li>📦 把多个相关脚本一起执行</li>
                <li>🔄 选择同时执行或按顺序执行</li>
                <li>⏰ 设置定时自动执行</li>
                <li>⚙️ 控制失败后是否继续</li>
              </ul>
            </div>

            <a-divider>执行模式对比</a-divider>

            <a-row :gutter="16">
              <a-col :span="12">
                <a-card title="🔄 并行执行" size="small">
                  <p><strong>所有脚本同时开始执行</strong></p>
                  <ul>
                    <li>✅ 充分利用多个执行机</li>
                    <li>✅ 执行时间短</li>
                    <li>✅ 适合无依赖关系的测试</li>
                  </ul>
                  <p><strong>举例：</strong>3个脚本同时执行，1分钟就完成</p>
                </a-card>
              </a-col>
              <a-col :span="12">
                <a-card title="📋 顺序执行" size="small">
                  <p><strong>按顺序一个一个执行</strong></p>
                  <ul>
                    <li>✅ 确保执行顺序</li>
                    <li>✅ 前一个完成再执行下一个</li>
                    <li>✅ 适合有依赖关系的测试</li>
                  </ul>
                  <p><strong>举例：</strong>3个脚本按顺序执行，需要3分钟</p>
                </a-card>
              </a-col>
            </a-row>

            <a-divider>创建测试计划</a-divider>

            <a-steps direction="vertical" :current="-1">
              <a-step title="步骤1：填写基本信息">
                <template #description>
                  <div class="step-detail">
                    <p>进入"测试计划"页面，点击"新建计划"：</p>
                    <ul>
                      <li><strong>计划名称</strong>：如"冒烟测试"、"回归测试"</li>
                      <li><strong>所属项目</strong>：选择关联的项目</li>
                      <li><strong>描述</strong>：选填，说明计划用途</li>
                    </ul>
                  </div>
                </template>
              </a-step>

              <a-step title="步骤2：选择脚本">
                <template #description>
                  <div class="step-detail">
                    <p>勾选要包含在计划中的脚本：</p>
                    <ul>
                      <li>从左侧脚本列表中勾选</li>
                      <li>可以跨多个项目选择脚本</li>
                      <li>选择后可以拖拽调整顺序</li>
                    </ul>
                  </div>
                </template>
              </a-step>

              <a-step title="步骤3：配置执行参数">
                <template #description>
                  <div class="step-detail">
                    <p><strong>执行模式：</strong></p>
                    <ul>
                      <li><strong>并行</strong>：所有脚本同时执行</li>
                      <li><strong>顺序</strong>：按列表顺序执行</li>
                    </ul>
                    <p><strong>失败后继续：</strong></p>
                    <ul>
                      <li>勾选：某个脚本失败后继续执行其他脚本</li>
                      <li>不勾选：某个脚本失败后停止整个计划</li>
                    </ul>
                  </div>
                </template>
              </a-step>

              <a-step title="步骤4：执行计划">
                <template #description>
                  <div class="step-detail">
                    <p>计划创建完成后：</p>
                    <ol>
                      <li>在计划列表中找到你的计划</li>
                      <li>点击"运行"按钮</li>
                      <li>系统按配置自动执行所有脚本</li>
                      <li>完成后查看统计报告</li>
                    </ol>
                  </div>
                </template>
              </a-step>
            </a-steps>

            <a-divider>定时执行（高级功能）</a-divider>

            <a-card title="使用 Cron 表达式设置定时任务" size="small">
              <p><strong>Cron 表达式示例：</strong></p>
              <ul>
                <li><code>0 0 * * *</code> - 每天凌晨0点执行</li>
                <li><code>0 */6 * * *</code> - 每6小时执行一次</li>
                <li><code>0 9 * * 1-5</code> - 工作日早上9点执行</li>
                <li><code>0 0 9 * * 1</code> - 每周一早上9点执行</li>
              </ul>
              <p>设置后，系统会自动按时执行，无需人工干预！</p>
            </a-card>
          </div>

          <!-- 执行测试 -->
          <div v-if="currentSection === 'execution'" class="help-content">
            <h3>▶️ 执行测试</h3>

            <a-divider>执行方式</a-divider>

            <a-row :gutter="16">
              <a-col :span="12">
                <a-card title="单脚本执行" hoverable>
                  <p>适合调试和快速测试：</p>
                  <ol>
                    <li>进入"脚本列表"</li>
                    <li>找到要运行的脚本</li>
                    <li>点击右侧"运行"按钮</li>
                    <li>执行机自动开始执行</li>
                  </ol>
                </a-card>
              </a-col>
              <a-col :span="12">
                <a-card title="计划执行" hoverable>
                  <p>适合批量测试：</p>
                  <ol>
                    <li>进入"测试计划"</li>
                    <li>点击计划右侧"运行"按钮</li>
                    <li>系统自动分配执行机</li>
                    <li>按配置执行所有脚本</li>
                  </ol>
                </a-card>
              </a-col>
            </a-row>

            <a-divider>执行状态说明</a-divider>

            <a-descriptions bordered :column="1">
              <a-descriptions-item label="🟡 等待中">任务已创建，排队等待执行机接取</a-descriptions-item>
              <a-descriptions-item label="🔵 执行中">脚本正在执行中</a-descriptions-item>
              <a-descriptions-item label="🟢 已完成">执行成功</a-descriptions-item>
              <a-descriptions-item label="🔴 已失败">执行失败，可查看日志和截图</a-descriptions-item>
              <a-descriptions-item label="⚫ 已停止">被手动停止</a-descriptions-item>
            </a-descriptions>

            <a-divider>执行控制</a-divider>

            <a-row :gutter="16">
              <a-col :span="8">
                <a-card title="⏹️ 停止执行" size="small">
                  <p>手动停止正在执行的任务：</p>
                  <ul>
                    <li>点击执行记录的"停止"按钮</li>
                    <li>执行机会立即停止当前任务</li>
                    <li>已完成的步骤不受影响</li>
                  </ul>
                </a-card>
              </a-col>
              <a-col :span="8">
                <a-card title="🔄 重新执行" size="small">
                  <p>再次运行失败的脚本：</p>
                  <ul>
                    <li>点击执行记录的"重新运行"</li>
                    <li>使用相同参数重新执行</li>
                    <li>生成新的执行记录</li>
                  </ul>
                </a-card>
              </a-col>
              <a-col :span="8">
                <a-card title="📋 查看详情" size="small">
                  <p>查看详细执行信息：</p>
                  <ul>
                    <li>点击"查看详情"查看步骤</li>
                    <li>查看实时执行日志</li>
                    <li>失败时自动截图</li>
                  </ul>
                </a-card>
              </a-col>
            </a-row>

            <a-divider>选择执行机</a-divider>

            <a-card title="如何选择执行机" size="small">
              <p><strong>自动分配（推荐）：</strong></p>
              <ul>
                <li>系统自动选择可用的执行机</li>
                <li>充分利用所有执行机资源</li>
                <li>负载均衡，效率最高</li>
              </ul>
              <p><strong>手动指定：</strong></p>
              <ul>
                <li>在执行时选择特定执行机</li>
                <li>适合需要特定环境的场景</li>
                <li>比如某个执行机安装了特定浏览器</li>
              </ul>
            </a-card>
          </div>

          <!-- 测试报告 -->
          <div v-if="currentSection === 'report'" class="help-content">
            <h3>📊 测试报告</h3>

            <a-divider>报告内容</a-divider>

            <a-row :gutter="16">
              <a-col :span="12">
                <a-card title="📈 测试概览" size="small">
                  <ul>
                    <li><strong>总用例数</strong>：执行了多少脚本/步骤</li>
                    <li><strong>通过数</strong>：成功了多少</li>
                    <li><strong>失败数</strong>：失败了多少</li>
                    <li><strong>通过率</strong>：成功百分比</li>
                    <li><strong>总耗时</strong>：总共花了多长时间</li>
                  </ul>
                </a-card>
              </a-col>
              <a-col :span="12">
                <a-card title="📊 图表展示" size="small">
                  <ul>
                    <li><strong>趋势图</strong>：各步骤耗时曲线</li>
                    <li><strong>饼图</strong>：成功失败比例</li>
                    <li><strong>柱状图</strong>：步骤耗时对比</li>
                  </ul>
                </a-card>
              </a-col>
            </a-row>

            <a-divider>报告操作</a-divider>

            <a-card title="可以做什么" size="small">
              <a-row :gutter="16">
                <a-col :span="8">
                  <h4>📥 导出报告</h4>
                  <p>导出为独立的 HTML 文件，可以在浏览器中打开，方便分享</p>
                </a-col>
                <a-col :span="8">
                  <h4>📸 查看截图</h4>
                  <p>失败步骤会自动截图，帮助快速定位问题</p>
                </a-col>
                <a-col :span="8">
                  <h4>📝 查看日志</h4>
                  <p>每个步骤的详细日志，包括错误堆栈信息</p>
                </a-col>
              </a-row>
            </a-card>
          </div>

          <!-- 常见问题 -->
          <div v-if="currentSection === 'faq'" class="help-content">
            <h3>❓ 常见问题</h3>

            <a-collapse accordion>
              <a-collapse-panel key="1" header="如何定位页面元素？">
                <p><strong>最简单的方法：</strong></p>
                <ol>
                  <li>在浏览器中按 F12 打开开发者工具</li>
                  <li>点击左上角的元素选择器图标（一个小箭头）</li>
                  <li>点击页面上的目标元素</li>
                  <li>在代码区域右键点击高亮的那一行</li>
                  <li>选择 Copy → Copy XPath</li>
                  <li>把复制的内容粘贴到步骤的定位器中</li>
                </ol>
              </a-collapse-panel>

              <a-collapse-panel key="2" header="测试执行失败怎么办？">
                <p><strong>排查步骤：</strong></p>
                <ol>
                  <li>查看执行记录中的错误信息</li>
                  <li>查看失败截图，看看页面当时是什么状态</li>
                  <li>检查元素定位器是否正确</li>
                  <li>如果是"找不到元素"，可能是页面加载慢，添加"等待元素"步骤</li>
                </ol>
              </a-collapse-panel>

              <a-collapse-panel key="3" header="页面加载慢导致失败？">
                <p><strong>解决方法：</strong></p>
                <ul>
                  <li>在操作前添加"等待元素"步骤</li>
                  <li>等待要操作的元素出现后再继续</li>
                  <li>或者添加"等待时间"步骤，等待几秒</li>
                </ul>
              </a-collapse-panel>

              <a-collapse-panel key="4" header="如何在 iframe 中操作？">
                <p><strong>解决方法：</strong></p>
                <ul>
                  <li>先添加"切换框架"步骤</li>
                  <li>填写 iframe 的标识（name 或 index）</li>
                  <li>切换后的操作会针对 iframe 内</li>
                  <li>完成后记得切回主文档</li>
                </ul>
              </a-collapse-panel>

              <a-collapse-panel key="5" header="执行机显示离线？">
                <p><strong>检查清单：</strong></p>
                <ul>
                  <li>✅ 执行机程序是否正在运行</li>
                  <li>✅ 是否已点击"连接服务器"按钮</li>
                  <li>✅ 网络连接是否正常</li>
                  <li>✅ 服务器地址是否正确</li>
                </ul>
                <p><strong>解决方法：</strong></p>
                <ul>
                  <li>重新点击"连接服务器"</li>
                  <li>查看执行机日志窗口的错误信息</li>
                  <li>联系管理员确认服务器是否正常</li>
                </ul>
              </a-collapse-panel>

              <a-collapse-panel key="6" header="如何进行参数化测试？">
                <p>使用变量功能：</p>
                <ol>
                  <li>进入"变量管理"创建变量</li>
                  <li>在脚本中使用 <code>${变量名}</code> 引用</li>
                  <li>修改变量值即可，无需修改脚本</li>
                </ol>
                <p>详细教程请点击"变量管理"</p>
              </a-collapse-panel>

              <a-collapse-panel key="7" header="测试计划不执行？">
                <p><strong>可能原因：</strong></p>
                <ul>
                  <li>计划中没有添加脚本</li>
                  <li>没有可用的在线执行机</li>
                  <li>执行机未配置浏览器</li>
                </ul>
                <p><strong>解决方法：</strong></p>
                <ul>
                  <li>确认计划中至少有一个脚本</li>
                  <li>检查执行机是否在线</li>
                  <li>确认执行机已配置浏览器</li>
                </ul>
              </a-collapse-panel>

              <a-collapse-panel key="8" header="远程执行机连接失败？">
                <p><strong>重要提示：</strong></p>
                <a-alert type="warning" show-icon style="margin-bottom: 12px;">
                  <template #description>
                    <p>远程执行机（与服务器不在同一台电脑）不能使用 guest 账号连接 RabbitMQ！</p>
                  </template>
                </a-alert>
                <p><strong>解决方法：</strong></p>
                <ol>
                  <li>联系超级管理员</li>
                  <li>管理员在"账号角色管理"→"角色管理"中创建 RabbitMQ 用户</li>
                  <li>使用创建的用户名和密码重新配置执行机</li>
                </ol>
              </a-collapse-panel>
            </a-collapse>
          </div>

          <!-- 搜索结果 -->
          <div v-if="currentSection === 'search'" class="help-content">
            <h3>🔍 搜索结果</h3>
            <p>关键词：<strong>{{ searchKeyword }}</strong></p>
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
  { title: '推荐指数', dataIndex: 'stars', key: 'stars' }
]

const locatorData = [
  { key: '1', locator: 'ID', stability: '最稳定', stars: '⭐⭐⭐⭐⭐' },
  { key: '2', locator: 'XPath', stability: '很稳定', stars: '⭐⭐⭐⭐⭐' },
  { key: '3', locator: 'CSS Selector', stability: '很稳定', stars: '⭐⭐⭐⭐' },
  { key: '4', locator: 'Name', stability: '一般', stars: '⭐⭐⭐' },
  { key: '5', locator: 'Class', stability: '较差', stars: '⭐⭐' }
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
  color: rgba(0, 0, 0, 0.85);
  font-weight: 600;
}

.help-content h4 {
  margin: 12px 0;
  font-size: 16px;
  color: rgba(0, 0, 0, 0.75);
  font-weight: 500;
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
  font-size: 16px;
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
