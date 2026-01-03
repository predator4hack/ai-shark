import { describe, it, expect, vi } from 'vitest'
import { screen, fireEvent } from '@testing-library/react'
import { renderWithProviders } from './testUtils'
import { DragDropZone } from '../components/FileUpload/DragDropZone'

describe('DragDropZone Component', () => {
  it('renders drag and drop zone', () => {
    const onFileSelect = vi.fn()
    renderWithProviders(<DragDropZone onFileSelect={onFileSelect} />)

    expect(screen.getByText(/Drag & drop your pitch deck/i)).toBeInTheDocument()
    expect(screen.getByText(/or click to browse/i)).toBeInTheDocument()
  })

  it('shows accepted file types', () => {
    const onFileSelect = vi.fn()
    renderWithProviders(<DragDropZone onFileSelect={onFileSelect} />)

    expect(screen.getByText(/Supported formats:.*\.pdf.*\.ppt.*\.pptx/i)).toBeInTheDocument()
  })

  it('shows max file size', () => {
    const onFileSelect = vi.fn()
    renderWithProviders(<DragDropZone onFileSelect={onFileSelect} maxSizeMB={100} />)

    expect(screen.getByText(/Max 100MB/i)).toBeInTheDocument()
  })

  it('can be disabled', () => {
    const onFileSelect = vi.fn()
    renderWithProviders(<DragDropZone onFileSelect={onFileSelect} disabled={true} />)

    const input = document.querySelector('input[type="file"]') as HTMLInputElement
    expect(input).toBeDisabled()
  })

  it('accepts valid PDF files', () => {
    const onFileSelect = vi.fn()
    renderWithProviders(<DragDropZone onFileSelect={onFileSelect} />)

    const file = new File(['test'], 'test.pdf', { type: 'application/pdf' })
    const input = document.querySelector('input[type="file"]') as HTMLInputElement

    fireEvent.change(input, { target: { files: [file] } })

    expect(onFileSelect).toHaveBeenCalledWith(file)
  })

  it('accepts PowerPoint files', () => {
    const onFileSelect = vi.fn()
    renderWithProviders(<DragDropZone onFileSelect={onFileSelect} />)

    const file = new File(['test'], 'presentation.pptx', {
      type: 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    })
    const input = document.querySelector('input[type="file"]') as HTMLInputElement

    fireEvent.change(input, { target: { files: [file] } })

    expect(onFileSelect).toHaveBeenCalledWith(file)
  })

  it('only accepts one file at a time', () => {
    const onFileSelect = vi.fn()
    renderWithProviders(<DragDropZone onFileSelect={onFileSelect} />)

    const input = document.querySelector('input[type="file"]') as HTMLInputElement
    expect(input).not.toHaveAttribute('multiple')
  })

  it('shows custom accepted file types when provided', () => {
    const onFileSelect = vi.fn()
    renderWithProviders(
      <DragDropZone onFileSelect={onFileSelect} acceptedFileTypes={['.pdf', '.doc']} />
    )

    expect(screen.getByText(/Supported formats:.*\.pdf.*\.doc/i)).toBeInTheDocument()
  })

  it('shows custom max size when provided', () => {
    const onFileSelect = vi.fn()
    renderWithProviders(<DragDropZone onFileSelect={onFileSelect} maxSizeMB={50} />)

    expect(screen.getByText(/Max 50MB/i)).toBeInTheDocument()
  })

  it('shows drag active state', () => {
    const onFileSelect = vi.fn()
    const { container } = renderWithProviders(<DragDropZone onFileSelect={onFileSelect} />)

    const dropzone = container.querySelector('[role="presentation"]')

    // Simulate drag enter
    if (dropzone) {
      fireEvent.dragEnter(dropzone, {
        dataTransfer: {
          items: [{ kind: 'file', type: 'application/pdf' }],
        },
      })

      expect(screen.getByText(/Drop the file here/i)).toBeInTheDocument()
    }
  })
})
