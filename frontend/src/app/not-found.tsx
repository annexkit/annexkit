import Link from "next/link";

export default function NotFound() {
  return (
    <div className="space-y-4">
      <h1 className="text-3xl font-bold text-neutral-900">Page not found</h1>
      <p className="text-neutral-700">
        The trust page or AI system you&rsquo;re looking for doesn&rsquo;t
        exist (or hasn&rsquo;t been declared yet on AnnexKit).
      </p>
      <p>
        <Link href="/" className="text-blue-700 underline">
          ← Back home
        </Link>
      </p>
    </div>
  );
}
