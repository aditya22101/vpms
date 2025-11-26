import axios, { type InternalAxiosRequestConfig } from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor to add token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('token')
    if (token) {
      // Axios may expose headers as an AxiosHeaders instance (with `set`) or
      // a plain object. Set the header in a way that works for both.
      if (config.headers) {
        // Use `set` if available (Axios v1+), otherwise assign directly
        if (typeof (config.headers as any).set === 'function') {
          (config.headers as any).set('Authorization', `Bearer ${token}`)
        } else {
          (config.headers as any)['Authorization'] = `Bearer ${token}`
        }
      }
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor to handle 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('role')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
