import client from './client'

export const fetchGame = appId => client.post('/games/fetch', { appId }).then(r => r.data)

export const searchGames = keyword =>
  client.get('/games/search', { params: { keyword } }).then(r => r.data)

export const getGame = steamAppId => client.get(`/games/${steamAppId}`).then(r => r.data)

export const sendQuery = (query, sessionId) =>
  client.post('/query', { query, sessionId }).then(r => r.data)
