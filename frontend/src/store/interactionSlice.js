import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import api from '../api/axios'

export const fetchInteractions = createAsyncThunk('interactions/fetchAll', async (params, { rejectWithValue }) => {
  try {
    const response = await api.get('/interactions', { params })
    return response.data
  } catch (err) {
    return rejectWithValue(err.response?.data?.detail || 'Failed to fetch interactions')
  }
})

export const createInteraction = createAsyncThunk('interactions/create', async (data, { rejectWithValue }) => {
  try {
    const response = await api.post('/interactions', data)
    return response.data
  } catch (err) {
    return rejectWithValue(err.response?.data?.detail || 'Failed to create interaction')
  }
})

const interactionSlice = createSlice({
  name: 'interactions',
  initialState: {
    items: [],
    total: 0,
    isLoading: false,
    error: null,
    currentInteraction: null,
  },
  reducers: {
    setCurrentInteraction: (state, action) => {
      state.currentInteraction = action.payload
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchInteractions.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(fetchInteractions.fulfilled, (state, action) => {
        state.isLoading = false
        state.items = action.payload.items
        state.total = action.payload.total
      })
      .addCase(fetchInteractions.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.payload
      })
      .addCase(createInteraction.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(createInteraction.fulfilled, (state, action) => {
        state.isLoading = false
        state.currentInteraction = action.payload
        // We don't necessarily append here, usually we refetch the list
      })
      .addCase(createInteraction.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.payload
      })
  },
})

export const { setCurrentInteraction } = interactionSlice.actions
export default interactionSlice.reducer
