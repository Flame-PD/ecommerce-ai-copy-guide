<template>
  <nav class="bg-white shadow-sm sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16 items-center">
        <div class="flex items-center space-x-8">
          <router-link to="/home" class="text-xl font-bold text-indigo-600">AI电商助手</router-link>
          <div class="hidden md:flex space-x-4">
            <router-link to="/home" class="text-gray-600 hover:text-indigo-600 px-3 py-2 rounded-md text-sm font-medium">首页</router-link>
            <router-link to="/orders" class="text-gray-600 hover:text-indigo-600 px-3 py-2 rounded-md text-sm font-medium">我的订单</router-link>
            <router-link to="/cart" class="text-gray-600 hover:text-indigo-600 px-3 py-2 rounded-md text-sm font-medium">购物车</router-link>
            <router-link to="/profile" class="text-gray-600 hover:text-indigo-600 px-3 py-2 rounded-md text-sm font-medium">个人中心</router-link>
          </div>
        </div>
        <div class="flex items-center space-x-4">
          <span class="text-sm text-gray-600">{{ auth.user?.nickname || auth.user?.username }}</span>
          <button @click="logout" class="text-sm text-red-500 hover:text-red-700">退出</button>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()

function logout() {
  auth.logout()
  router.push('/login')
}
</script>
