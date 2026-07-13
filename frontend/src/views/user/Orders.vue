<template>
  <div class="bg-white rounded-xl shadow-sm p-6">
    <h2 class="text-xl font-bold text-gray-800 mb-4">我的订单</h2>
    <div v-if="orders.length === 0" class="text-center py-20 text-gray-500">暂无订单</div>
    <div v-else class="space-y-4">
      <div v-for="order in orders" :key="order.id" class="border rounded-lg p-4">
        <div class="flex justify-between items-center mb-2">
          <span class="text-sm text-gray-500">订单号：{{ order.id }}</span>
          <span class="text-sm font-medium text-indigo-600">{{ statusText(order.status) }}</span>
        </div>
        <div class="space-y-2">
          <div v-for="item in order.items" :key="item.id" class="flex justify-between text-sm">
            <span>商品ID：{{ item.product_id }} × {{ item.quantity }}</span>
            <span>¥{{ item.price }}</span>
          </div>
        </div>
        <div class="mt-3 flex justify-between items-center border-t pt-3">
          <span class="font-bold">合计：¥{{ order.total_amount }}</span>
          <div class="space-x-2">
            <button v-if="order.status === 'pending'" @click="pay(order.id)" class="bg-green-500 text-white px-4 py-1.5 rounded-md text-sm hover:bg-green-600">模拟支付</button>
            <button v-if="order.status === 'shipped'" @click="complete(order.id)" class="bg-indigo-600 text-white px-4 py-1.5 rounded-md text-sm hover:bg-indigo-700">确认收货</button>
            <button v-if="order.status === 'completed'" @click="review(order)" class="bg-yellow-500 text-white px-4 py-1.5 rounded-md text-sm hover:bg-yellow-600">评价</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showReview" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl p-6 w-full max-w-md">
        <h3 class="font-bold mb-4">发表评价</h3>
        <div class="mb-4">
          <label class="block text-sm text-gray-600 mb-1">评分</label>
          <select v-model="reviewForm.rating" class="border rounded-lg px-3 py-2 w-full">
            <option v-for="n in 5" :key="n" :value="n">{{ n }}星</option>
          </select>
        </div>
        <div class="mb-4">
          <label class="block text-sm text-gray-600 mb-1">评价内容</label>
          <textarea v-model="reviewForm.content" rows="3" class="border rounded-lg px-3 py-2 w-full"></textarea>
        </div>
        <div class="flex justify-end space-x-2">
          <button @click="showReview = false" class="px-4 py-2 border rounded-lg">取消</button>
          <button @click="submitReview" class="px-4 py-2 bg-indigo-600 text-white rounded-lg">提交</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api/axios'

const orders = ref([])
const showReview = ref(false)
const reviewForm = ref({ order_id: null, product_id: null, rating: 5, content: '' })

function statusText(status) {
  const map = { pending: '待支付', paid: '已支付', shipped: '待收货', completed: '已完成', cancelled: '已取消' }
  return map[status] || status
}

async function loadOrders() {
  const res = await api.get('/orders/my')
  orders.value = res.data
}

async function pay(id) {
  await api.post(`/orders/${id}/pay`, {}, { params: { method: 'wechat' } })
  loadOrders()
}

async function complete(id) {
  await api.post(`/orders/${id}/complete`)
  loadOrders()
}

function review(order) {
  reviewForm.value.order_id = order.id
  reviewForm.value.product_id = order.items[0]?.product_id
  reviewForm.value.rating = 5
  reviewForm.value.content = ''
  showReview.value = true
}

async function submitReview() {
  await api.post('/reviews', reviewForm.value)
  showReview.value = false
  alert('评价成功')
  loadOrders()
}

onMounted(loadOrders)
</script>
