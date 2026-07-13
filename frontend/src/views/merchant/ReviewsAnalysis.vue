<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-800 mb-6">评论情感分析</h2>
    <div class="bg-white rounded-xl shadow-sm p-6 mb-6">
      <div class="flex flex-col md:flex-row gap-4">
        <select v-model="productId" class="border rounded-lg px-4 py-2 flex-1">
          <option value="">选择商品查看统计</option>
          <option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }}</option>
        </select>
        <button @click="loadStats" class="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700">查看统计</button>
      </div>
    </div>
    <div v-if="stats" class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
      <div class="bg-white rounded-xl shadow-sm p-6"><p class="text-sm text-gray-500">好评</p><p class="text-2xl font-bold text-green-600">{{ stats.positive }}</p></div>
      <div class="bg-white rounded-xl shadow-sm p-6"><p class="text-sm text-gray-500">中评</p><p class="text-2xl font-bold text-yellow-500">{{ stats.neutral }}</p></div>
      <div class="bg-white rounded-xl shadow-sm p-6"><p class="text-sm text-gray-500">差评</p><p class="text-2xl font-bold text-red-500">{{ stats.negative }}</p></div>
      <div class="bg-white rounded-xl shadow-sm p-6"><p class="text-sm text-gray-500">平均评分</p><p class="text-2xl font-bold text-indigo-600">{{ stats.avg_rating }}</p></div>
    </div>
    <div v-if="stats" class="bg-white rounded-xl shadow-sm p-6 mb-6">
      <p class="text-sm text-gray-600 mb-2">正面关键词：{{ stats.positive_keywords?.join('、') || '无' }}</p>
      <p class="text-sm text-gray-600">负面关键词：{{ stats.negative_keywords?.join('、') || '无' }}</p>
    </div>
    <div class="bg-white rounded-xl shadow-sm p-6">
      <h3 class="font-bold text-lg mb-4">上传评论文件分析</h3>
      <div class="flex flex-col md:flex-row gap-4">
        <select v-model="uploadProductId" class="border rounded-lg px-4 py-2">
          <option value="">不关联商品</option>
          <option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }}</option>
        </select>
        <input type="file" @change="upload" accept=".txt,.md,.xlsx,.docx" class="border rounded-lg px-3 py-2" />
      </div>
      <pre v-if="uploadResult" class="mt-4 bg-gray-50 p-4 rounded-lg text-sm whitespace-pre-wrap">{{ JSON.stringify(uploadResult, null, 2) }}</pre>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api/axios'

const products = ref([])
const productId = ref('')
const uploadProductId = ref('')
const stats = ref(null)
const uploadResult = ref(null)

async function loadProducts() {
  const res = await api.get('/products?status=')
  products.value = res.data
}

async function loadStats() {
  if (!productId.value) return
  const res = await api.get(`/reviews/stats/${productId.value}`)
  stats.value = res.data
}

async function upload(e) {
  const file = e.target.files[0]
  if (!file) return
  const formData = new FormData()
  formData.append('file', file)
  if (uploadProductId.value) formData.append('product_id', uploadProductId.value)
  const res = await api.post('/reviews/analyze', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
  uploadResult.value = res.data
}

onMounted(loadProducts)
</script>
