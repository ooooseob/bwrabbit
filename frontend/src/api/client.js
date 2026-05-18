import axios from 'axios'

const apiBaseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8080/api'

const client = axios.create({
  baseURL: apiBaseUrl,
  timeout: 300000, // LLM 응답은 최대 5분까지 걸릴 수 있음
})

export default client
