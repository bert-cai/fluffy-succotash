"use client";

import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";

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
        <p className="text-sm text-mid">
          {stepNumber} of ~{estimatedTotal}
        </p>
        <div className="mt-1 h-1.5 w-full rounded-full bg-subtle">
          <div
            className="h-1.5 rounded-full bg-accent transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      <div className="mb-6 text-dark [&>h1]:text-xl [&>h1]:font-semibold [&>h1]:mb-3 [&>p]:text-base [&>p]:mb-3 [&>p:last-child]:mb-0">
        <ReactMarkdown>{question}</ReactMarkdown>
      </div>

      <textarea
        ref={textareaRef}
        rows={5}
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Share as much specific detail as you can — numbers, timelines, and concrete examples make comments more effective"
        className="w-full rounded-lg border border-subtle px-4 py-3 text-sm text-dark placeholder-mid focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent"
        disabled={isLoading}
      />

      <div className="mt-2 flex items-center justify-between">
        <span className="text-xs text-mid">
          {text.length} characters
        </span>
        <button
          onClick={() => {
            onSubmit(text);
            setText("");
          }}
          disabled={text.length < 20 || isLoading}
          className="rounded-lg bg-accent px-6 py-3 text-sm font-medium font-heading text-light transition-colors hover:bg-accent-hover disabled:cursor-not-allowed disabled:bg-subtle disabled:text-mid"
        >
          {isLoading ? "Thinking..." : "Continue →"}
        </button>
      </div>
    </div>
  );
}
