import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import api from '../api/axios'

export const fetchDashboard = createAsyncThunk('dashboard/fetch', async (_, { rejectWithValue }) => {
  try {
    const response = await api.get('/dashboard')
    return response.data
  } catch (err) {
    return rejectWithValue(err.response?.data?.detail || 'Failed to fetch dashboard')
  }
})

const dashboardSlice = createSlice({
  name: 'dashboard',
  initialState: {
    stats: {
      todays_visits: 0,
      pending_follow_ups: 0,
      overdue_follow_ups: 0,
      weeks_interactions: 0,
      avg_sentiment: 0,
    },
    aiFocus: [],
    recentActivity: [],
    upcomingFollowUps: [],
    greeting: '',
    isLoading: true,
    error: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchDashboard.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(fetchDashboard.fulfilled, (state, action) => {
        state.isLoading = false
        state.stats = {
          todays_visits: action.payload.todays_visits,
          pending_follow_ups: action.payload.pending_follow_ups,
          overdue_follow_ups: action.payload.overdue_follow_ups,
          weeks_interactions: action.payload.weeks_interactions,
          avg_sentiment: action.payload.avg_sentiment,
        }
        state.aiFocus = action.payload.ai_focus || []
        state.recentActivity = action.payload.recent_activity || []
        state.upcomingFollowUps = action.payload.upcoming_follow_ups || []
        state.greeting = action.payload.greeting || ''
      })
      .addCase(fetchDashboard.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.payload
      })
  },
})

export default dashboardSlice.reducer
