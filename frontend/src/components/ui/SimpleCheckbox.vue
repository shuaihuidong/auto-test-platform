<template>
  <label :class="checkboxWrapperClasses">
    <input
      :checked="modelValue"
      :disabled="disabled"
      :indeterminate="indeterminate"
      type="checkbox"
      class="simple-checkbox__input"
      @change="handleChange"
    />

    <span class="simple-checkbox__box">
      <span v-if="modelValue && !indeterminate" class="simple-checkbox__check">✓</span>
      <span v-else-if="indeterminate" class="simple-checkbox__indeterminate">−</span>
    </span>

    <span v-if="$slots.default || label" class="simple-checkbox__label">
      <slot>{{ label }}</slot>
    </span>
  </label>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  modelValue?: boolean
  label?: string
  disabled?: boolean
  indeterminate?: boolean
  size?: 'small' | 'medium' | 'large'
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'change', value: boolean): void
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  indeterminate: false,
  size: 'medium'
})

const emit = defineEmits<Emits>()

const checkboxWrapperClasses = computed(() => [
  'simple-checkbox',
  `simple-checkbox--${props.size}`,
  {
    'simple-checkbox--checked': props.modelValue,
    'simple-checkbox--disabled': props.disabled,
    'simple-checkbox--indeterminate': props.indeterminate
  }
])

function handleChange(event: Event) {
  const target = event.target as HTMLInputElement
  const value = target.checked
  emit('update:modelValue', value)
  emit('change', value)
}
</script>

<style scoped>
.simple-checkbox {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-sm);
  cursor: pointer;
  user-select: none;
}

.simple-checkbox--disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.simple-checkbox__input {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.simple-checkbox__box {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-bg-primary);
  transition: all var(--transition-base);
}

/* Sizes */
.simple-checkbox--small .simple-checkbox__box {
  width: 16px;
  height: 16px;
}

.simple-checkbox--medium .simple-checkbox__box {
  width: 18px;
  height: 18px;
}

.simple-checkbox--large .simple-checkbox__box {
  width: 20px;
  height: 20px;
}

/* Hover state */
.simple-checkbox:hover .simple-checkbox__box {
  border-color: var(--color-primary);
}

/* Checked state */
.simple-checkbox--checked .simple-checkbox__box {
  background: var(--color-primary);
  border-color: var(--color-primary);
}

.simple-checkbox__check {
  color: white;
  font-size: 12px;
  font-weight: bold;
}

.simple-checkbox--small .simple-checkbox__check {
  font-size: 10px;
}

.simple-checkbox--large .simple-checkbox__check {
  font-size: 14px;
}

/* Indeterminate state */
.simple-checkbox--indeterminate .simple-checkbox__box {
  background: var(--color-primary);
  border-color: var(--color-primary);
}

.simple-checkbox__indeterminate {
  color: white;
  font-size: 12px;
  font-weight: bold;
}

.simple-checkbox--small .simple-checkbox__indeterminate {
  font-size: 10px;
}

.simple-checkbox--large .simple-checkbox__indeterminate {
  font-size: 14px;
}

/* Label */
.simple-checkbox__label {
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  line-height: 1;
}

/* Focus state */
.simple-checkbox__input:focus-visible + .simple-checkbox__box {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}
</style>
