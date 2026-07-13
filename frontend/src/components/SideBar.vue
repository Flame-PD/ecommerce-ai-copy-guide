<template>
  <aside class="w-64 bg-gray-900 text-white min-h-screen flex flex-col">
    <div class="p-6">
      <h1 class="text-xl font-bold">商家后台</h1>
      <p class="text-xs text-gray-400 mt-1">AI电商运营管理中心</p>
    </div>
    <nav class="flex-1 px-4 space-y-2">
      <router-link v-for="item in menu" :key="item.path" :to="item.path" :class="isActive(item.path) ? 'bg-indigo-600' : 'hover:bg-gray-800'" class="flex items-center px-4 py-3 rounded-lg transition">
        <span>{{ item.name }}</span>
      </router-link>
    </nav>
    <div class="p-4 border-t border-gray-800">
      <div class="text-sm text-gray-400 mb-2">{{ auth.user?.nickname || auth.user?.username }}</div>
      <button @click="logout" class="w-full text-left text-red-400 hover:text-red-300 text-sm">退出登录</button>
    </div>
  </aside>
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const menu = [
  { name: '数据看板', path: '/merchant/dashboard' },
  { name: '商品管理', path: '/merchant/products' },
  { name: 'AI文案生成', path: '/merchant/ai-copy' },
  { name: '知识库管理', path: '/merchant/knowledge' },
  { name: '评论情感分析', path: '/merchant/reviews' },
  { name: '直播/短视频脚本', path: '/merchant/live-script' },
  { name: '订单管理', path: '/merchant/orders' },
]

function isActive(path) {
  return route.path === path
}

function logout() {
  auth.logout()
  router.push('/login')
}
</script>
