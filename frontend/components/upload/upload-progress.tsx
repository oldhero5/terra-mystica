"use client";

import { UploadedImage } from "@/app/upload/page";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";
import {
  CheckCircle,
  XCircle,
  Loader2,
  RotateCcw,
  X,
  Image as ImageIcon,
} from "lucide-react";

interface UploadProgressProps {
  images: UploadedImage[];
  onRemove: (imageId: string) => void;
  onRetry: (imageId: string) => void;
}

export function UploadProgress({
  images,
  onRemove,
  onRetry,
}: UploadProgressProps) {
  const getStatusIcon = (image: UploadedImage) => {
    switch (image.status) {
      case "uploading":
        return <Loader2 className="w-4 h-4 animate-spin text-blue-500" />;
      case "completed":
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case "error":
        return <XCircle className="w-4 h-4 text-red-500" />;
      default:
        return null;
    }
  };

  const getStatusText = (image: UploadedImage) => {
    switch (image.status) {
      case "uploading":
        return `Uploading... ${image.progress}%`;
      case "completed":
        return "Upload complete";
      case "error":
        return `Error: ${image.error}`;
      default:
        return "";
    }
  };

  const getStatusColor = (status: UploadedImage["status"]) => {
    switch (status) {
      case "uploading":
        return "text-blue-600";
      case "completed":
        return "text-green-600";
      case "error":
        return "text-red-600";
      default:
        return "text-muted-foreground";
    }
  };

  if (images.length === 0) return null;

  const completedCount = images.filter((img) => img.status === "completed").length;
  const errorCount = images.filter((img) => img.status === "error").length;
  const uploadingCount = images.filter((img) => img.status === "uploading").length;

  return (
    <div className="space-y-4">
      {/* Overall Progress Summary */}
      <div className="flex items-center justify-between text-sm">
        <div className="flex items-center gap-4">
          <span className="text-muted-foreground">
            {completedCount} of {images.length} completed
          </span>
          {errorCount > 0 && (
            <span className="text-red-600">{errorCount} failed</span>
          )}
          {uploadingCount > 0 && (
            <span className="text-blue-600">{uploadingCount} uploading</span>
          )}
        </div>
      </div>

      {/* Individual File Progress */}
      <div className="space-y-3">
        {images.map((image) => (
          <div
            key={image.id}
            className={cn(
              "flex items-center gap-3 p-3 rounded-lg border",
              image.status === "error" && "border-red-200 bg-red-50",
              image.status === "completed" && "border-green-200 bg-green-50",
              image.status === "uploading" && "border-blue-200 bg-blue-50"
            )}
          >
            {/* Image Preview */}
            <div className="flex-shrink-0 w-12 h-12 rounded-md overflow-hidden bg-muted">
              {image.preview ? (
                <img
                  src={image.preview}
                  alt={image.originalFilename}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <ImageIcon className="w-6 h-6 text-muted-foreground" />
                </div>
              )}
            </div>

            {/* File Info */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <h4 className="text-sm font-medium truncate">
                  {image.originalFilename}
                </h4>
                {getStatusIcon(image)}
              </div>
              
              <p className={cn("text-xs", getStatusColor(image.status))}>
                {getStatusText(image)}
              </p>
              
              <p className="text-xs text-muted-foreground">
                {(image.fileSize / 1024 / 1024).toFixed(1)} MB
              </p>

              {/* Progress Bar */}
              {image.status === "uploading" && (
                <div className="mt-2">
                  <Progress value={image.progress} className="h-1" />
                </div>
              )}
            </div>

            {/* Actions */}
            <div className="flex items-center gap-1">
              {image.status === "error" && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onRetry(image.id)}
                  className="h-8 px-2"
                >
                  <RotateCcw className="w-3 h-3" />
                </Button>
              )}
              
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onRemove(image.id)}
                className="h-8 px-2 text-muted-foreground hover:text-foreground"
              >
                <X className="w-3 h-3" />
              </Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}