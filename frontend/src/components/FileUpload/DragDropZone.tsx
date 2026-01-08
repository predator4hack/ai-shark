import React, { useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Icon } from "@iconify/react";
import { FILE_UPLOAD } from "../../utils/constants";

interface DragDropZoneProps {
    onFileSelect: (file: File) => void;
    accept?: Record<string, string[]>;
    acceptedFileTypes?: string[];
    maxSize?: number;
    maxSizeMB?: number;
    disabled?: boolean;
    size?: "sm" | "md" | "lg";
}

export const DragDropZone: React.FC<DragDropZoneProps> = ({
    onFileSelect,
    accept,
    acceptedFileTypes = FILE_UPLOAD.ACCEPTED_TYPES,
    maxSize,
    maxSizeMB = FILE_UPLOAD.MAX_SIZE_MB,
    disabled = false,
    size = "sm",
}) => {
    // Size configurations
    const sizeConfig = {
        sm: {
            padding: "p-8",
            iconWrapperSize: "w-10 h-10",
            iconSize: "20",
            headingSize: "text-sm",
            textSize: "text-xs",
            subTextSize: "text-xs",
        },
        md: {
            padding: "p-8",
            iconWrapperSize: "w-12 h-12",
            iconSize: "24",
            headingSize: "text-lg",
            textSize: "text-sm",
            subTextSize: "text-xs",
        },
        lg: {
            padding: "p-12",
            iconWrapperSize: "w-16 h-16",
            iconSize: "32",
            headingSize: "text-xl",
            textSize: "text-sm",
            subTextSize: "text-xs",
        },
    };

    const config = sizeConfig[size];
    const onDrop = useCallback(
        (acceptedFiles: File[]) => {
            if (acceptedFiles.length > 0) {
                onFileSelect(acceptedFiles[0]);
            }
        },
        [onFileSelect]
    );

    const { getRootProps, getInputProps, isDragActive, fileRejections } =
        useDropzone({
            onDrop,
            accept: accept || FILE_UPLOAD.MIME_TYPES,
            maxSize: (maxSize || maxSizeMB * 1024 * 1024),
            multiple: false,
            disabled,
        });

    return (
        <div
            {...getRootProps()}
            className={`
        ${
            config.padding
        } text-center rounded-xl border-2 border-dashed transition-all group
        ${disabled ? "cursor-not-allowed opacity-50" : "cursor-pointer"}
        ${
            isDragActive
                ? "border-blue-400 bg-blue-50"
                : "border-slate-200 bg-white hover:border-blue-400 hover:bg-slate-50"
        }
        ${disabled ? "hover:border-slate-200 hover:bg-white" : ""}
      `}
        >
            <input {...getInputProps()} />

            <div className={`${config.iconWrapperSize} bg-blue-50 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform`}>
                <Icon
                    icon="lucide:upload-cloud"
                    width={config.iconSize}
                />
            </div>

            <p className={`${config.headingSize} font-medium text-slate-900`}>
                {isDragActive
                    ? "Drop the file here"
                    : "Click to upload or drag and drop"}
            </p>

            <p className={`${config.subTextSize} text-slate-500 mt-1`}>
                Supported formats: {acceptedFileTypes.join(", ")} (Max{" "}
                {maxSizeMB}MB)
            </p>

            {fileRejections.length > 0 && (
                <div className="mt-4 text-red-600 text-sm font-medium">
                    {fileRejections[0].errors[0].message}
                </div>
            )}
        </div>
    );
};
