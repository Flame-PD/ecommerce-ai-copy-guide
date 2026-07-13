<template>
  <div class="space-y-6">
    <div class="bg-white rounded-xl shadow-sm p-6">
      <h2 class="text-xl font-bold text-gray-800 mb-4">个人信息</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm text-gray-600 mb-1">账号</label>
          <input v-model="user.username" disabled class="w-full border rounded-lg px-3 py-2 bg-gray-100" />
        </div>
        <div>
          <label class="block text-sm text-gray-600 mb-1">昵称</label>
          <input v-model="user.nickname" class="w-full border rounded-lg px-3 py-2" />
        </div>
      </div>
    </div>

    <div class="bg-white rounded-xl shadow-sm p-6">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-xl font-bold text-gray-800">我的收藏</h2>
      </div>
      <div v-if="favorites.length === 0" class="text-gray-500 text-sm">暂无收藏</div>
      <div v-else class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div v-for="f in favorites" :key="f.id" @click="$router.push(`/product/${f.product_id}`)" class="bg-gray-50 rounded-lg p-3 cursor-pointer hover:shadow">
          <p class="text-sm font-medium">商品ID：{{ f.product_id }}</p>
        </div>
      </div>
    </div>

    <div class="bg-white rounded-xl shadow-sm p-6">
      <h2 class="text-xl font-bold text-gray-800 mb-4">浏览记录</h2>
      <div v-if="history.length === 0" class="text-gray-500 text-sm">暂无记录</div>
      <div v-else class="space-y-2">
        <div v-for="h in history" :key="h.id" @click="$router.push(`/product/${h.product.id}`)" class="flex justify-between text-sm border-b pb-2 cursor-pointer">
          <span>{{ h.product.ai_title || h.product.name }}</span>
          <span class="text-gray-400">{{ new Date(h.created_at).toLocaleString() }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import api from '../../api/axios'

const auth = useAuthStore()
const user = ref({ ...auth.user })
const favorites = ref([])
const history = ref([])

async function loadData() {
  const favRes = await api.get('/products/my/favorites')
  favorites.value = favRes.data
  const hisRes = await api.get('/products/my/browse-history')
  history.value = hisRes.data
}

onMounted(() => {
  auth.fetchUser()
  loadData()
})
</script>
