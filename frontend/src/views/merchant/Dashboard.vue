<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-800 mb-6">数据看板</h2>
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <div v-for="s in stats" :key="s.title" class="bg-white rounded-xl shadow-sm p-6">
        <p class="text-sm text-gray-500">{{ s.title }}</p>
        <p class="text-3xl font-bold text-indigo-600 mt-2">{{ s.value }}</p>
      </div>
    </div>
    <div class="mt-8 bg-white rounded-xl shadow-sm p-6">
      <h3 class="font-bold text-lg mb-4">最近订单</h3>
      <div class="overflow-x-auto">
        <table class="w-full text-sm text-left">
          <thead class="bg-gray-50 text-gray-600">
            <tr><th class="px-4 py-2">订单号</th><th>用户</th><th>金额</th><th>状态</th><th>时间</th></tr>
          </thead>
          <tbody>
            <tr v-for="o in recentOrders" :key="o.id" class="border-b">
              <td class="px-4 py-2">{{ o.id }}</td>
              <td>{{ o.user_id }}</td>
              <td>¥{{ o.total_amount }}</td>
              <td>{{ statusText(o.status) }}</td>
              <td>{{ new Date(o.created_at).toLocaleString() }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api/axios'

const stats = ref([
  { title: '商品总数', value: 0 },
  { title: '订单总数', value: 0 },
  { title: '评价总数', value: 0 },
  { title: '用户总数', value: 0 },
])
const recentOrders = ref([])

function statusText(status) {
  const map = { pending: '待支付', paid: '已支付', shipped: '待收货', completed: '已完成', cancelled: '已取消' }
  return map[status] || status
}

async function loadData() {
  const [products, orders, reviews, users] = await Promise.all([
    api.get('/products?status='),
    api.get('/orders/all/list'),
    api.get('/reviews/my').catch(() => ({ data: [] })),
    api.get('/users').catch(() => ({ data: [] })),
  ])
  stats.value[0].value = products.data.length
  stats.value[1].value = orders.data.length
  stats.value[2].value = reviews.data.length
  stats.value[3].value = users.data.length
  recentOrders.value = orders.data.slice(0, 5)
}

onMounted(loadData)
</script>
