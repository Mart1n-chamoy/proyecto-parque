import { create } from 'zustand'
import { clientsAPI, callsAPI, batchesAPI } from '../api/client'

export const useStore = create((set) => ({
  // Clients
  clients: [],
  clientLoading: false,
  fetchClients: async (params) => {
    set({ clientLoading: true })
    try {
      const response = await clientsAPI.getAll(params)
      set({ clients: response.data.results || response.data })
    } catch (error) {
      console.error('Error fetching clients:', error)
    } finally {
      set({ clientLoading: false })
    }
  },
  addClient: async (data) => {
    try {
      const response = await clientsAPI.create(data)
      set((state) => ({ clients: [...state.clients, response.data] }))
      return response.data
    } catch (error) {
      console.error('Error creating client:', error)
      throw error
    }
  },
  deleteClient: async (id) => {
    try {
      await clientsAPI.delete(id)
      set((state) => ({
        clients: state.clients.filter((c) => c.id !== id),
      }))
    } catch (error) {
      console.error('Error deleting client:', error)
      throw error
    }
  },

  // Calls
  calls: [],
  callLoading: false,
  fetchCalls: async (params) => {
    set({ callLoading: true })
    try {
      const response = await callsAPI.getAll(params)
      set({ calls: response.data.results || response.data })
    } catch (error) {
      console.error('Error fetching calls:', error)
    } finally {
      set({ callLoading: false })
    }
  },
  addCall: async (data) => {
    try {
      const response = await callsAPI.create(data)
      set((state) => ({ calls: [...state.calls, response.data] }))
      return response.data
    } catch (error) {
      console.error('Error creating call:', error)
      throw error
    }
  },

  // Batches
  batches: [],
  batchLoading: false,
  fetchBatches: async (params) => {
    set({ batchLoading: true })
    try {
      const response = await batchesAPI.getAll(params)
      set({ batches: response.data.results || response.data })
    } catch (error) {
      console.error('Error fetching batches:', error)
    } finally {
      set({ batchLoading: false })
    }
  },
  addBatch: async (data) => {
    try {
      const response = await batchesAPI.create(data)
      set((state) => ({ batches: [...state.batches, response.data] }))
      return response.data
    } catch (error) {
      console.error('Error creating batch:', error)
      throw error
    }
  },
  startBatch: async (id) => {
    try {
      const response = await batchesAPI.start(id)
      set((state) => ({
        batches: state.batches.map((b) => (b.id === id ? response.data : b)),
      }))
      return response.data
    } catch (error) {
      console.error('Error starting batch:', error)
      throw error
    }
  },
}))
