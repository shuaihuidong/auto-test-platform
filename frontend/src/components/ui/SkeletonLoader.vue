<template>
  <div :class="skeletonClasses">
    <div v-for="i in count" :key="i" class="skeleton-item">
      <!-- Avatar variant -->
      <div v-if="variant === 'avatar'" class="skeleton-avatar"></div>

      <!-- Button variant -->
      <div v-else-if="variant === 'button'" class="skeleton-button"></div>

      <!-- Input variant -->
      <div v-else-if="variant === 'input'" class="skeleton-input"></div>

      <!-- Text/default variant -->
      <template v-else>
        <div v-if="showAvatar" class="skeleton-avatar"></div>
        <div class="skeleton-content">
          <div class="skeleton-title"></div>
          <div class="skeleton-text"></div>
          <div v-if="i % 2 === 0" class="skeleton-text skeleton-text--narrow"></div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  count?: number
  variant?: 'text' | 'avatar' | 'button' | 'input' | 'custom'
  showAvatar?: boolean
  animated?: boolean
  size?: 'small' | 'medium' | 'large'
}

const props = withDefaults(defineProps<Props>(), {
  count: 3,
  variant: 'text',
  showAvatar: false,
  animated: true,
  size: 'medium'
})

const skeletonClasses = computed(() => [
  'skeleton-loader',
  `skeleton-loader--${props.size}`,
  {
    'skeleton-loader--animated': props.animated
  }
])
</script>

<style scoped>
.skeleton-loader {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.skeleton-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.skeleton-avatar {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  border-radius: var(--radius-full);
  background: linear-gradient(
    90deg,
    var(--color-bg-secondary) 25%,
    var(--color-hover-subtle) 50%,
    var(--color-bg-secondary) 75%
  );
  background-size: 200% 100%;
}

.skeleton-loader--small .skeleton-avatar {
  width: 32px;
  height: 32px;
}

.skeleton-loader--large .skeleton-avatar {
  width: 48px;
  height: 48px;
}

.skeleton-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.skeleton-title {
  height: 16px;
  width: 60%;
  border-radius: var(--radius-sm);
  background: linear-gradient(
    90deg,
    var(--color-bg-secondary) 25%,
    var(--color-hover-subtle) 50%,
    var(--color-bg-secondary) 75%
  );
  background-size: 200% 100%;
}

.skeleton-loader--small .skeleton-title {
  height: 14px;
}

.skeleton-loader--large .skeleton-title {
  height: 18px;
}

.skeleton-text {
  height: 14px;
  width: 100%;
  border-radius: var(--radius-sm);
  background: linear-gradient(
    90deg,
    var(--color-bg-secondary) 25%,
    var(--color-hover-subtle) 50%,
    var(--color-bg-secondary) 75%
  );
  background-size: 200% 100%;
}

.skeleton-text--narrow {
  width: 80%;
}

.skeleton-button {
  height: 40px;
  width: 120px;
  border-radius: var(--radius-lg);
  background: linear-gradient(
    90deg,
    var(--color-bg-secondary) 25%,
    var(--color-hover-subtle) 50%,
    var(--color-bg-secondary) 75%
  );
  background-size: 200% 100%;
}

.skeleton-loader--small .skeleton-button {
  height: 32px;
  width: 100px;
}

.skeleton-loader--large .skeleton-button {
  height: 48px;
  width: 140px;
}

.skeleton-input {
  height: 40px;
  width: 100%;
  border-radius: var(--radius-sm);
  background: linear-gradient(
    90deg,
    var(--color-bg-secondary) 25%,
    var(--color-hover-subtle) 50%,
    var(--color-bg-secondary) 75%
  );
  background-size: 200% 100%;
}

.skeleton-loader--small .skeleton-input {
  height: 32px;
}

.skeleton-loader--large .skeleton-input {
  height: 48px;
}

/* Animation */
.skeleton-loader--animated .skeleton-avatar,
.skeleton-loader--animated .skeleton-title,
.skeleton-loader--animated .skeleton-text,
.skeleton-loader--animated .skeleton-button,
.skeleton-loader--animated .skeleton-input {
  animation: skeleton-loading 1.5s ease-in-out infinite;
}

@keyframes skeleton-loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
</style>
