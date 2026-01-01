# AI-Shark Frontend

React + TypeScript frontend for the AI-Shark VC Document Analyzer.

## Tech Stack

- **React 19** with TypeScript
- **Vite** - Build tool
- **Material-UI (MUI) v7** - Component library
- **Redux Toolkit** - State management
- **React Router** - Routing
- **Axios** - HTTP client
- **React Dropzone** - File uploads

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
npm install
```

### Development

Start the development server (with API proxy to backend):

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

API requests to `/api/*` will be proxied to `http://localhost:8000` (FastAPI backend).

### Build

Build for production:

```bash
npm run build
```

Output will be in `dist/` directory.

### Environment Variables

Create a `.env` file:

```env
VITE_API_URL=/api
```

## Project Structure

```
src/
├── api/              # API client and endpoints
│   ├── client.ts
│   └── endpoints/
├── components/       # Reusable React components
│   ├── FileUpload/
│   ├── Layout/
│   └── common/
├── pages/           # Page components
│   ├── PitchDeckPage.tsx
│   └── NotFoundPage.tsx
├── store/           # Redux store
│   ├── index.ts
│   ├── hooks.ts
│   └── slices/
├── types/           # TypeScript types
│   ├── api.ts
│   └── models.ts
├── utils/           # Utilities and constants
│   └── constants.ts
├── App.tsx          # Root component
└── main.tsx         # Entry point
```

## Features Implemented

### Phase 1: Pitch Deck Processing

- ✅ Drag-and-drop file upload (PDF/PPT/PPTX)
- ✅ File size validation (100MB max)
- ✅ File type validation
- ✅ Upload progress indication
- ✅ Job status polling (every 2 seconds)
- ✅ Display processing results
- ✅ Company metadata display
- ✅ Generated files download

## API Integration

The frontend communicates with the FastAPI backend via REST APIs:

- `POST /api/v1/documents/pitch-deck` - Upload pitch deck
- `GET /api/v1/jobs/{job_id}/status` - Poll job status
- `GET /api/v1/files/download/{company}/{file}` - Download files

## State Management

Redux Toolkit is used for global state:

- `pitchDeckSlice` - Manages pitch deck upload/processing state
- `uiSlice` - Manages UI state (sidebar, theme, etc.)

Local storage is used for persistence.

## Styling

Material-UI theme with custom configuration for premium look:

- Custom color palette
- Typography settings (Inter font family)
- Component overrides
- Shadow system

## Next Steps

After Phase 1 is complete:

- Phase 2: Additional Documents Upload
- Phase 3: Multi-Agent Analysis
- Phase 4: Founder Simulation
- Phase 5: Final Memo Generation
