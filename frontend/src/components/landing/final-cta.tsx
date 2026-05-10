/**
 * Final CTA — last band before the footer. Brand-wash background ties
 * back to the hero so the page bookends visually. Single primary action,
 * supporting GitHub link as a "still on the fence?" escape hatch.
 */

import Link from "next/link";
import { ArrowRight, Github } from "lucide-react";

import { Button } from "@/components/ui/button";

export function FinalCTA() {
  return (
    <section className="relative overflow-hidden brand-wash">
      <div className="absolute inset-0 surface-grid opacity-30" aria-hidden />
      <div className="relative mx-auto flex max-w-4xl flex-col items-center gap-6 px-6 py-24 text-center">
        <span className="eyebrow">Ship a trust page in 10 minutes</span>
        <h2 className="max-w-3xl text-balance text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
          Your next AI Act audit shouldn&rsquo;t cost an engineering
          quarter.
        </h2>
        <p className="max-w-2xl text-lg text-muted-foreground">
          One <code className="inline-code">pip install</code>, one
          decorator, and a hosted endpoint. The Annex IV PDF is on the
          other side.
        </p>
        <div className="flex flex-wrap justify-center gap-3 pt-3">
          <Button size="lg" asChild>
            <Link href="/pricing">
              Get started
              <ArrowRight />
            </Link>
          </Button>
          <Button size="lg" variant="outline" asChild>
            <a
              href="https://github.com/annexkit/annexkit"
              target="_blank"
              rel="noreferrer"
            >
              <Github />
              Star on GitHub
            </a>
          </Button>
        </div>
      </div>
    </section>
  );
}
