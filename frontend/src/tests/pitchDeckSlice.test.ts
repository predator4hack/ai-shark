import { describe, it, expect } from 'vitest'
import pitchDeckReducer, {
  setJobId,
  updateStatus,
  setResult,
  setError,
  reset,
} from '../store/slices/pitchDeckSlice'

describe('pitchDeckSlice', () => {
  const initialState = {
    jobId: null,
    status: 'idle' as const,
    progressMessage: '',
    companyName: null,
    files: [],
    metadata: null,
    error: null,
  }

  it('should return initial state', () => {
    expect(pitchDeckReducer(undefined, { type: 'unknown' })).toEqual(initialState)
  })

  it('should handle setJobId', () => {
    const actual = pitchDeckReducer(initialState, setJobId('test-job-123'))

    expect(actual.jobId).toBe('test-job-123')
    expect(actual.status).toBe('processing')
  })

  it('should handle updateStatus', () => {
    const stateWithJob = { ...initialState, jobId: 'test-job-123' }

    const actual = pitchDeckReducer(
      stateWithJob,
      updateStatus({
        status: 'processing',
        progressMessage: 'Converting pitch deck...',
      })
    )

    expect(actual.status).toBe('processing')
    expect(actual.progressMessage).toBe('Converting pitch deck...')
  })

  it('should handle setResult', () => {
    const stateWithJob = {
      ...initialState,
      jobId: 'test-job-123',
      status: 'processing' as const,
    }

    const resultData = {
      companyName: 'TestCo',
      files: ['TestCo/pitch_deck.md', 'TestCo/metadata.json'],
      metadata: {
        sector: 'Technology',
        website: 'https://testco.com',
      },
    }

    const actual = pitchDeckReducer(stateWithJob, setResult(resultData))

    expect(actual.status).toBe('completed')
    expect(actual.companyName).toBe('TestCo')
    expect(actual.files).toEqual(['TestCo/pitch_deck.md', 'TestCo/metadata.json'])
    expect(actual.metadata).toEqual(resultData.metadata)
  })

  it('should handle setError', () => {
    const stateWithJob = {
      ...initialState,
      jobId: 'test-job-123',
      status: 'processing' as const,
    }

    const actual = pitchDeckReducer(stateWithJob, setError('Processing failed'))

    expect(actual.status).toBe('failed')
    expect(actual.error).toBe('Processing failed')
  })

  it('should handle reset', () => {
    const stateWithData = {
      jobId: 'test-job-123',
      status: 'completed' as const,
      progressMessage: 'Done',
      companyName: 'TestCo',
      files: ['file1.md'],
      metadata: { sector: 'Tech' },
      error: null,
    }

    const actual = pitchDeckReducer(stateWithData, reset())

    expect(actual).toEqual(initialState)
  })

  it('should handle complete workflow', () => {
    // 1. Set job ID
    let state = pitchDeckReducer(initialState, setJobId('workflow-job'))
    expect(state.jobId).toBe('workflow-job')
    expect(state.status).toBe('processing')

    // 2. Update status - processing
    state = pitchDeckReducer(
      state,
      updateStatus({
        status: 'processing',
        progressMessage: 'Step 1: Extracting content...',
      })
    )
    expect(state.progressMessage).toBe('Step 1: Extracting content...')

    // 3. Update status - still processing
    state = pitchDeckReducer(
      state,
      updateStatus({
        status: 'processing',
        progressMessage: 'Step 2: Analyzing structure...',
      })
    )
    expect(state.progressMessage).toBe('Step 2: Analyzing structure...')

    // 4. Set result - completed
    state = pitchDeckReducer(
      state,
      setResult({
        companyName: 'WorkflowCo',
        files: ['WorkflowCo/pitch_deck.md'],
        metadata: { sector: 'FinTech' },
      })
    )
    expect(state.status).toBe('completed')
    expect(state.companyName).toBe('WorkflowCo')

    // 5. Reset for new upload
    state = pitchDeckReducer(state, reset())
    expect(state).toEqual(initialState)
  })

  it('should handle error workflow', () => {
    // 1. Start with job
    let state = pitchDeckReducer(initialState, setJobId('error-job'))

    // 2. Update status - processing
    state = pitchDeckReducer(
      state,
      updateStatus({
        status: 'processing',
        progressMessage: 'Processing...',
      })
    )

    // 3. Error occurs
    state = pitchDeckReducer(state, setError('Invalid PDF format'))

    expect(state.status).toBe('failed')
    expect(state.error).toBe('Invalid PDF format')

    // 4. Can reset after error
    state = pitchDeckReducer(state, reset())
    expect(state.error).toBeNull()
    expect(state.status).toBe('idle')
  })

  it('should preserve jobId through status updates', () => {
    let state = pitchDeckReducer(initialState, setJobId('persistent-job'))

    state = pitchDeckReducer(
      state,
      updateStatus({
        status: 'processing',
        progressMessage: 'Processing...',
      })
    )

    expect(state.jobId).toBe('persistent-job')

    state = pitchDeckReducer(
      state,
      setResult({
        companyName: 'Test',
        files: ['test.md'],
        metadata: {},
      })
    )

    expect(state.jobId).toBe('persistent-job')
  })
})
