import type { RiskTier } from "@/lib/api";

const labels: Record<RiskTier, { en: string; it: string }> = {
  unacceptable: { en: "UNACCEPTABLE", it: "INACCETTABILE" },
  high: { en: "HIGH RISK", it: "ALTO RISCHIO" },
  limited: { en: "LIMITED", it: "RISCHIO LIMITATO" },
  minimal: { en: "MINIMAL", it: "RISCHIO MINIMO" },
  auto: { en: "PENDING", it: "IN ATTESA" },
};

const colours: Record<RiskTier, string> = {
  unacceptable:
    "bg-tier-unacceptable-bg text-tier-unacceptable border-tier-unacceptable",
  high: "bg-tier-high-bg text-tier-high border-tier-high",
  limited: "bg-tier-limited-bg text-tier-limited border-tier-limited",
  minimal: "bg-tier-minimal-bg text-tier-minimal border-tier-minimal",
  auto: "bg-tier-auto-bg text-tier-auto border-tier-auto",
};

interface Props {
  tier: RiskTier;
  size?: "sm" | "md" | "lg";
  bilingual?: boolean;
}

/**
 * Pill-shaped badge for one of the four EU AI Act risk tiers (plus
 * ``auto`` for systems where a span arrived before the tenant declared
 * the system). Colours match the Annex IV PDF cover page so the trust
 * page reads as the same product.
 */
export function RiskBadge({ tier, size = "md", bilingual = false }: Props) {
  const padding =
    size === "lg"
      ? "px-4 py-2 text-base"
      : size === "sm"
        ? "px-2 py-0.5 text-xs"
        : "px-3 py-1 text-sm";
  const { en, it } = labels[tier];
  return (
    <span
      className={`inline-block rounded-full border font-semibold tracking-wider ${padding} ${colours[tier]}`}
    >
      {bilingual ? `${en} / ${it}` : en}
    </span>
  );
}
