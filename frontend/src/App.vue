<template>
  <a-config-provider :locale="zhCN">
    <router-view />
  </a-config-provider>
</template>

<script setup lang="ts">
import zhCN from 'ant-design-vue/es/locale/zh_CN'
import 'dayjs/locale/zh-cn'

// Import global styles
import '@/styles/global.css'
</script>

<style>
/* ============================================
   STARRY SKY BLUE THEME
   Global styles override for Ant Design
   ============================================ */

/* Reset & Base */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC',
              'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif;
  font-size: 14px;
  line-height: 1.5;
  color: var(--color-text-primary, #E5E7EB);
  background: var(--color-bg-primary, #0B1026);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  min-height: 100vh;
}

/* ============================================
   ANTD DESIGN OVERRIDES - STARRY SKY BLUE
   Transforming Ant Design components to dark blue theme
   ============================================ */

/* Layout */
:deep(.ant-layout) {
  background: var(--color-bg-secondary, #121936);
}

:deep(.ant-layout-header) {
  background: var(--color-bg-elevated, #1E2A5C);
  border-bottom: 1px solid var(--color-border, #1E2A5C);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

:deep(.ant-layout-content) {
  background: var(--color-bg-secondary, #121936);
}

:deep(.ant-layout-sider) {
  background: var(--color-bg-elevated, #1E2A5C);
  border-right: 1px solid var(--color-border, #1E2A5C);
}

:deep(.ant-menu) {
  background: transparent;
  border-right: none;
}

:deep(.ant-menu-item) {
  color: var(--color-text-secondary, #9CA3AF);
  border-radius: var(--radius-md, 6px);
  margin: 2px 0;
}

:deep(.ant-menu-item:hover) {
  color: var(--color-text-primary, #E5E7EB);
  background: var(--color-hover, #1E2A5C);
}

:deep(.ant-menu-item-selected) {
  color: var(--color-text-primary, #E5E7EB);
  background: var(--color-hover, #1E2A5C);
}

:deep(.ant-menu-item .anticon) {
  color: inherit;
}

/* Card */
:deep(.ant-card) {
  background: var(--color-bg-elevated, #1E2A5C);
  border: 1px solid var(--color-border, #1E2A5C);
  border-radius: var(--radius-lg, 8px);
  box-shadow: none;
}

:deep(.ant-card-hoverable:hover) {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
  border-color: var(--color-border, #1E2A5C);
}

:deep(.ant-card-head) {
  background: var(--color-bg-elevated, #1E2A5C);
  border-bottom: 1px solid var(--color-border-light, #1A2452);
  border-radius: var(--radius-lg, 8px) var(--radius-lg, 8px) 0 0;
}

:deep(.ant-card-head-title) {
  color: var(--color-text-primary, #E5E7EB);
  font-weight: var(--font-weight-semibold, 600);
}

:deep(.ant-card-body) {
  color: var(--color-text-primary, #E5E7EB);
}

:deep(.ant-card-bordered) {
  border: 1px solid var(--color-border, #1E2A5C);
}

/* Table */
:deep(.ant-table) {
  color: var(--color-text-primary, #E5E7EB);
}

:deep(.ant-table-thead > tr > th) {
  background: var(--color-bg-tertiary, #1A2452);
  color: var(--color-text-secondary, #9CA3AF);
  font-weight: var(--font-weight-medium, 500);
  border-bottom: 1px solid var(--color-border, #1E2A5C);
}

:deep(.ant-table-tbody > tr > td) {
  border-bottom: 1px solid var(--color-border-light, #1A2452);
  color: var(--color-text-primary, #E5E7EB);
}

:deep(.ant-table-tbody > tr:hover > td) {
  background: var(--color-hover, #1E2A5C);
}

:deep(.ant-table-placeholder) {
  color: var(--color-text-tertiary, #6B7280);
}

/* Button - Gray background with black text */
:deep(.ant-btn) {
  height: auto;
  padding: 10px 20px;
  border-radius: var(--radius-lg, 8px);
  font-weight: var(--font-weight-normal, 400);
  border: 1px solid #D1D5DB;
  background: #E5E7EB;
  color: #1F2937;
  box-shadow: none;
  transition: all var(--transition-base, 0.2s);
}

:deep(.ant-btn:hover) {
  border-color: #9CA3AF;
  background: #D1D5DB;
  color: #1F2937;
}

:deep(.ant-btn-primary) {
  background: #E5E7EB;
  border-color: #D1D5DB;
  color: #1F2937;
}

:deep(.ant-btn-primary:hover) {
  background: #D1D5DB;
  border-color: #9CA3AF;
  color: #1F2937;
}

:deep(.ant-btn-primary:active) {
  background: #9CA3AF;
}

:deep(.ant-btn-default) {
  background: #E5E7EB;
  border-color: #D1D5DB;
  color: #1F2937;
}

:deep(.ant-btn-default:hover) {
  background: #D1D5DB;
  border-color: #9CA3AF;
  color: #1F2937;
}

:deep(.ant-btn-text) {
  background: #E5E7EB;
  border-color: #D1D5DB;
  color: #1F2937;
}

:deep(.ant-btn-text:hover) {
  background: #D1D5DB;
  border-color: #9CA3AF;
  color: #1F2937;
}

:deep(.ant-btn-link) {
  background: #E5E7EB;
  border-color: #D1D5DB;
  color: #1F2937;
}

:deep(.ant-btn-link:hover) {
  background: #D1D5DB;
  border-color: #9CA3AF;
  color: #1F2937;
}

:deep(.ant-btn-dangerous) {
  background: #E5E7EB;
  border-color: #D1D5DB;
  color: #1F2937;
}

:deep(.ant-btn-dangerous:hover) {
  background: #D1D5DB;
  border-color: #9CA3AF;
  color: #1F2937;
}

:deep(.ant-btn-sm) {
  padding: 6px 12px;
  font-size: 12px;
}

:deep(.ant-btn-lg) {
  padding: 14px 28px;
  font-size: 16px;
}

/* Input */
:deep(.ant-input),
:deep(.ant-input-number) {
  border: 1px solid var(--color-border, #1E2A5C);
  border-radius: 0;
  background: var(--color-bg-tertiary, #1A2452);
  color: var(--color-text-primary, #E5E7EB);
  padding: 10px 12px;
  font-size: 14px;
  transition: border-color var(--transition-base, 0.2s);
}

:deep(.ant-input::placeholder),
:deep(.ant-input-number-input::placeholder) {
  color: var(--color-text-disabled, #4B5563);
}

:deep(.ant-input:hover),
:deep(.ant-input-number:hover) {
  border-color: var(--color-primary, #E5E7EB);
}

:deep(.ant-input:focus),
:deep(.ant-input-number:focus),
:deep(.ant-input-number-focused) {
  border-color: var(--color-primary, #E5E7EB);
  box-shadow: none;
  outline: none;
}

:deep(.ant-input-disabled),
:deep(.ant-input-number-disabled) {
  background: var(--color-bg-secondary, #121936);
  color: var(--color-text-disabled, #4B5563);
  cursor: not-allowed;
}

:deep(.ant-input-affix-wrapper) {
  border: 1px solid var(--color-border, #1E2A5C);
  border-radius: 0;
  background: var(--color-bg-tertiary, #1A2452);
  padding: 0;
}

:deep(.ant-input-affix-wrapper-focused) {
  border-color: var(--color-primary, #E5E7EB);
  box-shadow: none;
}

:deep(.ant-input-affix-wrapper:hover) {
  border-color: var(--color-primary, #E5E7EB);
}

/* Select */
:deep(.ant-select-selector) {
  border: 1px solid var(--color-border, #1E2A5C) !important;
  border-radius: var(--radius-md, 6px) !important;
  background: var(--color-bg-tertiary, #1A2452) !important;
  color: var(--color-text-primary, #E5E7EB) !important;
}

:deep(.ant-select:hover .ant-select-selector) {
  border-color: var(--color-primary, #E5E7EB) !important;
}

:deep(.ant-select-focused .ant-select-selector) {
  border-color: var(--color-primary, #E5E7EB) !important;
  box-shadow: none !important;
}

:deep(.ant-select-selection-placeholder) {
  color: var(--color-text-disabled, #4B5563);
}

:deep(.ant-select-dropdown) {
  background: var(--color-bg-elevated, #1E2A5C);
  border: 1px solid var(--color-border, #1E2A5C);
  border-radius: var(--radius-md, 6px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5);
}

:deep(.ant-select-item) {
  color: var(--color-text-primary, #E5E7EB);
}

:deep(.ant-select-item-option-selected) {
  background: var(--color-hover, #1E2A5C);
  color: var(--color-text-primary, #E5E7EB);
}

:deep(.ant-select-item-option-active) {
  background: var(--color-hover, #1E2A5C);
}

/* Checkbox */
:deep(.ant-checkbox-wrapper) {
  color: var(--color-text-primary, #E5E7EB);
}

:deep(.ant-checkbox-inner) {
  border-radius: var(--radius-xs, 2px);
  border-color: var(--color-border, #1E2A5C);
  background: var(--color-bg-tertiary, #1A2452);
}

:deep(.ant-checkbox:hover .ant-checkbox-inner) {
  border-color: var(--color-primary, #E5E7EB);
}

:deep(.ant-checkbox-checked .ant-checkbox-inner) {
  background: var(--color-primary, #E5E7EB);
  border-color: var(--color-primary, #E5E7EB);
}

:deep(.ant-checkbox-checked .ant-checkbox-inner::after) {
  border-color: var(--color-bg-primary, #0B1026);
}

:deep(.ant-checkbox-indeterminate .ant-checkbox-inner) {
  background: var(--color-primary, #E5E7EB);
  border-color: var(--color-primary, #E5E7EB);
}

:deep(.ant-checkbox-indeterminate .ant-checkbox-inner::after) {
  background-color: var(--color-bg-primary, #0B1026);
}

/* Radio */
:deep(.ant-radio-wrapper) {
  color: var(--color-text-primary, #E5E7EB);
}

:deep(.ant-radio-inner) {
  border-color: var(--color-border, #1E2A5C);
  background: var(--color-bg-tertiary, #1A2452);
}

:deep(.ant-radio:hover .ant-radio-inner) {
  border-color: var(--color-primary, #E5E7EB);
}

:deep(.ant-radio-checked .ant-radio-inner) {
  border-color: var(--color-primary, #E5E7EB);
  background: var(--color-bg-tertiary, #1A2452);
}

:deep(.ant-radio-checked .ant-radio-inner::after) {
  background: var(--color-primary, #E5E7EB);
}

/* Switch */
:deep(.ant-switch) {
  background: var(--color-border, #1E2A5C);
}

:deep(.ant-switch-checked) {
  background: var(--color-primary, #E5E7EB);
}

/* Modal */
:deep(.ant-modal-content) {
  background: var(--color-bg-elevated, #1E2A5C);
  border-radius: var(--radius-xl, 12px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
}

:deep(.ant-modal-header) {
  background: var(--color-bg-elevated, #1E2A5C);
  border-bottom: 1px solid var(--color-border-light, #1A2452);
  border-radius: var(--radius-xl, 12px) var(--radius-xl, 12px) 0 0;
}

:deep(.ant-modal-title) {
  color: var(--color-text-primary, #E5E7EB);
  font-weight: var(--font-weight-semibold, 600);
}

:deep(.ant-modal-close) {
  color: var(--color-text-tertiary, #6B7280);
}

:deep(.ant-modal-close:hover) {
  color: var(--color-text-primary, #E5E7EB);
}

:deep(.ant-modal-body) {
  color: var(--color-text-primary, #E5E7EB);
}

:deep(.ant-modal-footer) {
  border-top: 1px solid var(--color-border-light, #1A2452);
}

/* Form */
:deep(.ant-form-item-label > label) {
  color: var(--color-text-primary, #E5E7EB);
  font-weight: var(--font-weight-medium, 500);
  height: auto;
}

:deep(.ant-form-item-explain-error) {
  color: var(--color-error, #EF4444);
}

:deep(.ant-form-item-has-error .ant-input),
:deep(.ant-form-item-has-error .ant-input-affix-wrapper),
:deep(.ant-form-item-has-error .ant-select-selector) {
  border-color: var(--color-error, #EF4444);
}

:deep(.ant-form-item-has-error .ant-input:focus),
:deep(.ant-form-item-has-error .ant-input-affix-wrapper-focused),
:deep(.ant-form-item-has-error .ant-select-focused .ant-select-selector) {
  border-color: var(--color-error, #EF4444);
  box-shadow: none;
}

/* Alert */
:deep(.ant-alert) {
  border-radius: var(--radius-md, 6px);
  border: 1px solid;
}

:deep(.ant-alert-info) {
  background: var(--color-info-bg, rgba(59, 130, 246, 0.15));
  border-color: rgba(59, 130, 246, 0.3);
}

:deep(.ant-alert-success) {
  background: var(--color-success-bg, rgba(16, 185, 129, 0.15));
  border-color: rgba(16, 185, 129, 0.3);
}

:deep(.ant-alert-warning) {
  background: var(--color-warning-bg, rgba(245, 158, 11, 0.15));
  border-color: rgba(245, 158, 11, 0.3);
}

:deep(.ant-alert-error) {
  background: var(--color-error-bg, rgba(239, 68, 68, 0.15));
  border-color: rgba(239, 68, 68, 0.3);
}

:deep(.ant-alert-message) {
  color: var(--color-text-primary, #E5E7EB);
}

:deep(.ant-alert-description) {
  color: var(--color-text-secondary, #9CA3AF);
}

/* Message */
:deep(.ant-message-notice-content) {
  background: var(--color-bg-elevated, #1E2A5C);
  border-radius: var(--radius-lg, 8px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5);
  color: var(--color-text-primary, #E5E7EB);
}

/* Notification */
:deep(.ant-notification-notice) {
  background: var(--color-bg-elevated, #1E2A5C);
  border-radius: var(--radius-lg, 8px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
  border: 1px solid var(--color-border, #1E2A5C);
}

:deep(.ant-notification-notice-message) {
  color: var(--color-text-primary, #E5E7EB);
}

:deep(.ant-notification-notice-description) {
  color: var(--color-text-secondary, #9CA3AF);
}

/* Popover */
:deep(.ant-popover-inner) {
  background: var(--color-bg-elevated, #1E2A5C);
  border-radius: var(--radius-md, 6px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5);
}

:deep(.ant-popover-arrow) {
  display: none;
}

:deep(.ant-popover-inner-content) {
  color: var(--color-text-primary, #E5E7EB);
}

/* Tooltip */
:deep(.ant-tooltip-inner) {
  background: rgba(11, 16, 38, 0.95);
  border-radius: var(--radius-sm, 4px);
  color: white;
}

:deep(.ant-tooltip-arrow-content) {
  background: rgba(11, 16, 38, 0.95);
}

/* Dropdown */
:deep(.ant-dropdown-menu) {
  background: var(--color-bg-elevated, #1E2A5C);
  border-radius: var(--radius-md, 6px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5);
  border: 1px solid var(--color-border, #1E2A5C);
}

:deep(.ant-dropdown-menu-item) {
  color: var(--color-text-primary, #E5E7EB);
  border-radius: var(--radius-sm, 4px);
}

:deep(.ant-dropdown-menu-item:hover) {
  background: var(--color-hover, #1E2A5C);
}

:deep(.ant-dropdown-menu-item-selected) {
  background: var(--color-hover, #1E2A5C);
  color: var(--color-text-primary, #E5E7EB);
}

:deep(.ant-dropdown-menu-item-divider) {
  background: var(--color-border-light, #1A2452);
}

/* Tag */
:deep(.ant-tag) {
  background: #F3F4F6;
  border: 1px solid #E5E7EB;
  border-radius: var(--radius-sm, 4px);
  color: #1F2937;
}

/* Badge */
:deep(.ant-badge-count) {
  background: var(--color-error, #EF4444);
  border-radius: var(--radius-full, 9999px);
  box-shadow: none;
}

/* Tabs */
:deep(.ant-tabs-tab) {
  color: var(--color-text-secondary, #9CA3AF);
  padding: 12px 16px;
}

:deep(.ant-tabs-tab:hover) {
  color: var(--color-text-primary, #E5E7EB);
}

:deep(.ant-tabs-tab-active) {
  color: var(--color-text-primary, #E5E7EB);
}

:deep(.ant-tabs-ink-bar) {
  background: var(--color-primary, #E5E7EB);
}

:deep(.ant-tabs-content) {
  color: var(--color-text-primary, #E5E7EB);
}

/* Divider */
:deep(.ant-divider) {
  border-color: var(--color-border-light, #1A2452);
}

:deep(.ant-divider-vertical) {
  border-color: var(--color-border-light, #1A2452);
}

/* Spin */
:deep(.ant-spin-dot-item) {
  background: var(--color-primary, #E5E7EB);
}

/* Progress */
:deep(.ant-progress-bg) {
  background: linear-gradient(90deg, var(--color-primary, #E5E7EB) 0%, #D1D5DB 100%);
}

:deep(.ant-progress-success-bg) {
  background: var(--color-success, #10B981);
}

/* Pagination */
:deep(.ant-pagination-item) {
  border: 1px solid var(--color-border, #1E2A5C);
  border-radius: var(--radius-md, 6px);
  background: var(--color-bg-tertiary, #1A2452);
}

:deep(.ant-pagination-item a) {
  color: var(--color-text-primary, #E5E7EB);
}

:deep(.ant-pagination-item:hover) {
  border-color: var(--color-primary, #E5E7EB);
}

:deep(.ant-pagination-item:hover a) {
  color: var(--color-text-primary, #E5E7EB);
}

:deep(.ant-pagination-item-active) {
  background: var(--color-primary, #E5E7EB);
  border-color: var(--color-primary, #E5E7EB);
}

:deep(.ant-pagination-item-active a) {
  color: #1F2937;
}

:deep(.ant-pagination-prev),
:deep(.ant-pagination-next) {
  border-radius: var(--radius-md, 6px);
}

:deep(.ant-pagination-disabled:hover) {
  border-color: var(--color-border, #1E2A5C);
}

/* Descriptions */
:deep(.ant-descriptions-item-label) {
  color: var(--color-text-secondary, #9CA3AF);
  background: var(--color-bg-tertiary, #1A2452);
}

:deep(.ant-descriptions-item-content) {
  color: var(--color-text-primary, #E5E7EB);
}

/* Empty */
:deep(.ant-empty-description) {
  color: var(--color-text-tertiary, #6B7280);
}

/* Space */
:deep(.ant-space) {
  display: flex;
}

/* Drawer */
:deep(.ant-drawer-content) {
  background: var(--color-bg-elevated, #1E2A5C);
}

:deep(.ant-drawer-header) {
  background: var(--color-bg-elevated, #1E2A5C);
  border-bottom: 1px solid var(--color-border-light, #1A2452);
}

:deep(.ant-drawer-title) {
  color: var(--color-text-primary, #E5E7EB);
}

:deep(.ant-drawer-body) {
  color: var(--color-text-primary, #E5E7EB);
}

/* Steps */
:deep(.ant-steps-item-title) {
  color: var(--color-text-primary, #E5E7EB) !important;
}

:deep(.ant-steps-item-description) {
  color: var(--color-text-secondary, #9CA3AF) !important;
}

:deep(.ant-steps-item-process .ant-steps-item-icon) {
  background: var(--color-primary, #E5E7EB);
  border-color: var(--color-primary, #E5E7EB);
}

:deep(.ant-steps-item-finish .ant-steps-item-icon) {
  border-color: var(--color-primary, #E5E7EB);
}

:deep(.ant-steps-item-finish .ant-steps-item-title) {
  color: var(--color-text-primary, #E5E7EB) !important;
}

/* Timeline */
:deep(.ant-timeline-item-tail) {
  border-color: var(--color-border-light, #1A2452);
}

:deep(.ant-timeline-item-head) {
  background: var(--color-bg-primary, #0B1026);
  border-color: var(--color-border, #1E2A5C);
}

/* Collapse */
:deep(.ant-collapse) {
  background: transparent;
  border: none;
}

:deep(.ant-collapse-item) {
  border: 1px solid var(--color-border-light, #1A2452);
  border-radius: var(--radius-md, 6px);
  margin-bottom: 8px;
}

:deep(.ant-collapse-header) {
  color: var(--color-text-primary, #E5E7EB);
}

:deep(.ant-collapse-content-box) {
  color: var(--color-text-primary, #E5E7EB);
}

/* Rate */
:deep(.ant-rate-star) {
  color: var(--color-border, #1E2A5C);
}

:deep(.ant-rate-star-full) {
  color: var(--color-warning, #F59E0B);
}

/* Slider */
:deep(.ant-slider-rail) {
  background: var(--color-border-light, #1A2452);
}

:deep(.ant-slider-track) {
  background: var(--color-primary, #E5E7EB);
}

:deep(.ant-slider-handle) {
  border: 2px solid var(--color-primary, #E5E7EB);
}

/* Transfer */
:deep(.ant-transfer-list) {
  background: var(--color-bg-tertiary, #1A2452);
  border: 1px solid var(--color-border, #1E2A5C);
  border-radius: var(--radius-md, 6px);
}

:deep(.ant-transfer-list-header) {
  color: var(--color-text-secondary, #9CA3AF);
  border-bottom: 1px solid var(--color-border-light, #1A2452);
}

:deep(.ant-transfer-list-body) {
  background: var(--color-bg-tertiary, #1A2452);
}

/* Tree */
:deep(.ant-tree-node-selected .ant-tree-node-content-wrapper) {
  background: var(--color-hover, #1E2A5C);
  color: var(--color-text-primary, #E5E7EB);
}

:deep(.ant-tree-node-content-wrapper:hover) {
  background: var(--color-hover, #1E2A5C);
}

/* Breadcrumb */
:deep(.ant-breadcrumb-link) {
  color: var(--color-text-secondary, #9CA3AF);
}

:deep(.ant-breadcrumb-separator) {
  color: var(--color-text-tertiary, #6B7280);
}

:deep(.ant-breadcrumb-item:last-child .ant-breadcrumb-link) {
  color: var(--color-text-primary, #E5E7EB);
}

/* Calendar */
:deep(.ant-picker-calendar-header) {
  color: var(--color-text-primary, #E5E7EB);
}

:deep(.ant-picker-calendar-date-value) {
  color: var(--color-text-primary, #E5E7EB);
}

/* DatePicker */
:deep(.ant-picker) {
  border: 1px solid var(--color-border, #1E2A5C);
  border-radius: var(--radius-md, 6px);
}

:deep(.ant-picker:hover) {
  border-color: var(--color-primary, #E5E7EB);
}

:deep(.ant-picker-focused) {
  border-color: var(--color-primary, #E5E7EB);
  box-shadow: none;
}

:deep(.ant-picker-dropdown) {
  background: var(--color-bg-elevated, #1E2A5C);
  border: 1px solid var(--color-border, #1E2A5C);
  border-radius: var(--radius-md, 6px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5);
}

:deep(.ant-picker-cell-in-view) {
  color: var(--color-text-primary, #E5E7EB);
}

:deep(.ant-picker-cell-selected) {
  background: var(--color-primary, #E5E7EB);
}

:deep(.ant-picker-cell-selected .ant-picker-cell-inner) {
  background: var(--color-primary, #E5E7EB);
  color: #1F2937;
}

:deep(.ant-picker-today .ant-picker-cell-inner) {
  border-color: var(--color-primary, #E5E7EB);
}

/* TimePicker */
:deep(.ant-picker-panel-container) {
  background: var(--color-bg-elevated, #1E2A5C);
}

/* Upload */
:deep(.ant-upload) {
  color: var(--color-text-primary, #E5E7EB);
}

:deep(.ant-upload-drag) {
  background: var(--color-bg-secondary, #121936);
  border: 2px dashed var(--color-border, #1E2A5C);
  border-radius: var(--radius-lg, 8px);
}

:deep(.ant-upload-drag:hover) {
  border-color: var(--color-primary, #E5E7EB);
}

:deep(.ant-upload-drag-container) {
  color: var(--color-text-secondary, #9CA3AF);
}

/* Result */
:deep(.ant-result-title) {
  color: var(--color-text-primary, #E5E7EB);
}

:deep(.ant-result-subtitle) {
  color: var(--color-text-secondary, #9CA3AF);
}

/* Statistic */
:deep(.ant-statistic-title) {
  color: var(--color-text-secondary, #9CA3AF);
}

:deep(.ant-statistic-content) {
  color: var(--color-text-primary, #E5E7EB);
}

/* Skeleton */
:deep(.ant-skeleton-content) {
  background: var(--color-bg-tertiary, #1A2452);
}

:deep(.ant-skeleton-input) {
  background: var(--color-bg-secondary, #121936);
}

:deep(.ant-skeleton-button) {
  background: var(--color-bg-secondary, #121936);
}

/* QR Code */
:deep(.ant-qrcode) {
  border: 1px solid var(--color-border-light, #1A2452);
  border-radius: var(--radius-md, 6px);
  padding: 8px;
}

/* Tour */
:deep(.ant-tour-content) {
  background: var(--color-bg-elevated, #1E2A5C);
  border-radius: var(--radius-lg, 8px);
}

:deep(.ant-tour-title) {
  color: var(--color-text-primary, #E5E7EB);
}

:deep(.ant-tour-description) {
  color: var(--color-text-secondary, #9CA3AF);
}

/* Float Button */
:deep(.ant-float-btn-body) {
  background: var(--color-primary, #E5E7EB);
  border-radius: var(--radius-full, 9999px);
}

:deep(.ant-float-btn-body:hover) {
  background: var(--color-primary-hover, #D1D5DB);
}

/* Segmented */
:deep(.ant-segmented) {
  background: var(--color-bg-secondary, #121936);
  border-radius: var(--radius-md, 6px);
  padding: 2px;
}

:deep(.ant-segmented-item) {
  border-radius: var(--radius-sm, 4px);
  color: var(--color-text-secondary, #9CA3AF);
}

:deep(.ant-segmented-item-selected) {
  background: var(--color-bg-tertiary, #1A2452);
  color: var(--color-text-primary, #E5E7EB);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

/* AutoComplete */
:deep(.ant-auto-complete) {
  width: 100%;
}

/* Mentions */
:deep(.ant-mentions) {
  border: 1px solid var(--color-border, #1E2A5C);
  border-radius: var(--radius-md, 6px);
  background: var(--color-bg-tertiary, #1A2452);
}

/* TreeSelect */
:deep(.ant-tree-select-dropdown) {
  background: var(--color-bg-elevated, #1E2A5C);
  border: 1px solid var(--color-border, #1E2A5C);
}

/* Cascader */
:deep(.ant-cascader-dropdown) {
  background: var(--color-bg-elevated, #1E2A5C);
  border: 1px solid var(--color-border, #1E2A5C);
}

/* Row Selection */
:deep(.ant-table-selection-column) {
  width: 50px;
}

:deep(.ant-table-selection) {
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Filter */
:deep(.ant-table-filter-trigger) {
  color: var(--color-text-tertiary, #6B7280);
}

:deep(.ant-table-filter-trigger:hover) {
  color: var(--color-text-primary, #E5E7EB);
}

:deep(.ant-table-filter-trigger.active) {
  color: var(--color-text-primary, #E5E7EB);
}

/* Sorter */
:deep(.ant-table-column-sorter-up),
:deep(.ant-table-column-sorter-down) {
  color: var(--color-text-tertiary, #6B7280);
}

:deep(.ant-table-column-sorter-up.active),
:deep(.ant-table-column-sorter-down.active) {
  color: var(--color-text-primary, #E5E7EB);
}

/* Expand Icon */
:deep(.ant-table-expand-icon) {
  color: var(--color-text-tertiary, #6B7280);
}

/* Scrollbar - Dark Theme */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: var(--color-border, #1E2A5C);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--color-text-tertiary, #6B7280);
}

/* Selection */
::selection {
  background: #1890ff;
  color: #ffffff;
}

::-moz-selection {
  background: #1890ff;
  color: #ffffff;
}

/* Focus Visible */
:focus-visible {
  outline: 2px solid var(--color-primary, #E5E7EB);
  outline-offset: 2px;
}

/* Print Styles */
@media print {
  body {
    background: white;
    color: black;
  }

  :deep(.ant-layout),
  :deep(.ant-card) {
    background: white;
    box-shadow: none;
    border: 1px solid #ddd;
  }
}
</style>
