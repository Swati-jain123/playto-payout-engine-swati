import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: {
    'Content-Type': 'application/json',
  }
})

api.interceptors.request.use((config) => {
  const merchantEmail = localStorage.getItem('merchant_email')

  if (merchantEmail) {
    config.headers['X-Merchant-Email'] = merchantEmail
  }

  // safer check (important fix)
  if (['post', 'put', 'patch'].includes(config.method?.toLowerCase())) {
    config.headers['Idempotency-Key'] = crypto.randomUUID()
  }

  return config
})

export default api
