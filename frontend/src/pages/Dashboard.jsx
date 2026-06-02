import { useEffect } from 'react'
import { useStore } from '../store'
import { Phone, Users, Clock, CheckCircle } from 'lucide-react'

export default function Dashboard() {
  const { fetchClients, fetchCalls, fetchBatches, clients, calls, batches } = useStore()

  useEffect(() => {
    fetchClients()
    fetchCalls()
    fetchBatches()
  }, [])

  const stats = [
    {
      title: 'Total de Clientes',
      value: clients.length || 0,
      icon: Users,
      color: 'bg-blue-500',
    },
    {
      title: 'Llamadas Pendientes',
      value: calls.filter((c) => c.status === 'pending').length || 0,
      icon: Clock,
      color: 'bg-yellow-500',
    },
    {
      title: 'Llamadas Completadas',
      value: calls.filter((c) => c.status === 'completed').length || 0,
      icon: CheckCircle,
      color: 'bg-green-500',
    },
    {
      title: 'Lotes Activos',
      value: batches.filter((b) => b.status === 'processing').length || 0,
      icon: Phone,
      color: 'bg-purple-500',
    },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          Dashboard - Sistema de Cobranza
        </h1>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat) => {
            const Icon = stat.icon
            return (
              <div
                key={stat.title}
                className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-600 text-sm">{stat.title}</p>
                    <p className="text-3xl font-bold text-gray-900 mt-2">
                      {stat.value}
                    </p>
                  </div>
                  <div className={`${stat.color} p-3 rounded-full`}>
                    <Icon size={24} className="text-white" />
                  </div>
                </div>
              </div>
            )
          })}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Últimos Clientes */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Últimos Clientes</h2>
            <div className="space-y-3">
              {clients.slice(0, 5).map((client) => (
                <div
                  key={client.id}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded border border-gray-200"
                >
                  <div>
                    <p className="font-medium text-gray-900">
                      {client.first_name} {client.last_name}
                    </p>
                    <p className="text-sm text-gray-600">{client.phone}</p>
                  </div>
                  <span className="font-bold text-gray-900">
                    ${client.debt_amount}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Lotes Activos */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Lotes en Procesamiento</h2>
            <div className="space-y-3">
              {batches
                .filter((b) => b.status === 'processing')
                .slice(0, 5)
                .map((batch) => (
                  <div
                    key={batch.id}
                    className="p-3 bg-gray-50 rounded border border-gray-200"
                  >
                    <div className="flex justify-between items-start mb-2">
                      <p className="font-medium text-gray-900">{batch.name}</p>
                      <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded">
                        {batch.status}
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
                    <p className="text-xs text-gray-600 mt-1">
                      {batch.processed_clients} / {batch.total_clients} procesadas
                    </p>
                  </div>
                ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
