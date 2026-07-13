<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-800 mb-6">订单管理</h2>
    <div class="bg-white rounded-xl shadow-sm overflow-hidden">
      <table class="w-full text-sm text-left">
        <thead class="bg-gray-50 text-gray-600">
          <tr>
            <th class="px-4 py-3">订单号</th>
            <th>用户ID</th>
            <th>商品</th>
            <th>金额</th>
            <th>地址</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="order in orders" :key="order.id" class="border-b hover:bg-gray-50">
            <td class="px-4 py-3">{{ order.id }}</td>
            <td>{{ order.user_id }}</td>
            <td>
              <div v-for="item in order.items" :key="item.id" class="text-xs">ID{{ item.product_id }} × {{ item.quantity }}</div>
            </td>
            <td>¥{{ order.total_amount }}</td>
            <td class="truncate max-w-xs">{{ order.address }}</td>
            <td>{{ statusText(order.status) }}</td>
            <td>
              <button v-if="order.status === 'paid'" @click="ship(order.id)" class="bg-indigo-600 text-white px-3 py-1 rounded-md text-xs hover:bg-indigo-700">发货</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api/axios'

const orders = ref([])

function statusText(status) {
  const map = { pending: '待支付', paid: '已支付', shipped: '待收货', completed: '已完成', cancelled: '已取消' }
  return map[status] || status
}

async function loadOrders() {
  const res = await api.get('/orders/all/list')
  orders.value = res.data
}

async function ship(id) {
  await api.post(`/orders/${id}/ship`)
  loadOrders()
}

onMounted(loadOrders)
</script>
