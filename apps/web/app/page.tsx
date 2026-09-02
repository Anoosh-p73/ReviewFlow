const currentCapabilities = [
  "A responsive, accessible application shell",
  "An API process liveness endpoint",
  "A documented incremental delivery roadmap",
] as const;

export default function Home() {
  return (
    <div className="relative min-h-screen overflow-hidden bg-canvas text-ink">
      <a className="skip-link" href="#main-content">
        Skip to main content
      </a>

      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-x-0 top-0 h-96 bg-[radial-gradient(circle_at_top_left,rgba(35,126,95,0.16),transparent_55%)]"
      />

      <div className="relative mx-auto flex min-h-screen w-full max-w-7xl flex-col px-5 sm:px-8 lg:px-12">
        <header className="flex items-center justify-between border-b border-line py-6 sm:py-8">
          <p className="flex items-center gap-3 text-sm font-semibold tracking-[0.16em] uppercase">
            <span
              aria-hidden="true"
              className="grid size-9 place-items-center rounded-lg bg-ink text-xs tracking-normal text-canvas shadow-sm"
            >
              RF
            </span>
            ReviewFlow
          </p>
          <p className="text-xs font-medium tracking-[0.14em] text-muted uppercase">
            Foundation preview
          </p>
        </header>

        <main
          className="grid flex-1 items-center gap-12 py-16 sm:py-24 lg:grid-cols-[minmax(0,1.25fr)_minmax(20rem,0.75fr)] lg:gap-20 lg:py-28"
          id="main-content"
          tabIndex={-1}
        >
          <section aria-labelledby="page-title" className="max-w-3xl">
            <p className="mb-6 flex items-center gap-3 text-xs font-bold tracking-[0.18em] text-accent uppercase">
              <span aria-hidden="true" className="h-px w-9 bg-accent" />
              Engineering review workspace
            </p>
            <h1
              className="max-w-4xl text-5xl leading-[0.98] font-semibold tracking-[-0.045em] text-balance sm:text-6xl lg:text-7xl"
              id="page-title"
            >
              Clear decisions start with a clear review trail.
            </h1>
            <p className="mt-8 max-w-2xl text-lg leading-8 text-muted sm:text-xl sm:leading-9">
              ReviewFlow is being built for interdisciplinary engineering teams to manage document
              reviews, comments, and resolution history with confidence.
            </p>

            <div className="mt-10 max-w-2xl border-l-2 border-accent bg-surface/70 px-5 py-4 sm:px-6">
              <p className="text-sm font-semibold text-ink">This release is foundation-only.</p>
              <p className="mt-1 text-sm leading-6 text-muted">
                Product workflows are not available yet. They will appear only as the roadmap adds
                real, tested behavior.
              </p>
            </div>
          </section>

          <aside
            aria-labelledby="current-scope-title"
            className="rounded-3xl border border-line bg-surface/90 p-6 shadow-panel backdrop-blur-sm sm:p-8"
          >
            <div className="flex items-center justify-between gap-4 border-b border-line pb-5">
              <p className="text-xs font-bold tracking-[0.16em] text-muted uppercase">
                Project status
              </p>
              <p className="flex items-center gap-2 text-xs font-semibold text-accent-strong">
                <span aria-hidden="true" className="size-2 rounded-full bg-accent" />
                In development
              </p>
            </div>

            <h2
              className="mt-7 text-2xl font-semibold tracking-[-0.025em]"
              id="current-scope-title"
            >
              What exists today
            </h2>
            <ul className="mt-6 space-y-4">
              {currentCapabilities.map((capability) => (
                <li className="flex gap-3 text-sm leading-6 text-muted" key={capability}>
                  <span
                    aria-hidden="true"
                    className="mt-2 size-1.5 shrink-0 rounded-full bg-accent"
                  />
                  {capability}
                </li>
              ))}
            </ul>

            <div className="mt-8 rounded-2xl bg-canvas px-5 py-4">
              <p className="text-sm font-semibold text-ink">Intentionally deferred</p>
              <p className="mt-1 text-sm leading-6 text-muted">
                Sign-in, navigation, dashboards, and review controls arrive in later roadmap tasks.
              </p>
            </div>
          </aside>
        </main>

        <footer className="flex flex-col gap-2 border-t border-line py-6 text-xs text-muted sm:flex-row sm:items-center sm:justify-between sm:py-8">
          <p>Technical document review and comment resolution.</p>
          <p>Planning-stage software</p>
        </footer>
      </div>
    </div>
  );
}
