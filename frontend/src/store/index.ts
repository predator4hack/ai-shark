import { configureStore } from '@reduxjs/toolkit'
import pitchDeckReducer from './slices/pitchDeckSlice'
import uiReducer from './slices/uiSlice'

export const store = configureStore({
  reducer: {
    pitchDeck: pitchDeckReducer,
    ui: uiReducer,
  },
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
