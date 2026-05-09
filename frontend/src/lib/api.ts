/**
 * Backend trust-center API client.
 *
 * Everything is server-side rendered (no React Suspense / client
 * fetches yet) so the backend URL only needs to resolve from the
 * Next.js process. ``BACKEND_URL`` differs by environment:
 *
 *   - host dev (``npm run dev``):  http://localhost:8033
 *   - docker compose:              http://backend:8000
 *   - prod:                        whatever the cluster maps
 *
 * No auth is sent — the trust endpoints are intentionally public.
 *
 * Resilience contract:
 *   * 404 from the collector → ``fetchJson`` returns ``null``. Page
 *     handlers turn that into ``notFound()`` (Next.js 404 page).
 *   * Anything else (5xx, network failure, JSON parse error) →
 *     ``BackendUnavailableError`` is thrown. Page handlers catch it
 *     and render the ``<BackendUnavailable />`` component instead of
 *     bubbling to a generic Next.js 500.
 *
 * The 60-second revalidation window means trust pages cache between
 * requests; trust data does not change second-to-second so this is a
 * good trade-off for collector load + perceived performance.
 */

export const BACKEND_URL =
  process.env.BACKEND_URL ?? "http://localhost:8033";

const REVALIDATE_SECONDS = 60;

/**
 * Thrown when the collector is unreachable, returns 5xx, or returns
 * malformed JSON. Page handlers catch this to render a graceful
 * "temporarily unavailable" component.
 */
export class BackendUnavailableError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "BackendUnavailableError";
  }
}

export type RiskTier =
  | "unacceptable"
  | "high"
  | "limited"
  | "minimal"
  | "auto";

export interface PublicTenant {
  name: string;
  slug: string;
}

export interface TierBreakdown {
  unacceptable: number;
  high: number;
  limited: number;
  minimal: number;
  auto: number;
}

export interface TrustOverview {
  tenant: PublicTenant;
  total_systems: number;
  by_tier: TierBreakdown;
  annexkit_version: string;
  as_of: string;
}

export interface PublicSystemSummary {
  system_id: string;
  purpose: string | null;
  risk_tier: RiskTier;
  annex_iii_categories: string[];
  transparency_triggers: string[];
  is_gpai: boolean;
  rules_version: string;
  classified_at: string;
}

export interface TrustSystemsResponse {
  tenant: PublicTenant;
  systems: PublicSystemSummary[];
  annexkit_version: string;
  as_of: string;
}

export interface PublicReasoningEntry {
  rule_id: string;
  rule_type: string;
  article: string;
  name_it: string;
  name_en: string;
}

export interface PublicProviderInfo {
  legal_name: string | null;
  address: string | null;
  country: string | null;
  authorised_representative: string | null;
  system_version: string | null;
  software_environment: string | null;
  hardware_environment: string | null;
}

export interface PublicSystemDetail {
  system_id: string;
  purpose: string | null;
  risk_tier: RiskTier;
  annex_iii_categories: string[];
  prohibited_practices: string[];
  transparency_triggers: string[];
  is_gpai: boolean;
  rules_version: string;
  reasoning: PublicReasoningEntry[];
  classified_at: string;
  created_at: string;
  updated_at: string;
  provider_info: PublicProviderInfo;
}

export interface TrustSystemDetailResponse {
  tenant: PublicTenant;
  system: PublicSystemDetail;
  annexkit_version: string;
  as_of: string;
}

async function fetchJson<T>(path: string): Promise<T | null> {
  const url = `${BACKEND_URL}${path}`;
  let res: Response;
  try {
    res = await fetch(url, { next: { revalidate: REVALIDATE_SECONDS } });
  } catch (err) {
    // Network failure (DNS, ECONNREFUSED, TLS, etc.). Don't leak the
    // backend URL to the user — page handlers render a friendly
    // component on this error class.
    throw new BackendUnavailableError(
      `Network failure reaching collector at path ${path}`,
    );
  }
  if (res.status === 404) return null;
  if (res.status >= 500) {
    throw new BackendUnavailableError(
      `Collector returned ${res.status} for ${path}`,
    );
  }
  if (!res.ok) {
    // Treat 4xx (other than 404) as backend unavailability rather
    // than crashing the page — these shouldn't happen for unauthed
    // public endpoints, but if they do (e.g. a future rate limit)
    // the user gets the friendly fallback.
    throw new BackendUnavailableError(
      `Collector returned ${res.status} for ${path}`,
    );
  }
  try {
    return (await res.json()) as T;
  } catch (err) {
    throw new BackendUnavailableError(
      `Collector returned malformed JSON for ${path}`,
    );
  }
}

export const trustApi = {
  overview: (slug: string) =>
    fetchJson<TrustOverview>(`/api/v1/trust/${encodeURIComponent(slug)}`),
  listSystems: (slug: string) =>
    fetchJson<TrustSystemsResponse>(
      `/api/v1/trust/${encodeURIComponent(slug)}/systems`,
    ),
  getSystem: (slug: string, systemId: string) =>
    fetchJson<TrustSystemDetailResponse>(
      `/api/v1/trust/${encodeURIComponent(slug)}/systems/${encodeURIComponent(systemId)}`,
    ),
};
