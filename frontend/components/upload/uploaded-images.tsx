"use client";

import { useState } from "react";
import { UploadedImage } from "@/app/upload/page";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import {
  ExternalLink,
  MapPin,
  Download,
  Eye,
  Image as ImageIcon,
} from "lucide-react";

interface UploadedImagesProps {
  images: UploadedImage[];
}

export function UploadedImages({ images }: UploadedImagesProps) {
  const [selectedImage, setSelectedImage] = useState<UploadedImage | null>(null);

  if (images.length === 0) return null;

  const formatFileSize = (bytes: number) => {
    return (bytes / 1024 / 1024).toFixed(1) + " MB";
  };

  const openInNewTab = (url: string) => {
    window.open(url, "_blank", "noopener,noreferrer");
  };

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {images.map((image) => (
          <Card key={image.id} className="overflow-hidden">
            <div className="aspect-video relative bg-muted">
              {image.thumbnails?.medium || image.s3Url ? (
                <img
                  src={image.thumbnails?.medium || image.s3Url}
                  alt={image.originalFilename}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <ImageIcon className="w-12 h-12 text-muted-foreground" />
                </div>
              )}
              
              {/* Overlay with actions */}
              <div className="absolute inset-0 bg-black/50 opacity-0 hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                <Dialog>
                  <DialogTrigger asChild>
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => setSelectedImage(image)}
                    >
                      <Eye className="w-4 h-4" />
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="max-w-4xl">
                    <DialogHeader>
                      <DialogTitle>{selectedImage?.originalFilename}</DialogTitle>
                    </DialogHeader>
                    <div className="space-y-4">
                      <div className="aspect-video relative bg-muted rounded-lg overflow-hidden">
                        {selectedImage?.s3Url && (
                          <img
                            src={selectedImage.s3Url}
                            alt={selectedImage.originalFilename}
                            className="w-full h-full object-contain"
                          />
                        )}
                      </div>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <p className="font-medium">File Size</p>
                          <p className="text-muted-foreground">
                            {selectedImage && formatFileSize(selectedImage.fileSize)}
                          </p>
                        </div>
                        <div>
                          <p className="font-medium">Status</p>
                          <Badge variant="outline" className="mt-1">
                            {selectedImage?.status}
                          </Badge>
                        </div>
                      </div>
                    </div>
                  </DialogContent>
                </Dialog>

                {image.s3Url && (
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => openInNewTab(image.s3Url!)}
                  >
                    <ExternalLink className="w-4 h-4" />
                  </Button>
                )}
              </div>
            </div>

            <CardContent className="p-4">
              <div className="space-y-2">
                <h3 className="font-medium text-sm truncate" title={image.originalFilename}>
                  {image.originalFilename}
                </h3>
                
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span>{formatFileSize(image.fileSize)}</span>
                  <Badge variant="outline" className="text-xs">
                    {image.status}
                  </Badge>
                </div>

                {/* Action buttons */}
                <div className="flex gap-2 pt-2">
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex-1 text-xs"
                    disabled
                  >
                    <MapPin className="w-3 h-3 mr-1" />
                    Analyze
                  </Button>
                  
                  {image.s3Url && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => openInNewTab(image.s3Url!)}
                      className="text-xs"
                    >
                      <Download className="w-3 h-3" />
                    </Button>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Summary */}
      <div className="text-center text-sm text-muted-foreground">
        {images.length} {images.length === 1 ? "image" : "images"} uploaded successfully
      </div>
    </div>
  );
}