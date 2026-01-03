import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { renderWithProviders } from './testUtils'
import { PitchDeckPage } from '../pages/PitchDeckPage'
import * as documentsApi from '../api/endpoints/documents'

// Mock the documents API
vi.mock('../api/endpoints/documents', () => ({
  documentsApi: {
    uploadPitchDeck: vi.fn(),
    getJobStatus: vi.fn(),
    downloadFile: vi.fn((company, file) => `/api/v1/files/download/${company}/${file}`),
  },
}))

describe('PitchDeckPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the pitch deck upload page', () => {
    renderWithProviders(<PitchDeckPage />)

    expect(screen.getByText(/Phase 1: Pitch Deck Analysis/i)).toBeInTheDocument()
    expect(screen.getByText(/Upload your pitch deck/i)).toBeInTheDocument()
  })

  it('shows drag and drop zone initially', () => {
    renderWithProviders(<PitchDeckPage />)

    expect(screen.getByText(/Drag & drop your pitch deck/i)).toBeInTheDocument()
  })

  it('handles file upload successfully', async () => {
    const user = userEvent.setup()

    // Mock successful upload
    vi.mocked(documentsApi.documentsApi.uploadPitchDeck).mockResolvedValue({
      job_id: 'test-job-123',
      message: 'Upload successful',
    })

    // Mock job status - completed immediately
    vi.mocked(documentsApi.documentsApi.getJobStatus).mockResolvedValue({
      job_id: 'test-job-123',
      status: 'completed',
      progress_message: 'Processing complete',
      result: {
        success: true,
        company_name: 'TestCo',
        files_created: ['TestCo/pitch_deck.md', 'TestCo/metadata.json'],
        metadata: {
          sector: 'Technology',
          website: 'https://testco.com',
        },
        processing_time: 45.2,
      },
    })

    renderWithProviders(<PitchDeckPage />)

    // Create a file
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' })

    // Find the input element (it's hidden in the dropzone)
    const input = document.querySelector('input[type="file"]') as HTMLInputElement

    // Upload the file
    await user.upload(input, file)

    // Wait for processing to complete
    await waitFor(
      () => {
        expect(screen.getByText(/Processing Complete/i)).toBeInTheDocument()
      },
      { timeout: 5000 }
    )

    // Check company name is displayed
    expect(screen.getByText(/Company: TestCo/i)).toBeInTheDocument()

    // Check files are listed
    expect(screen.getByText(/pitch_deck.md/i)).toBeInTheDocument()
    expect(screen.getByText(/metadata.json/i)).toBeInTheDocument()
  })

  it('shows processing status during upload', async () => {
    const user = userEvent.setup()

    // Mock upload
    vi.mocked(documentsApi.documentsApi.uploadPitchDeck).mockResolvedValue({
      job_id: 'test-job-456',
      message: 'Upload successful',
    })

    // Mock job status - processing
    vi.mocked(documentsApi.documentsApi.getJobStatus).mockResolvedValue({
      job_id: 'test-job-456',
      status: 'processing',
      progress_message: 'Converting pitch deck to images...',
    })

    renderWithProviders(<PitchDeckPage />)

    const file = new File(['test'], 'test.pdf', { type: 'application/pdf' })
    const input = document.querySelector('input[type="file"]') as HTMLInputElement

    await user.upload(input, file)

    // Should show processing message
    await waitFor(() => {
      expect(screen.getByText(/Processing.../i)).toBeInTheDocument()
    })
  })

  it('handles upload errors gracefully', async () => {
    const user = userEvent.setup()

    // Mock upload failure
    vi.mocked(documentsApi.documentsApi.uploadPitchDeck).mockRejectedValue({
      response: {
        data: {
          detail: 'Invalid file type',
        },
      },
    })

    renderWithProviders(<PitchDeckPage />)

    const file = new File(['test'], 'test.txt', { type: 'text/plain' })
    const input = document.querySelector('input[type="file"]') as HTMLInputElement

    await user.upload(input, file)

    // Should show error message
    await waitFor(() => {
      expect(screen.getByText(/Invalid file type/i)).toBeInTheDocument()
    })
  })

  it('handles processing failures', async () => {
    const user = userEvent.setup()

    vi.mocked(documentsApi.documentsApi.uploadPitchDeck).mockResolvedValue({
      job_id: 'test-job-789',
      message: 'Upload successful',
    })

    // Mock job status - failed
    vi.mocked(documentsApi.documentsApi.getJobStatus).mockResolvedValue({
      job_id: 'test-job-789',
      status: 'failed',
      progress_message: 'Processing failed',
      error: 'Failed to extract PDF content',
    })

    renderWithProviders(<PitchDeckPage />)

    const file = new File(['test'], 'test.pdf', { type: 'application/pdf' })
    const input = document.querySelector('input[type="file"]') as HTMLInputElement

    await user.upload(input, file)

    // Should show error
    await waitFor(() => {
      expect(screen.getByText(/Failed to extract PDF content/i)).toBeInTheDocument()
    })
  })

  it('displays download links for completed processing', async () => {
    const user = userEvent.setup()

    vi.mocked(documentsApi.documentsApi.uploadPitchDeck).mockResolvedValue({
      job_id: 'test-job-999',
      message: 'Upload successful',
    })

    vi.mocked(documentsApi.documentsApi.getJobStatus).mockResolvedValue({
      job_id: 'test-job-999',
      status: 'completed',
      progress_message: 'Complete',
      result: {
        success: true,
        company_name: 'DownloadTest',
        files_created: ['DownloadTest/pitch_deck.md'],
        metadata: {},
        processing_time: 30,
      },
    })

    renderWithProviders(<PitchDeckPage />)

    const file = new File(['test'], 'test.pdf', { type: 'application/pdf' })
    const input = document.querySelector('input[type="file"]') as HTMLInputElement

    await user.upload(input, file)

    // Wait for completion
    await waitFor(() => {
      expect(screen.getByText(/Processing Complete/i)).toBeInTheDocument()
    })

    // Check download button exists
    const downloadButton = screen.getByText(/Download/i)
    expect(downloadButton).toBeInTheDocument()
  })

  it('polls job status at regular intervals', async () => {
    const user = userEvent.setup()

    vi.mocked(documentsApi.documentsApi.uploadPitchDeck).mockResolvedValue({
      job_id: 'test-job-poll',
      message: 'Upload successful',
    })

    // Mock multiple status responses
    let callCount = 0
    vi.mocked(documentsApi.documentsApi.getJobStatus).mockImplementation(() => {
      callCount++
      if (callCount < 3) {
        return Promise.resolve({
          job_id: 'test-job-poll',
          status: 'processing',
          progress_message: `Step ${callCount}`,
        })
      } else {
        return Promise.resolve({
          job_id: 'test-job-poll',
          status: 'completed',
          progress_message: 'Complete',
          result: {
            success: true,
            company_name: 'PollTest',
            files_created: ['PollTest/pitch_deck.md'],
            metadata: {},
            processing_time: 20,
          },
        })
      }
    })

    renderWithProviders(<PitchDeckPage />)

    const file = new File(['test'], 'test.pdf', { type: 'application/pdf' })
    const input = document.querySelector('input[type="file"]') as HTMLInputElement

    await user.upload(input, file)

    // Wait for completion
    await waitFor(
      () => {
        expect(screen.getByText(/Processing Complete/i)).toBeInTheDocument()
      },
      { timeout: 10000 }
    )

    // Should have called getJobStatus multiple times
    expect(callCount).toBeGreaterThanOrEqual(3)
  })
})
