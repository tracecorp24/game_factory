// CreativeForge Intelligence Studio v3.0 - ComfyUI Deep Hybrid Integration
// components/comfy/ComfyJsonImporter.tsx

'use client';

import React, { useRef, useState } from 'react';
import { Upload, Download, Copy, Check, FileJson, AlertCircle } from 'lucide-react';

interface ComfyJsonImporterProps {
  onImportJson: (json: Record<string, any>) => void;
  onExportJson: () => Record<string, any>;
}

export function ComfyJsonImporter({ onImportJson, onExportJson }: ComfyJsonImporterProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [copied, setCopied] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const processJsonText = (text: string) => {
    try {
      setErrorMessage(null);
      const parsed = JSON.parse(text);
      if (typeof parsed !== 'object' || parsed === null || Array.isArray(parsed)) {
        throw new Error('Invalid ComfyUI JSON format: root must be a dictionary of nodes.');
      }
      onImportJson(parsed);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to parse JSON file.');
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target?.result as string;
      if (content) processJsonText(content);
    };
    reader.readAsText(file);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target?.result as string;
      if (content) processJsonText(content);
    };
    reader.readAsText(file);
  };

  const handleExportDownload = () => {
    const data = onExportJson();
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `comfy_workflow_${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleCopyClipboard = async () => {
    const data = onExportJson();
    await navigator.clipboard.writeText(JSON.stringify(data, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex items-center gap-2 select-none">
      {/* Hidden File Input */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".json"
        onChange={handleFileChange}
        className="hidden"
      />

      {/* Drag & Drop Import Trigger */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-mono font-medium border cursor-pointer transition-colors ${
          dragOver
            ? 'bg-cyan-950/80 border-cyan-400 text-cyan-200'
            : 'bg-slate-900 border-slate-800 text-slate-300 hover:border-slate-700 hover:text-slate-100'
        }`}
        title="Import ComfyUI JSON file (or drag and drop here)"
      >
        <Upload className="w-3.5 h-3.5 text-cyan-400" />
        <span>Import JSON</span>
      </div>

      {/* Export Actions */}
      <button
        onClick={handleExportDownload}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-mono font-medium bg-slate-900 border border-slate-800 text-slate-300 hover:border-slate-700 hover:text-slate-100 transition-colors"
        title="Download ComfyUI API JSON format"
      >
        <Download className="w-3.5 h-3.5 text-blue-400" />
        <span>Export Comfy API</span>
      </button>

      <button
        onClick={handleCopyClipboard}
        className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs font-mono font-medium bg-slate-900 border border-slate-800 text-slate-300 hover:border-slate-700 hover:text-slate-100 transition-colors"
        title="Copy Comfy API JSON to clipboard"
      >
        {copied ? (
          <>
            <Check className="w-3.5 h-3.5 text-emerald-400" />
            <span className="text-emerald-400">Copied!</span>
          </>
        ) : (
          <>
            <Copy className="w-3.5 h-3.5 text-slate-400" />
            <span>Copy</span>
          </>
        )}
      </button>

      {errorMessage && (
        <div className="flex items-center gap-1 text-[10px] font-mono text-rose-400 bg-rose-950/60 px-2 py-1 rounded border border-rose-800/80">
          <AlertCircle className="w-3 h-3" />
          <span>{errorMessage}</span>
        </div>
      )}
    </div>
  );
}
