"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, Image as ImageIcon, X, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { useAuth } from "@/hooks/use-auth";

interface ImageUploadZoneProps {
  onUploadStart: (files: File[]) => any[];
  onUploadProgress: (imageId: string, progress: number) => void;
  onUploadComplete: (imageId: string, result: any) => void;
  onUploadError: (imageId: string, error: string) => void;
  onUploadFinish: () => void;
  disabled?: boolean;
  maxFiles?: number;
  maxFileSize?: number;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function ImageUploadZone({
  onUploadStart,
  onUploadProgress,
  onUploadComplete,
  onUploadError,
  onUploadFinish,
  disabled = false,
  maxFiles = 10,
  maxFileSize = 10 * 1024 * 1024, // 10MB
}: ImageUploadZoneProps) {
  const { user } = useAuth();
  const { toast } = useToast();
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);

  const uploadFile = async (file: File, imageId: string) => {
    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`${API_BASE_URL}/api/v1/images/upload`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${user?.accessToken}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Upload failed");
      }

      const result = await response.json();
      onUploadComplete(imageId, result);
      
      toast({
        title: "Upload successful",
        description: `${file.name} has been uploaded successfully.`,
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Upload failed";
      onUploadError(imageId, errorMessage);
      
      toast({
        title: "Upload failed",
        description: `Failed to upload ${file.name}: ${errorMessage}`,
        variant: "destructive",
      });
    }
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) return;

    const imageIds = onUploadStart(selectedFiles);
    
    // Upload files concurrently
    const uploadPromises = selectedFiles.map((file, index) => {
      const imageId = imageIds[index].id;
      return uploadFile(file, imageId);
    });

    try {
      await Promise.all(uploadPromises);
    } catch (error) {
      console.error("Some uploads failed:", error);
    } finally {
      setSelectedFiles([]);
      onUploadFinish();
    }
  };

  const onDrop = useCallback(
    (acceptedFiles: File[], rejectedFiles: any[]) => {
      // Handle rejected files
      rejectedFiles.forEach((rejection) => {
        const { file, errors } = rejection;
        errors.forEach((error: any) => {
          let message = `File ${file.name} was rejected`;
          if (error.code === "file-too-large") {
            message = `File ${file.name} is too large. Maximum size is ${(maxFileSize / 1024 / 1024).toFixed(1)}MB`;
          } else if (error.code === "file-invalid-type") {
            message = `File ${file.name} is not a supported image format`;
          }
          toast({
            title: "File rejected",
            description: message,
            variant: "destructive",
          });
        });
      });

      // Add accepted files
      if (acceptedFiles.length > 0) {
        setSelectedFiles((prev) => {
          const newFiles = [...prev, ...acceptedFiles];
          if (newFiles.length > maxFiles) {
            toast({
              title: "Too many files",
              description: `Maximum ${maxFiles} files allowed. Extra files were removed.`,
              variant: "destructive",
            });
            return newFiles.slice(0, maxFiles);
          }
          return newFiles;
        });
      }
    },
    [maxFiles, maxFileSize, toast]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "image/*": [".jpeg", ".jpg", ".png", ".webp", ".gif", ".bmp", ".tiff"],
    },
    maxFiles,
    maxSize: maxFileSize,
    disabled: disabled || selectedFiles.length >= maxFiles,
  });

  const removeFile = (index: number) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const clearAll = () => {
    setSelectedFiles([]);
  };

  return (
    <div className="space-y-4">
      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={cn(
          "border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors",
          isDragActive
            ? "border-primary bg-primary/5"
            : "border-muted-foreground/25 hover:border-primary/50",
          disabled && "opacity-50 cursor-not-allowed",
          selectedFiles.length >= maxFiles && "opacity-50 cursor-not-allowed"
        )}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center gap-4">
          <div className="p-4 rounded-full bg-muted">
            <Upload className="w-8 h-8 text-muted-foreground" />
          </div>
          
          <div className="space-y-2">
            <h3 className="text-lg font-semibold">
              {isDragActive ? "Drop images here" : "Upload Images"}
            </h3>
            <p className="text-sm text-muted-foreground">
              {isDragActive
                ? "Drop your images to add them"
                : "Drag and drop images here, or click to select files"}
            </p>
            <p className="text-xs text-muted-foreground">
              Supports JPEG, PNG, WebP, GIF, BMP, TIFF • Max {(maxFileSize / 1024 / 1024).toFixed(1)}MB per file • Up to {maxFiles} files
            </p>
          </div>
        </div>
      </div>

      {/* Selected Files Preview */}
      {selectedFiles.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-medium">
              Selected Files ({selectedFiles.length})
            </h4>
            <Button
              variant="outline"
              size="sm"
              onClick={clearAll}
              className="text-xs"
            >
              Clear All
            </Button>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {selectedFiles.map((file, index) => (
              <div
                key={`${file.name}-${index}`}
                className="relative group rounded-lg border bg-card overflow-hidden"
              >
                <div className="aspect-square relative bg-muted flex items-center justify-center">
                  <ImageIcon className="w-8 h-8 text-muted-foreground" />
                  {file.type.startsWith("image/") && (
                    <img
                      src={URL.createObjectURL(file)}
                      alt={file.name}
                      className="absolute inset-0 w-full h-full object-cover"
                      onLoad={(e) => {
                        URL.revokeObjectURL((e.target as HTMLImageElement).src);
                      }}
                    />
                  )}
                </div>
                
                <div className="p-2">
                  <p className="text-xs font-medium truncate" title={file.name}>
                    {file.name}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {(file.size / 1024 / 1024).toFixed(1)} MB
                  </p>
                </div>
                
                <Button
                  variant="destructive"
                  size="sm"
                  className="absolute top-2 right-2 w-6 h-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
                  onClick={() => removeFile(index)}
                >
                  <X className="w-3 h-3" />
                </Button>
              </div>
            ))}
          </div>
          
          <div className="flex gap-2">
            <Button
              onClick={handleUpload}
              disabled={disabled || selectedFiles.length === 0}
              className="flex-1"
            >
              <Upload className="w-4 h-4 mr-2" />
              Upload {selectedFiles.length} {selectedFiles.length === 1 ? "Image" : "Images"}
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}