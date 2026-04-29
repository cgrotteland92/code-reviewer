"use client";

import { useState } from "react";
import { ReviewResult } from "@/lib/types";
import { CodeEditor } from "@/components/CodeEditor";
import { ReviewResults } from "@/components/ReviewResults";

const LANGUAGES = [
  "Auto-detect",
  "Python",
  "JavaScript",
  "TypeScript",
  "Java",
  "C#",
  "C++",
  "Go",
  "Rust",
  "PHP",
  "Ruby",
  "SQL",
  "Shell / Bash",
  "Other",
];

export default function Home() {
  const [code, setCode] = useState("");
  const [language, setLanguage] = useState("Auto-detect");
  const [result, setResult] = useState<ReviewResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleReview() {
    if (!code.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const lang = language === "Auto-detect" ? "unspecified" : language;
      const res = await fetch("http://localhost:8000/api/review", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code, language: lang }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail ?? `Request failed (${res.status})`);
      }
      setResult(await res.json());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  function handleClear() {
    setCode("");
    setResult(null);
    setError(null);
  }

  return (
    <main className="min-h-screen bg-zinc-950 text-zinc-100 p-6">
      <div className="max-w-5xl mx-auto space-y-6">
        <header>
          <h1 className="text-2xl font-bold tracking-tight">
            🔍 AI Code Reviewer
          </h1>
          <p className="text-sm text-zinc-400 mt-1">
            Multi-agent analysis powered by Claude Sonnet · Four specialist
            agents run in parallel, then a coordinator synthesizes results.
          </p>
        </header>

        <CodeEditor
          code={code}
          onCodeChange={setCode}
          language={language}
          onLanguageChange={setLanguage}
          languages={LANGUAGES}
          onReview={handleReview}
          onClear={handleClear}
          loading={loading}
        />

        {error && (
          <div className="rounded-md bg-red-950 border border-red-800 p-4 text-red-300 text-sm">
            {error}
          </div>
        )}

        {result && <ReviewResults result={result} />}
      </div>
    </main>
  );
}
