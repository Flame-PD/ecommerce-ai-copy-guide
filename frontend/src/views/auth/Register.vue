<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-600 to-purple-700 p-6">
    <div class="bg-white rounded-2xl shadow-xl w-full max-w-md p-8">
      <h2 class="text-2xl font-bold text-gray-800 mb-6 text-center">用户注册</h2>
      <div class="space-y-4">
        <div>
          <label class="block text-sm text-gray-600 mb-1">账号</label>
          <input v-model="form.username" type="text" class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500" placeholder="请输入账号" />
        </div>
        <div>
          <label class="block text-sm text-gray-600 mb-1">昵称</label>
          <input v-model="form.nickname" type="text" class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500" placeholder="请输入昵称" />
        </div>
        <div>
          <label class="block text-sm text-gray-600 mb-1">密码</label>
          <input v-model="form.password" type="password" class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500" placeholder="至少6位" />
        </div>
        <div>
          <label class="block text-sm text-gray-600 mb-1">确认密码</label>
          <input v-model="form.confirmPassword" type="password" class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500" placeholder="再次输入密码" />
        </div>
        <button @click="handleRegister" :disabled="loading" class="w-full bg-indigo-600 text-white py-2.5 rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-60">
          {{ loading ? '注册中...' : '注册' }}
        </button>
        <p v-if="error" class="text-red-500 text-sm text-center">{{ error }}</p>
        <p v-if="success" class="text-green-600 text-sm text-center">注册成功，请登录</p>
      </div>
      <div class="mt-6 text-center text-sm text-gray-500">
        <router-link to="/login" class="text-indigo-600 hover:underline">已有账号？去登录</router-link>
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
const success = ref(false)
const form = reactive({ username: '', nickname: '', password: '', confirmPassword: '' })

async function handleRegister() {
  if (!form.username || !form.password) {
    error.value = '请填写完整信息'
    return
  }
  if (form.password.length < 6) {
    error.value = '密码至少6位'
    return
  }
  if (form.password !== form.confirmPassword) {
    error.value = '两次密码不一致'
    return
  }
  loading.value = true
  error.value = ''
  try {
    await auth.register({ username: form.username, password: form.password, nickname: form.nickname })
    success.value = true
    setTimeout(() => router.push('/login'), 1000)
  } catch (e) {
    error.value = e.response?.data?.detail || '注册失败'
  } finally {
    loading.value = false
  }
}
</script>
