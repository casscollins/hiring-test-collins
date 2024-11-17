<script setup>
defineProps({
  isActive: Boolean,
  value: String,
})
</script>

<template>
  <button :class="['tag', isActive && 'active']" v-text="`#${value}`" />
</template>

<style scoped>
.tag {
  font-weight: 500;
  color: #374747;
}

.tag:hover,
.tag:focus-visible,
.tag:active,
.tag.active {
  text-decoration: underline;
}
</style>
