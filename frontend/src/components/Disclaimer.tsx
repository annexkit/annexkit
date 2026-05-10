/**
 * Permanent disclaimer required on every public trust surface.
 *
 * Project non-negotiable: any UI surface that gives compliance output
 * must say "AnnexKit non è uno studio legale". Trust pages are exactly
 * that kind of surface.
 *
 * Visual: a muted cobalt-tinted callout. Doesn't shout (this is not an
 * error or a warning), but the cobalt left-border + slight tint on the
 * background pull the eye enough that the reader notices the disclaimer
 * before they leave the page.
 */
export function Disclaimer() {
  return (
    <aside className="rounded-lg border border-border bg-secondary/60 p-4 text-sm text-foreground">
      <p className="border-l-2 border-[var(--brand-cobalt)] pl-3">
        <strong className="font-semibold">
          AnnexKit is not a law firm / AnnexKit non è uno studio legale.
        </strong>{" "}
        <span className="text-muted-foreground">
          Trust pages render technical declarations the named tenant has
          published via the AnnexKit pipeline. The presence of a system on
          this page does not constitute a conformity assessment or legal
          certification; the tenant&rsquo;s legal counsel is responsible
          for the related Article 47 EU declaration of conformity.
        </span>
      </p>
    </aside>
  );
}
