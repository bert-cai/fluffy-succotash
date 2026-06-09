import Image from "next/image";
import Link from "next/link";

export default function LandingPage() {
  return (
    <div className="bg-light">
      {/* Nav */}
      <nav className="flex items-center justify-between px-6 py-4">
        <Link href="/" className="font-heading font-semibold text-dark">
          Civly
        </Link>
      </nav>

      {/* Hero */}
      <div className="mx-auto max-w-3xl px-6 pt-24 pb-16 text-center">
        <h1 className="font-heading text-5xl font-bold leading-tight text-balance text-dark max-md:text-4xl">
          Democratizing the rulemaking process
        </h1>
        <p className="mx-auto mt-6 max-w-2xl font-body text-xl text-ink-soft">
          Federal agencies must consider your feedback on proposed rules, but
          the process is dominated by corporate lobbyists. We cut through the
          sludge so your voice counts, completely free.
        </p>
        <Link
          href="/browse"
          className="mt-10 inline-block rounded-lg bg-accent px-8 py-4 font-heading text-lg font-semibold text-light transition-opacity hover:opacity-90"
        >
          Try it now →
        </Link>

        {/* Decorative accent bar */}
        <div className="mx-auto mt-12 h-1 w-24 rounded-full bg-accent" />
      </div>

      {/* Live closing-soon comment periods; falls back to the product screenshot */}
      <div className="mt-8 pb-16">
        <ClosingSoon />
      </div>

      {/* Value props */}
      <section className="border-t border-subtle">
        <div className="mx-auto grid max-w-3xl gap-x-10 gap-y-12 px-6 py-20 md:grid-cols-2">
          <div>
            <h2 className="font-heading text-lg font-semibold text-dark">
              Your input is legally binding
            </h2>
            <p className="mt-3 font-body text-sm leading-relaxed text-ink-soft">
              Under the Administrative Procedure Act, agencies must respond to
              substantive comments on the record. Unlike a petition or a
              protest, you are guaranteed a response.
            </p>
          </div>
          <div>
            <h2 className="font-heading text-lg font-semibold text-dark">
              We do the hard part
            </h2>
            <p className="mt-3 font-body text-sm leading-relaxed text-ink-soft">
              We read the proposed rule, pinpoint how it affects your business,
              and draft a comment that makes your case.
            </p>
          </div>
        </div>
      </section>

      {/* Closing CTA */}
      <section className="border-t border-subtle">
        <div className="mx-auto max-w-3xl px-6 py-20 text-center">
          <h2 className="font-heading text-3xl font-bold text-balance text-dark max-md:text-2xl">
            Find the rule that affects you
          </h2>
          <p className="mx-auto mt-4 max-w-xl font-body text-base leading-relaxed text-ink-soft">
            It takes a few minutes. We help you write a comment the agency is
            legally required to answer, on the record.
          </p>
          <Link
            href="/browse"
            className="mt-8 inline-block rounded-lg bg-accent px-8 py-4 font-heading text-lg font-semibold text-light transition-opacity hover:opacity-90"
          >
            Browse open rules →
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-subtle bg-light py-8">
        <p className="text-center font-body text-sm text-mid">
          Civly &middot; Data from Regulations.gov &middot; Built for the public
        </p>
        <p className="mt-2 text-center font-body text-sm text-ink-soft">
          Problems? Feature suggestions?{' '}
          <a
            href="mailto:albert@albertcai.org"
            className="text-accent underline"
          >
            Let me know
          </a>
        </p>
      </footer>
    </div>
  );
}
