"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/use-auth";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ImageUploadZone } from "@/components/upload/image-upload-zone";
import { UploadProgress } from "@/components/upload/upload-progress";
import { UploadedImages } from "@/components/upload/uploaded-images";
import { ArrowLeft, Upload } from "lucide-react";

export interface UploadedImage {
  id: string;
  filename: string;
  originalFilename: string;
  fileSize: number;
  status: "uploading" | "completed" | "error";
  progress: number;
  preview?: string;
  s3Url?: string;
  thumbnails?: {
    small?: string;
    medium?: string;
    large?: string;
  };
  error?: string;
}

export default function UploadPage() {
  const { user, isAuthenticated } = useAuth();
  const router = useRouter();
  const [uploadedImages, setUploadedImages] = useState<UploadedImage[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  if (!isAuthenticated) {
    router.push("/auth/login");
    return null;
  }

  const handleUploadStart = (files: File[]) => {
    setIsUploading(true);
    const newImages: UploadedImage[] = files.map((file) => ({
      id: Math.random().toString(36).substring(7),
      filename: file.name,
      originalFilename: file.name,
      fileSize: file.size,
      status: "uploading",
      progress: 0,
      preview: URL.createObjectURL(file),
    }));
    
    setUploadedImages((prev) => [...prev, ...newImages]);
    return newImages;
  };

  const handleUploadProgress = (imageId: string, progress: number) => {
    setUploadedImages((prev) =>
      prev.map((img) =>
        img.id === imageId ? { ...img, progress } : img
      )
    );
  };

  const handleUploadComplete = (imageId: string, result: any) => {
    setUploadedImages((prev) =>
      prev.map((img) =>
        img.id === imageId
          ? {
              ...img,
              status: "completed",
              progress: 100,
              s3Url: result.s3_url,
              thumbnails: {
                small: result.thumbnail_small_url,
                medium: result.thumbnail_medium_url,
                large: result.thumbnail_large_url,
              },
            }
          : img
      )
    );
  };

  const handleUploadError = (imageId: string, error: string) => {
    setUploadedImages((prev) =>
      prev.map((img) =>
        img.id === imageId
          ? { ...img, status: "error", error }
          : img
      )
    );
  };

  const handleUploadFinish = () => {
    setIsUploading(false);
  };

  const removeImage = (imageId: string) => {
    setUploadedImages((prev) => prev.filter((img) => img.id !== imageId));
  };

  const retryUpload = (imageId: string) => {
    setUploadedImages((prev) =>
      prev.map((img) =>
        img.id === imageId
          ? { ...img, status: "uploading", progress: 0, error: undefined }
          : img
      )
    );
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="flex items-center gap-4 mb-8">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.back()}
          className="flex items-center gap-2"
        >
          <ArrowLeft className="w-4 h-4" />
          Back
        </Button>
        <div>
          <h1 className="text-3xl font-bold">Upload Images</h1>
          <p className="text-muted-foreground">
            Upload images to discover their geographic locations
          </p>
        </div>
      </div>

      <div className="space-y-6">
        {/* Upload Zone */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Upload className="w-5 h-5" />
              Select Images
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ImageUploadZone
              onUploadStart={handleUploadStart}
              onUploadProgress={handleUploadProgress}
              onUploadComplete={handleUploadComplete}
              onUploadError={handleUploadError}
              onUploadFinish={handleUploadFinish}
              disabled={isUploading}
            />
          </CardContent>
        </Card>

        {/* Upload Progress */}
        {uploadedImages.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Upload Progress</CardTitle>
            </CardHeader>
            <CardContent>
              <UploadProgress
                images={uploadedImages}
                onRemove={removeImage}
                onRetry={retryUpload}
              />
            </CardContent>
          </Card>
        )}

        {/* Uploaded Images Gallery */}
        {uploadedImages.some((img) => img.status === "completed") && (
          <Card>
            <CardHeader>
              <CardTitle>Uploaded Images</CardTitle>
            </CardHeader>
            <CardContent>
              <UploadedImages
                images={uploadedImages.filter((img) => img.status === "completed")}
              />
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}