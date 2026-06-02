import { useEffect, useState } from 'react'
import { useStore } from '../store'
import { Repeat2, Loader } from 'lucide-react'

export default function Calls() {
  const { calls, fetchCalls, callLoading } = useStore()
  const [filter, setFilter] = useState('all')
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    fetchCalls()
    const interval = setInterval(fetchCalls, 5000) // Actualizar cada 5 segundos
    return () => clearInterval(interval)
  }, [])

  const handleRetry = async (callId) => {
    try {
      setRefreshing(true)
      // Aquí iría la lógica para reintentar una llamada
      // await retryCall(callId)
      await fetchCalls()
    } catch (err) {
      alert('Error al reintentar la llamada')
    } finally {
      setRefreshing(false)
    }
  }

  const filteredCalls = calls.filter((call) => {
    if (filter === 'all') return true
    return call.status === filter
  })

  const getStatusColor = (status) => {
    const colors = {
      pending: 'bg-gray-100 text-gray-700',
      dialing: 'bg-blue-100 text-blue-700',
      completed: 'bg-green-100 text-green-700',
      failed: 'bg-red-100 text-red-700',
      no_answer: 'bg-yellow-100 text-yellow-700',
    }
    return colors[status] || 'bg-gray-100 text-gray-700'
  }

  const getStatusLabel = (status) => {
    const labels = {
      pending: 'Pendiente',
      dialing: 'Marcando',
      completed: 'Completada',
      failed: 'Fallida',
      no_answer: 'Sin respuesta',
    }
    return labels[status] || status
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Llamadas</h1>
          <button
            onClick={() => fetchCalls()}
            disabled={refreshing}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700 transition disabled:bg-blue-400"
          >
            {refreshing ? <Loader size={20} className="animate-spin" /> : <Repeat2 size={20} />}
            Actualizar
          </button>
        </div>

        {/* Filtros */}
        <div className="bg-white rounded-lg shadow p-4 mb-6 flex flex-wrap gap-2">
          {['all', 'pending', 'dialing', 'completed', 'failed', 'no_answer'].map((status) => (
            <button
              key={status}
              onClick={() => setFilter(status)}
              className={`px-4 py-2 rounded transition ${
                filter === status
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {status === 'all'
                ? 'Todas'
                : status === 'pending'
                ? 'Pendientes'
                : status === 'dialing'
                ? 'Marcando'
                : status === 'completed'
                ? 'Completadas'
                : status === 'failed'
                ? 'Fallidas'
                : 'Sin respuesta'}
            </button>
          ))}
        </div>

        {/* Tabla */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          {callLoading ? (
            <div className="p-8 text-center text-gray-600">
              <Loader size={32} className="animate-spin mx-auto mb-2" />
              Cargando llamadas...
            </div>
          ) : filteredCalls.length === 0 ? (
            <div className="p-8 text-center text-gray-600">
              No hay llamadas con ese estado
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-100 border-b">
                  <tr>
                    <th className="px-6 py-3 text-left text-sm font-medium text-gray-900">
                      Cliente
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-medium text-gray-900">
                      Teléfono
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-medium text-gray-900">
                      Lote
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-medium text-gray-900">
                      Estado
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-medium text-gray-900">
                      Intento
                    </th>
                    <th className="px-6 py-3 text-center text-sm font-medium text-gray-900">
                      Acciones
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {filteredCalls.map((call) => (
                    <tr key={call.id} className="hover:bg-gray-50 transition">
                      <td className="px-6 py-4 text-sm text-gray-900 font-medium">
                        {call.client_name || 'N/A'}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {call.phone_number || 'N/A'}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {call.batch_name || 'N/A'}
                      </td>
                      <td className="px-6 py-4 text-sm">
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(call.status)}`}>
                          {getStatusLabel(call.status)}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {call.retry_count || 0}
                      </td>
                      <td className="px-6 py-4 text-center">
                        {call.status === 'failed' && (
                          <button
                            onClick={() => handleRetry(call.id)}
                            disabled={refreshing}
                            className="text-blue-600 hover:text-blue-800 text-sm font-medium disabled:text-gray-400"
                          >
                            Reintentar
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Estadísticas */}
        {filteredCalls.length > 0 && (
          <div className="mt-8 grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="bg-white rounded-lg shadow p-4 text-center">
              <div className="text-sm text-gray-600">Total</div>
              <div className="text-2xl font-bold text-gray-900">{filteredCalls.length}</div>
            </div>
            <div className="bg-green-50 rounded-lg shadow p-4 text-center">
              <div className="text-sm text-green-600">Completadas</div>
              <div className="text-2xl font-bold text-green-700">
                {filteredCalls.filter((c) => c.status === 'completed').length}
              </div>
            </div>
            <div className="bg-red-50 rounded-lg shadow p-4 text-center">
              <div className="text-sm text-red-600">Fallidas</div>
              <div className="text-2xl font-bold text-red-700">
                {filteredCalls.filter((c) => c.status === 'failed').length}
              </div>
            </div>
            <div className="bg-blue-50 rounded-lg shadow p-4 text-center">
              <div className="text-sm text-blue-600">Marcando</div>
              <div className="text-2xl font-bold text-blue-700">
                {filteredCalls.filter((c) => c.status === 'dialing').length}
              </div>
            </div>
            <div className="bg-gray-50 rounded-lg shadow p-4 text-center">
              <div className="text-sm text-gray-600">Pendientes</div>
              <div className="text-2xl font-bold text-gray-700">
                {filteredCalls.filter((c) => c.status === 'pending').length}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
