<template>
  <div>
    <div class="bg-white rounded-xl p-6 shadow-sm mb-6">
      <div class="flex flex-col md:flex-row md:items-center gap-4">
        <input v-model="keyword" @keydown.enter="loadProducts" type="text" placeholder="搜索商品" class="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500" />
        <select v-model="category" @change="loadProducts" class="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500">
          <option value="">全部分类</option>
          <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
        </select>
        <button @click="loadProducts" class="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700">搜索</button>
      </div>
    </div>
    <div v-if="loading" class="text-center py-20 text-gray-500">加载中...</div>
    <div v-else-if="products.length === 0" class="text-center py-20 text-gray-500">暂无商品</div>
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      <ProductCard v-for="p in products" :key="p.id" :product="p" @click="goDetail(p.id)" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../api/axios'
import ProductCard from '../../components/ProductCard.vue'

const router = useRouter()
const products = ref([])
const categories = ref([])
const keyword = ref('')
const category = ref('')
const loading = ref(false)

async function loadProducts() {
  loading.value = true
  try {
    const params = { status: 'on' }
    if (keyword.value) params.keyword = keyword.value
    if (category.value) params.category = category.value
    const res = await api.get('/products', { params })
    products.value = res.data
  } finally {
    loading.value = false
  }
}

async function loadCategories() {
  try {
    const res = await api.get('/products/categories/list')
    categories.value = res.data
  } catch (e) {}
}

function goDetail(id) {
  router.push(`/product/${id}`)
}

onMounted(() => {
  loadCategories()
  loadProducts()
})
</script>
