import { useEffect, useState } from 'react'
import { useStore } from '../store'
import { Play, Trash2, Plus } from 'lucide-react'

export default function Batches() {
  const { batches, fetchBatches, addBatch, startBatch, batchLoading } = useStore()
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    total_clients: '',
  })
  const [error, setError] = useState('')

  useEffect(() => {
    fetchBatches()
    const interval = setInterval(fetchBatches, 5000) // Actualizar cada 5 segundos
    return () => clearInterval(interval)
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      setError('')
      await addBatch(formData)
      setFormData({ name: '', description: '', total_clients: '' })
      setShowForm(false)
    } catch (err) {
      setError('Error al crear lote')
    }
  }

  const handleStart = async (id) => {
    try {
      await startBatch(id)
    } catch (err) {
      alert('Error al iniciar lote')
    }
  }

  const getStatusColor = (status) => {
    const colors = {
      pending: 'bg-gray-100 text-gray-700',
      processing: 'bg-blue-100 text-blue-700',
      completed: 'bg-green-100 text-green-700',
      failed: 'bg-red-100 text-red-700',
    }
    return colors[status] || 'bg-gray-100 text-gray-700'
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Lotes de Llamadas</h1>
          <button
            onClick={() => setShowForm(!showForm)}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700 transition"
          >
            <Plus size={20} />
            Nuevo Lote
          </button>
        </div>

        {/* Formulario */}
        {showForm && (
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Crear Nuevo Lote</h2>
            {error && <div className="mb-4 p-4 bg-red-100 text-red-700 rounded">{error}</div>}
            <form onSubmit={handleSubmit} className="space-y-4">
              <input
                type="text"
                placeholder="Nombre del Lote"
                required
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <textarea
                placeholder="Descripción"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows="3"
              ></textarea>
              <input
                type="number"
                placeholder="Total de Clientes"
                required
                value={formData.total_clients}
                onChange={(e) => setFormData({ ...formData, total_clients: e.target.value })}
                className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <div className="flex gap-2">
                <button
                  type="submit"
                  className="flex-1 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition"
                >
                  Crear Lote
                </button>
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="flex-1 bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400 transition"
                >
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Tabla de Lotes */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {batchLoading ? (
            <div className="p-8 text-center text-gray-600 col-span-2">
              Cargando lotes...
            </div>
          ) : batches.length === 0 ? (
            <div className="p-8 text-center text-gray-600 col-span-2">
              No hay lotes registrados
            </div>
          ) : (
            batches.map((batch) => (
              <div
                key={batch.id}
                className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition"
              >
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-lg font-bold text-gray-900">{batch.name}</h3>
                    <p className="text-sm text-gray-600 mt-1">
                      {batch.description || 'Sin descripción'}
                    </p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(batch.status)}`}>
                    {batch.status}
                  </span>
                </div>

                <div className="space-y-3">
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-600">Progreso:</span>
                    <span className="font-medium text-gray-900">
                      {batch.processed_clients} / {batch.total_clients}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all"
                      style={{
                        width: `${
                          batch.total_clients > 0
                            ? (batch.processed_clients / batch.total_clients) * 100
                            : 0
                        }%`,
                      }}
                    ></div>
                  </div>

                  {batch.created_at && (
                    <p className="text-xs text-gray-500">
                      Creado: {new Date(batch.created_at).toLocaleDateString()}
                    </p>
                  )}
                </div>

                <div className="mt-4 flex gap-2">
                  {batch.status === 'pending' && (
                    <button
                      onClick={() => handleStart(batch.id)}
                      className="flex-1 bg-green-600 text-white px-4 py-2 rounded flex items-center justify-center gap-2 hover:bg-green-700 transition"
                    >
                      <Play size={18} />
                      Iniciar
                    </button>
                  )}
                  <button className="flex-1 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition flex items-center justify-center gap-2">
                    <Trash2 size={18} />
                    Eliminar
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
