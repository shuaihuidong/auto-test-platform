<template>
  <div
    ref="containerRef"
    :class="selectWrapperClasses"
    @click="toggleDropdown"
  >
    <label v-if="label" class="simple-select__label">
      {{ label }}
      <span v-if="required" class="simple-select__required">*</span>
    </label>

    <div class="simple-select__trigger">
      <span v-if="selectedLabel" class="simple-select__value">
        {{ selectedLabel }}
      </span>
      <span v-else class="simple-select__placeholder">
        {{ placeholder }}
      </span>
      <span class="simple-select__arrow" :class="{ 'simple-select__arrow--open': dropdownOpen }">
        ▼
      </span>
    </div>

    <Teleport to="body">
      <Transition name="dropdown">
        <div
          v-if="dropdownOpen"
          ref="dropdownRef"
          :class="dropdownClasses"
          :style="dropdownStyles"
        >
          <div
            v-for="option in options"
            :key="String(option.value)"
            :class="optionClasses(option)"
            @click.stop="selectOption(option)"
          >
            <slot name="option" :option="option">
              {{ option.label }}
            </slot>
          </div>
          <div v-if="options.length === 0" class="simple-select__empty">
            {{ emptyText }}
          </div>
        </div>
      </Transition>
    </Teleport>

    <span v-if="error" class="simple-select__error">
      {{ error }}
    </span>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'

export interface SelectOption {
  label: string
  value: string | number | boolean
  disabled?: boolean
}

interface Props {
  modelValue?: string | number | boolean | null
  options: SelectOption[]
  label?: string
  placeholder?: string
  emptyText?: string
  disabled?: boolean
  required?: boolean
  error?: string
  size?: 'small' | 'medium' | 'large'
}

interface Emits {
  (e: 'update:modelValue', value: string | number | boolean): void
  (e: 'change', value: string | number | boolean, option: SelectOption): void
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '请选择',
  emptyText: '暂无数据',
  disabled: false,
  required: false,
  size: 'medium'
})

const emit = defineEmits<Emits>()

const containerRef = ref<HTMLElement>()
const dropdownRef = ref<HTMLElement>()
const dropdownOpen = ref(false)
const dropdownPosition = ref({ top: '0px', left: '0px', width: '0px' })

const selectedOption = computed(() => {
  return props.options.find(opt => opt.value === props.modelValue)
})

const selectedLabel = computed(() => {
  return selectedOption.value?.label
})

const selectWrapperClasses = computed(() => [
  'simple-select',
  `simple-select--${props.size}`,
  {
    'simple-select--open': dropdownOpen.value,
    'simple-select--error': props.error,
    'simple-select--disabled': props.disabled
  }
])

const dropdownClasses = computed(() => [
  'simple-select__dropdown',
  `simple-select__dropdown--${props.size}`
])

const dropdownStyles = computed(() => ({
  top: dropdownPosition.value.top,
  left: dropdownPosition.value.left,
  width: dropdownPosition.value.width
}))

function optionClasses(option: SelectOption) {
  return [
    'simple-select__option',
    {
      'simple-select__option--selected': option.value === props.modelValue,
      'simple-select__option--disabled': option.disabled
    }
  ]
}

function toggleDropdown() {
  if (props.disabled) return
  dropdownOpen.value = !dropdownOpen.value
  if (dropdownOpen.value) {
    nextTick(updateDropdownPosition)
  }
}

function selectOption(option: SelectOption) {
  if (option.disabled) return
  emit('update:modelValue', option.value)
  emit('change', option.value, option)
  dropdownOpen.value = false
}

function updateDropdownPosition() {
  if (!containerRef.value || !dropdownRef.value) return

  const containerRect = containerRef.value.getBoundingClientRect()
  const dropdownHeight = dropdownRef.value.offsetHeight
  const windowHeight = window.innerHeight

  let top = containerRect.bottom + 4
  const shouldFlip = top + dropdownHeight > windowHeight - 20

  if (shouldFlip) {
    top = containerRect.top - dropdownHeight - 4
  }

  dropdownPosition.value = {
    top: `${top}px`,
    left: `${containerRect.left}px`,
    width: `${containerRect.width}px`
  }
}

function closeDropdown(event: MouseEvent) {
  if (dropdownOpen.value && containerRef.value) {
    const target = event.target as Node
    if (!containerRef.value.contains(target) && !dropdownRef.value?.contains(target)) {
      dropdownOpen.value = false
    }
  }
}

// Watch model value changes
watch(() => props.modelValue, () => {
  // Handle external value changes
})

// Click outside to close
onMounted(() => {
  document.addEventListener('click', closeDropdown)
  window.addEventListener('scroll', updateDropdownPosition, true)
  window.addEventListener('resize', updateDropdownPosition)
})

onUnmounted(() => {
  document.removeEventListener('click', closeDropdown)
  window.removeEventListener('scroll', updateDropdownPosition, true)
  window.removeEventListener('resize', updateDropdownPosition)
})

defineExpose({
  close: () => { dropdownOpen.value = false },
  open: () => {
    dropdownOpen.value = true
    nextTick(updateDropdownPosition)
  }
})
</script>

<style scoped>
.simple-select {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
  position: relative;
}

.simple-select__label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.simple-select__required {
  color: var(--color-error);
  margin-left: 2px;
}

.simple-select__trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px var(--spacing-md);
  background: var(--color-bg-primary);
  border-bottom: 1px solid var(--color-border);
  border-radius: 0;
  cursor: pointer;
  transition: border-color var(--transition-base);
  user-select: none;
}

.simple-select--open .simple-select__trigger,
.simple-select__trigger:hover {
  border-bottom-color: var(--color-primary);
}

.simple-select--disabled .simple-select__trigger {
  cursor: not-allowed;
  opacity: 0.5;
}

.simple-select--error .simple-select__trigger {
  border-bottom-color: var(--color-error);
}

.simple-select__value {
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
}

.simple-select__placeholder {
  font-size: var(--font-size-base);
  color: var(--color-text-disabled);
}

.simple-select__arrow {
  font-size: 10px;
  color: var(--color-text-tertiary);
  transition: transform var(--transition-fast);
}

.simple-select__arrow--open {
  transform: rotate(180deg);
}

/* Dropdown */
.simple-select__dropdown {
  position: fixed;
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  max-height: 250px;
  overflow-y: auto;
  z-index: var(--z-dropdown);
}

.simple-select__option {
  padding: 10px var(--spacing-md);
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.simple-select__option:hover:not(.simple-select__option--disabled) {
  background: var(--color-hover);
}

.simple-select__option--selected {
  color: var(--color-primary);
  font-weight: var(--font-weight-medium);
}

.simple-select__option--disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.simple-select__empty {
  padding: var(--spacing-lg);
  text-align: center;
  color: var(--color-text-tertiary);
  font-size: var(--font-size-sm);
}

/* Error message */
.simple-select__error {
  font-size: var(--font-size-xs);
  color: var(--color-error);
}

/* Sizes */
.simple-select--small .simple-select__trigger {
  padding: 6px var(--spacing-sm);
  font-size: var(--font-size-sm);
}

.simple-select--large .simple-select__trigger {
  padding: 14px var(--spacing-lg);
  font-size: var(--font-size-lg);
}

/* Dropdown transition */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all var(--transition-base);
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
