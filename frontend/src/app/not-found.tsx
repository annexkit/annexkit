import Link from "next/link";
import { ArrowLeft } from "lucide-react";

import { Button } from "@/components/ui/button";

export default function NotFound() {
  return (
    <div className="mx-auto max-w-3xl px-6 py-20">
      <div className="space-y-6">
        <span className="eyebrow">404</span>
        <h1 className="text-balance text-4xl font-bold tracking-tight text-foreground">
          Page not found
        </h1>
        <p className="text-muted-foreground">
          The trust page or AI system you&rsquo;re looking for
          doesn&rsquo;t exist (or hasn&rsquo;t been declared yet on
          AnnexKit).
        </p>
        <div className="pt-2">
          <Button variant="outline" asChild>
            <Link href="/">
              <ArrowLeft />
              Back to home
            </Link>
          </Button>
        </div>
      </div>
    </div>
  );
}
