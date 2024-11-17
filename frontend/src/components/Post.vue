<script setup>
import { computed } from 'vue'
import Tag from './Tag.vue'
import Like from './Like.vue'

const props = defineProps({
  username: String,
  createdAt: String,
  avatarUrl: String,
  content: String,
  tags: Array,
  likes: Number,
  liked: Boolean,
  onLikeClicked: Function,
  isLiking: Boolean
})

defineEmits(['tagClick'])

const secondRanges = {
  years: 3600 * 24 * 365,
  months: 3600 * 24 * 30,
  weeks: 3600 * 24 * 7,
  days: 3600 * 24,
  hours: 3600,
  minutes: 60,
  seconds: 1,
}

const createdAtFormatted = computed(() => {
  try {
    const createdAtDate = new Date(props.createdAt)
    const formatter = new Intl.RelativeTimeFormat('en')
    const seconds = (createdAtDate.getTime() - Date.now()) / 1000

    for (const key in secondRanges) {
      if (secondRanges[key] < Math.abs(seconds)) {
        const delta = seconds / secondRanges[key]
        return formatter.format(Math.round(delta), key)
      }
    }
  } catch {
    return null
  }
})
</script>

<template>
  <article class="wrapper">
    <div class="main">
      <header class="header">
        <img
          class="avatar"
          :src="props.avatarUrl"
          :alt="`avatar of ${props.username}`"
        />

        <div class="header-text">
          <h3 class="username">{{ props.username }}</h3>
          <div v-if="createdAtFormatted" class="created-at">
            {{ createdAtFormatted }}
          </div>
        </div>
      </header>

      <div class="body">{{ props.content }}</div>

      <footer class="footer">
        <ul v-if="props.tags?.length" class="tags">
          <li v-for="tag in props.tags" :key="tag" class="tag-item">
            <Tag class="tag" @click="$emit('tagClick', tag)" :value="tag" />
          </li>
        </ul>
        <Like class="like" :numberOfLikes="likes" :likedByUser="liked" :onLikeClicked="onLikeClicked" :isUpdating="isLiking"/>
      </footer>
    </div>
  </article>
</template>

<style scoped>
.wrapper {
  container-type: inline-size;
  container-name: post;
}

.main {
  border: 1px solid currentColor;
  padding: 20px;
  box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
}

@container post (max-width: 400px) {
  .main {
    padding: 16px;
    font-size: 14px;
  }
}

.header {
  display: flex;
  column-gap: 14px;
}

.avatar {
  min-inline-size: 54px;
  block-size: 54px;
  border-radius: 1000px;
  overflow: hidden;
}

@container post (max-width: 400px) {
  .avatar {
    min-inline-size: 40px;
    block-size: 40px;
  }
}

.header-text {
  inline-size: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  column-gap: 30px;
}

@container post (max-width: 400px) {
  .header-text {
    flex-direction: column;
    align-items: flex-start;
    row-gap: 6px;
  }
}

.username {
  font-size: 18px;
  font-weight: 500;
}

@container post (max-width: 400px) {
  .username {
    font-size: 16px;
  }
}

.created-at {
  color: #6b6b6b;
  font-size: 14px;
  align-self: flex-start;
}

@container post (max-width: 400px) {
  .created-at {
    font-size: 13px;
  }
}

.body {
  margin-block-start: 20px;
  line-height: 1.5;
}

.footer {
  display: flex;
  margin-block-start: 45px;
  column-gap: 30px;
  align-items: flex-end;
  justify-content: space-between;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  margin-block-start: 5px;
  column-gap: 16px;
  row-gap: 10px;
}
</style>