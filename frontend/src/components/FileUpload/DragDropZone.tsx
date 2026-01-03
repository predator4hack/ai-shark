import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Icon } from '@iconify/react';
import { FILE_UPLOAD } from '../../utils/constants';

interface DragDropZoneProps {
  onFileSelect: (file: File) => void;
  acceptedFileTypes?: string[];
  maxSizeMB?: number;
  disabled?: boolean;
}

export const DragDropZone: React.FC<DragDropZoneProps> = ({
  onFileSelect,
  acceptedFileTypes = FILE_UPLOAD.ACCEPTED_TYPES,
  maxSizeMB = FILE_UPLOAD.MAX_SIZE_MB,
  disabled = false,
}) => {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        onFileSelect(acceptedFiles[0]);
      }
    },
    [onFileSelect]
  );

  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    onDrop,
    accept: FILE_UPLOAD.MIME_TYPES,
    maxSize: maxSizeMB * 1024 * 1024,
    multiple: false,
    disabled,
  });

  return (
    <div
      {...getRootProps()}
      className={`
        p-12 text-center rounded-xl border-2 border-dashed transition-all duration-200
        ${disabled ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'}
        ${
          isDragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-slate-300 bg-white hover:border-blue-500 hover:bg-blue-50'
        }
        ${disabled ? 'hover:border-slate-300 hover:bg-white' : ''}
      `}
    >
      <input {...getInputProps()} />

      <Icon
        icon="lucide:cloud-upload"
        className={`mx-auto mb-4 ${isDragActive ? 'text-blue-600' : 'text-blue-500'}`}
        width="64"
      />

      <h3 className="text-xl font-semibold text-slate-900 mb-2">
        {isDragActive ? 'Drop the file here' : 'Drag & drop your pitch deck'}
      </h3>

      <p className="text-sm text-slate-500 mb-4">or click to browse</p>

      <p className="text-xs text-slate-400">
        Supported formats: {acceptedFileTypes.join(', ')} (Max {maxSizeMB}MB)
      </p>

      {fileRejections.length > 0 && (
        <div className="mt-4 text-red-600 text-sm font-medium">
          {fileRejections[0].errors[0].message}
        </div>
      )}
    </div>
  );
};
