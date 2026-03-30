import Image from "next/image";

export default function LandingPage() {
  return (
    <div className="bg-light">
      {/* Nav */}
      <nav className="flex items-center justify-between px-6 py-4">
        <a href="/" className="font-heading font-semibold text-dark">
          Civly
        </a>
      </nav>

      {/* Hero */}
      <div className="mx-auto max-w-3xl px-6 pt-24 pb-16 text-center">
        <h1 className="font-heading text-5xl font-bold leading-tight text-dark max-md:text-4xl">
          Democratizing the rulemaking process
        </h1>
        <p className="mx-auto mt-6 max-w-2xl font-body text-xl text-mid">
          Federal agencies are legally required to listen to your feedback,
          but the process is dominanted by powerful corporate lobbyists. We
          cut through the sludge. Make your voice heard today, completely free.
        </p>
        <a
          href="/browse"
          className="mt-10 inline-block rounded-lg bg-accent px-8 py-4 font-heading text-lg font-semibold text-light transition-opacity hover:opacity-90"
        >
          Try it now →
        </a>

        {/* Decorative accent bar */}
        <div className="mx-auto mt-12 h-1 w-24 rounded-full bg-accent" />
      </div>

      {/* Product screenshot */}
      <div className="mx-auto max-w-4xl px-6 pb-16 mt-8">
        <Image
          src="/app-screenshot.png"
          alt="Civly app showing open federal comment periods"
          width={2940}
          height={1666}
          className="rounded-xl border border-subtle shadow-2xl"
          priority
        />
      </div>

      {/* Value props */}
      <section className="border-t border-subtle">
        <div className="mx-auto grid max-w-4xl gap-12 px-6 py-16 md:grid-cols-3">
          <div className="border-l-[3px] border-accent pl-4">
            <h2 className="font-heading text-lg font-semibold text-dark">
              Open right now
            </h2>
            <p className="mt-2 font-body text-sm text-mid">
              Dozens of federal regulations accept public comments at any given
              time. We surface the ones that matter and tell you how long you
              have.
            </p>
          </div>
          <div className="border-l-[3px] border-secondary pl-4">
            <h2 className="font-heading text-lg font-semibold text-dark">
              Your input is legally binding
            </h2>
            <p className="mt-2 font-body text-sm text-mid">
              Under the Administrative Procedure Act, agencies must respond to
              substantive comments on the record. Unlike petitions or protests,
              your impact is guaranteed.
            </p>
          </div>
          <div className="border-l-[3px] border-tertiary pl-4">
            <h2 className="font-heading text-lg font-semibold text-dark">
              We do the hard part
            </h2>
            <p className="mt-2 font-body text-sm text-mid">
              Our AI-powered software helps you to identify how
              new regulations will impact your small business, then writes a detailed
              comment outlining your case that the relevant agencies are obligated to answer.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-subtle bg-light py-8">
        <p className="text-center font-body text-sm text-mid">
          Civly &middot; Data from Regulations.gov &middot; Built for the public
        </p>
        <p className="text-center font-body text-sm text-mid">
          Problems? Feature suggestions?{' '}
          <a> 
            href="mailto:albert@albertcai.org"style={{ color: '#0000FF', textDecoration: 'none' }}
            let me know 
          </a>
        </p>
      </footer>
    </div>
  );
}
