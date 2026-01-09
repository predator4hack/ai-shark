import { configureStore } from '@reduxjs/toolkit'
import pitchDeckReducer from './slices/pitchDeckSlice'
import uiReducer from './slices/uiSlice'
import analysisReducer from './slices/analysisSlice'

export const store = configureStore({
  reducer: {
    pitchDeck: pitchDeckReducer,
    ui: uiReducer,
    analysis: analysisReducer,
  },
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
