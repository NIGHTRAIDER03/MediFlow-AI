import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import api from '../api/axios'

export const sendMessage = createAsyncThunk('chat/sendMessage', async ({ message, threadId }, { rejectWithValue }) => {
  try {
    const response = await api.post('/chat', { message, thread_id: threadId })
    return response.data
  } catch (err) {
    return rejectWithValue(err.response?.data?.detail || 'Failed to send message')
  }
})

const chatSlice = createSlice({
  name: 'chat',
  initialState: {
    messages: [],
    isLoading: false,
    threadId: null,
    thinkingSteps: [],
    toolResults: [],
    error: null,
  },
  reducers: {
    addMessage: (state, action) => {
      state.messages.push(action.payload)
    },
    clearChat: (state) => {
      state.messages = []
      state.thinkingSteps = []
      state.toolResults = []
      state.error = null
    },
    setThreadId: (state, action) => {
      state.threadId = action.payload
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendMessage.pending, (state) => {
        state.isLoading = true
        state.error = null
        state.thinkingSteps = [] // Reset thinking for new message
        state.toolResults = []
      })
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.isLoading = false
        if (action.payload.response) {
          state.messages.push({ role: 'ai', content: action.payload.response, timestamp: new Date().toISOString() })
        }
        state.toolResults = action.payload.tool_results || []
        // Mock thinking steps based on tool results if needed
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.payload
      })
  },
})

export const { addMessage, clearChat, setThreadId } = chatSlice.actions
export default chatSlice.reducer
