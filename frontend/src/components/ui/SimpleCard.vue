<template>
  <div :class="cardClasses" @click="handleClick">
    <div v-if="$slots.header || title" class="simple-card__header">
      <slot name="header">
        <h3 class="simple-card__title">{{ title }}</h3>
      </slot>
    </div>

    <div v-if="$slots.default" class="simple-card__body">
      <slot />
    </div>

    <div v-if="$slots.footer" class="simple-card__footer">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  title?: string
  hoverable?: boolean
  clickable?: boolean
  bordered?: boolean
  shadow?: 'none' | 'sm' | 'md' | 'lg'
  padding?: 'none' | 'sm' | 'md' | 'lg'
}

interface Emits {
  (e: 'click', event: MouseEvent): void
}

const props = withDefaults(defineProps<Props>(), {
  hoverable: false,
  clickable: false,
  bordered: true,
  shadow: 'sm',
  padding: 'md'
})

const emit = defineEmits<Emits>()

const cardClasses = computed(() => [
  'simple-card',
  `simple-card--shadow-${props.shadow}`,
  `simple-card--padding-${props.padding}`,
  {
    'simple-card--hoverable': props.hoverable,
    'simple-card--clickable': props.clickable,
    'simple-card--bordered': props.bordered
  }
])

function handleClick(event: MouseEvent) {
  if (props.clickable) {
    emit('click', event)
  }
}
</script>

<style scoped>
.simple-card {
  background: var(--color-bg-primary);
  border-radius: var(--radius-lg);
  transition: all var(--transition-base);
  overflow: hidden;
}

/* Border */
.simple-card--bordered {
  border: 1px solid var(--color-border-light);
}

/* Shadow */
.simple-card--shadow-none {
  box-shadow: none;
}

.simple-card--shadow-sm {
  box-shadow: var(--shadow-sm);
}

.simple-card--shadow-md {
  box-shadow: var(--shadow-md);
}

.simple-card--shadow-lg {
  box-shadow: var(--shadow-lg);
}

/* Hoverable */
.simple-card--hoverable:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

/* Clickable */
.simple-card--clickable {
  cursor: pointer;
}

.simple-card--clickable:hover {
  border-color: var(--color-primary);
}

/* Header */
.simple-card__header {
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--color-border-light);
}

.simple-card__title {
  margin: 0;
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

/* Body */
.simple-card__body {
  padding: var(--spacing-lg);
}

.simple-card--padding-none .simple-card__body {
  padding: 0;
}

.simple-card--padding-sm .simple-card__body {
  padding: var(--spacing-sm);
}

.simple-card--padding-md .simple-card__body {
  padding: var(--spacing-md);
}

.simple-card--padding-lg .simple-card__body {
  padding: var(--spacing-lg);
}

/* Footer */
.simple-card__footer {
  padding: var(--spacing-md) var(--spacing-lg);
  border-top: 1px solid var(--color-border-light);
}
</style>
