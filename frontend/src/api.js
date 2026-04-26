import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  }
})

// ✅ Attach merchant identity + idempotency
api.interceptors.request.use((config) => {
  const merchantEmail = localStorage.getItem('merchant_email')

  // 🔥 REQUIRED FOR YOUR BACKEND
  if (merchantEmail) {
    config.headers['X-Merchant-Email'] = merchantEmail
  }

  // 🔥 Idempotency only for POST/PUT/PATCH
  if (['post', 'put', 'patch'].includes(config.method)) {
    config.headers['Idempotency-Key'] = crypto.randomUUID()
  }

  return config
})

export default api