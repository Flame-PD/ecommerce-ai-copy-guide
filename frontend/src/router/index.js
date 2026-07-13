import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import UserLayout from '../layouts/UserLayout.vue'
import MerchantLayout from '../layouts/MerchantLayout.vue'
import Login from '../views/auth/Login.vue'
import Register from '../views/auth/Register.vue'
import ForgotPassword from '../views/auth/ForgotPassword.vue'
import UserHome from '../views/user/Home.vue'
import ProductDetail from '../views/user/ProductDetail.vue'
import Cart from '../views/user/Cart.vue'
import Orders from '../views/user/Orders.vue'
import Profile from '../views/user/Profile.vue'
import MerchantDashboard from '../views/merchant/Dashboard.vue'
import MerchantProducts from '../views/merchant/Products.vue'
import MerchantAICopy from '../views/merchant/AICopy.vue'
import MerchantKnowledge from '../views/merchant/Knowledge.vue'
import MerchantReviews from '../views/merchant/ReviewsAnalysis.vue'
import MerchantLiveScript from '../views/merchant/LiveScript.vue'
import MerchantOrders from '../views/merchant/OrdersManage.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { path: '/forgot-password', component: ForgotPassword },
  {
    path: '/',
    component: UserLayout,
    meta: { requiresAuth: true, role: 'user' },
    children: [
      { path: 'home', component: UserHome },
      { path: 'product/:id', component: ProductDetail },
      { path: 'cart', component: Cart },
      { path: 'orders', component: Orders },
      { path: 'profile', component: Profile },
    ]
  },
  {
    path: '/merchant',
    component: MerchantLayout,
    meta: { requiresAuth: true, role: 'merchant' },
    children: [
      { path: '', redirect: '/merchant/dashboard' },
      { path: 'dashboard', component: MerchantDashboard },
      { path: 'products', component: MerchantProducts },
      { path: 'ai-copy', component: MerchantAICopy },
      { path: 'knowledge', component: MerchantKnowledge },
      { path: 'reviews', component: MerchantReviews },
      { path: 'live-script', component: MerchantLiveScript },
      { path: 'orders', component: MerchantOrders },
    ]
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth) {
    if (!auth.isLoggedIn) return next('/login')
    if (to.meta.role && auth.role !== to.meta.role) {
      return next(auth.role === 'merchant' ? '/merchant' : '/home')
    }
  }
  if ((to.path === '/login' || to.path === '/register') && auth.isLoggedIn) {
    return next(auth.role === 'merchant' ? '/merchant' : '/home')
  }
  next()
})

export default router
