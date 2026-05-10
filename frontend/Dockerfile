# --------------------------------------------------------------------------
# AnnexKit trust-center frontend — Next.js 16
# --------------------------------------------------------------------------
# Multi-stage build:
#   1. deps    : install node_modules (cached on package.json change)
#   2. builder : compile + produce the standalone bundle
#   3. runner  : minimal runtime image with only what `next start` needs
# --------------------------------------------------------------------------

FROM node:22-bookworm-slim AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install --no-audit --no-fund

FROM node:22-bookworm-slim AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

FROM node:22-bookworm-slim AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
# Bind Next.js standalone server.js to all interfaces. Without this it
# listens on the container hostname's primary IP only, which breaks
# reverse proxying when the container is attached to multiple Docker
# networks (e.g. an external proxy on a shared network).
ENV HOSTNAME=0.0.0.0
ENV PORT=3000
# Standalone output bundles the minimal node_modules + a server.js entry.
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
EXPOSE 3000
CMD ["node", "server.js"]
