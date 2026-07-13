<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-gray-800">商品管理</h2>
      <div class="space-x-2">
        <button @click="showForm = true" class="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700">新增商品</button>
        <button @click="exportProducts" class="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700">导出</button>
        <input type="file" @change="importProducts" accept=".json,.xlsx" class="hidden" ref="fileInput" />
        <button @click="$refs.fileInput.click()" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">导入</button>
      </div>
    </div>
    <div class="bg-white rounded-xl shadow-sm overflow-hidden">
      <table class="w-full text-sm text-left">
        <thead class="bg-gray-50 text-gray-600">
          <tr>
            <th class="px-4 py-3">ID</th>
            <th>名称</th>
            <th>分类</th>
            <th>价格</th>
            <th>库存</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in products" :key="p.id" class="border-b hover:bg-gray-50">
            <td class="px-4 py-3">{{ p.id }}</td>
            <td>{{ p.name }}</td>
            <td>{{ p.category }}</td>
            <td>¥{{ p.price }}</td>
            <td>{{ p.stock }}</td>
            <td><span :class="p.status === 'on' ? 'text-green-600' : 'text-gray-500'">{{ p.status === 'on' ? '上架' : '下架' }}</span></td>
            <td class="space-x-2">
              <button @click="edit(p)" class="text-indigo-600 hover:underline">编辑</button>
              <button @click="remove(p.id)" class="text-red-500 hover:underline">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showForm" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <h3 class="font-bold text-lg mb-4">{{ editing ? '编辑商品' : '新增商品' }}</h3>
        <div class="space-y-3">
          <input v-model="form.name" placeholder="商品名称" class="w-full border rounded-lg px-3 py-2" />
          <input v-model="form.category" placeholder="分类" class="w-full border rounded-lg px-3 py-2" />
          <textarea v-model="form.description" placeholder="描述" rows="2" class="w-full border rounded-lg px-3 py-2"></textarea>
          <div class="grid grid-cols-2 gap-3">
            <input v-model.number="form.price" type="number" placeholder="价格" class="w-full border rounded-lg px-3 py-2" />
            <input v-model.number="form.stock" type="number" placeholder="库存" class="w-full border rounded-lg px-3 py-2" />
          </div>
          <input v-model="specsText" placeholder="规格，用逗号分隔" class="w-full border rounded-lg px-3 py-2" />
          <input v-model="form.image_url" placeholder="图片URL" class="w-full border rounded-lg px-3 py-2" />
          <select v-model="form.status" class="w-full border rounded-lg px-3 py-2">
            <option value="on">上架</option>
            <option value="off">下架</option>
          </select>
        </div>
        <div class="mt-6 flex justify-end space-x-2">
          <button @click="showForm = false" class="px-4 py-2 border rounded-lg">取消</button>
          <button @click="save" class="px-4 py-2 bg-indigo-600 text-white rounded-lg">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../api/axios'

const products = ref([])
const showForm = ref(false)
const editing = ref(false)
const form = ref({ name: '', category: '', description: '', price: 0, stock: 0, specs: [], image_url: '', status: 'off' })
const specsText = ref('')

async function loadProducts() {
  const res = await api.get('/products?status=')
  products.value = res.data
}

function edit(p) {
  editing.value = true
  form.value = { ...p }
  specsText.value = (p.specs || []).join(',')
  showForm.value = true
}

async function save() {
  form.value.specs = specsText.value.split(',').map(s => s.trim()).filter(Boolean)
  if (editing.value) {
    await api.put(`/products/${form.value.id}`, form.value)
  } else {
    await api.post('/products', form.value)
  }
  showForm.value = false
  editing.value = false
  form.value = { name: '', category: '', description: '', price: 0, stock: 0, specs: [], image_url: '', status: 'off' }
  specsText.value = ''
  loadProducts()
}

async function remove(id) {
  if (!confirm('确定删除？')) return
  await api.delete(`/products/${id}`)
  loadProducts()
}

async function exportProducts() {
  const res = await api.get('/products/export/data')
  const blob = new Blob([JSON.stringify(res.data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'products.json'
  a.click()
}

async function importProducts(e) {
  const file = e.target.files[0]
  if (!file) return
  const formData = new FormData()
  formData.append('file', file)
  await api.post('/products/import', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
  alert('导入成功')
  loadProducts()
}

onMounted(loadProducts)
</script>
