import React, { useState, useEffect } from "react";
import { Icon } from "@iconify/react";

import { DragDropZone } from "../components/FileUpload/DragDropZone";
import { Button } from "../components/ui/Button";
import { Card, CardContent } from "../components/ui/Card";
import { Alert } from "../components/ui/Alert";
import { Badge } from "../components/ui/Badge";
import { ProgressBar } from "../components/ui/ProgressBar";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import {
    setJobId,
    updateStatus,
    setResult,
    setError,
    reset,
} from "../store/slices/pitchDeckSlice";
import { documentsApi } from "../api/endpoints/documents";
import { POLLING } from "../utils/constants";

export const PitchDeckPage: React.FC = () => {
    const dispatch = useAppDispatch();
    const pitchDeck = useAppSelector((state) => state.pitchDeck);
    const [polling, setPolling] = useState(false);

    // Handle file upload
    const handleFileSelect = async (file: File) => {
        try {
            dispatch(
                updateStatus({
                    status: "uploading",
                    progressMessage: "Uploading file...",
                })
            );

            const response = await documentsApi.uploadPitchDeck(file);
            dispatch(setJobId(response.job_id));
            setPolling(true);
        } catch (error: any) {
            dispatch(setError(error.response?.data?.detail || "Upload failed"));
        }
    };

    // Poll job status
    useEffect(() => {
        if (!polling || !pitchDeck.jobId) return;

        const pollInterval = setInterval(async () => {
            try {
                const status = await documentsApi.getJobStatus(
                    pitchDeck.jobId!
                );

                dispatch(
                    updateStatus({
                        status: status.status as any,
                        progressMessage: status.progress_message,
                    })
                );

                if (status.status === "completed" && status.result) {
                    dispatch(
                        setResult({
                            companyName: status.result.company_name,
                            files: status.result.files_created,
                            metadata: {
                                company_name: status.result.company_name,
                                ...status.result.metadata,
                            },
                        })
                    );
                    setPolling(false);
                } else if (status.status === "failed") {
                    dispatch(setError(status.error || "Processing failed"));
                    setPolling(false);
                }
            } catch (error: any) {
                console.error("Polling error:", error);
                dispatch(setError("Failed to fetch job status"));
                setPolling(false);
            }
        }, POLLING.INTERVAL_MS);

        return () => clearInterval(pollInterval);
    }, [polling, pitchDeck.jobId, dispatch]);

    // Handle reset
    const handleReset = () => {
        dispatch(reset());
        setPolling(false);
    };

    return (
        <div className="min-h-screen bg-slate-50">
            <div className="max-w-6xl mx-auto px-6 py-8">
                {/* Header */}
                <div className="mb-8">
                    <Badge variant="primary" className="mb-4">
                        Phase 1
                    </Badge>
                    <h1 className="text-4xl font-semibold tracking-tight text-slate-900 mb-3">
                        Pitch Deck Analysis
                    </h1>
                    <p className="text-lg text-slate-600 max-w-3xl">
                        Upload your pitch deck (PDF or PowerPoint) to extract
                        company metadata, table of contents, and structured
                        analysis.
                    </p>
                </div>

                {/* Upload Zone */}
                {pitchDeck.status === "idle" && (
                    <div className="my-8">
                        <DragDropZone onFileSelect={handleFileSelect} />
                    </div>
                )}

                {/* Processing Status */}
                {(pitchDeck.status === "uploading" ||
                    pitchDeck.status === "processing") && (
                    <Card className="my-8">
                        <CardContent>
                            <div className="flex items-center mb-4">
                                <h2 className="text-xl font-semibold text-slate-900 flex-1">
                                    Processing Pitch Deck...
                                </h2>
                                <div className="animate-spin">
                                    <Icon
                                        icon="lucide:loader-2"
                                        className="text-blue-600"
                                        width="24"
                                    />
                                </div>
                            </div>
                            <ProgressBar indeterminate className="my-4" />
                            <p className="text-sm text-slate-600">
                                {pitchDeck.progressMessage}
                            </p>
                        </CardContent>
                    </Card>
                )}

                {/* Error */}
                {pitchDeck.status === "failed" && (
                    <div className="my-8">
                        <Alert type="error" title="Processing Failed">
                            <div className="flex items-center justify-between">
                                <span>{pitchDeck.error}</span>
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={handleReset}
                                    className="ml-4"
                                >
                                    Try Again
                                </Button>
                            </div>
                        </Alert>
                    </div>
                )}

                {/* Results */}
                {pitchDeck.status === "completed" && pitchDeck.companyName && (
                    <Card className="my-8" shadow="xl">
                        <CardContent>
                            <div className="flex items-center mb-6">
                                <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center mr-3">
                                    <Icon
                                        icon="lucide:check-circle"
                                        className="text-green-600"
                                        width="24"
                                    />
                                </div>
                                <h2 className="text-2xl font-semibold text-slate-900">
                                    Processing Complete
                                </h2>
                            </div>

                            {/* Company Info */}
                            <div className="mb-6 p-6 bg-slate-50 rounded-xl border border-slate-200">
                                <h3 className="text-xl font-semibold text-slate-900 mb-4">
                                    {pitchDeck.companyName}
                                </h3>
                                {pitchDeck.metadata && (
                                    <div className="space-y-2">
                                        {pitchDeck.metadata.sector && (
                                            <p className="text-sm text-slate-600">
                                                <strong className="font-medium text-slate-900">
                                                    Sector:
                                                </strong>{" "}
                                                {pitchDeck.metadata.sector}
                                            </p>
                                        )}
                                        {pitchDeck.metadata.website && (
                                            <p className="text-sm text-slate-600">
                                                <strong className="font-medium text-slate-900">
                                                    Website:
                                                </strong>{" "}
                                                {pitchDeck.metadata.website}
                                            </p>
                                        )}
                                        {pitchDeck.metadata.founding_year && (
                                            <p className="text-sm text-slate-600">
                                                <strong className="font-medium text-slate-900">
                                                    Founded:
                                                </strong>{" "}
                                                {
                                                    pitchDeck.metadata
                                                        .founding_year
                                                }
                                            </p>
                                        )}
                                        {pitchDeck.metadata.location && (
                                            <p className="text-sm text-slate-600">
                                                <strong className="font-medium text-slate-900">
                                                    Location:
                                                </strong>{" "}
                                                {pitchDeck.metadata.location}
                                            </p>
                                        )}
                                    </div>
                                )}
                            </div>

                            {/* Files List */}
                            <h3 className="text-lg font-semibold text-slate-900 mb-4">
                                Generated Files
                            </h3>
                            <div className="space-y-3">
                                {pitchDeck.files.map((file) => {
                                    const fileName =
                                        file.split("/").pop() || file;
                                    return (
                                        <div
                                            key={file}
                                            className="flex items-center justify-between p-4 bg-white rounded-lg border border-slate-200 hover:border-slate-300 transition-colors"
                                        >
                                            <div className="flex items-center gap-3 flex-1 min-w-0">
                                                <div className="shrink-0">
                                                    <Icon
                                                        icon="lucide:file-text"
                                                        className="text-blue-600"
                                                        width="24"
                                                    />
                                                </div>
                                                <div className="min-w-0 flex-1">
                                                    <p className="text-sm font-medium text-slate-900 truncate">
                                                        {fileName}
                                                    </p>
                                                    <p className="text-xs text-slate-500 truncate">
                                                        {file}
                                                    </p>
                                                </div>
                                            </div>
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                onClick={() =>
                                                    window.open(
                                                        documentsApi.downloadFile(
                                                            pitchDeck.companyName!,
                                                            fileName
                                                        ),
                                                        "_blank"
                                                    )
                                                }
                                                className="ml-4 shrink-0"
                                            >
                                                <Icon
                                                    icon="lucide:download"
                                                    width="16"
                                                />
                                                Download
                                            </Button>
                                        </div>
                                    );
                                })}
                            </div>

                            {/* Reset Button */}
                            <div className="mt-8 text-center">
                                <Button variant="outline" onClick={handleReset}>
                                    Process Another Pitch Deck
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                )}
            </div>
        </div>
    );
};
