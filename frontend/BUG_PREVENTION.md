# BUG Prevention Guide
# BUG 预防指南

Automated Test Management Platform - Script Editor
自动化测试管理平台 - 脚本编辑器

---

## Table of Contents / 目录

1. [Edge Cases & Boundary Handling](#edge-cases--boundary-handling)
2. [Input Validation](#input-validation)
3. [State Management](#state-management)
4. [Drag & Drop Handling](#drag--drop-handling)
5. [Error Recovery](#error-recovery)
6. [Testing Strategies](#testing-strategies)

---

## Edge Cases & Boundary Handling
## 边界情况处理

### Empty Canvas States
### 空画布状态处理

**Problem**: What happens when the canvas is empty?
**问题**: 画布为空时会发生什么？

**Solution**:
**解决方案**:
- Display `EmptyState` component with helpful message
- Show "drag steps here" hint
- Disable save/export buttons when canvas is empty
- 使用 `EmptyState` 组件显示提示信息
- 显示"拖拽步骤至此"的提示
- 画布为空时禁用保存/导出按钮

```typescript
// ✅ Correct
if (steps.length === 0) {
  return <EmptyState icon="inbox" message="将左侧步骤拖拽至此开始编排" />
}

// ❌ Incorrect - No empty state handling
return <div></div>
```

### Type Switching With Existing Steps
### 有步骤时切换类型

**Problem**: User switches script type when canvas has steps
**问题**: 用户在有步骤时切换脚本类型

**Solution**:
**解决方案**:
- Show confirmation modal before clearing canvas
- Warn that type change will clear all steps
- Allow user to cancel the operation
- 显示确认模态框再清空画布
- 警告类型切换将清空所有步骤
- 允许用户取消操作

```typescript
// ✅ Correct
async function handleTypeChange() {
  if (steps.value.length > 0) {
    Modal.confirm({
      title: '切换测试类型',
      content: '切换类型将清空当前画布，是否继续？',
      onOk: () => {
        steps.value = []
        // Clear and reset
      }
    })
  }
}
```

### Variable Value Preview Overflow
### 变量值预览溢出

**Problem**: Long variable values break layout
**问题**: 长变量值破坏布局

**Solution**:
**解决方案**:
- Truncate values to 50 characters
- Add ellipsis (...) for truncated values
- Show full value in tooltip on hover
- 将值截断到50个字符
- 添加省略号（...）
- 悬停时在工具提示中显示完整值

```typescript
// ✅ Correct
function formatVariablePreview(value: string): string {
  if (value.length > 50) {
    return value.substring(0, 50) + '...'
  }
  return value
}
```

---

## Input Validation
## 输入验证

### Selector Validation
### 选择器验证

**Problem**: Malicious selector input (XSS, injection)
**问题**: 恶意选择器输入（XSS、注入）

**Solution**:
**解决方案**:
- Validate XPath syntax
- Validate CSS selector syntax
- Check for HTML tags, JavaScript code
- Validate using `validateSelector()` utility
- 验证 XPath 语法
- 验证 CSS 选择器语法
- 检查 HTML 标签、JavaScript 代码
- 使用 `validateSelector()` 工具验证

```typescript
import { validateSelector } from '@/utils/validation'

const result = validateSelector(inputValue)
if (!result.valid) {
  showError(result.error)
}
```

### URL Validation
### URL 验证

**Problem**: Invalid or malicious URLs
**问题**: 无效或恶意的 URL

**Solution**:
**解决方案**:
- Block `javascript:` protocol (XSS risk)
- Block `data:` protocol
- Only allow http, https, file protocols
- Use `validateUrl()` utility
- 阻止 `javascript:` 协议（XSS 风险）
- 阻止 `data:` 协议
- 仅允许 http、https、file 协议
- 使用 `validateUrl()` 工具

```typescript
import { validateUrl } from '@/utils/validation'

const result = validateUrl(urlInput)
if (!result.valid) {
  showError(result.error)
}
```

### JSON Input Validation
### JSON 输入验证

**Problem**: Invalid JSON in JSON editor mode
**问题**: JSON 编辑器模式中的无效 JSON

**Solution**:
**解决方案**:
- Try-catch JSON parsing
- Show specific error messages
- Don't update canvas until JSON is valid
- Highlight line number if possible
- Try-catch JSON 解析
- 显示具体的错误消息
- JSON 有效前不更新画布
- 尽可能高亮行号

```typescript
// ✅ Correct
function syncFromJson() {
  try {
    const parsed = JSON.parse(jsonContent.value)
    if (Array.isArray(parsed.steps)) {
      steps.value = parsed.steps
      jsonError.value = ''
    }
  } catch (e) {
    jsonError.value = `JSON解析错误: ${e.message}`
  }
}
```

### Number Range Validation
### 数字范围验证

**Problem**: Timeout values outside acceptable range
**问题**: 超时值超出可接受范围

**Solution**:
**解决方案**:
- Set min/max for numeric inputs
- Validate on blur and save
- Show inline error messages
- 为数字输入设置最小值/最大值
- 在失焦和保存时验证
- 显示内联错误消息

```typescript
import { validateNumber } from '@/utils/validation'

const result = validateNumber(timeoutValue, {
  min: 0.1,
  max: 3600,
  fieldName: '超时时间'
})
```

---

## State Management
## 状态管理

### Undo/Redo Stack Management
### 撤销/重做栈管理

**Problem**: Stack overflow with unlimited history
**问题**: 无限制历史记录导致栈溢出

**Solution**:
**解决方案**:
- Limit history stack size to 50 entries
- Remove oldest entries when limit reached
- Use deep copy to prevent reference issues
- 限制历史记录栈大小为50个条目
- 达到限制时删除最早的条目
- 使用深拷贝防止引用问题

```typescript
const maxHistorySize = 50

watch(steps, (newValue) => {
  const snapshot = JSON.parse(JSON.stringify(newValue))
  historyStack.value.push(snapshot)
  if (historyStack.value.length > maxHistorySize) {
    historyStack.value.shift()
  }
}, { deep: true })
```

### Step Selection State
### 步骤选择状态

**Problem**: Selected step doesn't exist (deleted)
**问题**: 选中的步骤不存在（已删除）

**Solution**:
**解决方案**:
- Clear selection when step is deleted
- Check if selected step exists before accessing
- Clear selection when canvas is cleared
- 删除步骤时清除选择
- 访问前检查选中的步骤是否存在
- 清空画布时清除选择

```typescript
// ✅ Correct
function removeStep(step: TestStep) {
  steps.value = steps.value.filter(s => s.id !== step.id)
  if (selectedStepId.value === step.id) {
    selectedStepId.value = null
    selectedStep.value = null
  }
}
```

### Loading State Handling
### 加载状态处理

**Problem**: Multiple simultaneous save operations
**问题**: 多个同时保存操作

**Solution**:
**解决方案**:
- Disable save button while saving
- Show loading indicator
- Prevent concurrent save calls
- 保存时禁用保存按钮
- 显示加载指示器
- 防止并发保存调用

```typescript
// ✅ Correct
<SimpleButton
  @click="handleSave"
  :loading="saving"
  :disabled="saving"
>
```

---

## Drag & Drop Handling
## 拖放处理

### Drop Target Validation
### 放置目标验证

**Problem**: Drop outside canvas area
**问题**: 在画布区域外放置

**Solution**:
**解决方案**:
- Only allow drops within canvas area
- Add visual feedback for valid drop zones
- Prevent default on invalid drop targets
- 仅允许在画布区域内放置
- 为有效的放置区域添加视觉反馈
- 在无效的放置目标上阻止默认行为

```typescript
function handleDragOver(event: DragEvent) {
  event.preventDefault()
  const canvas = document.querySelector('.canvas-area')
  const rect = canvas?.getBoundingClientRect()
  // Check if within canvas bounds
  // 检查是否在画布边界内
}
```

### Step Drag Data Integrity
### 步骤拖拽数据完整性

**Problem**: Lost step data during drag
**问题**: 拖拽期间丢失步骤数据

**Solution**:
**解决方案**:
- Store complete step definition in dataTransfer
- Include default params in drag data
- Validate data on drop
- 在 dataTransfer 中存储完整的步骤定义
- 在拖拽数据中包含默认参数
- 放置时验证数据

```typescript
// ✅ Correct
function handleDragStart(event: DragEvent, step: StepDefinition) {
  if (event.dataTransfer) {
    event.dataTransfer.setData('application/json', JSON.stringify({
      type: step.type,
      label: step.label,
      defaultParams: step.defaultParams
    }))
  }
}
```

---

## Error Recovery
## 错误恢复

### API Failure Recovery
### API 失败恢复

**Problem**: Save operation fails
**问题**: 保存操作失败

**Solution**:
**解决方案**:
- Show user-friendly error message
- Keep unsaved changes in editor
- Allow user to retry save
- 显示用户友好的错误消息
- 在编辑器中保留未保存的更改
- 允许用户重试保存

```typescript
// ✅ Correct
async function handleSave() {
  saving.value = true
  try {
    await createScript(form.value)
    message.success('保存成功')
    goBack()
  } catch (error) {
    // Error handled by interceptor
    // Keep form data for retry
    // 保留表单数据以供重试
  } finally {
    saving.value = false
  }
}
```

### JSON Parse Error Recovery
### JSON 解析错误恢复

**Problem**: Invalid JSON when switching from visual to JSON mode
**问题**: 从可视化模式切换到 JSON 模式时 JSON 无效

**Solution**:
**解决方案**:
- Don't switch to JSON mode if current JSON is invalid
- Keep last valid JSON content
- Show error message
- 如果当前 JSON 无效，不切换到 JSON 模式
- 保留最后有效的 JSON 内容
- 显示错误消息

```typescript
watch(editorMode, (newMode) => {
  if (newMode === 'json') {
    const jsonStr = JSON.stringify({ steps: steps.value }, null, 2)
    jsonContent.value = jsonStr
    jsonError.value = ''
  } else {
    if (jsonError.value) {
      // Stay in JSON mode if error
      // 如果有错误，保持在 JSON 模式
      editorMode.value = 'json'
    } else {
      syncFromJson()
    }
  }
})
```

---

## Testing Strategies
## 测试策略

### Unit Testing
### 单元测试

**Test Cases**:
**测试用例**:

1. **Type Selection**
   - Modal opens when creating new script
   - Correct framework options shown for each type
   - Confirm emits correct selection
   - 创建新脚本时打开模态框
   - 每种类型显示正确的框架选项
   - 确认发出正确的选择

2. **Drag & Drop**
   - Step is added to canvas when dropped
   - Step has correct default parameters
   - Step is selected after drop
   - 放置时步骤添加到画布
   - 步骤具有正确的默认参数
   - 放置后选中步骤

3. **Input Validation**
   - Invalid selector shows error
   - Invalid URL shows error
   - Valid inputs pass validation
   - 无效选择器显示错误
   - 无效 URL 显示错误
   - 有效输入通过验证

4. **Undo/Redo**
   - Undo restores previous state
   - Redo restores undone state
   - History limit enforced
   - 撤销恢复到之前的状态
   - 重做恢复到已撤销的状态
   - 强制执行历史记录限制

### Integration Testing
### 集成测试

**Test Cases**:
**测试用例**:

1. **Full Script Creation Flow**
   - Open type modal → Select type → Create steps → Save
   - 打开类型模态框 → 选择类型 → 创建步骤 → 保存

2. **Type Switching Flow**
   - Create steps → Try to switch type → Confirm → Canvas cleared
   - 创建步骤 → 尝试切换类型 → 确认 → 画布已清空

3. **Save & Load**
   - Create script → Save → Navigate away → Return → Load
   - 创建脚本 → 保存 → 导航离开 → 返回 → 加载

### Manual Testing Checklist
### 手动测试清单

- [ ] Create new script → Type selection modal appears
- [ ] Select Web type → Only Selenium/Playwright shown
- [ ] Select Mobile type → Only Appium shown
- [ ] Select API type → Only HttpRunner shown
- [ ] Drag step to canvas → Step added
- [ ] Click step → Property panel shows
- [ ] Edit step parameters → Changes saved
- [ ] Delete step → Step removed
- [ ] Undo → Last action undone
- [ ] Redo → Undone action redone
- [ ] Save with empty name → Error shown
- [ ] Save with valid data → Success message
- [ ] Switch type with steps → Confirmation shown
- [ ] Switch type empty → Immediate switch
- [ ] Visual → JSON mode → JSON content shown
- [ ] Edit JSON → Switch to visual → Changes applied
- [ ] Invalid JSON → Error shown, mode not switched
- [ ] 创建新脚本 → 出现类型选择模态框
- [ ] 选择 Web 类型 → 仅显示 Selenium/Playwright
- [ ] 选择 Mobile 类型 → 仅显示 Appium
- [ ] 选择 API 类型 → 仅显示 HttpRunner
- [ ] 拖动步骤到画布 → 步骤已添加
- [ ] 点击步骤 → 显示属性面板
- [ ] 编辑步骤参数 → 更改已保存
- [ ] 删除步骤 → 步骤已移除
- [ ] 撤销 → 上一步操作已撤销
- [ ] 重做 → 已撤销的操作已重做
- [ ] 保存时名称为空 → 显示错误
- [ ] 保存有效数据 → 显示成功消息
- [ ] 有步骤时切换类型 → 显示确认
- [ ] 空时切换类型 → 立即切换
- [ ] 可视化 → JSON 模式 → 显示 JSON 内容
- [ ] 编辑 JSON → 切换到可视化 → 应用更改
- [ ] 无效 JSON → 显示错误，模式未切换

---

## Common Bugs to Watch For
## 需要注意的常见错误

1. **Memory Leaks** / **内存泄漏**
   - Not cleaning up event listeners on unmount
   - Not disposing of subscriptions
   - 组件卸载时未清理事件监听器
   - 未清理订阅

2. **State Inconsistency** / **状态不一致**
   - Steps array and selectedStep out of sync
   - History stack not updated properly
   - steps 数组和 selectedStep 不同步
   - 历史记录栈未正确更新

3. **Reference Issues** / **引用问题**
   - Shallow copying arrays/objects in history
   - Multiple references to same object
   - 历史记录中的数组/对象浅拷贝
   - 对同一对象的多个引用

4. **Race Conditions** / **竞态条件**
   - Multiple simultaneous saves
   - Rapid undo/redo operations
   - 多个同时保存操作
   - 快速撤销/重做操作

---

## Best Practices
## 最佳实践

1. **Always validate user input** / **始终验证用户输入**
2. **Use TypeScript strict mode** / **使用 TypeScript 严格模式**
3. **Implement proper error boundaries** / **实现适当的错误边界**
4. **Test edge cases thoroughly** / **彻底测试边界情况**
5. **Provide clear user feedback** / **提供清晰的用户反馈**
6. **Maintain state consistency** / **保持状态一致性**
7. **Clean up resources** / **清理资源**
8. **Use defensive programming** / **使用防御性编程**

---

## Quick Reference
## 快速参考

### Validation Utilities
### 验证工具

```typescript
import {
  validateSelector,
  validateUrl,
  validateText,
  validateNumber,
  validateJson,
  validateVariableName
} from '@/utils/validation'
```

### Error Handling Pattern
### 错误处理模式

```typescript
try {
  await riskyOperation()
} catch (error) {
  // Error already handled by axios interceptor
  // 错误已由 axios 拦截器处理
  console.error('Operation failed:', error)
} finally {
  loading.value = false
}
```

### User Feedback Pattern
### 用户反馈模式

```typescript
// Success
message.success('操作成功')

// Error
message.error('操作失败：具体原因')

// Warning
message.warning('请注意：警告信息')

// Info
message.info('提示信息')
```

---

For questions or issues, please refer to the project documentation or contact the development team.
如有问题或疑问，请参考项目文档或联系开发团队。

Last updated: 2025-02-03
最后更新：2025-02-03
