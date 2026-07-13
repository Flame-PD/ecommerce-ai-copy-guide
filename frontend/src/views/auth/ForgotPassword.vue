<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-600 to-purple-700 p-6">
    <div class="bg-white rounded-2xl shadow-xl w-full max-w-md p-8">
      <h2 class="text-2xl font-bold text-gray-800 mb-6 text-center">找回密码</h2>
      <div v-if="step === 1" class="space-y-4">
        <div>
          <label class="block text-sm text-gray-600 mb-1">账号</label>
          <input v-model="username" type="text" class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500" placeholder="请输入账号" />
        </div>
        <button @click="verifyAccount" :disabled="loading" class="w-full bg-indigo-600 text-white py-2.5 rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-60">
          {{ loading ? '校验中...' : '下一步' }}
        </button>
      </div>
      <div v-else class="space-y-4">
        <p class="text-sm text-gray-600">账号：{{ username }}</p>
        <div>
          <label class="block text-sm text-gray-600 mb-1">新密码</label>
          <input v-model="newPassword" type="password" class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500" placeholder="至少6位" />
        </div>
        <div>
          <label class="block text-sm text-gray-600 mb-1">确认新密码</label>
          <input v-model="confirmPassword" type="password" class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500" placeholder="再次输入新密码" />
        </div>
        <button @click="resetPassword" :disabled="loading" class="w-full bg-indigo-600 text-white py-2.5 rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-60">
          {{ loading ? '重置中...' : '重置密码' }}
        </button>
      </div>
      <p v-if="error" class="text-red-500 text-sm text-center mt-4">{{ error }}</p>
      <p v-if="success" class="text-green-600 text-sm text-center mt-4">密码重置成功，请登录</p>
      <div class="mt-6 text-center text-sm text-gray-500">
        <router-link to="/login" class="text-indigo-600 hover:underline">返回登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../api/axios'

const router = useRouter()
const step = ref(1)
const username = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')
const success = ref(false)

async function verifyAccount() {
  if (!username.value) {
    error.value = '请输入账号'
    return
  }
  loading.value = true
  error.value = ''
  try {
    await api.post('/auth/forgot-password', { username: username.value, new_password: '' })
    step.value = 2
  } catch (e) {
    error.value = e.response?.data?.detail || '账号不存在'
  } finally {
    loading.value = false
  }
}

async function resetPassword() {
  if (newPassword.value.length < 6) {
    error.value = '密码至少6位'
    return
  }
  if (newPassword.value !== confirmPassword.value) {
    error.value = '两次密码不一致'
    return
  }
  loading.value = true
  error.value = ''
  try {
    await api.post('/auth/reset-password', { username: username.value, new_password: newPassword.value })
    success.value = true
    setTimeout(() => router.push('/login'), 1000)
  } catch (e) {
    error.value = e.response?.data?.detail || '重置失败'
  } finally {
    loading.value = false
  }
}
</script>
