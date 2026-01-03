import { ReactElement } from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { Provider } from 'react-redux'
import { BrowserRouter } from 'react-router-dom'
import { ThemeProvider, createTheme } from '@mui/material'
import { configureStore } from '@reduxjs/toolkit'
import pitchDeckReducer from '../store/slices/pitchDeckSlice'
import uiReducer from '../store/slices/uiSlice'

// Create test theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
  },
})

// Create test store
export function createTestStore(preloadedState = {}) {
  return configureStore({
    reducer: {
      pitchDeck: pitchDeckReducer,
      ui: uiReducer,
    },
    preloadedState,
  })
}

interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  preloadedState?: any
  store?: any
}

// Custom render function with all providers
export function renderWithProviders(
  ui: ReactElement,
  {
    preloadedState = {},
    store = createTestStore(preloadedState),
    ...renderOptions
  }: CustomRenderOptions = {}
) {
  function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <Provider store={store}>
        <ThemeProvider theme={theme}>
          <BrowserRouter>{children}</BrowserRouter>
        </ThemeProvider>
      </Provider>
    )
  }

  return { store, ...render(ui, { wrapper: Wrapper, ...renderOptions }) }
}

// Re-export everything from testing library
export * from '@testing-library/react'
export { renderWithProviders as render }
