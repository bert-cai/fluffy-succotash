"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { respondToInterview, getArgument } from "@/lib/api";
import { InterviewStep } from "@/components/InterviewStep";

export default function InterviewPage() {
  const router = useRouter();
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<string[]>([]);
  const [stepNumber, setStepNumber] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [isBuilding, setIsBuilding] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [failedMessage, setFailedMessage] = useState<string | null>(null);

  useEffect(() => {
    const stored = sessionStorage.getItem("firstMessage");
    const id = sessionStorage.getItem("sessionId");
    if (!stored || !id) {
      router.push("/");
      return;
    }
    setSessionId(id);
    setMessages([stored]);
  }, [router]);

  const handleSubmit = useCallback(
    async (userMessage: string) => {
      if (!sessionId) return;
      setIsLoading(true);
      setError(null);
      setFailedMessage(null);
      try {
        const resp = await respondToInterview(sessionId, userMessage);
        setMessages((prev) => [...prev, userMessage, resp.message]);
        setStepNumber((n) => n + 1);

        if (resp.is_complete) {
          setIsBuilding(true);
          const argument = await getArgument(sessionId);
          const regUrl = sessionStorage.getItem("regulationsGovUrl") ?? "";
          sessionStorage.setItem("argument", JSON.stringify(argument));
          sessionStorage.setItem("regulationsGovUrl", regUrl);
          router.push(`/interview/${encodeURIComponent(sessionId)}/result`);
        }
      } catch (e) {
        setError(e instanceof Error ? e.message : "Something went wrong");
        setFailedMessage(userMessage);
      } finally {
        setIsLoading(false);
      }
    },
    [sessionId, router],
  );

  const handleRetry = useCallback(() => {
    if (failedMessage) {
      handleSubmit(failedMessage);
    }
  }, [failedMessage, handleSubmit]);

  if (!sessionId || messages.length === 0) {
    return null;
  }

  if (isBuilding) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-8">
        <header className="mb-6">
          <a href="/" className="text-xl font-bold text-dark">
            Participate
          </a>
        </header>
        <div className="flex flex-col items-center gap-3 py-20">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-accent border-t-transparent" />
          <p className="text-sm text-mid">
            Building your comment argument...
          </p>
        </div>
      </div>
    );
  }

  const lastAssistantMessage = messages[messages.length - 1];

  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      <header className="mb-6">
        <a href="/" className="text-xl font-bold text-dark">
          Participate
        </a>
      </header>

      <InterviewStep
        question={lastAssistantMessage}
        onSubmit={handleSubmit}
        isLoading={isLoading}
        stepNumber={stepNumber}
        estimatedTotal={4}
      />

      {error && (
        <div className="mt-4 rounded-lg bg-accent/10 p-4">
          <p className="text-sm text-accent">{error}</p>
          <button
            onClick={handleRetry}
            className="mt-2 text-sm font-medium text-accent hover:text-accent-hover"
          >
            Try again
          </button>
        </div>
      )}
    </div>
  );
}
