"use client";

import { useState, useRef, useEffect } from "react";

export function InterviewStep({
  question,
  onSubmit,
  isLoading,
  stepNumber,
  estimatedTotal,
}: {
  question: string;
  onSubmit: (message: string) => void;
  isLoading: boolean;
  stepNumber: number;
  estimatedTotal: number;
}) {
  const [text, setText] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    textareaRef.current?.focus();
  }, [question]);

  const progress = Math.min((stepNumber / estimatedTotal) * 100, 100);

  return (
    <div>
      <div className="mb-6">
        <p className="text-sm text-slate-500">
          {stepNumber} of ~{estimatedTotal}
        </p>
        <div className="mt-1 h-1.5 w-full rounded-full bg-slate-200">
          <div
            className="h-1.5 rounded-full bg-blue-600 transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      <p className="mb-6 text-xl font-medium text-slate-900">{question}</p>

      <textarea
        ref={textareaRef}
        rows={5}
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Share as much specific detail as you can — numbers, timelines, and concrete examples make comments more effective"
        className="w-full rounded-lg border border-slate-300 px-4 py-3 text-sm text-slate-900 placeholder-slate-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        disabled={isLoading}
      />

      <div className="mt-2 flex items-center justify-between">
        <span className="text-xs text-slate-400">
          {text.length} characters
        </span>
        <button
          onClick={() => {
            onSubmit(text);
            setText("");
          }}
          disabled={text.length < 20 || isLoading}
          className="rounded-lg bg-blue-600 px-6 py-3 text-sm font-medium text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-300 disabled:text-slate-500"
        >
          {isLoading ? "Thinking..." : "Continue →"}
        </button>
      </div>
    </div>
  );
}
