"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ArgumentDisplay } from "@/components/ArgumentDisplay";
import type { CommentArgument } from "@/types";

export default function ResultPage() {
  const router = useRouter();
  const [argument, setArgument] = useState<CommentArgument | null>(null);
  const [regulationsGovUrl, setRegulationsGovUrl] = useState("");

  useEffect(() => {
    const stored = sessionStorage.getItem("argument");
    const url = sessionStorage.getItem("regulationsGovUrl");
    if (!stored || !url) {
      router.push("/");
      return;
    }
    setArgument(JSON.parse(stored) as CommentArgument);
    setRegulationsGovUrl(url);
  }, [router]);

  if (!argument) {
    return null;
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      <header className="mb-6">
        <a href="/" className="text-xl font-bold text-slate-900">
          Participate
        </a>
      </header>

      <h1 className="mb-6 text-2xl font-bold text-slate-900">
        Your comment argument
      </h1>

      <ArgumentDisplay
        argument={argument}
        regulationsGovUrl={regulationsGovUrl}
      />
    </div>
  );
}
