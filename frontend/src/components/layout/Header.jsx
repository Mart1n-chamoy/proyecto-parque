import { Link, useNavigate } from 'react-router-dom'
import { BarChart3, Phone, Users, Layout, PhoneCall, LogOut } from 'lucide-react'
import { useState } from 'react'

export default function Header() {
  const navigate = useNavigate()
  const [user] = useState(() => {
    const userData = localStorage.getItem('user')
    return userData ? JSON.parse(userData) : null
  })

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    navigate('/login')
  }

  return (
    <header className="bg-gradient-to-r from-blue-600 to-blue-800 text-white shadow-lg">
      <nav className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3 text-xl font-bold hover:opacity-90">
          <BarChart3 size={28} />
          <span>Proyecto-Parque</span>
        </Link>

        <div className="flex items-center gap-8">
          <Link
            to="/dashboard"
            className="flex items-center gap-2 hover:bg-blue-700 px-3 py-2 rounded transition"
          >
            <Layout size={20} />
            <span>Dashboard</span>
          </Link>

          <Link
            to="/clients"
            className="flex items-center gap-2 hover:bg-blue-700 px-3 py-2 rounded transition"
          >
            <Users size={20} />
            <span>Clientes</span>
          </Link>

          <Link
            to="/batches"
            className="flex items-center gap-2 hover:bg-blue-700 px-3 py-2 rounded transition"
          >
            <Phone size={20} />
            <span>Lotes</span>
          </Link>

          <Link
            to="/calls"
            className="flex items-center gap-2 hover:bg-blue-700 px-3 py-2 rounded transition"
          >
            <PhoneCall size={20} />
            <span>Llamadas</span>
          </Link>

          <div className="border-l border-blue-500 pl-8 flex items-center gap-4">
            {user && (
              <span className="text-sm">
                Hola, <strong>{user.first_name || user.username}</strong>
              </span>
            )}
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 hover:bg-blue-700 px-3 py-2 rounded transition"
            >
              <LogOut size={20} />
              <span>Salir</span>
            </button>
          </div>
        </div>
      </nav>
    </header>
  )
}
