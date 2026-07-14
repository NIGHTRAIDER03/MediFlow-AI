import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import api from '../api/axios'

export const fetchHCPs = createAsyncThunk('hcp/fetchAll', async (params, { rejectWithValue }) => {
  try {
    const response = await api.get('/hcps', { params })
    return response.data.items
  } catch (err) {
    return rejectWithValue(err.response?.data?.detail || 'Failed to fetch HCPs')
  }
})

export const searchHCPs = createAsyncThunk('hcp/search', async (query, { rejectWithValue }) => {
  try {
    const response = await api.get('/hcps', { params: { search: query } })
    return response.data.items
  } catch (err) {
    return rejectWithValue(err.response?.data?.detail || 'Search failed')
  }
})

export const fetchMeetingBrief = createAsyncThunk('hcp/fetchBrief', async (hcpId, { rejectWithValue }) => {
  try {
    const response = await api.get(`/hcps/${hcpId}/meeting-brief`)
    return { hcpId, brief: response.data.brief }
  } catch (err) {
    return rejectWithValue(err.response?.data?.detail || 'Failed to fetch meeting brief')
  }
})

const hcpSlice = createSlice({
  name: 'hcp',
  initialState: {
    items: [],
    searchResults: [],
    currentHcp: null,
    meetingBriefs: {}, // Cache by hcpId
    isLoading: false,
    isBriefLoading: false,
    error: null,
  },
  reducers: {
    setCurrentHcp: (state, action) => {
      state.currentHcp = action.payload
    },
    clearSearchResults: (state) => {
      state.searchResults = []
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchHCPs.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(fetchHCPs.fulfilled, (state, action) => {
        state.isLoading = false
        state.items = action.payload
      })
      .addCase(fetchHCPs.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.payload
      })
      .addCase(searchHCPs.fulfilled, (state, action) => {
        state.searchResults = action.payload
      })
      .addCase(fetchMeetingBrief.pending, (state) => {
        state.isBriefLoading = true
      })
      .addCase(fetchMeetingBrief.fulfilled, (state, action) => {
        state.isBriefLoading = false
        state.meetingBriefs[action.payload.hcpId] = action.payload.brief
      })
      .addCase(fetchMeetingBrief.rejected, (state, action) => {
        state.isBriefLoading = false
        state.error = action.payload
      })
  },
})

export const { setCurrentHcp, clearSearchResults } = hcpSlice.actions
export default hcpSlice.reducer
