<template>
  <div class="min-h-screen flex bg-gradient-to-br from-indigo-600 to-purple-700">
    <div class="hidden md:flex w-1/2 flex-col justify-center px-16 text-white">
      <h1 class="text-4xl font-bold mb-4">电商AI商品文案生成与智能导购助手</h1>
      <p class="text-lg opacity-90 mb-8">为商家提供AI文案、RAG导购、评论分析；为用户提供智能购物、AI咨询、模拟下单。</p>
      <ul class="space-y-3 opacity-90">
        <li>✦ AI自动生成商品文案与直播脚本</li>
        <li>✦ 基于私有知识库的智能导购问答</li>
        <li>✦ 评论情感分析与商品优化建议</li>
        <li>✦ 统一登录，商家/用户双端闭环</li>
      </ul>
    </div>
    <div class="w-full md:w-1/2 flex items-center justify-center p-6">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-md p-8">
        <h2 class="text-2xl font-bold text-gray-800 mb-6 text-center">欢迎登录</h2>
        <div class="flex justify-center mb-6 space-x-2 bg-gray-100 rounded-lg p-1">
          <button @click="form.role = 'user'" :class="form.role === 'user' ? 'bg-white shadow text-indigo-600' : 'text-gray-500'" class="flex-1 py-2 rounded-md text-sm font-medium transition">普通用户</button>
          <button @click="form.role = 'merchant'" :class="form.role === 'merchant' ? 'bg-white shadow text-indigo-600' : 'text-gray-500'" class="flex-1 py-2 rounded-md text-sm font-medium transition">商家管理员</button>
        </div>
        <div class="space-y-4">
          <div>
            <label class="block text-sm text-gray-600 mb-1">账号</label>
            <input v-model="form.username" type="text" class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500" placeholder="请输入账号" />
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">密码</label>
            <input v-model="form.password" type="password" class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500" placeholder="请输入密码" />
          </div>
          <button @click="handleLogin" :disabled="loading" class="w-full bg-indigo-600 text-white py-2.5 rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-60">
            {{ loading ? '登录中...' : '登录' }}
          </button>
          <p v-if="error" class="text-red-500 text-sm text-center">{{ error }}</p>
        </div>
        <div class="mt-6 text-center text-sm text-gray-500 space-x-4">
          <router-link to="/register" class="text-indigo-600 hover:underline">用户注册</router-link>
          <router-link to="/forgot-password" class="text-indigo-600 hover:underline">找回密码</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const loading = ref(false)
const error = ref('')
const form = reactive({ username: '', password: '', role: 'user' })

async function handleLogin() {
  if (!form.username || !form.password) {
    error.value = '请输入账号和密码'
    return
  }
  loading.value = true
  error.value = ''
  try {
    await auth.login(form)
    router.push(form.role === 'merchant' ? '/merchant' : '/home')
  } catch (e) {
    error.value = e.response?.data?.detail || '登录失败'
  } finally {
    loading.value = false
  }
}
</script>
