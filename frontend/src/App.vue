<script setup>
import { ref, onBeforeMount } from 'vue'
import Post from './components/Post.vue'
import Tag from './components/Tag.vue'

// Hardcoding for simplicity but this would normally be defined as an
// environment variable
const API_URL = 'http://localhost:5000'

const sorts = [
  { id: 'popular', text: 'Popular' },
  { id: 'latest', text: 'Latest' },
]

const tags = ref([])
const posts = ref([])
const featuredPost = ref(null)

const currentTag = ref(null)
const currentSortId = ref('latest')

const isLoading = ref(false)
// Rather than overload the posts data with state to track async liking/unliking
// we are creating a set to track that separately.
const isLikingPostSet = ref(new Set())

// Helper for api requests. It prevents exceptions from being thrown so we can
// more easily work with the resulting value. It also makes usage with
// `Promise.all` a lot easier.
async function apiRequest(path, options) {
  try {
    const response = await fetch(API_URL + path, options)
    if (!response.ok) {
      throw new Error(`Response status: ${response.status}`)
    }

    return response.json()
  } catch (exception) {
    return exception
  }
}

async function onLikePost(postId) {
    // Do not call API if already updating
    if(isLikingPostSet.value.has(postId)){
      return
    }
    isLikingPostSet.value.add(postId)
    const [maybeSuccess] = await Promise.all([
      apiRequest(`/like/${postId}`, { method: 'POST'}),
      sleep(250),
    ])
    if (maybeSuccess instanceof Error) {
      console.error(maybeSuccess)
    }

    await loadPosts(currentSortId.value, currentTag.value, true)
    isLikingPostSet.value.delete(postId)
}

// For creating artificial loading delays to avoid UI flickering
function sleep(duration) {
  return new Promise((resolve) => {
    setTimeout(resolve, duration)
  })
}

function setPosts(rawPosts) {
  posts.value = rawPosts.map(transformPost)

  if(featuredPost.value?.id){
    const updatedPost = rawPosts.find(post => post.id === featuredPost.value.id)
    if(updatedPost){
      featuredPost.value = transformPost(updatedPost)
    }
  }
}

function transformPost(post) {
  return {
    ...post,
    // Convert to camel case
    createdAt: post.created_at,
    // We are just doing this the easy way for the
    // sake of the demo.
    avatarUrl: `/images/avatar_${post.username}.jpg`,
  }
}

async function loadPosts(sortId, tag, disableScroll = false) {
  // When updating posts after a like, we do not want to scroll to the top
  if(!disableScroll){
    window.scrollTo({ top: 0 })
  }

  currentSortId.value = sortId
  currentTag.value = tag

  isLoading.value = true

  const [maybePosts] = await Promise.all([
    apiRequest(`/posts?sort=${sortId}${tag ? `&tag=${tag}` : ''}`),
    sleep(250),
  ])

  isLoading.value = false

  if (maybePosts instanceof Error) {
    console.error(maybePosts)
    return
  }

  setPosts(maybePosts)
}

onBeforeMount(async () => {
  const [maybePosts, maybeTags, maybeFeaturedPost] = await Promise.all([
    apiRequest(`/posts?sorting=${currentSortId.value}`),
    apiRequest('/tags'),
    apiRequest('/posts/featured'),
  ])

  if (maybePosts instanceof Error) {
    console.error(maybePosts)
  } else {
    setPosts(maybePosts)
  }

  if (maybeTags instanceof Error) {
    console.error(maybeTags)
  } else {
    tags.value = maybeTags
  }

  if (maybeFeaturedPost instanceof Error) {
    console.error(maybeFeaturedPost)
  } else {
    featuredPost.value = transformPost(maybeFeaturedPost)
  }
})
</script>

<template>
  <div class="root">
    <div v-if="isLoading" class="loading-bar">
      <div class="loading-bar-inner" />
    </div>

    <main class="main">
      <aside class="aside">
        <div v-if="tags.length" class="aside-section">
          <h2 class="aside-heading">Tags</h2>

          <ul class="tags">
            <li class="tag" v-for="tag in tags" :key="tag.id">
              <Tag
                :value="tag.name"
                :disabled="isLoading"
                :is-active="currentTag === tag.name"
                @click="loadPosts(currentSortId, tag.name)"
              />
            </li>
          </ul>
        </div>

        <div v-if="featuredPost" class="aside-section">
          <h2 class="aside-heading">Featured post</h2>

          <Post
            v-bind="{
              ...featuredPost,
              isLiking: isLikingPostSet.has(featuredPost.id),
              onLikeClicked: () => onLikePost(featuredPost.id)
            }"
            class="featured-post"
            @tagClick="loadPosts(currentSortId, $event)"
          />
        </div>
      </aside>

      <div class="listing">
        <div class="filter-buttons">
          <div class="filter-buttons-main">
            <button
              v-for="sort in sorts"
              :key="sort.id"
              :disabled="isLoading"
              :class="['filter-button', currentSortId === sort.id && 'active']"
              @click="loadPosts(sort.id, currentTag)"
            >
              {{ sort.text }}
            </button>
          </div>

          <button
            v-if="currentTag"
            class="filter-button tag"
            :disabled="isLoading"
            @click="loadPosts(currentSortId, null)"
          >
            <span class="sr-only">Remove tag</span>
            <span>#{{ currentTag }}</span>
            <svg viewBox="0 0 24 24" class="filter-button-icon">
              <path
                d="M11.9997 10.5865L16.9495 5.63672L18.3637 7.05093L13.4139 12.0007L18.3637 16.9504L16.9495 18.3646L11.9997 13.4149L7.04996 18.3646L5.63574 16.9504L10.5855 12.0007L5.63574 7.05093L7.04996 5.63672L11.9997 10.5865Z"
              ></path>
            </svg>
          </button>
        </div>

        <ul class="small-tags">
          <li class="small-tag" v-for="tag in tags" :key="tag.id">
            <Tag
              :value="tag.name"
              :disabled="isLoading"
              :is-active="currentTag === tag.name"
              @click="loadPosts(currentSortId, tag.name)"
            />
          </li>
        </ul>

        <div class="posts">
          <span v-if="!posts.length"> No posts found </span>
          <Post
            v-for="post in posts"
            :key="post.id"
            v-bind="{
              ...post,
              isLiking: isLikingPostSet.has(post.id),
              onLikeClicked: () => onLikePost(post.id)
            }"
            class="post"
            @tagClick="loadPosts(currentSortId, $event)"
          />
        </div>
      </div>
    </main>
  </div>
</template>

<!-- Reset -->
<style>
body {
  font-family: 'Work Sans', sans-serif;
  font-optical-sizing: auto;
  overflow-y: scroll;
}

button {
  appearance: none;
  border-radius: 0;
  text-align: inherit;
  background: none;
  box-shadow: none;
  padding: 0;
  cursor: pointer;
  border: none;
  color: inherit;
  font: inherit;
}

h1,
h2,
h3,
h4,
h5,
h6 {
  margin: 0;
}

ul {
  list-style-type: none;
  padding: 0;
  margin: 0;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
</style>

<style scoped>
@keyframes slide {
  to {
    transform: translateX(-50%);
  }
}

.loading-bar {
  inset-inline-start: 0;
  inset-block-start: 0;
  position: fixed;
  block-size: 10px;
  inline-size: 100%;
  overflow: hidden;
}

.loading-bar-inner {
  position: absolute;
  inset-inline-start: 0;
  inset-block-start: 0;
  block-size: 100%;
  inline-size: 200%;
  background: linear-gradient(
    90deg,
    #b4e1d8 0%,
    #4e9e8e 25%,
    #b4e1d8 50%,
    #4e9e8e 75%,
    #b4e1d8 100%
  );
  animation-name: slide;
  animation-duration: 1000ms;
  animation-timing-function: linear;
  animation-iteration-count: infinite;
  animation-play-state: running;
}

.root {
  display: flex;
  justify-content: center;
}

.main {
  inline-size: 1061px;
  max-inline-size: 100%;
  padding-inline: 52px;
  display: flex;
  flex-direction: row-reverse;
  justify-content: space-between;
}

@media (max-width: 1018px) {
  .main {
    padding-inline: 24px;
    justify-content: center;
  }
}

.aside {
  padding-block: 52px;
  display: flex;
  max-inline-size: 249px;
  inline-size: 100%;
  flex-direction: column;
  row-gap: 55px;
}

@media (max-width: 1018px) {
  .aside {
    display: none;
  }
}

.aside-section {
  display: flex;
  flex-direction: column;
  row-gap: 24px;
}

.aside-heading {
  font-weight: 500;
  font-size: 20px;
}

.tags {
  display: flex;
  flex-direction: column;
  row-gap: 12px;
}

.listing {
  padding-block: 52px;
  max-inline-size: 578px;
  inline-size: 100%;
}

@media (max-width: 623px) {
  .listing {
    padding-block: 24px;
  }
}

.filter-buttons {
  display: flex;
  column-gap: 9px;
}

.filter-buttons-main {
  display: flex;
  padding: 2px;
  background-color: black;
  column-gap: 2px;
}

.filter-button {
  padding: 9px 15px;
  font-weight: 500;
  font-size: 14px;
  background-color: white;
  display: flex;
  align-items: center;
  column-gap: 0.5em;
}

.filter-button.active,
.filter-button.tag,
.filter-button:hover,
.filter-button:focus-visible,
.filter-button:active {
  background-color: black;
  color: white;
}

.filter-button-icon {
  fill: currentColor;
  inline-size: 1em;
}

.small-tags {
  display: none;
}

@media (max-width: 1018px) {
  .small-tags {
    display: flex;
    flex-wrap: wrap;
    margin-block-start: 24px;
    column-gap: 16px;
    row-gap: 10px;
  }
}

.posts {
  margin-block-start: 52px;
  display: flex;
  flex-direction: column;
  row-gap: 52px;
}

@media (max-width: 1018px) {
  .posts {
    margin-block-start: 24px;
  }
}

@media (max-width: 623px) {
  .posts {
    row-gap: 24px;
  }
}
</style>