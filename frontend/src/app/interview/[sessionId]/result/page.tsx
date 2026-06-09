"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
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
      router.push("/browse");
      return;
    }
    // Hydrate state once from sessionStorage (a browser-only external store)
    // on mount; this data isn't available during SSR.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setArgument(JSON.parse(stored) as CommentArgument);
    setRegulationsGovUrl(url);
  }, [router]);

  if (!argument) {
    return null;
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      <header className="mb-6">
        <Link href="/" className="text-xl font-bold text-dark font-heading">
          Civly
        </Link>
      </header>

      <h1 className="mb-6 text-2xl font-bold text-dark">
        Your comment argument
      </h1>

      <ArgumentDisplay
        argument={argument}
        regulationsGovUrl={regulationsGovUrl}
      />
    </div>
  );
}
