<template>
  <div v-if="product" class="bg-white rounded-xl shadow-sm p-6">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
      <div class="h-80 bg-gray-200 rounded-xl flex items-center justify-center overflow-hidden">
        <img v-if="product.image_url" :src="product.image_url" class="w-full h-full object-cover" />
        <span v-else class="text-gray-400">暂无图片</span>
      </div>
      <div>
        <h1 class="text-2xl font-bold text-gray-800">{{ product.ai_title || product.name }}</h1>
        <p class="text-red-500 text-2xl font-bold mt-4">¥{{ product.price }}</p>
        <p class="text-sm text-gray-500 mt-2">分类：{{ product.category }} | 库存：{{ product.stock }}</p>
        <div class="mt-4 flex flex-wrap gap-2" v-if="product.specs && product.specs.length">
          <button v-for="spec in product.specs" :key="spec" @click="selectedSpec = spec" :class="selectedSpec === spec ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-700'" class="px-3 py-1 rounded-md text-sm border">{{ spec }}</button>
        </div>
        <div class="mt-6 flex space-x-3">
          <button @click="addToCart" class="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700">加入购物车</button>
          <button @click="toggleFavorite" :class="favorited ? 'text-red-500 border-red-500' : 'text-gray-600 border-gray-300'" class="px-4 py-2 rounded-lg border hover:bg-gray-50">{{ favorited ? '已收藏' : '收藏' }}</button>
        </div>
      </div>
    </div>
    <div class="mt-8 border-t pt-6">
      <h3 class="font-bold text-lg mb-3">AI生成详情</h3>
      <div class="bg-indigo-50 rounded-lg p-4 text-sm text-gray-700 space-y-2">
        <p><span class="font-semibold">核心卖点：</span>{{ product.ai_selling_points || '暂无' }}</p>
        <p><span class="font-semibold">详情文案：</span>{{ product.ai_detail || '暂无' }}</p>
        <p><span class="font-semibold">广告语：</span>{{ product.ai_slogan || '暂无' }}</p>
      </div>
    </div>
    <div class="mt-8 border-t pt-6">
      <h3 class="font-bold text-lg mb-3">用户评价</h3>
      <div v-if="reviews.length === 0" class="text-gray-500 text-sm">暂无评价</div>
      <div v-else class="space-y-3">
        <div v-for="r in reviews" :key="r.id" class="border-b pb-3">
          <div class="flex items-center justify-between">
            <span class="text-yellow-500">{{ '★'.repeat(r.rating) }}{{ '☆'.repeat(5 - r.rating) }}</span>
            <span class="text-xs text-gray-400">{{ r.sentiment }}</span>
          </div>
          <p class="text-sm text-gray-700 mt-1">{{ r.content }}</p>
        </div>
      </div>
    </div>
  </div>
  <div v-else class="text-center py-20 text-gray-500">加载中...</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../api/axios'

const route = useRoute()
const product = ref(null)
const reviews = ref([])
const selectedSpec = ref('')
const favorited = ref(false)

async function loadProduct() {
  const res = await api.get(`/products/${route.params.id}`)
  product.value = res.data
  if (res.data.specs && res.data.specs.length) selectedSpec.value = res.data.specs[0]
  await api.post(`/products/${route.params.id}/browse`)
}

async function loadReviews() {
  const res = await api.get(`/reviews/product/${route.params.id}`)
  reviews.value = res.data
}

function addToCart() {
  const cart = JSON.parse(localStorage.getItem('cart') || '[]')
  const item = {
    product_id: product.value.id,
    name: product.value.name,
    price: product.value.price,
    spec: selectedSpec.value,
    quantity: 1,
    image_url: product.value.image_url
  }
  const exist = cart.find(i => i.product_id === item.product_id && i.spec === item.spec)
  if (exist) {
    exist.quantity += 1
  } else {
    cart.push(item)
  }
  localStorage.setItem('cart', JSON.stringify(cart))
  alert('已加入购物车')
}

async function toggleFavorite() {
  const res = await api.post(`/products/${route.params.id}/favorite`)
  favorited.value = res.data.favorited
}

onMounted(async () => {
  await loadProduct()
  await loadReviews()
})
</script>
