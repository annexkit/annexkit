"use client";

/**
 * Client-side download buttons + tabbed usage examples for
 * /tools/logging-schema.
 *
 * Two downloads:
 *   - Vanilla schema (`v1.json`)            — for validators / CI
 *   - Annotated schema (`v1.json` + x-aiact-*) — for docs / training
 *
 * Three usage tabs:
 *   - Python (Pydantic) — validate inbound spans
 *   - TypeScript (AJV)  — validate inbound spans
 *   - curl              — fetch the schema directly
 */

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { CLIENT_API_URL } from "@/lib/api";
import { cn } from "@/lib/utils";

export interface AnnotatedSchemaProperty {
  description?: string;
  "x-aiact-clause"?: string;
  "x-purpose"?: string;
  [key: string]: unknown;
}

export interface AnnotatedSchema {
  title: string;
  "x-version": string;
  "x-source": string;
  properties: Record<string, AnnotatedSchemaProperty>;
  required?: string[];
  [key: string]: unknown;
}

type Tab = "python" | "typescript" | "curl";

const VANILLA_URL = `${CLIENT_API_URL}/api/v1/tools/article-12-schema/v1.json`;
const ANNOTATED_URL = `${CLIENT_API_URL}/api/v1/tools/article-12-schema-annotated/v1.json`;

const PYTHON_EXAMPLE = `# Validate spans before sending — fail fast in CI.
# pip install pydantic httpx

from pydantic import BaseModel, ConfigDict
import httpx

# Pull the schema from the AnnexKit collector. Pin to /v1.json
# so a future shape change doesn't surprise your CI.
schema = httpx.get(
    "https://annexkit.dev/api/v1/tools/article-12-schema/v1.json",
    timeout=5,
).json()

# Or just use the SDK's Pydantic class directly:
from annexkit.schema import Span

s = Span(
    system_id="loan-screener",
    started_at="2026-05-23T16:20:00Z",
    sdk_version="0.1.3",
)
print(s.model_dump_json())
`;

const TYPESCRIPT_EXAMPLE = `// Validate spans before sending — drop-in for Node / Edge runtimes.
// npm i ajv ajv-formats

import Ajv from "ajv";
import addFormats from "ajv-formats";

const schema = await fetch(
  "https://annexkit.dev/api/v1/tools/article-12-schema/v1.json",
).then((r) => r.json());

const ajv = new Ajv({ strict: false });
addFormats(ajv);
const validate = ajv.compile(schema);

const span = {
  trace_id: crypto.randomUUID().replace(/-/g, ""),
  span_id: crypto.randomUUID().replace(/-/g, "").slice(0, 16),
  system_id: "loan-screener",
  started_at: new Date().toISOString(),
  sdk_version: "0.1.0",
};

if (!validate(span)) {
  console.error("Span rejected by AnnexKit schema:", validate.errors);
}
`;

const CURL_EXAMPLE = `# Fetch the schemas straight to a file.

curl -o article-12-schema.v1.json \\
  https://annexkit.dev/api/v1/tools/article-12-schema/v1.json

curl -o article-12-schema-annotated.v1.json \\
  https://annexkit.dev/api/v1/tools/article-12-schema-annotated/v1.json

# Inspect the annotated variant — every field carries x-aiact-clause:
cat article-12-schema-annotated.v1.json | \\
  jq '.properties | to_entries[] | {field: .key, clause: .value."x-aiact-clause"}'
`;

export function SchemaTool({ schema }: { schema: AnnotatedSchema }) {
  const [activeTab, setActiveTab] = useState<Tab>("python");
  const [downloading, setDownloading] = useState<"vanilla" | "annotated" | null>(null);

  async function downloadSchema(variant: "vanilla" | "annotated") {
    if (downloading) return;
    setDownloading(variant);
    try {
      const url = variant === "vanilla" ? VANILLA_URL : ANNOTATED_URL;
      const filename =
        variant === "vanilla"
          ? "article-12-schema.v1.json"
          : "article-12-schema-annotated.v1.json";
      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const blob = await res.blob();
      const objUrl = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = objUrl;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(objUrl);
    } catch (err) {
      console.error("Schema download failed:", err);
      alert("Schema download failed. Please retry or use the curl example below.");
    } finally {
      setDownloading(null);
    }
  }

  const fieldCount = Object.keys(schema.properties).length;

  return (
    <>
      {/* --- Download buttons --- */}
      <section className="grid gap-4 sm:grid-cols-2">
        <div className="rounded-lg border border-border bg-card p-6">
          <h3 className="mb-2 text-lg font-semibold text-foreground">
            Vanilla schema (v1)
          </h3>
          <p className="mb-4 text-sm text-muted-foreground">
            {fieldCount} fields. Pydantic JSON-Schema export. Drop into any
            validator (AJV, jsonschema, OTel collector).
          </p>
          <Button
            onClick={() => downloadSchema("vanilla")}
            disabled={downloading !== null}
            className="w-full"
          >
            {downloading === "vanilla" ? "Downloading…" : "Download v1.json"}
          </Button>
        </div>

        <div className="rounded-lg border border-[var(--brand-cobalt)]/40 bg-[var(--brand-cobalt)]/5 p-6">
          <h3 className="mb-2 text-lg font-semibold text-foreground">
            Annotated schema (v1)
          </h3>
          <p className="mb-4 text-sm text-muted-foreground">
            Same fields, plus <code className="inline-code">x-aiact-clause</code>
            {" "}+ <code className="inline-code">x-purpose</code> on each
            property. For docs, training, audit packs.
          </p>
          <Button
            onClick={() => downloadSchema("annotated")}
            disabled={downloading !== null}
            variant="secondary"
            className="w-full"
          >
            {downloading === "annotated" ? "Downloading…" : "Download annotated v1.json"}
          </Button>
        </div>
      </section>

      {/* --- Tabs --- */}
      <section className="mt-10">
        <h2 className="mb-4 text-2xl font-semibold text-foreground">
          Use the schema
        </h2>
        <div className="border-b border-border">
          <nav className="flex gap-1" role="tablist">
            {(["python", "typescript", "curl"] as const).map((t) => (
              <button
                key={t}
                role="tab"
                aria-selected={activeTab === t}
                onClick={() => setActiveTab(t)}
                className={cn(
                  "rounded-t-md px-4 py-2 text-sm font-medium transition-colors",
                  activeTab === t
                    ? "border border-b-0 border-border bg-card text-foreground"
                    : "text-muted-foreground hover:bg-muted/40 hover:text-foreground",
                )}
              >
                {t === "python" && "Python (Pydantic)"}
                {t === "typescript" && "TypeScript (AJV)"}
                {t === "curl" && "curl + jq"}
              </button>
            ))}
          </nav>
        </div>
        <pre className="overflow-x-auto rounded-b-md rounded-tr-md border border-t-0 border-border bg-card p-4 text-xs leading-relaxed">
          <code>
            {activeTab === "python" && PYTHON_EXAMPLE}
            {activeTab === "typescript" && TYPESCRIPT_EXAMPLE}
            {activeTab === "curl" && CURL_EXAMPLE}
          </code>
        </pre>
      </section>
    </>
  );
}
