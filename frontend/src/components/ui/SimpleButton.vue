<template>
  <button
    :class="buttonClasses"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <span v-if="loading" class="simple-button__spinner"></span>
    <slot v-else />
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  variant?: 'primary' | 'default' | 'text' | 'danger'
  size?: 'small' | 'medium' | 'large'
  disabled?: boolean
  loading?: boolean
  block?: boolean
}

interface Emits {
  (e: 'click', event: MouseEvent): void
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  size: 'medium',
  disabled: false,
  loading: false,
  block: false
})

const emit = defineEmits<Emits>()

const buttonClasses = computed(() => [
  'simple-button',
  `simple-button--${props.variant}`,
  `simple-button--${props.size}`,
  {
    'simple-button--disabled': props.disabled || props.loading,
    'simple-button--loading': props.loading,
    'simple-button--block': props.block
  }
])

function handleClick(event: MouseEvent) {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>

<style scoped>
.simple-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-family);
  font-size: var(--font-size-body);
  font-weight: var(--font-weight-normal);
  border-radius: var(--radius-lg);
  border: none;
  cursor: pointer;
  transition: all var(--transition-base);
  white-space: nowrap;
  user-select: none;
  position: relative;
}

/* Sizes */
.simple-button--small {
  padding: 6px 12px;
  font-size: var(--font-size-sm);
}

.simple-button--medium {
  padding: 10px 20px;
  font-size: var(--font-size-base);
}

.simple-button--large {
  padding: 14px 28px;
  font-size: var(--font-size-lg);
}

/* Block */
.simple-button--block {
  width: 100%;
  display: flex;
}

/* Variants */
/* Primary 和 Default 使用相同的灰色样式 */
.simple-button--primary,
.simple-button--default {
  background: var(--color-bg-secondary);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
}

.simple-button--primary:hover:not(.simple-button--disabled),
.simple-button--default:hover:not(.simple-button--disabled) {
  background: var(--color-hover);
  border-color: var(--color-border-focus);
}

.simple-button--primary:active:not(.simple-button--disabled) {
  background: var(--color-hover);
}

.simple-button--text {
  background: transparent;
  color: var(--color-primary);
  padding: 8px 12px;
}

.simple-button--text:hover:not(.simple-button--disabled) {
  background: var(--color-hover);
}

.simple-button--danger {
  background: var(--color-error-bg);
  color: var(--color-error);
  border: 1px solid var(--color-error);
}

.simple-button--danger:hover:not(.simple-button--disabled) {
  background: var(--color-error);
  color: white;
}

/* Disabled state */
.simple-button--disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

/* Loading state */
.simple-button--loading {
  cursor: wait;
}

.simple-button__spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Focus state */
.simple-button:focus-visible {
  outline: 2px solid var(--color-focus);
  outline-offset: 2px;
}
</style>
