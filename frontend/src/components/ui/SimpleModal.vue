<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="modelValue"
        class="simple-modal-backdrop"
        @click="handleBackdropClick"
      >
        <div
          :class="modalClasses"
          @click.stop
        >
          <div v-if="$slots.header || title" class="simple-modal__header">
            <slot name="header">
              <div class="simple-modal__header-content">
                <h3 class="simple-modal__title">{{ title }}</h3>
                <p v-if="subtitle" class="simple-modal__subtitle">{{ subtitle }}</p>
              </div>
            </slot>
            <button
              v-if="closable"
              class="simple-modal__close"
              @click="handleClose"
            >
              ×
            </button>
          </div>

          <div class="simple-modal__body">
            <slot />
          </div>

          <div v-if="$slots.footer" class="simple-modal__footer">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, watch, onMounted, onUnmounted } from 'vue'

interface Props {
  modelValue: boolean
  title?: string
  subtitle?: string
  size?: 'small' | 'medium' | 'large' | 'full'
  closable?: boolean
  maskClosable?: boolean
  escClosable?: boolean
  centered?: boolean
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'open'): void
  (e: 'close'): void
  (e: 'before-close', done: () => void): void
}

const props = withDefaults(defineProps<Props>(), {
  size: 'medium',
  closable: true,
  maskClosable: true,
  escClosable: true,
  centered: true
})

const emit = defineEmits<Emits>()

const modalClasses = computed(() => [
  'simple-modal',
  `simple-modal--${props.size}`,
  {
    'simple-modal--centered': props.centered
  }
])

function handleBackdropClick() {
  if (props.maskClosable) {
    handleClose()
  }
}

function handleClose() {
  emit('before-close', () => {
    emit('update:modelValue', false)
    emit('close')
  })
}

function handleEscKey(event: KeyboardEvent) {
  if (props.escClosable && event.key === 'Escape' && props.modelValue) {
    handleClose()
  }
}

// Watch for open/close
watch(() => props.modelValue, (newValue) => {
  if (newValue) {
    emit('open')
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})

// Mount/unmount handlers
onMounted(() => {
  document.addEventListener('keydown', handleEscKey)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleEscKey)
  document.body.style.overflow = ''
})
</script>

<style scoped>
.simple-modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--color-bg-overlay);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal);
  padding: var(--spacing-lg);
}

.simple-modal {
  background: var(--color-bg-primary);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  max-height: calc(100vh - var(--spacing-2xl));
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Sizes */
.simple-modal--small {
  width: 400px;
}

.simple-modal--medium {
  width: 560px;
}

.simple-modal--large {
  width: 800px;
}

.simple-modal--full {
  width: 100%;
  height: 100%;
  max-height: 100vh;
  border-radius: 0;
}

/* Centered */
.simple-modal--centered {
  margin: auto;
}

/* Header */
.simple-modal__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: var(--spacing-lg) var(--spacing-xl);
  border-bottom: 1px solid var(--color-border-light);
}

.simple-modal__header-content {
  flex: 1;
}

.simple-modal__title {
  margin: 0;
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.simple-modal__subtitle {
  margin: var(--spacing-xs) 0 0 0;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.simple-modal__close {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md);
  background: transparent;
  border: none;
  color: var(--color-text-tertiary);
  font-size: 24px;
  line-height: 1;
  cursor: pointer;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
}

.simple-modal__close:hover {
  background: var(--color-hover-subtle);
  color: var(--color-text-primary);
}

/* Body */
.simple-modal__body {
  flex: 1;
  padding: var(--spacing-xl);
  overflow-y: auto;
}

/* Footer */
.simple-modal__footer {
  padding: var(--spacing-lg) var(--spacing-xl);
  border-top: 1px solid var(--color-border-light);
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-sm);
}

/* Transitions */
.modal-enter-active,
.modal-leave-active {
  transition: opacity var(--transition-base);
}

.modal-enter-active .simple-modal,
.modal-leave-active .simple-modal {
  transition: transform var(--transition-base), opacity var(--transition-base);
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .simple-modal,
.modal-leave-to .simple-modal {
  transform: scale(0.95);
  opacity: 0;
}
</style>
