<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-800 mb-6">AI文案生成</h2>
    <div class="bg-white rounded-xl shadow-sm p-6 mb-6">
      <div class="flex flex-col md:flex-row gap-4">
        <select v-model="productId" class="border rounded-lg px-4 py-2 flex-1">
          <option value="">请选择商品</option>
          <option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }}</option>
        </select>
        <select v-model="style" class="border rounded-lg px-4 py-2">
          <option value="professional">专业</option>
          <option value="concise">简洁</option>
          <option value="premium">高端</option>
          <option value="lively">活泼</option>
          <option value="promotional">促销</option>
          <option value="lifestyle">生活化</option>
        </select>
        <button @click="generate" :disabled="!productId || loading" class="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-60">生成文案</button>
      </div>
    </div>
    <div v-if="result" class="bg-white rounded-xl shadow-sm p-6">
      <h3 class="font-bold text-lg mb-3">生成结果</h3>
      <pre class="bg-gray-50 p-4 rounded-lg text-sm text-gray-700 whitespace-pre-wrap">{{ result }}</pre>
      <div class="mt-4 flex justify-end space-x-2">
        <button @click="copy" class="px-4 py-2 border rounded-lg hover:bg-gray-50">复制</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api/axios'

const products = ref([])
const productId = ref('')
const style = ref('professional')
const result = ref('')
const loading = ref(false)

async function loadProducts() {
  const res = await api.get('/products?status=')
  products.value = res.data
}

async function generate() {
  loading.value = true
  try {
    const res = await api.post('/ai/copy', { product_id: productId.value, style: style.value })
    result.value = res.data.result
  } finally {
    loading.value = false
  }
}

function copy() {
  navigator.clipboard.writeText(result.value)
  alert('已复制')
}

onMounted(loadProducts)
</script>
