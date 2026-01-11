import React, { useState, useEffect } from "react";
import { Icon } from "@iconify/react";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import { DragDropZone } from "../components/FileUpload/DragDropZone";
import { documentsApi } from "../api/endpoints/documents";
import { analysisApi } from "../api/endpoints/analysis";
import { simulationApi } from "../api/endpoints/simulation";
import { POLLING } from "../utils/constants";
import type { QuestionnaireResult } from "../types/models";
import {
    updatePhaseStatus,
    updateAgentWeights,
    applyWeightTemplate,
    setSimulationMode,
    // removeDocument, // Commented out - used in Phase 2 (Additional Documents)
    setUploadJobId,
    updateUploadStatus,
    setUploadResult,
    setUploadError,
    resetUpload,
    setAvailableAgents,
    toggleAgentSelection,
    setAnalysisJobId,
    setAnalysisResult,
    setAnalysisError,
    setSimulationJobId,
    setSimulationResult,
    setSimulationError,
    setMemoJobId,
    setMemoResult,
    setMemoError,
} from "../store/slices/analysisSlice";

// Define all 4 agent cards - always shown regardless of availability
const ALL_AGENTS = [
    {
        agent_type: "market",
        agent_name: "Market Analysis Agent",
        description:
            "Analyzes TAM, SAM, CAGR and competitive landscape density.",
        color: "blue",
        icon: "lucide:trending-up",
    },
    {
        agent_type: "tech",
        agent_name: "Technical Analysis Agent",
        description:
            "Evaluates architecture stack, IP defensibility, and roadmap feasibility.",
        color: "purple",
        icon: "lucide:cpu",
    },
    {
        agent_type: "risk",
        agent_name: "Risk Assessment Agent",
        description:
            "Identifies regulatory hurdles, execution risks, and cap table issues.",
        color: "orange",
        icon: "lucide:shield-alert",
    },
    {
        agent_type: "business",
        agent_name: "Business Analysis Agent",
        description:
            "Audits unit economics, GTM strategy, and financial projections.",
        color: "emerald",
        icon: "lucide:briefcase",
    },
] as const;

// Helper to check if questionnaire is available for Phase 4
const isQuestionnaireAvailable = (
    questionnaire?: QuestionnaireResult
): boolean => {
    if (!questionnaire) return false;
    return (
        questionnaire.success ||
        questionnaire.metadata?.reason === "skip_generation"
    );
};

export const AnalysisPage: React.FC = () => {
    const dispatch = useAppDispatch();
    const {
        metadata,
        // documents, // Commented out - used in Phase 2 (Additional Documents)
        agentWeights,
        simulationMode,
        phases,
        uploadJobId,
        uploadStatus,
        uploadProgress,
        companyName,
        availableAgents,
        selectedAgents,
        analysisJobId,
        simulationJobId,
        memoJobId,
    } = useAppSelector((state) => state.analysis);

    const [sliderValues, setSliderValues] = useState(agentWeights);
    const [uploadPolling, setUploadPolling] = useState(false);
    const [analysisPolling, setAnalysisPolling] = useState(false);
    const [simulationPolling, setSimulationPolling] = useState(false);
    const [memoPolling, setMemoPolling] = useState(false);
    const [showQuestionnaireError, setShowQuestionnaireError] = useState(false);
    const [showQuestionnairePreview, setShowQuestionnairePreview] =
        useState(false);

    // Extract questionnaire data
    const questionnaireResult = phases.phase3.questionnaire;
    const hasQuestionnaire = questionnaireResult?.success || false;
    const questionnaireError = questionnaireResult?.error_message || null;
    const isSkippedGeneration =
        questionnaireResult?.metadata?.reason === "skip_generation";

    // Handle file upload
    const handleFileSelect = async (file: File) => {
        try {
            dispatch(
                updateUploadStatus({
                    status: "uploading",
                    progressMessage: "Uploading file...",
                })
            );

            const response = await documentsApi.uploadPitchDeck(file);
            dispatch(setUploadJobId(response.job_id));
            setUploadPolling(true);
        } catch (error: any) {
            dispatch(
                setUploadError(error.response?.data?.detail || "Upload failed")
            );
        }
    };

    // Poll job status
    useEffect(() => {
        if (!uploadPolling || !uploadJobId) return;

        const pollInterval = setInterval(async () => {
            try {
                const status = await documentsApi.getJobStatus(uploadJobId);

                dispatch(
                    updateUploadStatus({
                        status: status.status as any,
                        progressMessage: status.progress_message,
                    })
                );

                if (status.status === "completed" && status.result) {
                    dispatch(
                        setUploadResult({
                            companyName:
                                status.result.company_name ||
                                status.result.metadata?.startup_name,
                            metadata: {
                                company_name: status.result.company_name,
                                startup_name:
                                    status.result.metadata?.startup_name,
                                sector: status.result.metadata?.sector,
                                sub_sector: status.result.metadata?.sub_sector,
                                website: status.result.metadata?.website,
                                ...status.result.metadata,
                            },
                            files: status.result.files_created || [],
                        })
                    );
                    setUploadPolling(false);
                } else if (status.status === "failed") {
                    dispatch(
                        setUploadError(status.error || "Processing failed")
                    );
                    setUploadPolling(false);
                }
            } catch (error: any) {
                console.error("Polling error:", error);
                dispatch(setUploadError("Failed to fetch job status"));
                setUploadPolling(false);
            }
        }, POLLING.INTERVAL_MS);

        return () => clearInterval(pollInterval);
    }, [uploadPolling, uploadJobId, dispatch]);

    // Discover agents on mount
    useEffect(() => {
        const discoverAgents = async () => {
            try {
                const response = await analysisApi.discoverAgents();
                dispatch(setAvailableAgents(response.agents));
            } catch (error: any) {
                console.error("Failed to discover agents:", error);
            }
        };

        discoverAgents();
    }, [dispatch]);

    // Poll analysis job status
    useEffect(() => {
        if (!analysisPolling || !analysisJobId) return;

        const pollInterval = setInterval(async () => {
            try {
                const status = await documentsApi.getJobStatus(analysisJobId);

                dispatch(
                    updatePhaseStatus({
                        phaseId: "phase3",
                        status: status.status as any,
                        progressMessage: status.progress_message,
                    })
                );

                if (status.status === "completed" && status.result) {
                    dispatch(setAnalysisResult(status.result));

                    // Check for questionnaire errors and show modal
                    const result = status.result as Record<string, unknown>;
                    const questionnaire = result.questionnaire as
                        | QuestionnaireResult
                        | undefined;
                    if (
                        questionnaire &&
                        !questionnaire.success &&
                        questionnaire.metadata?.reason !== "skip_generation"
                    ) {
                        setShowQuestionnaireError(true);
                    }

                    setAnalysisPolling(false);
                } else if (status.status === "failed") {
                    dispatch(
                        setAnalysisError(status.error || "Analysis failed")
                    );
                    setAnalysisPolling(false);
                }
            } catch (error: any) {
                console.error("Analysis polling error:", error);
                dispatch(setAnalysisError("Failed to fetch analysis status"));
                setAnalysisPolling(false);
            }
        }, POLLING.INTERVAL_MS);

        return () => clearInterval(pollInterval);
    }, [analysisPolling, analysisJobId, dispatch]);

    // Poll simulation job status
    useEffect(() => {
        if (!simulationPolling || !simulationJobId) return;

        const pollInterval = setInterval(async () => {
            try {
                const status = await documentsApi.getJobStatus(simulationJobId);

                dispatch(
                    updatePhaseStatus({
                        phaseId: "phase4",
                        status: status.status as any,
                        progressMessage: status.progress_message,
                    })
                );

                if (status.status === "completed" && status.result) {
                    dispatch(setSimulationResult(status.result));
                    setSimulationPolling(false);
                } else if (status.status === "failed") {
                    dispatch(
                        setSimulationError(status.error || "Simulation failed")
                    );
                    setSimulationPolling(false);
                }
            } catch (error: any) {
                console.error("Simulation polling error:", error);
                dispatch(
                    setSimulationError("Failed to fetch simulation status")
                );
                setSimulationPolling(false);
            }
        }, POLLING.INTERVAL_MS);

        return () => clearInterval(pollInterval);
    }, [simulationPolling, simulationJobId, dispatch]);

    // Poll memo generation job status
    useEffect(() => {
        if (!memoPolling || !memoJobId) return;

        const pollInterval = setInterval(async () => {
            try {
                const status = await documentsApi.getJobStatus(memoJobId);

                dispatch(
                    updatePhaseStatus({
                        phaseId: "phase5",
                        status: status.status as any,
                        progressMessage: status.progress_message,
                    })
                );

                if (status.status === "completed" && status.result) {
                    dispatch(setMemoResult(status.result));
                    setMemoPolling(false);
                } else if (status.status === "failed") {
                    dispatch(
                        setMemoError(status.error || "Memo generation failed")
                    );
                    setMemoPolling(false);
                }
            } catch (error: any) {
                console.error("Memo polling error:", error);
                dispatch(setMemoError("Failed to fetch memo generation status"));
                setMemoPolling(false);
            }
        }, POLLING.INTERVAL_MS);

        return () => clearInterval(pollInterval);
    }, [memoPolling, memoJobId, dispatch]);

    // Sync local slider state with Redux when templates are applied
    useEffect(() => {
        setSliderValues(agentWeights);
    }, [agentWeights]);

    // Handle reset
    const handleResetUpload = () => {
        dispatch(resetUpload());
        setUploadPolling(false);
    };

    const handleRunAnalysis = async () => {
        if (!companyName || selectedAgents.length === 0) {
            dispatch(setAnalysisError("Please select at least one agent"));
            return;
        }

        try {
            const response = await analysisApi.runAnalysis({
                company_name: companyName,
                selected_agents: selectedAgents,
            });

            dispatch(setAnalysisJobId(response.job_id));
            setAnalysisPolling(true);
        } catch (error: any) {
            dispatch(
                setAnalysisError(
                    error.response?.data?.detail || "Failed to start analysis"
                )
            );
        }
    };

    const handleSimulateQA = async () => {
        if (!companyName) {
            dispatch(setSimulationError("Company name is required"));
            return;
        }

        try {
            const response = await simulationApi.simulateQA(companyName);
            dispatch(setSimulationJobId(response.job_id));
            setSimulationPolling(true);
        } catch (error: any) {
            dispatch(
                setSimulationError(
                    error.response?.data?.detail || "Failed to start simulation"
                )
            );
        }
    };

    const handleDirectQAUpload = async (file: File) => {
        if (!companyName) {
            dispatch(setSimulationError("Company name is required"));
            return;
        }

        try {
            const response = await simulationApi.uploadDirectQA(
                file,
                companyName
            );
            dispatch(setSimulationJobId(response.job_id));
            setSimulationPolling(true);
        } catch (error: any) {
            dispatch(
                setSimulationError(
                    error.response?.data?.detail ||
                        "Failed to upload Q&A document"
                )
            );
        }
    };

    const handleGenerateMemo = async () => {
        if (!companyName) {
            dispatch(setMemoError("Company name is required"));
            return;
        }

        // Convert agentWeights to simple key-value pairs
        const weights: { [key: string]: number } = {};
        Object.entries(sliderValues).forEach(([key, config]) => {
            weights[key] = config.weight;
        });

        try {
            const response = await analysisApi.generateMemo({
                company_name: companyName,
                agent_weights: weights,
            });

            dispatch(setMemoJobId(response.job_id));
            setMemoPolling(true);
        } catch (error: any) {
            dispatch(
                setMemoError(
                    error.response?.data?.detail || "Failed to start memo generation"
                )
            );
        }
    };

    const handleWeightChange = (
        agent: keyof typeof agentWeights,
        value: number
    ) => {
        setSliderValues({
            ...sliderValues,
            [agent]: { ...sliderValues[agent], weight: value },
        });
    };

    const autoBalanceWeights = () => {
        const total = Object.values(sliderValues).reduce(
            (sum, w) => sum + w.weight,
            0
        );
        const balanced = Object.entries(sliderValues).reduce(
            (acc, [key, config]) => ({
                ...acc,
                [key]: {
                    ...config,
                    weight: Math.round((config.weight / total) * 100),
                },
            }),
            {} as typeof sliderValues
        );
        setSliderValues(balanced);
        dispatch(updateAgentWeights(balanced));
    };

    const getTotalWeight = () => {
        return Object.values(sliderValues).reduce(
            (sum, w) => sum + w.weight,
            0
        );
    };

    const getPhaseIndicatorClass = (status: string) => {
        switch (status) {
            case "completed":
                return "border-green-200 bg-green-50 text-green-600";
            case "running":
                return "border-blue-200 bg-blue-50 text-blue-600 ring-4 ring-white";
            case "failed":
                return "border-red-200 bg-red-50 text-red-600";
            default:
                return "border-slate-200 bg-white text-slate-500";
        }
    };

    const getStatusBadge = (status: string) => {
        switch (status) {
            case "completed":
                return (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-medium bg-green-50 text-green-700 border border-green-100">
                        <span className="w-1.5 h-1.5 rounded-full bg-green-500"></span>
                        Completed
                    </span>
                );
            case "running":
                return (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-medium bg-blue-50 text-blue-600 border border-blue-200">
                        <Icon
                            icon="lucide:loader-2"
                            width={12}
                            className="animate-spin"
                        />
                        Processing
                    </span>
                );
            case "failed":
                return (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-medium bg-red-50 text-red-700 border border-red-100">
                        <Icon icon="lucide:alert-circle" width={12} />
                        Failed
                    </span>
                );
            default:
                return null;
        }
    };

    // Questionnaire Card Component
    const QuestionnaireCard: React.FC<{
        result: QuestionnaireResult;
        companyName: string;
    }> = ({ result, companyName }) => {
        const handlePreview = () => {
            setShowQuestionnairePreview(true);
        };

        const handleDownload = () => {
            const link = document.createElement("a");
            link.href = `/api/v1/files/${companyName}/founders-checklist.md`;
            link.download = "founders-checklist.md";
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        };

        const fileName =
            result.markdown_file?.split("/").pop() || "founders-checklist.md";
        const processingTime = result.processing_time.toFixed(2);
        const fileSize = result.metadata?.file_size
            ? `${(result.metadata.file_size / 1024).toFixed(1)} KB`
            : "Size unknown";

        return (
            <div className="flex bg-white border-slate-200 border rounded-lg mb-4 pt-3 pr-3 pb-3 pl-3 shadow-sm items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-blue-50 text-blue-500 flex items-center justify-center border border-blue-100">
                        <Icon icon="lucide:file-text" width={20} />
                    </div>
                    <div>
                        <div className="text-sm font-medium text-slate-900">
                            {fileName}
                        </div>
                        <div className="text-xs text-slate-400">
                            {fileSize} • Processed in {processingTime}s
                        </div>
                    </div>
                </div>
                <div className="flex gap-2">
                    <button
                        onClick={handlePreview}
                        className="p-2 text-slate-400 hover:text-blue-600 transition-colors"
                        title="Preview questionnaire"
                    >
                        <Icon icon="lucide:eye" width={16} />
                    </button>
                    <button
                        onClick={handleDownload}
                        className="p-2 text-slate-400 hover:text-blue-600 transition-colors"
                        title="Download questionnaire"
                    >
                        <Icon icon="lucide:download" width={16} />
                    </button>
                </div>
            </div>
        );
    };

    // Questionnaire Error Modal Component
    const QuestionnaireErrorModal: React.FC<{
        error: string;
        onClose: () => void;
    }> = ({ error, onClose }) => {
        return (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                <div className="bg-white rounded-xl p-6 max-w-md mx-4 shadow-2xl">
                    <div className="flex items-start gap-4 mb-4">
                        <div className="w-12 h-12 rounded-full bg-red-50 flex items-center justify-center flex-shrink-0">
                            <Icon
                                icon="lucide:alert-circle"
                                width={24}
                                className="text-red-600"
                            />
                        </div>
                        <div className="flex-1">
                            <h3 className="text-lg font-semibold text-slate-900 mb-2">
                                Questionnaire Generation Failed
                            </h3>
                            <p className="text-sm text-slate-600 leading-relaxed mb-3">
                                {error}
                            </p>
                            <p className="text-xs text-slate-500">
                                The analysis was successful, but we
                                couldn&apos;t generate the founder
                                questionnaire. You can proceed to the next step
                                without it.
                            </p>
                        </div>
                    </div>
                    <div className="flex gap-3 justify-end">
                        <button
                            onClick={onClose}
                            className="px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 rounded-lg transition-colors"
                        >
                            Close
                        </button>
                    </div>
                </div>
            </div>
        );
    };

    // Questionnaire Preview Modal Component
    const QuestionnairePreviewModal: React.FC<{
        companyName: string;
        onClose: () => void;
    }> = ({ companyName, onClose }) => {
        const [content, setContent] = useState<string>("");
        const [loading, setLoading] = useState(true);
        const [error, setError] = useState<string | null>(null);

        useEffect(() => {
            const fetchContent = async () => {
                try {
                    const response = await fetch(
                        `/api/v1/files/${companyName}/founders-checklist.md`
                    );
                    if (!response.ok) throw new Error("Failed to load file");
                    const text = await response.text();
                    setContent(text);
                } catch (err) {
                    setError("Failed to load questionnaire content");
                } finally {
                    setLoading(false);
                }
            };
            fetchContent();
        }, [companyName]);

        const handleDownload = () => {
            const link = document.createElement("a");
            link.href = `/api/v1/files/${companyName}/founders-checklist.md`;
            link.download = "founders-checklist.md";
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        };

        return (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                <div className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] flex flex-col shadow-2xl">
                    <div className="flex items-center justify-between p-6 border-b border-slate-200">
                        <div className="flex items-center gap-3">
                            <Icon
                                icon="lucide:file-text"
                                width={24}
                                className="text-blue-600"
                            />
                            <div>
                                <h2 className="text-lg font-semibold text-slate-900">
                                    Founder Questionnaire
                                </h2>
                                <p className="text-xs text-slate-500">
                                    Due Diligence Checklist
                                </p>
                            </div>
                        </div>
                        <button
                            onClick={onClose}
                            className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
                        >
                            <Icon
                                icon="lucide:x"
                                width={20}
                                className="text-slate-500"
                            />
                        </button>
                    </div>

                    <div className="flex-1 overflow-y-auto p-6 bg-slate-50">
                        {loading && (
                            <div className="flex items-center justify-center h-64">
                                <Icon
                                    icon="lucide:loader-2"
                                    width={32}
                                    className="animate-spin text-blue-600"
                                />
                            </div>
                        )}
                        {error && (
                            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                                <p className="text-sm text-red-700">{error}</p>
                            </div>
                        )}
                        {!loading && !error && (
                            <div className="prose prose-sm max-w-none bg-white rounded-lg p-6 border border-slate-200">
                                <pre className="whitespace-pre-wrap text-sm text-slate-700 font-mono">
                                    {content}
                                </pre>
                            </div>
                        )}
                    </div>

                    <div className="flex items-center justify-end gap-3 p-6 border-t border-slate-200">
                        <button
                            onClick={onClose}
                            className="px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
                        >
                            Close
                        </button>
                        <button
                            onClick={handleDownload}
                            className="px-4 py-2 text-sm font-medium bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors inline-flex items-center gap-2"
                        >
                            <Icon icon="lucide:download" width={16} />
                            Download
                        </button>
                    </div>
                </div>
            </div>
        );
    };

    return (
        <div className="min-h-screen bg-slate-50 antialiased selection:bg-blue-100 selection:text-blue-900">
            {/* Navigation */}
            <nav className="fixed top-0 w-full z-50 bg-white/85 backdrop-blur-sm border-b border-slate-200">
                <div className="flex h-14 max-w-7xl mx-auto px-6 items-center justify-between">
                    <div className="flex items-center gap-1 group cursor-pointer">
                        <a href="/" className="flex items-center gap-2">
                            <Icon
                                icon="lucide:zap"
                                width={20}
                                className="text-blue-600"
                            />
                            <span className="text-sm font-medium tracking-tight text-slate-900">
                                AI-Shark
                            </span>
                        </a>
                        <span className="mx-2 text-slate-300">/</span>
                        <span className="text-sm text-slate-500">
                            New Analysis
                        </span>
                    </div>

                    <div className="flex items-center gap-4">
                        <button className="text-slate-500 hover:text-slate-900 transition-colors">
                            <Icon icon="lucide:bell" width={18} />
                        </button>
                        <div className="flex text-xs font-medium text-blue-700 bg-blue-100 w-8 h-8 border-blue-200 border rounded-full items-center justify-center">
                            JD
                        </div>
                    </div>
                </div>
            </nav>

            {/* Main Content */}
            <main className="pt-24 max-w-3xl mx-auto px-6">
                <header className="mb-10">
                    <h1 className="text-3xl font-semibold tracking-tight text-slate-900 mb-2">
                        Deal Analysis Pipeline
                    </h1>
                    <p className="text-sm text-slate-500">
                        Configure agents and simulate founder interviews to
                        generate your investment memo.
                    </p>
                </header>

                <div className="flex flex-col gap-8 relative">
                    {/* PHASE 1: Pitch Deck Processing */}
                    <div className="relative z-10">
                        <div className="phase-connector"></div>

                        <div className="flex gap-6">
                            <div
                                className={`flex-shrink-0 w-12 h-12 rounded-full border flex items-center justify-center font-medium text-sm z-10 shadow-sm ${getPhaseIndicatorClass(
                                    phases.phase1.status
                                )}`}
                            >
                                {phases.phase1.status === "completed" ? (
                                    <Icon icon="lucide:check" width={20} />
                                ) : phases.phase1.status === "running" ? (
                                    <Icon
                                        icon="lucide:loader-2"
                                        width={20}
                                        className="animate-spin"
                                    />
                                ) : (
                                    "01"
                                )}
                            </div>

                            <div className="bg-white border border-slate-200 rounded-xl w-full overflow-hidden shadow-sm">
                                <div className="p-5 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
                                    <div>
                                        <h2 className="text-sm font-semibold text-slate-900">
                                            1. Pitch Deck Processing
                                        </h2>
                                        <p className="text-xs text-slate-500 mt-0.5">
                                            Upload your pitch deck to begin
                                            analysis.
                                        </p>
                                    </div>
                                    {getStatusBadge(phases.phase1.status)}
                                </div>

                                <div className="p-5">
                                    {/* Upload Zone - Show only when idle */}
                                    {uploadStatus === "idle" && (
                                        <DragDropZone
                                            onFileSelect={handleFileSelect}
                                            size="sm"
                                        />
                                    )}

                                    {/* Processing Status */}
                                    {(uploadStatus === "uploading" ||
                                        uploadStatus === "processing") && (
                                        <div className="py-8">
                                            <div className="flex items-center justify-center mb-4">
                                                <Icon
                                                    icon="lucide:loader-2"
                                                    width={32}
                                                    className="text-blue-600 animate-spin"
                                                />
                                            </div>
                                            <p className="text-center text-sm text-slate-600 mb-2">
                                                {uploadProgress ||
                                                    "Processing pitch deck..."}
                                            </p>
                                            <div className="w-full bg-slate-100 h-1 rounded-full overflow-hidden">
                                                <div className="h-full bg-blue-600 w-2/3 animate-pulse"></div>
                                            </div>
                                        </div>
                                    )}

                                    {/* Error State */}
                                    {uploadStatus === "failed" && (
                                        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                                            <div className="flex items-start gap-3">
                                                <Icon
                                                    icon="lucide:alert-circle"
                                                    width={20}
                                                    className="text-red-600 mt-0.5"
                                                />
                                                <div className="flex-1">
                                                    <h4 className="text-sm font-semibold text-red-900">
                                                        Upload Failed
                                                    </h4>
                                                    <p className="text-xs text-red-700 mt-1">
                                                        {phases.phase1.error}
                                                    </p>
                                                </div>
                                                <button
                                                    onClick={handleResetUpload}
                                                    className="px-3 py-1.5 bg-white border border-red-200 text-red-700 text-xs font-medium rounded-lg hover:bg-red-50 transition-colors"
                                                >
                                                    Try Again
                                                </button>
                                            </div>
                                        </div>
                                    )}

                                    {/* Success - Show Metadata Cards */}
                                    {uploadStatus === "completed" &&
                                        metadata && (
                                            <>
                                                <div className="flex items-center justify-between p-3 rounded-lg border border-green-200 bg-green-50 mb-4">
                                                    <div className="flex items-center gap-3">
                                                        <Icon
                                                            icon="lucide:check-circle"
                                                            width={20}
                                                            className="text-green-600"
                                                        />
                                                        <span className="text-sm font-medium text-green-900">
                                                            Processing Complete
                                                        </span>
                                                    </div>
                                                    <button
                                                        onClick={
                                                            handleResetUpload
                                                        }
                                                        className="text-xs text-green-700 hover:underline"
                                                    >
                                                        Upload Different Deck
                                                    </button>
                                                </div>

                                                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                                                    <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                                                        <div className="text-[10px] uppercase tracking-wider text-slate-400 font-medium mb-1">
                                                            Company
                                                        </div>
                                                        <div className="text-xs font-semibold text-slate-700">
                                                            {metadata.startup_name ||
                                                                metadata.company_name ||
                                                                "N/A"}
                                                        </div>
                                                    </div>

                                                    <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                                                        <div className="text-[10px] uppercase tracking-wider text-slate-400 font-medium mb-1">
                                                            Sector
                                                        </div>
                                                        <div className="text-xs font-semibold text-slate-700">
                                                            {metadata.sector ||
                                                                "N/A"}
                                                        </div>
                                                    </div>

                                                    <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                                                        <div className="text-[10px] uppercase tracking-wider text-slate-400 font-medium mb-1">
                                                            Sub-sector
                                                        </div>
                                                        <div className="text-xs font-semibold text-slate-700">
                                                            {metadata.sub_sector ||
                                                                "N/A"}
                                                        </div>
                                                    </div>

                                                    <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                                                        <div className="text-[10px] uppercase tracking-wider text-slate-400 font-medium mb-1">
                                                            Website
                                                        </div>
                                                        <div className="text-xs font-semibold text-slate-700">
                                                            {metadata.website ? (
                                                                <a
                                                                    href={
                                                                        metadata.website
                                                                    }
                                                                    target="_blank"
                                                                    rel="noopener noreferrer"
                                                                    className="text-blue-600 hover:underline truncate block"
                                                                >
                                                                    {metadata.website.replace(
                                                                        /^https?:\/\//,
                                                                        ""
                                                                    )}
                                                                </a>
                                                            ) : (
                                                                "N/A"
                                                            )}
                                                        </div>
                                                    </div>
                                                </div>
                                            </>
                                        )}
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* PHASE 2: Additional Documents - COMMENTED OUT (Backend API not implemented yet)
                    <div className="relative z-10">
                        <div className="phase-connector"></div>

                        <div className="flex gap-6">
                            <div
                                className={`flex-shrink-0 w-12 h-12 rounded-full border flex items-center justify-center font-medium text-sm z-10 shadow-sm ring-4 ring-white ${getPhaseIndicatorClass(
                                    "pending"
                                )}`}
                            >
                                02
                            </div>

                            <div className="bg-white border border-slate-200 rounded-xl w-full overflow-hidden shadow-sm">
                                <div className="p-5 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
                                    <div>
                                        <h2 className="text-sm font-semibold text-slate-900">
                                            2. Additional Documents
                                        </h2>
                                        <p className="text-xs text-slate-500 mt-0.5">
                                            Financials, technical papers, or
                                            legal docs.
                                        </p>
                                    </div>
                                </div>

                                <div className="p-5">
                                    <div className="border-2 border-dashed border-slate-200 rounded-xl p-8 text-center hover:bg-slate-50 hover:border-blue-400 transition-all cursor-pointer group">
                                        <div className="w-10 h-10 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform">
                                            <Icon
                                                icon="lucide:upload-cloud"
                                                width={20}
                                            />
                                        </div>
                                        <p className="text-sm font-medium text-slate-900">
                                            Click to upload or drag and drop
                                        </p>
                                        <p className="text-xs text-slate-500 mt-1">
                                            Supports PDF, XLSX, DOCX (Max 50MB)
                                        </p>
                                    </div>

                                    {documents.additionalDocs.length > 0 && (
                                        <div className="mt-4 space-y-2">
                                            {documents.additionalDocs.map(
                                                (doc, index) => (
                                                    <div
                                                        key={index}
                                                        className="flex items-center justify-between p-2 rounded-lg border border-slate-100 bg-slate-50/50"
                                                    >
                                                        <div className="flex items-center gap-3">
                                                            <Icon
                                                                icon="lucide:file-spreadsheet"
                                                                className="text-emerald-600 ml-2"
                                                                width={16}
                                                            />
                                                            <span className="text-xs font-medium text-slate-600">
                                                                {doc}
                                                            </span>
                                                        </div>
                                                        <button
                                                            onClick={() =>
                                                                dispatch(
                                                                    removeDocument(
                                                                        doc
                                                                    )
                                                                )
                                                            }
                                                            className="text-slate-400 hover:text-red-500 px-2"
                                                        >
                                                            <Icon
                                                                icon="lucide:x"
                                                                width={14}
                                                            />
                                                        </button>
                                                    </div>
                                                )
                                            )}
                                        </div>
                                    )}

                                    <div className="mt-4 flex justify-end">
                                        <button className="px-4 py-2 bg-white border border-slate-200 text-slate-700 text-xs font-medium rounded-lg hover:bg-slate-50 hover:border-slate-300 transition-all shadow-sm">
                                            Process Documents
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    END PHASE 2 COMMENT */}

                    {/* PHASE 2: Multi-Agent Analysis (was Phase 3) */}
                    <div className="relative z-10">
                        <div className="phase-connector"></div>

                        <div className="flex gap-6">
                            <div
                                className={`flex-shrink-0 w-12 h-12 rounded-full border flex items-center justify-center font-medium text-sm z-10 shadow-sm ring-4 ring-white ${getPhaseIndicatorClass(
                                    phases.phase3.status
                                )}`}
                            >
                                {phases.phase3.status === "completed" ? (
                                    <Icon icon="lucide:check" width={20} />
                                ) : (
                                    "02"
                                )}
                            </div>

                            <div className="bg-white border border-slate-200 rounded-xl w-full overflow-hidden shadow-sm">
                                <div className="p-5 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
                                    <div>
                                        <h2 className="text-sm font-semibold text-slate-900">
                                            2. Multi-Agent Analysis
                                        </h2>
                                        <p className="text-xs text-slate-500 mt-0.5">
                                            Specialized LLM agents analyze
                                            documents independently.
                                        </p>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        {phases.phase1.status ===
                                        "completed" ? (
                                            <>
                                                <span className="text-[10px] font-medium text-slate-400">
                                                    Requires Step 1
                                                </span>
                                                <Icon
                                                    icon="lucide:check-circle-2"
                                                    className="text-green-500"
                                                    width={14}
                                                />
                                            </>
                                        ) : (
                                            <span className="text-[10px] font-medium text-red-500">
                                                Locked
                                            </span>
                                        )}
                                    </div>
                                </div>

                                <div className="p-5">
                                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
                                        {ALL_AGENTS.map((agentDef) => {
                                            // Check if this agent is discovered and available
                                            const discoveredAgent =
                                                availableAgents.find(
                                                    (a) =>
                                                        a.agent_type ===
                                                        agentDef.agent_type
                                                );
                                            const isAvailable =
                                                discoveredAgent?.available ||
                                                false;
                                            const isPhase1Complete =
                                                phases.phase1.status ===
                                                "completed";
                                            const isDisabled =
                                                !isAvailable ||
                                                !isPhase1Complete;
                                            const isSelected =
                                                selectedAgents.includes(
                                                    agentDef.agent_type
                                                );

                                            return (
                                                <div
                                                    key={agentDef.agent_type}
                                                    onClick={() => {
                                                        if (!isDisabled) {
                                                            dispatch(
                                                                toggleAgentSelection(
                                                                    agentDef.agent_type
                                                                )
                                                            );
                                                        }
                                                    }}
                                                    className={`p-4 rounded-xl border bg-white transition-all ${
                                                        isDisabled
                                                            ? "border-slate-200 opacity-50 cursor-not-allowed"
                                                            : "cursor-pointer hover:shadow-sm " +
                                                              (isSelected
                                                                  ? `border-${agentDef.color}-400 shadow-md ring-2 ring-${agentDef.color}-100`
                                                                  : `border-slate-200 hover:border-${agentDef.color}-200`)
                                                    }`}
                                                >
                                                    <div className="flex items-start justify-between mb-3">
                                                        <div
                                                            className={`p-2 rounded-lg bg-${agentDef.color}-50 text-${agentDef.color}-600`}
                                                        >
                                                            <Icon
                                                                icon={
                                                                    agentDef.icon
                                                                }
                                                                width={18}
                                                            />
                                                        </div>
                                                        {!isPhase1Complete && (
                                                            <span className="text-[9px] font-medium text-slate-400 uppercase px-2 py-1 bg-slate-100 rounded">
                                                                Locked
                                                            </span>
                                                        )}
                                                        {isPhase1Complete &&
                                                            !isAvailable && (
                                                                <span className="text-[9px] font-medium text-slate-400 uppercase px-2 py-1 bg-slate-100 rounded">
                                                                    Unavailable
                                                                </span>
                                                            )}
                                                    </div>
                                                    <h3 className="text-xs font-semibold text-slate-900">
                                                        {agentDef.agent_name}
                                                    </h3>
                                                    <p className="text-[10px] text-slate-500 mt-1 leading-relaxed">
                                                        {agentDef.description}
                                                    </p>
                                                </div>
                                            );
                                        })}
                                    </div>

                                    {/* Questionnaire Result Card - Shows after analysis completes */}
                                    {hasQuestionnaire &&
                                        questionnaireResult &&
                                        companyName && (
                                            <QuestionnaireCard
                                                result={questionnaireResult}
                                                companyName={companyName}
                                            />
                                        )}

                                    {/* Questionnaire Error State */}
                                    {questionnaireError &&
                                        phases.phase3.status === "completed" &&
                                        !isSkippedGeneration && (
                                            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
                                                <div className="flex items-start gap-3">
                                                    <Icon
                                                        icon="lucide:alert-circle"
                                                        width={20}
                                                        className="text-red-600 mt-0.5"
                                                    />
                                                    <div className="flex-1">
                                                        <h4 className="text-sm font-semibold text-red-900">
                                                            Questionnaire
                                                            Generation Issue
                                                        </h4>
                                                        <p className="text-xs text-red-700 mt-1">
                                                            {questionnaireError}
                                                        </p>
                                                        <button
                                                            onClick={() =>
                                                                setShowQuestionnaireError(
                                                                    true
                                                                )
                                                            }
                                                            className="text-xs text-red-600 hover:underline mt-2"
                                                        >
                                                            View Details
                                                        </button>
                                                    </div>
                                                </div>
                                            </div>
                                        )}

                                    {selectedAgents.length > 0 && (
                                        <div className="mb-4 p-3 bg-blue-50 border border-blue-100 rounded-lg">
                                            <p className="text-xs text-blue-700">
                                                <Icon
                                                    icon="lucide:info"
                                                    className="inline mr-1"
                                                    width={14}
                                                />
                                                {selectedAgents.length} agent
                                                {selectedAgents.length > 1
                                                    ? "s"
                                                    : ""}{" "}
                                                selected
                                            </p>
                                        </div>
                                    )}

                                    {/* Phase 3 Failed - Retry Button */}
                                    {phases.phase3.status === "failed" && (
                                        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
                                            <div className="flex items-start gap-3">
                                                <Icon
                                                    icon="lucide:alert-circle"
                                                    width={20}
                                                    className="text-red-600 mt-0.5"
                                                />
                                                <div className="flex-1">
                                                    <h4 className="text-sm font-semibold text-red-900">
                                                        Analysis Failed
                                                    </h4>
                                                    <p className="text-xs text-red-700 mt-1">
                                                        {phases.phase3.error ||
                                                            "An error occurred during multi-agent analysis"}
                                                    </p>
                                                </div>
                                                <button
                                                    onClick={handleRunAnalysis}
                                                    disabled={
                                                        selectedAgents.length ===
                                                        0
                                                    }
                                                    className="px-3 py-1.5 bg-white border border-red-200 text-red-700 text-xs font-medium rounded-lg hover:bg-red-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                                >
                                                    Retry Analysis
                                                </button>
                                            </div>
                                        </div>
                                    )}

                                    <button
                                        onClick={handleRunAnalysis}
                                        disabled={
                                            phases.phase1.status !==
                                                "completed" ||
                                            phases.phase3.status ===
                                                "running" ||
                                            selectedAgents.length === 0
                                        }
                                        className="w-full py-2.5 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-medium transition-all flex items-center justify-center gap-2 shadow-lg shadow-slate-900/10 disabled:opacity-50 disabled:cursor-not-allowed"
                                    >
                                        {phases.phase3.status === "running" ? (
                                            <>
                                                <Icon
                                                    icon="lucide:loader-2"
                                                    width={14}
                                                    className="animate-spin"
                                                />
                                                Running Analysis...
                                            </>
                                        ) : (
                                            <>
                                                <Icon
                                                    icon="lucide:play"
                                                    width={14}
                                                />
                                                Run Multi-Agent Analysis
                                            </>
                                        )}
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* PHASE 3: Founder Simulation (was Phase 4) */}
                    <div className="relative z-10">
                        <div className="phase-connector"></div>

                        <div className="flex gap-6">
                            <div
                                className={`flex-shrink-0 w-12 h-12 rounded-full border flex items-center justify-center font-medium text-sm z-10 shadow-sm ring-4 ring-white ${getPhaseIndicatorClass(
                                    phases.phase4.status
                                )}`}
                            >
                                {phases.phase4.status === "completed" ? (
                                    <Icon icon="lucide:check" width={20} />
                                ) : (
                                    "03"
                                )}
                            </div>

                            <div className="bg-white border border-slate-200 rounded-xl w-full overflow-hidden shadow-sm">
                                <div className="p-5 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
                                    <div>
                                        <h2 className="text-sm font-semibold text-slate-900">
                                            3. Data Curation
                                        </h2>
                                        <p className="text-xs text-slate-500 mt-0.5">
                                            Answer the questionnare document
                                            prepared in the previous step to
                                            prepare detailed analysis
                                        </p>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        {phases.phase3.status === "completed" &&
                                        isQuestionnaireAvailable(
                                            phases.phase3.questionnaire
                                        ) ? (
                                            <>
                                                <span className="text-[10px] font-medium text-slate-400">
                                                    Questionnaire Ready
                                                </span>
                                                <Icon
                                                    icon="lucide:check-circle-2"
                                                    className="text-green-500"
                                                    width={14}
                                                />
                                            </>
                                        ) : phases.phase3.status ===
                                          "running" ? (
                                            <>
                                                <span className="text-[10px] font-medium text-orange-500">
                                                    Waiting for Analysis
                                                </span>
                                                <Icon
                                                    icon="lucide:clock"
                                                    className="text-orange-500"
                                                    width={14}
                                                />
                                            </>
                                        ) : phases.phase3.status ===
                                          "failed" ? (
                                            <>
                                                <span className="text-[10px] font-medium text-red-500">
                                                    Analysis Failed
                                                </span>
                                                <Icon
                                                    icon="lucide:x-circle"
                                                    className="text-red-500"
                                                    width={14}
                                                />
                                            </>
                                        ) : (
                                            <>
                                                <span className="text-[10px] font-medium text-red-500">
                                                    Locked
                                                </span>
                                                <Icon
                                                    icon="lucide:lock"
                                                    className="text-red-500"
                                                    width={14}
                                                />
                                            </>
                                        )}
                                    </div>
                                </div>

                                <div className="p-5">
                                    <div className="flex bg-slate-100/50 p-1 rounded-lg border border-slate-100 mb-6 w-full sm:w-fit">
                                        <label className="flex-1 sm:flex-none cursor-pointer">
                                            <input
                                                type="radio"
                                                name="sim_mode"
                                                value="context"
                                                checked={
                                                    simulationMode === "context"
                                                }
                                                onChange={() =>
                                                    dispatch(
                                                        setSimulationMode(
                                                            "context"
                                                        )
                                                    )
                                                }
                                                className="hidden custom-radio"
                                            />
                                            <div className="px-4 py-1.5 rounded-md text-xs font-medium text-slate-500 transition-all flex items-center gap-2 border border-transparent">
                                                <div className="w-2 h-2 rounded-full border border-slate-400 radio-dot bg-transparent"></div>
                                                Simulate Response
                                            </div>
                                        </label>
                                        <label className="flex-1 sm:flex-none cursor-pointer">
                                            <input
                                                type="radio"
                                                name="sim_mode"
                                                value="direct-qa"
                                                checked={
                                                    simulationMode ===
                                                    "direct-qa"
                                                }
                                                onChange={() =>
                                                    dispatch(
                                                        setSimulationMode(
                                                            "direct-qa"
                                                        )
                                                    )
                                                }
                                                className="hidden custom-radio"
                                            />
                                            <div className="px-4 py-1.5 rounded-md text-xs font-medium text-slate-500 transition-all flex items-center gap-2 border border-transparent">
                                                <div className="w-2 h-2 rounded-full border border-slate-400 radio-dot bg-transparent"></div>
                                                Direct Q&A Upload
                                            </div>
                                        </label>
                                    </div>

                                    {simulationMode === "context" ? (
                                        <>
                                            <div className="bg-blue-50/50 border border-blue-100 rounded-lg p-4 mb-6">
                                                <div className="flex gap-3">
                                                    <div className="mt-0.5 text-blue-500">
                                                        <Icon
                                                            icon="lucide:info"
                                                            width={16}
                                                        />
                                                    </div>
                                                    <div>
                                                        <h4 className="text-xs font-semibold text-blue-900">
                                                            AI Simulation Mode
                                                        </h4>
                                                        <p className="text-[11px] leading-relaxed text-blue-700/80 mt-1">
                                                            The system will use
                                                            the questionnaire
                                                            from Phase 3 and
                                                            analysis reports to
                                                            generate contextual
                                                            Q&A responses.
                                                        </p>
                                                    </div>
                                                </div>
                                            </div>

                                            <div className="flex justify-end">
                                                <button
                                                    onClick={handleSimulateQA}
                                                    disabled={
                                                        phases.phase3.status !==
                                                            "completed" ||
                                                        !isQuestionnaireAvailable(
                                                            phases.phase3
                                                                .questionnaire
                                                        ) ||
                                                        phases.phase4.status ===
                                                            "running" ||
                                                        simulationJobId !== null
                                                    }
                                                    className="px-4 py-2 bg-white border border-slate-200 text-slate-700 text-xs font-medium rounded-lg hover:bg-slate-50 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                                                >
                                                    {phases.phase4.status ===
                                                        "running" ||
                                                    simulationJobId !== null ? (
                                                        <>
                                                            <Icon
                                                                icon="lucide:loader-2"
                                                                width={12}
                                                                className="animate-spin"
                                                            />
                                                            Generating
                                                            Responses...
                                                        </>
                                                    ) : (
                                                        <>
                                                            <Icon
                                                                icon="lucide:sparkles"
                                                                width={12}
                                                            />
                                                            Simulate
                                                            Questionnaire
                                                            Response
                                                        </>
                                                    )}
                                                </button>
                                            </div>
                                        </>
                                    ) : (
                                        <>
                                            <div className="bg-purple-50/50 border border-purple-100 rounded-lg p-4 mb-6">
                                                <div className="flex gap-3">
                                                    <div className="mt-0.5 text-purple-500">
                                                        <Icon
                                                            icon="lucide:upload"
                                                            width={16}
                                                        />
                                                    </div>
                                                    <div>
                                                        <h4 className="text-xs font-semibold text-purple-900">
                                                            Direct Upload Mode
                                                        </h4>
                                                        <p className="text-[11px] leading-relaxed text-purple-700/80 mt-1">
                                                            Upload your
                                                            pre-answered Q&A
                                                            document (MD, PDF,
                                                            or DOCX format).
                                                        </p>
                                                    </div>
                                                </div>
                                            </div>

                                            <DragDropZone
                                                onFileSelect={
                                                    handleDirectQAUpload
                                                }
                                                accept={{
                                                    "text/markdown": [".md"],
                                                    "application/pdf": [".pdf"],
                                                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                                                        [".docx"],
                                                    "text/plain": [".txt"],
                                                }}
                                                maxSize={10 * 1024 * 1024}
                                                disabled={
                                                    phases.phase3.status !==
                                                        "completed" ||
                                                    !isQuestionnaireAvailable(
                                                        phases.phase3
                                                            .questionnaire
                                                    ) ||
                                                    phases.phase4.status ===
                                                        "running" ||
                                                    simulationJobId !== null
                                                }
                                            />

                                            {(phases.phase4.status ===
                                                "running" ||
                                                simulationJobId !== null) && (
                                                <div className="mt-4 flex items-center gap-2 text-xs text-slate-600">
                                                    <Icon
                                                        icon="lucide:loader-2"
                                                        width={14}
                                                        className="animate-spin"
                                                    />
                                                    Processing uploaded Q&A
                                                    document...
                                                </div>
                                            )}
                                        </>
                                    )}

                                    {phases.phase4.status === "failed" && (
                                        <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-4">
                                            <div className="flex gap-3">
                                                <div className="mt-0.5 text-red-500">
                                                    <Icon
                                                        icon="lucide:alert-circle"
                                                        width={18}
                                                    />
                                                </div>
                                                <div className="flex-1">
                                                    <h4 className="text-sm font-semibold text-red-900">
                                                        {simulationMode ===
                                                        "context"
                                                            ? "Simulation Failed"
                                                            : "Upload Processing Failed"}
                                                    </h4>
                                                    <p className="text-xs text-red-700 mt-1">
                                                        {phases.phase4.error ||
                                                            "An error occurred during processing"}
                                                    </p>
                                                </div>
                                                <button
                                                    onClick={() => {
                                                        if (
                                                            simulationMode ===
                                                            "context"
                                                        ) {
                                                            handleSimulateQA();
                                                        }
                                                    }}
                                                    className="px-3 py-1.5 bg-white border border-red-200 text-red-700 text-xs font-medium rounded-lg hover:bg-red-50 transition-colors"
                                                >
                                                    Retry
                                                </button>
                                            </div>
                                        </div>
                                    )}

                                    {phases.phase4.status === "completed" &&
                                        phases.phase4.simulationResult && (
                                            <div className="mt-6 pt-6 border-t border-slate-100">
                                                <div className="flex items-center justify-between mb-3">
                                                    <h4 className="text-xs font-semibold text-slate-900">
                                                        Q&A Responses Generated
                                                    </h4>
                                                    <span className="text-[10px] text-green-600 flex items-center gap-1">
                                                        <Icon
                                                            icon="lucide:check-circle-2"
                                                            width={12}
                                                        />
                                                        Complete
                                                    </span>
                                                </div>
                                                <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
                                                    <div className="flex items-center justify-between">
                                                        <div className="flex items-center gap-3">
                                                            <Icon
                                                                icon="lucide:file-text"
                                                                width={20}
                                                                className="text-slate-400"
                                                            />
                                                            <div>
                                                                <p className="text-xs font-medium text-slate-900">
                                                                    founders-qa-responses.md
                                                                </p>
                                                                <p className="text-[10px] text-slate-500">
                                                                    Generated
                                                                    via{" "}
                                                                    {phases
                                                                        .phase4
                                                                        .simulationResult
                                                                        .metadata
                                                                        ?.mode ===
                                                                    "ai_simulation"
                                                                        ? "AI Simulation"
                                                                        : "Direct Upload"}
                                                                </p>
                                                            </div>
                                                        </div>
                                                        <a
                                                            href={`/api/v1/files/download?path=${encodeURIComponent(
                                                                phases.phase4
                                                                    .simulationResult
                                                                    .qa_file ||
                                                                    ""
                                                            )}`}
                                                            download
                                                            className="px-3 py-1.5 bg-white border border-slate-200 text-slate-700 text-xs font-medium rounded-lg hover:bg-slate-50 transition-colors flex items-center gap-2"
                                                        >
                                                            <Icon
                                                                icon="lucide:download"
                                                                width={12}
                                                            />
                                                            Download
                                                        </a>
                                                    </div>
                                                </div>
                                            </div>
                                        )}
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* PHASE 4: Final Investment Memo (was Phase 5) */}
                    <div className="relative z-10">
                        <div className="flex gap-6">
                            <div
                                className={`flex-shrink-0 w-12 h-12 rounded-full border flex items-center justify-center font-medium text-sm z-10 shadow-sm ring-4 ring-white ${getPhaseIndicatorClass(
                                    phases.phase5.status
                                )}`}
                            >
                                {phases.phase5.status === "completed" ? (
                                    <Icon icon="lucide:check" width={20} />
                                ) : (
                                    "04"
                                )}
                            </div>

                            <div className="bg-white border border-slate-200 rounded-xl w-full overflow-hidden shadow-sm">
                                <div className="p-5 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
                                    <div>
                                        <h2 className="text-sm font-semibold text-slate-900">
                                            4. Final Investment Memo
                                        </h2>
                                        <p className="text-xs text-slate-500 mt-0.5">
                                            Synthesize findings and generate the
                                            final PDF/Doc.
                                        </p>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        {phases.phase4.status === "completed" &&
                                        phases.phase4.simulationResult
                                            ?.qa_file ? (
                                            <>
                                                <span className="text-[10px] font-medium text-slate-400">
                                                    Ready to Generate
                                                </span>
                                                <Icon
                                                    icon="lucide:check-circle-2"
                                                    className="text-green-500"
                                                    width={14}
                                                />
                                            </>
                                        ) : phases.phase4.status ===
                                          "running" ? (
                                            <>
                                                <span className="text-[10px] font-medium text-orange-500">
                                                    Waiting for Simulation
                                                </span>
                                                <Icon
                                                    icon="lucide:clock"
                                                    className="text-orange-500"
                                                    width={14}
                                                />
                                            </>
                                        ) : phases.phase4.status ===
                                          "failed" ? (
                                            <>
                                                <span className="text-[10px] font-medium text-red-500">
                                                    Simulation Failed
                                                </span>
                                                <Icon
                                                    icon="lucide:x-circle"
                                                    className="text-red-500"
                                                    width={14}
                                                />
                                            </>
                                        ) : (
                                            <>
                                                <span className="text-[10px] font-medium text-red-500">
                                                    Locked
                                                </span>
                                                <Icon
                                                    icon="lucide:lock"
                                                    className="text-red-500"
                                                    width={14}
                                                />
                                            </>
                                        )}
                                    </div>
                                </div>

                                <div className="p-6">
                                    <div className="flex gap-4 mb-8 pb-6 border-b border-slate-100">
                                        <div className="flex items-center gap-2 text-xs text-slate-500">
                                            <div
                                                className={`w-1.5 h-1.5 rounded-full ${
                                                    phases.phase3.status ===
                                                    "completed"
                                                        ? "bg-green-500"
                                                        : "bg-slate-300"
                                                }`}
                                            ></div>
                                            Analysis Phase
                                        </div>
                                        <div className="flex items-center gap-2 text-xs text-slate-500">
                                            <div
                                                className={`w-1.5 h-1.5 rounded-full ${
                                                    phases.phase4.status ===
                                                    "completed"
                                                        ? "bg-green-500"
                                                        : "bg-slate-300"
                                                }`}
                                            ></div>
                                            Questionnaire Response Simulation
                                        </div>
                                    </div>

                                    <div className="mb-6">
                                        <div className="flex justify-between items-end mb-4">
                                            <label className="text-xs font-semibold text-slate-900 uppercase tracking-wider">
                                                Analysis Weighting
                                            </label>
                                            <div className="flex gap-2">
                                                <button
                                                    onClick={() =>
                                                        dispatch(
                                                            applyWeightTemplate(
                                                                "balanced"
                                                            )
                                                        )
                                                    }
                                                    className="px-2 py-1 rounded text-[10px] font-medium bg-slate-100 text-slate-600 hover:bg-slate-200 transition-colors"
                                                >
                                                    Balanced
                                                </button>
                                                <button
                                                    onClick={() =>
                                                        dispatch(
                                                            applyWeightTemplate(
                                                                "tech-focused"
                                                            )
                                                        )
                                                    }
                                                    className="px-2 py-1 rounded text-[10px] font-medium border border-slate-200 text-slate-500 hover:border-blue-300 hover:text-blue-600 transition-colors"
                                                >
                                                    Tech-Focused
                                                </button>
                                                <button
                                                    onClick={() =>
                                                        dispatch(
                                                            applyWeightTemplate(
                                                                "market-focused"
                                                            )
                                                        )
                                                    }
                                                    className="px-2 py-1 rounded text-[10px] font-medium border border-slate-200 text-slate-500 hover:border-blue-300 hover:text-blue-600 transition-colors"
                                                >
                                                    Market-Focused
                                                </button>
                                            </div>
                                        </div>

                                        <div className="space-y-5 bg-slate-50 p-5 rounded-xl border border-slate-100">
                                            <div className="grid grid-cols-[100px_1fr_40px] gap-4 items-center">
                                                <span className="text-xs font-medium text-slate-700">
                                                    Market
                                                </span>
                                                <input
                                                    type="range"
                                                    min="0"
                                                    max="100"
                                                    value={
                                                        sliderValues.market
                                                            .weight
                                                    }
                                                    onChange={(e) =>
                                                        handleWeightChange(
                                                            "market",
                                                            parseInt(
                                                                e.target.value
                                                            )
                                                        )
                                                    }
                                                />
                                                <span className="text-xs font-mono text-slate-500 text-right">
                                                    {sliderValues.market.weight}
                                                    %
                                                </span>
                                            </div>

                                            <div className="grid grid-cols-[100px_1fr_40px] gap-4 items-center">
                                                <span className="text-xs font-medium text-slate-700">
                                                    Product/Tech
                                                </span>
                                                <input
                                                    type="range"
                                                    min="0"
                                                    max="100"
                                                    value={
                                                        sliderValues.tech.weight
                                                    }
                                                    onChange={(e) =>
                                                        handleWeightChange(
                                                            "tech",
                                                            parseInt(
                                                                e.target.value
                                                            )
                                                        )
                                                    }
                                                />
                                                <span className="text-xs font-mono text-slate-500 text-right">
                                                    {sliderValues.tech.weight}%
                                                </span>
                                            </div>

                                            <div className="grid grid-cols-[100px_1fr_40px] gap-4 items-center">
                                                <span className="text-xs font-medium text-slate-700">
                                                    Business
                                                </span>
                                                <input
                                                    type="range"
                                                    min="0"
                                                    max="100"
                                                    value={
                                                        sliderValues.business
                                                            .weight
                                                    }
                                                    onChange={(e) =>
                                                        handleWeightChange(
                                                            "business",
                                                            parseInt(
                                                                e.target.value
                                                            )
                                                        )
                                                    }
                                                />
                                                <span className="text-xs font-mono text-slate-500 text-right">
                                                    {
                                                        sliderValues.business
                                                            .weight
                                                    }
                                                    %
                                                </span>
                                            </div>

                                            <div className="grid grid-cols-[100px_1fr_40px] gap-4 items-center">
                                                <span className="text-xs font-medium text-slate-700">
                                                    Risk
                                                </span>
                                                <input
                                                    type="range"
                                                    min="0"
                                                    max="100"
                                                    value={
                                                        sliderValues.risk.weight
                                                    }
                                                    onChange={(e) =>
                                                        handleWeightChange(
                                                            "risk",
                                                            parseInt(
                                                                e.target.value
                                                            )
                                                        )
                                                    }
                                                />
                                                <span className="text-xs font-mono text-slate-500 text-right">
                                                    {sliderValues.risk.weight}%
                                                </span>
                                            </div>

                                            <div className="pt-3 border-t border-slate-200 mt-2 flex justify-between items-center">
                                                <button
                                                    onClick={autoBalanceWeights}
                                                    className="text-[10px] text-blue-600 font-medium hover:underline flex items-center gap-1"
                                                >
                                                    <Icon
                                                        icon="lucide:wand-2"
                                                        width={12}
                                                    />
                                                    Auto-Balance
                                                </button>
                                                <div className="flex items-center gap-2">
                                                    <span className="text-[10px] text-slate-400 uppercase tracking-widest font-semibold">
                                                        Total
                                                    </span>
                                                    <span
                                                        className={`text-xs font-bold px-2 py-0.5 rounded border shadow-sm ${
                                                            getTotalWeight() ===
                                                            100
                                                                ? "text-slate-900 bg-white border-slate-200"
                                                                : "text-orange-900 bg-orange-50 border-orange-200"
                                                        }`}
                                                    >
                                                        {getTotalWeight()}%
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="flex items-center justify-between mt-8 pt-6 border-t border-slate-100">
                                        <div className="flex items-center gap-2">
                                            <div className="h-8 w-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-400 bg-slate-50">
                                                <Icon
                                                    icon="lucide:file-text"
                                                    width={16}
                                                />
                                            </div>
                                            <div className="flex flex-col">
                                                <span className="text-[10px] font-medium text-slate-500 uppercase">
                                                    Output Format
                                                </span>
                                                <span className="text-xs font-medium text-slate-900">
                                                    PDF & Markdown
                                                </span>
                                            </div>
                                        </div>
                                        <button
                                            onClick={handleGenerateMemo}
                                            disabled={
                                                phases.phase3.status !==
                                                    "completed" ||
                                                phases.phase4.status !==
                                                    "completed" ||
                                                !phases.phase4.simulationResult
                                                    ?.qa_file ||
                                                getTotalWeight() !== 100 ||
                                                phases.phase5.status ===
                                                    "running"
                                            }
                                            className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-full text-sm font-medium transition-all shadow-lg shadow-blue-500/20 flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                                        >
                                            {phases.phase5.status ===
                                            "running" ? (
                                                <>
                                                    <Icon
                                                        icon="lucide:loader-2"
                                                        width={16}
                                                        className="animate-spin"
                                                    />
                                                    Generating...
                                                </>
                                            ) : (
                                                <>
                                                    Generate Final Memo
                                                    <Icon
                                                        icon="lucide:arrow-right"
                                                        width={16}
                                                    />
                                                </>
                                            )}
                                        </button>
                                    </div>

                                    {/* Memo Generation Success State */}
                                    {phases.phase5.status === "completed" &&
                                        phases.phase5.memoResult && (
                                            <div className="mt-6 pt-6 border-t border-slate-100">
                                                <div className="flex items-center justify-between mb-3">
                                                    <h4 className="text-xs font-semibold text-slate-900">
                                                        Investment Memo Generated
                                                    </h4>
                                                    <span className="text-[10px] text-green-600 flex items-center gap-1">
                                                        <Icon
                                                            icon="lucide:check-circle-2"
                                                            width={12}
                                                        />
                                                        Complete
                                                    </span>
                                                </div>
                                                <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
                                                    <div className="flex items-center justify-between">
                                                        <div className="flex items-center gap-3">
                                                            <Icon
                                                                icon="lucide:file-text"
                                                                width={20}
                                                                className="text-slate-400"
                                                            />
                                                            <div>
                                                                <p className="text-xs font-medium text-slate-900">
                                                                    investment-memo.md
                                                                </p>
                                                                <p className="text-[10px] text-slate-500">
                                                                    {phases.phase5.memoResult
                                                                        .metadata?.content_length
                                                                        ? `${(
                                                                              phases.phase5
                                                                                  .memoResult.metadata
                                                                                  .content_length / 1024
                                                                          ).toFixed(1)} KB`
                                                                        : "Markdown format"}
                                                                </p>
                                                            </div>
                                                        </div>
                                                        <div className="flex gap-2">
                                                            <a
                                                                href={`/api/v1/files/download?path=${encodeURIComponent(
                                                                    phases.phase5.memoResult
                                                                        .memo_file || ""
                                                                )}`}
                                                                download
                                                                className="px-3 py-1.5 bg-white border border-slate-200 text-slate-700 text-xs font-medium rounded-lg hover:bg-slate-50 transition-colors flex items-center gap-2"
                                                            >
                                                                <Icon
                                                                    icon="lucide:download"
                                                                    width={12}
                                                                />
                                                                Markdown
                                                            </a>
                                                            {phases.phase5.memoResult.pdf_file && (
                                                                <a
                                                                    href={`/api/v1/files/download?path=${encodeURIComponent(
                                                                        phases.phase5.memoResult
                                                                            .pdf_file
                                                                    )}`}
                                                                    download
                                                                    className="px-3 py-1.5 bg-blue-600 text-white text-xs font-medium rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
                                                                >
                                                                    <Icon
                                                                        icon="lucide:file-text"
                                                                        width={12}
                                                                    />
                                                                    PDF
                                                                </a>
                                                            )}
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        )}

                                    {/* Memo Generation Failed State */}
                                    {phases.phase5.status === "failed" && (
                                        <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-4">
                                            <div className="flex gap-3">
                                                <div className="mt-0.5 text-red-500">
                                                    <Icon
                                                        icon="lucide:alert-circle"
                                                        width={18}
                                                    />
                                                </div>
                                                <div className="flex-1">
                                                    <h4 className="text-sm font-semibold text-red-900">
                                                        Memo Generation Failed
                                                    </h4>
                                                    <p className="text-xs text-red-700 mt-1">
                                                        {phases.phase5.error ||
                                                            "An error occurred during memo generation"}
                                                    </p>
                                                </div>
                                                <button
                                                    onClick={handleGenerateMemo}
                                                    disabled={getTotalWeight() !== 100}
                                                    className="px-3 py-1.5 bg-white border border-red-200 text-red-700 text-xs font-medium rounded-lg hover:bg-red-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                                >
                                                    Retry
                                                </button>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </main>

            {/* Footer */}
            <footer className="mt-20 border-t border-slate-200 py-8 bg-white">
                <div className="max-w-7xl mx-auto px-6 flex justify-between items-center text-xs text-slate-400">
                    <div>© 2024 AI-Shark Inc.</div>
                    <div className="flex gap-4">
                        <a href="#" className="hover:text-slate-600">
                            Privacy
                        </a>
                        <a href="#" className="hover:text-slate-600">
                            Help Center
                        </a>
                    </div>
                </div>
            </footer>

            {/* Questionnaire Error Modal */}
            {showQuestionnaireError &&
                questionnaireError &&
                !isSkippedGeneration && (
                    <QuestionnaireErrorModal
                        error={questionnaireError}
                        onClose={() => setShowQuestionnaireError(false)}
                    />
                )}

            {/* Questionnaire Preview Modal */}
            {showQuestionnairePreview && companyName && (
                <QuestionnairePreviewModal
                    companyName={companyName}
                    onClose={() => setShowQuestionnairePreview(false)}
                />
            )}
        </div>
    );
};
