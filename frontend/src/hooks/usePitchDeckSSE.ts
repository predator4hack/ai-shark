import { useState, useRef, useCallback, useEffect } from 'react'
import { API_BASE_URL } from '../utils/constants'
import type { SSEProgressEvent, SSECompleteEvent, SSEErrorEvent } from '../types/api'

interface UsePitchDeckSSEOptions {
  onProgress: (event: SSEProgressEvent) => void
  onComplete: (event: SSECompleteEvent) => void
  onError: (event: SSEErrorEvent) => void
  onConnectionError: (error: Error) => void
}

interface UsePitchDeckSSEReturn {
  startProcessing: (file: File) => Promise<void>
  isProcessing: boolean
  isConnected: boolean
  abort: () => void
}

export function usePitchDeckSSE(options: UsePitchDeckSSEOptions): UsePitchDeckSSEReturn {
  const [isProcessing, setIsProcessing] = useState(false)
  const [isConnected, setIsConnected] = useState(false)
  const abortControllerRef = useRef<AbortController | null>(null)
  const receivedCompleteEventRef = useRef(false)

  const abort = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      abortControllerRef.current = null
    }
    setIsProcessing(false)
    setIsConnected(false)
  }, [])

  const parseSSEEvent = useCallback((eventText: string) => {
    const lines = eventText.trim().split('\n')
    let eventType = ''
    let data = ''

    for (const line of lines) {
      if (line.startsWith('event: ')) {
        eventType = line.substring(7).trim()
      } else if (line.startsWith('data: ')) {
        data = line.substring(6).trim()
      }
    }

    if (!eventType || !data) return

    try {
      const parsedData = JSON.parse(data)

      switch (eventType) {
        case 'progress':
          console.log('[SSE] Progress event:', parsedData)
          options.onProgress(parsedData)
          break
        case 'complete':
          console.log('[SSE] Complete event:', parsedData)
          receivedCompleteEventRef.current = true
          options.onComplete(parsedData)
          setIsProcessing(false)
          setIsConnected(false)
          break
        case 'error':
          console.log('[SSE] Error event:', parsedData)
          options.onError(parsedData)
          setIsProcessing(false)
          setIsConnected(false)
          break
      }
    } catch (error) {
      console.error('Failed to parse SSE event data:', error)
    }
  }, [options])

  const startProcessing = useCallback(async (file: File) => {
    // Abort any existing processing
    abort()

    console.log('[SSE] Starting pitch deck processing with SSE...', file.name)
    receivedCompleteEventRef.current = false
    setIsProcessing(true)

    const abortController = new AbortController()
    abortControllerRef.current = abortController

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch(`${API_BASE_URL}/v1/documents/pitch-deck/stream`, {
        method: 'POST',
        body: formData,
        signal: abortController.signal,
      })

      if (!response.ok) {
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`
        try {
          const errorData = await response.json()
          errorMessage = errorData.detail || errorMessage
        } catch {
          // Response not JSON, use status text
        }
        throw new Error(errorMessage)
      }

      if (!response.body) {
        throw new Error('No response body')
      }

      setIsConnected(true)

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()

        if (done) {
          // Connection closed - check if we received complete event
          if (!receivedCompleteEventRef.current && !abortController.signal.aborted) {
            options.onConnectionError(new Error('Connection closed unexpectedly'))
          }
          break
        }

        buffer += decoder.decode(value, { stream: true })

        // Parse SSE events from buffer (events are separated by double newlines)
        const events = buffer.split('\n\n')
        buffer = events.pop() || '' // Keep incomplete event in buffer

        for (const event of events) {
          if (event.trim()) {
            parseSSEEvent(event)
          }
        }
      }
    } catch (error: any) {
      if (error.name === 'AbortError') {
        // User aborted - don't treat as error
        return
      }

      if (error instanceof TypeError) {
        // Network error
        options.onConnectionError(new Error('Network error - please check your connection'))
      } else {
        options.onConnectionError(error)
      }
    } finally {
      setIsProcessing(false)
      setIsConnected(false)
      abortControllerRef.current = null
    }
  }, [abort, options, parseSSEEvent])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      abort()
    }
  }, [abort])

  return {
    startProcessing,
    isProcessing,
    isConnected,
    abort,
  }
}
