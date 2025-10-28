import React, { useState, useRef } from "react";
import { Button } from "../ui/button";
import { Plus, Filter, FileText } from "lucide-react";

type FileUploadProps = {
  onFileProcessed?: (file: File) => void;
};

const FileUpload = ({ onFileProcessed }: FileUploadProps) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [fileName, setFileName] = useState<string | null>(null);

  const triggerFileDialog = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      const file = files[0];
      setFileName(file.name);

      // Notify parent component if needed
      if (onFileProcessed) {
        onFileProcessed(file);
      }

      // File processing logic can be added here
    } else {
      setFileName(null);
    }
  };

  return (
    <>
      <input
        type="file"
        id="file-upload"
        style={{ display: "none" }}
        onChange={handleFileChange}
        ref={fileInputRef}
      />

      {fileName ? (
        <div className="w-full mb-4 border border-dashed rounded-md p-3">
          <div className="flex items-center gap-2">
            <FileText className="size-4 text-blue-500" />
            <span className="text-sm font-medium flex-1 truncate">
              {fileName}
            </span>
            <Button
              variant="ghost"
              size="sm"
              onClick={triggerFileDialog}
              className="h-8 px-2"
            >
              Change
            </Button>
          </div>
        </div>
      ) : (
        <Button
          variant="outline"
          className="w-full mb-4 border-dashed py-6 flex items-center justify-center gap-2 text-muted-foreground"
          onClick={triggerFileDialog}
        >
          <Filter className="size-4" />
          <span>Handmatig bronnen toevoegen</span>
          <Plus className="size-4" />
        </Button>
      )}
    </>
  );
};

export default FileUpload;
