import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Search from './pages/Search'
import GameDetail from './pages/GameDetail'
import Fetch from './pages/Fetch'
import Chat from './pages/Chat'

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path='/' element={<Home />} />
        <Route path='/search' element={<Search />} />
        <Route path='/game/:steamAppId' element={<GameDetail />} />
        <Route path='/fetch' element={<Fetch />} />
        <Route path='/chat' element={<Chat />} />
      </Routes>
    </BrowserRouter>
  )
}
