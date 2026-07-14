import { createSlice } from '@reduxjs/toolkit'

const uiSlice = createSlice({
  name: 'ui',
  initialState: {
    activeMode: 'form', // 'form' | 'copilot'
    sidebarCollapsed: false,
    askMediFlowOpen: false,
  },
  reducers: {
    toggleMode: (state) => {
      state.activeMode = state.activeMode === 'form' ? 'copilot' : 'form'
    },
    setMode: (state, action) => {
      state.activeMode = action.payload
    },
    toggleSidebar: (state) => {
      state.sidebarCollapsed = !state.sidebarCollapsed
    },
    setAskMediFlowOpen: (state, action) => {
      state.askMediFlowOpen = action.payload
    },
  },
})

export const { toggleMode, setMode, toggleSidebar, setAskMediFlowOpen } = uiSlice.actions
export default uiSlice.reducer
