import { createSlice } from '@reduxjs/toolkit'
import type { PayloadAction } from '@reduxjs/toolkit'

interface UIState {
  sidebarOpen: boolean
  currentPhase: number
  isDarkMode: boolean
}

const initialState: UIState = {
  sidebarOpen: true,
  currentPhase: 1,
  isDarkMode: false,
}

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen
    },
    setCurrentPhase: (state, action: PayloadAction<number>) => {
      state.currentPhase = action.payload
    },
    toggleDarkMode: (state) => {
      state.isDarkMode = !state.isDarkMode
    },
  },
})

export const { toggleSidebar, setCurrentPhase, toggleDarkMode } = uiSlice.actions
export default uiSlice.reducer
