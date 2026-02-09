<template>
  <div :class="emptyStateClasses">
    <component :is="iconComponent" class="empty-state__icon" />
    <h3 v-if="title" class="empty-state__title">{{ title }}</h3>
    <p v-if="message" class="empty-state__message">{{ message }}</p>
    <div v-if="$slots.action" class="empty-state__action">
      <slot name="action" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Component } from 'vue'

// Default icons
import {
  FileTextOutlined,
  InboxOutlined,
  SearchOutlined,
  WarningOutlined,
  CloudServerOutlined,
  DatabaseOutlined,
  SettingOutlined,
  RobotOutlined
} from '@ant-design/icons-vue'

interface Props {
  icon?: string | Component
  title?: string
  message: string
  size?: 'small' | 'medium' | 'large'
  type?: 'default' | 'no-data' | 'no-results' | 'error' | 'loading' | 'no-connection'
}

const props = withDefaults(defineProps<Props>(), {
  size: 'medium',
  type: 'default'
})

const ICON_MAP: Record<string, Component> = {
  'file': FileTextOutlined,
  'inbox': InboxOutlined,
  'search': SearchOutlined,
  'warning': WarningOutlined,
  'server': CloudServerOutlined,
  'database': DatabaseOutlined,
  'setting': SettingOutlined,
  'robot': RobotOutlined
}

const iconComponent = computed(() => {
  if (typeof props.icon === 'string') {
    return ICON_MAP[props.icon] || InboxOutlined
  }
  return props.icon || getDefaultIconForType()
})

function getDefaultIconForType(): Component {
  switch (props.type) {
    case 'no-data':
      return InboxOutlined
    case 'no-results':
      return SearchOutlined
    case 'error':
      return WarningOutlined
    case 'loading':
      return RobotOutlined
    case 'no-connection':
      return CloudServerOutlined
    default:
      return FileTextOutlined
  }
}

const emptyStateClasses = computed(() => [
  'empty-state',
  `empty-state--${props.size}`,
  `empty-state--${props.type}`
])
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-2xl);
  text-align: center;
}

.empty-state--small {
  padding: var(--spacing-lg);
}

.empty-state--large {
  padding: var(--spacing-3xl);
}

.empty-state__icon {
  font-size: 48px;
  color: var(--color-text-tertiary);
  margin-bottom: var(--spacing-md);
  opacity: 0.5;
}

.empty-state--small .empty-state__icon {
  font-size: 32px;
  margin-bottom: var(--spacing-sm);
}

.empty-state--large .empty-state__icon {
  font-size: 64px;
  margin-bottom: var(--spacing-lg);
}

.empty-state__title {
  margin: 0 0 var(--spacing-sm) 0;
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.empty-state--small .empty-state__title {
  font-size: var(--font-size-base);
}

.empty-state--large .empty-state__title {
  font-size: var(--font-size-xl);
}

.empty-state__message {
  margin: 0 0 var(--spacing-md) 0;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  max-width: 400px;
}

.empty-state__action {
  margin-top: var(--spacing-md);
}

/* Type-specific styles */
.empty-state--error .empty-state__icon {
  color: var(--color-error);
}

.empty-state--loading .empty-state__icon {
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 0.5;
  }
  50% {
    opacity: 1;
  }
}
</style>
