/**
 * Permanent disclaimer required on every public trust surface.
 *
 * Project non-negotiable #6: "Disclaimer is permanent. Any UI surface
 * that gives compliance output must say 'AnnexKit non è uno studio
 * legale'." The trust pages are exactly that kind of surface.
 */
export function Disclaimer() {
  return (
    <aside className="rounded border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
      <strong>AnnexKit is not a law firm / AnnexKit non è uno studio legale.</strong>{" "}
      Trust pages render technical declarations the named tenant has
      published via the AnnexKit pipeline. The presence of a system on
      this page does not constitute a conformity assessment or legal
      certification; the tenant&rsquo;s legal counsel is responsible for
      the related Article 47 EU declaration of conformity.
    </aside>
  );
}
