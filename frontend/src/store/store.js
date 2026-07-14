import { configureStore } from '@reduxjs/toolkit'
import authReducer from './authSlice'
import chatReducer from './chatSlice'
import interactionReducer from './interactionSlice'
import hcpReducer from './hcpSlice'
import dashboardReducer from './dashboardSlice'
import uiReducer from './uiSlice'
// import analyticsReducer from './analyticsSlice'

export const store = configureStore({
  reducer: {
    auth: authReducer,
    chat: chatReducer,
    interactions: interactionReducer,
    hcp: hcpReducer,
    dashboard: dashboardReducer,
    ui: uiReducer,
    // analytics: analyticsReducer,
  },
})
