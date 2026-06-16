/**
 * Locale-friendly formatting helpers.
 *
 * The trust pages are public + likely to be skim-read; raw ISO 8601
 * timestamps make the page feel "engineering tool that escaped the
 * dashboard." Intl.DateTimeFormat in en-GB gives us
 * "7 May 2026, 14:23 UTC" — readable to a procurement officer
 * without translation, machine-parseable, locale-stable across
 * server + client (we always render in UTC).
 */

const DATE_TIME = new Intl.DateTimeFormat("en-GB", {
  day: "numeric",
  month: "long",
  year: "numeric",
  hour: "2-digit",
  minute: "2-digit",
  timeZone: "UTC",
  timeZoneName: "short",
});

const DATE_ONLY = new Intl.DateTimeFormat("en-GB", {
  day: "numeric",
  month: "long",
  year: "numeric",
  timeZone: "UTC",
});

export function formatDateTime(iso: string | null | undefined): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return DATE_TIME.format(d);
}

export function formatDate(iso: string | null | undefined): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return DATE_ONLY.format(d);
}
