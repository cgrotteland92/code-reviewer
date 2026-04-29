"use client";

import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface Props {
  code: string;
  onCodeChange: (v: string) => void;
  language: string;
  onLanguageChange: (v: string) => void;
  languages: string[];
  onReview: () => void;
  onClear: () => void;
  loading: boolean;
}

export function CodeEditor({
  code,
  onCodeChange,
  language,
  onLanguageChange,
  languages,
  onReview,
  onClear,
  loading,
}: Props) {
  return (
    <div className="flex gap-4">
      <textarea
        className="flex-1 h-80 bg-zinc-900 border border-zinc-800 rounded-lg p-4 font-mono text-sm text-zinc-100 placeholder:text-zinc-600 resize-none focus:outline-none focus:ring-1 focus:ring-zinc-600"
        placeholder="Paste your code here…"
        value={code}
        onChange={(e) => onCodeChange(e.target.value)}
        spellCheck={false}
      />
      <div className="flex flex-col gap-3 w-44">
        <Select value={language} onValueChange={(v) => { if (v !== null) onLanguageChange(v); }}>
          <SelectTrigger className="w-full">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {languages.map((l) => (
              <SelectItem key={l} value={l}>
                {l}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Button
          onClick={onReview}
          disabled={loading || !code.trim()}
          className="bg-indigo-600 hover:bg-indigo-500 text-white disabled:opacity-50"
        >
          {loading ? (
            <span className="flex items-center gap-2">
              <svg
                className="animate-spin h-4 w-4"
                viewBox="0 0 24 24"
                fill="none"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8v8z"
                />
              </svg>
              Reviewing…
            </span>
          ) : (
            "Review Code"
          )}
        </Button>
        <Button
          onClick={onClear}
          variant="outline"
          className="border-zinc-700 text-zinc-300 hover:bg-zinc-800 hover:text-zinc-100"
        >
          Clear
        </Button>
      </div>
    </div>
  );
}
