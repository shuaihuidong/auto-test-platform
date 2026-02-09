/**
 * Validation Utilities
 * Input validation with XSS protection and security measures
 */

import type { ValidationResult, Locator } from '@/types/script-editor'

// ============================================
// SELECTOR VALIDATION
// ============================================

/**
 * Validate CSS selector / XPath value
 * Protects against XSS and injection attacks
 */
export function validateSelector(value: string): ValidationResult {
  if (!value || value.trim() === '') {
    return { valid: false, error: '选择器值不能为空', field: 'selector' }
  }

  const trimmed = value.trim()

  // Check for HTML tags (XSS protection)
  if (/<[^>]*>/.test(trimmed)) {
    return { valid: false, error: '选择器值不能包含 HTML 标签', field: 'selector' }
  }

  // Check for JavaScript code (injection protection)
  const jsPatterns = [
    /javascript:/i,
    /on\w+\s*=/i,  // onclick=, onload=, etc.
    /<script/i,
    /\beval\s*\(/i,
    /document\./i,
    /window\./i
  ]

  for (const pattern of jsPatterns) {
    if (pattern.test(trimmed)) {
      return { valid: false, error: '选择器值包含非法内容', field: 'selector' }
    }
  }

  // Validate XPath syntax if starts with //
  if (trimmed.startsWith('//')) {
    if (!validateXPath(trimmed)) {
      return { valid: false, error: 'XPath 语法无效', field: 'selector' }
    }
  }

  // Validate CSS selector syntax
  if (trimmed.startsWith('#') || trimmed.startsWith('.')) {
    if (!validateCssSelector(trimmed)) {
      return { valid: false, error: 'CSS 选择器语法无效', field: 'selector' }
    }
  }

  return { valid: true }
}

/**
 * Validate XPath syntax
 */
function validateXPath(xpath: string): boolean {
  try {
    // Basic XPath validation
    if (/\/\/\/\//.test(xpath)) return false // Invalid triple slash
    if (/[<>](?![a-zA-Z\/=!])/ .test(xpath)) return false // Invalid comparison

    // Check for balanced brackets
    let openBrackets = 0
    for (const char of xpath) {
      if (char === '[') openBrackets++
      if (char === ']') openBrackets--
      if (openBrackets < 0) return false
    }
    if (openBrackets !== 0) return false

    return true
  } catch {
    return false
  }
}

/**
 * Validate CSS selector syntax
 */
function validateCssSelector(selector: string): boolean {
  try {
    // Check for balanced brackets and parentheses
    let openBrackets = 0
    let openParens = 0

    for (const char of selector) {
      if (char === '[') openBrackets++
      if (char === ']') openBrackets--
      if (char === '(') openParens++
      if (char === ')') openParens--
      if (openBrackets < 0 || openParens < 0) return false
    }

    if (openBrackets !== 0 || openParens !== 0) return false

    // Check for invalid characters
    if (/[\s{}\\]/.test(selector)) return false

    return true
  } catch {
    return false
  }
}

/**
 * Validate complete locator object
 */
export function validateLocator(locator: Locator): ValidationResult {
  if (!locator) {
    return { valid: false, error: '定位器不能为空', field: 'locator' }
  }

  const validTypes: string[] = ['xpath', 'css', 'id', 'name', 'class', 'tag', 'link_text', 'partial_link_text']

  if (!locator.type || !validTypes.includes(locator.type)) {
    return { valid: false, error: '无效的定位器类型', field: 'locator.type' }
  }

  return validateSelector(locator.value)
}

// ============================================
// URL VALIDATION
// ============================================

/**
 * Validate URL format
 */
export function validateUrl(url: string): ValidationResult {
  if (!url || url.trim() === '') {
    return { valid: false, error: 'URL 不能为空', field: 'url' }
  }

  const trimmed = url.trim()

  // Check for javascript: protocol (security)
  if (/^javascript:/i.test(trimmed)) {
    return { valid: false, error: '不允许使用 javascript: 协议', field: 'url' }
  }

  // Check for data: protocol (security)
  if (/^data:/i.test(trimmed)) {
    return { valid: false, error: '不允许使用 data: 协议', field: 'url' }
  }

  try {
    const urlObj = new URL(trimmed)

    // Only allow safe protocols
    const allowedProtocols = ['http:', 'https:', 'file:']
    if (!allowedProtocols.includes(urlObj.protocol)) {
      return { valid: false, error: `不支持的协议: ${urlObj.protocol}`, field: 'url' }
    }

    return { valid: true }
  } catch (e) {
    return { valid: false, error: '请输入有效的 URL', field: 'url' }
  }
}

// ============================================
// TEXT INPUT VALIDATION
// ============================================

/**
 * Validate text input (general purpose)
 */
export function validateText(value: string, options: {
  minLength?: number
  maxLength?: number
  required?: boolean
  pattern?: RegExp
  fieldName?: string
} = {}): ValidationResult {
  const {
    minLength = 0,
    maxLength = 10000,
    required = false,
    pattern,
    fieldName = 'text'
  } = options

  if (required && (!value || value.trim() === '')) {
    return { valid: false, error: `${fieldName} 不能为空`, field: fieldName }
  }

  if (value && value.length < minLength) {
    return { valid: false, error: `${fieldName} 最小长度为 ${minLength}`, field: fieldName }
  }

  if (value && value.length > maxLength) {
    return { valid: false, error: `${fieldName} 最大长度为 ${maxLength}`, field: fieldName }
  }

  if (value && pattern && !pattern.test(value)) {
    return { valid: false, error: `${fieldName} 格式不正确`, field: fieldName }
  }

  return { valid: true }
}

/**
 * Validate step name
 */
export function validateStepName(name: string): ValidationResult {
  return validateText(name, {
    required: true,
    minLength: 1,
    maxLength: 100,
    fieldName: '步骤名称'
  })
}

/**
 * Validate script name
 */
export function validateScriptName(name: string): ValidationResult {
  return validateText(name, {
    required: true,
    minLength: 2,
    maxLength: 100,
    pattern: /^[a-zA-Z0-9_\-\s\u4e00-\u9fa5]+$/,
    fieldName: '脚本名称'
  })
}

// ============================================
// NUMBER VALIDATION
// ============================================

/**
 * Validate number input
 */
export function validateNumber(value: number | string, options: {
  min?: number
  max?: number
  required?: boolean
  integer?: boolean
  fieldName?: string
} = {}): ValidationResult {
  const {
    min,
    max,
    required = false,
    integer = false,
    fieldName = 'number'
  } = options

  const numValue = typeof value === 'string' ? parseFloat(value) : value

  if (required && (value === null || value === undefined || value === '')) {
    return { valid: false, error: `${fieldName} 不能为空`, field: fieldName }
  }

  if (value !== null && value !== undefined && value !== '' && isNaN(numValue)) {
    return { valid: false, error: `${fieldName} 必须是有效数字`, field: fieldName }
  }

  if (integer && !Number.isInteger(numValue)) {
    return { valid: false, error: `${fieldName} 必须是整数`, field: fieldName }
  }

  if (min !== undefined && numValue < min) {
    return { valid: false, error: `${fieldName} 不能小于 ${min}`, field: fieldName }
  }

  if (max !== undefined && numValue > max) {
    return { valid: false, error: `${fieldName} 不能大于 ${max}`, field: fieldName }
  }

  return { valid: true }
}

/**
 * Validate timeout value (in seconds)
 */
export function validateTimeout(timeout: number | string): ValidationResult {
  return validateNumber(timeout, {
    min: 0.1,
    max: 3600,
    required: true,
    fieldName: '超时时间'
  })
}

// ============================================
// JSON VALIDATION
// ============================================

/**
 * Validate JSON string
 */
export function validateJson(jsonString: string, options: {
  required?: boolean
  fieldName?: string
} = {}): ValidationResult {
  const { required = false, fieldName = 'json' } = options

  if (required && (!jsonString || jsonString.trim() === '')) {
    return { valid: false, error: `${fieldName} 不能为空`, field: fieldName }
  }

  if (!jsonString || jsonString.trim() === '') {
    return { valid: true }
  }

  try {
    JSON.parse(jsonString)
    return { valid: true }
  } catch (e) {
    return { valid: false, error: `${fieldName} 格式无效: ${(e as Error).message}`, field: fieldName }
  }
}

// ============================================
// ASSERTION VALIDATION
// ============================================

/**
 * Validate assertion value
 */
export function validateAssertion(value: any, assertionType: string): ValidationResult {
  if (value === null || value === undefined || value === '') {
    return { valid: false, error: '断言值不能为空', field: 'assertion.value' }
  }

  // Type-specific validation
  switch (assertionType) {
    case 'regex':
      try {
        new RegExp(value)
        return { valid: true }
      } catch {
        return { valid: false, error: '无效的正则表达式', field: 'assertion.value' }
      }

    case 'jsonpath':
      if (!/^\$/.test(value)) {
        return { valid: false, error: 'JSONPath 必须以 $ 开头', field: 'assertion.value' }
      }
      return { valid: true }

    case 'numeric':
      if (typeof value !== 'number' && isNaN(parseFloat(value))) {
        return { valid: false, error: '断言值必须是数字', field: 'assertion.value' }
      }
      return { valid: true }

    default:
      return { valid: true }
  }
}

// ============================================
// FILE PATH VALIDATION
// ============================================

/**
 * Validate file path (local system)
 */
export function validateFilePath(filePath: string): ValidationResult {
  if (!filePath || filePath.trim() === '') {
    return { valid: false, error: '文件路径不能为空', field: 'filePath' }
  }

  const trimmed = filePath.trim()

  // Check for path traversal attacks
  if (/\.\.[\/\\]/.test(trimmed)) {
    return { valid: false, error: '文件路径不能包含 ../', field: 'filePath' }
  }

  // Check for invalid characters
  const invalidChars = /[<>:"|?*\x00-\x1f]/
  if (invalidChars.test(trimmed)) {
    return { valid: false, error: '文件路径包含非法字符', field: 'filePath' }
  }

  return { valid: true }
}

// ============================================
// VARIABLE NAME VALIDATION
// ============================================

/**
 * Validate variable name
 */
export function validateVariableName(name: string): ValidationResult {
  if (!name || name.trim() === '') {
    return { valid: false, error: '变量名不能为空', field: 'variableName' }
  }

  const trimmed = name.trim()

  // Must start with letter or underscore
  if (!/^[a-zA-Z_]/.test(trimmed)) {
    return { valid: false, error: '变量名必须以字母或下划线开头', field: 'variableName' }
  }

  // Only contain letters, numbers, and underscores
  if (!/^[a-zA-Z_][a-zA-Z0-9_]*$/.test(trimmed)) {
    return { valid: false, error: '变量名只能包含字母、数字和下划线', field: 'variableName' }
  }

  // Check for reserved keywords
  const reservedKeywords = ['true', 'false', 'null', 'undefined', 'NaN', 'Infinity']
  if (reservedKeywords.includes(trimmed)) {
    return { valid: false, error: `'${trimmed}' 是保留关键字`, field: 'variableName' }
  }

  return { valid: true }
}

// ============================================
// BATCH VALIDATION
// ============================================

/**
 * Validate multiple fields and return all errors
 */
export function validateFields(fields: Record<string, {
  value: any
  validator: (value: any) => ValidationResult
}>): {
  valid: boolean
  errors: Record<string, string>
} {
  const errors: Record<string, string> = {}

  for (const [fieldName, field] of Object.entries(fields)) {
    const result = field.validator(field.value)
    if (!result.valid && result.error) {
      errors[fieldName] = result.error
    }
  }

  return {
    valid: Object.keys(errors).length === 0,
    errors
  }
}

// ============================================
// SANITIZATION
// ============================================

/**
 * Sanitize user input to prevent XSS
 */
export function sanitizeInput(input: string): string {
  if (!input) return ''

  return input
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/\//g, '&#x2F;')
}

/**
 * Sanitize selector input (preserve syntax but remove dangerous content)
 */
export function sanitizeSelector(selector: string): string {
  if (!selector) return ''

  let sanitized = selector.trim()

  // Remove any script tags or event handlers
  sanitized = sanitized.replace(/<script[^>]*>.*?<\/script>/gi, '')
  sanitized = sanitized.replace(/on\w+\s*=\s*["'][^"']*["']/gi, '')

  // Remove javascript: protocol
  sanitized = sanitized.replace(/javascript:/gi, '')

  return sanitized
}
