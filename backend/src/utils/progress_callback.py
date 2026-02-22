"""
Progress callback system for tracking long-running operations.
Allows async generators to emit progress updates during processing.
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum


class ProgressEventType(str, Enum):
    """Types of progress events that can be reported"""
    IMAGE_CONVERSION = "image_conversion"
    METADATA_EXTRACTION = "metadata_extraction"
    TOPIC_EXTRACTION = "topic_extraction"
    MARKDOWN_GENERATION = "markdown_generation"
    FILE_SAVING = "file_saving"
    PUBLIC_DATA_EXTRACTION = "public_data_extraction"


class ProgressCallback:
    """
    Thread-safe callback for tracking progress of long-running operations.
    Supports both sync callbacks (from existing code) and async iteration.

    Usage:
        # In SSE generator:
        callback = ProgressCallback()
        task = asyncio.create_task(process_with_callback(callback))

        async for progress in callback.listen():
            yield format_sse("progress", progress)

        result = await task

        # In sync processing code:
        callback.report_progress(
            ProgressEventType.IMAGE_CONVERSION,
            current=5,
            total=10,
            message="Converted 5/10 pages"
        )
    """

    def __init__(self):
        self._queue: asyncio.Queue = asyncio.Queue()
        self._completed = False

    def report_progress(
        self,
        event_type: Optional[str],
        current: Optional[int] = None,
        total: Optional[int] = None,
        message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Report progress from synchronous code.
        Safe to call from sync functions running in thread pool.

        Args:
            event_type: Type of progress event (use None to signal completion)
            current: Current progress value (e.g., page 5)
            total: Total items (e.g., 10 pages)
            message: Human-readable progress message
            metadata: Additional metadata for this progress event
        """
        # Signal completion if event_type is None
        if event_type is None:
            self.mark_complete()
            return

        progress_data = {
            "type": event_type,
            "current": current,
            "total": total,
            "message": message,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat()
        }

        # Use thread-safe put_nowait via call_soon_threadsafe
        try:
            loop = asyncio.get_event_loop()
            loop.call_soon_threadsafe(
                self._queue.put_nowait,
                progress_data
            )
        except RuntimeError:
            # No event loop in this thread - this is expected
            # in some edge cases, just skip progress update
            pass

    def mark_complete(self):
        """Mark processing as complete - signals listener to stop"""
        self._completed = True
        try:
            loop = asyncio.get_event_loop()
            loop.call_soon_threadsafe(
                self._queue.put_nowait,
                None  # Sentinel value for completion
            )
        except RuntimeError:
            pass

    async def listen(self):
        """
        Async generator that yields progress updates.
        Used by SSE generator to stream events.

        Yields:
            Progress dictionaries with type, current, total, message, timestamp

        Stops when:
            - mark_complete() is called
            - Timeout occurs (30 seconds with no progress)
        """
        while True:
            try:
                # Wait for next progress update with timeout
                progress = await asyncio.wait_for(
                    self._queue.get(),
                    timeout=30.0
                )

                if progress is None:  # Completion sentinel
                    break

                yield progress

            except asyncio.TimeoutError:
                # No progress for 30s, continue waiting
                # This is normal for long-running operations like LLM API calls
                continue
            except asyncio.CancelledError:
                # Stream cancelled (client disconnected)
                break
