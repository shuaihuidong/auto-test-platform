<template>
  <div
    :class="stepCardClasses"
    draggable="true"
    @click="handleClick"
    @dragstart="handleDragStart"
  >
    <component :is="icon" class="step-card__icon" />
    <span class="step-card__label" :title="description || label">{{ label }}</span>
    <a-tooltip v-if="description" :title="description" placement="right">
      <InfoCircleOutlined class="step-card__info-icon" />
    </a-tooltip>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { InfoCircleOutlined } from '@ant-design/icons-vue'
import type { Component } from 'vue'

interface Props {
  label: string
  icon: Component
  description?: string
  selected?: boolean
  size?: 'small' | 'medium' | 'large'
}

interface Emits {
  (e: 'click'): void
  (e: 'dragstart', event: DragEvent): void
}

const props = withDefaults(defineProps<Props>(), {
  selected: false,
  size: 'medium'
})

const emit = defineEmits<Emits>()

const stepCardClasses = computed(() => [
  'step-card',
  `step-card--${props.size}`,
  {
    'step-card--selected': props.selected
  }
])

function handleClick() {
  emit('click')
}

function handleDragStart(event: DragEvent) {
  if (event.dataTransfer) {
    event.dataTransfer.setData('application/json', JSON.stringify({
      label: props.label,
      description: props.description
    }))
    event.dataTransfer.effectAllowed = 'copy'
  }
  emit('dragstart', event)
}
</script>

<style scoped>
.step-card {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-md);
  cursor: grab;
  transition: all var(--transition-fast);
  user-select: none;
}

.step-card:hover {
  border-color: var(--color-primary);
  background: var(--color-hover);
  box-shadow: var(--shadow-sm);
}

.step-card:active {
  cursor: grabbing;
}

.step-card--selected {
  border-color: var(--color-primary);
  background: var(--color-hover);
}

.step-card__icon {
  flex-shrink: 0;
  font-size: 16px;
  color: var(--color-primary);
}

.step-card--small .step-card__icon {
  font-size: 14px;
}

.step-card--large .step-card__icon {
  font-size: 18px;
}

.step-card__label {
  flex: 1;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  white-space: nowrap;
}

.step-card__info-icon {
  flex-shrink: 0;
  font-size: 12px;
  color: var(--color-text-tertiary);
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.step-card:hover .step-card__info-icon {
  opacity: 1;
}

.step-card__info-icon:hover {
  color: var(--color-primary);
}

/* Sizes */
.step-card--small {
  padding: var(--spacing-xs) var(--spacing-sm);
  font-size: var(--font-size-sm);
}

.step-card--large {
  padding: var(--spacing-md) var(--spacing-lg);
  font-size: var(--font-size-base);
}
</style>
