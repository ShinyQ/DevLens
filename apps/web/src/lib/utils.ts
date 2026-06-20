import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatTokens(tokens: number | undefined): string {
  if (tokens === undefined || tokens === null) return "—";
  if (tokens >= 1_000_000_000) return `${(tokens / 1_000_000_000).toFixed(1)}B`;
  if (tokens >= 1_000_000) return `${(tokens / 1_000_000).toFixed(1)}M`;
  if (tokens >= 1_000) return `${(tokens / 1_000).toFixed(1)}K`;
  return tokens.toString();
}

export function formatCost(cost: number | undefined): string {
  if (cost === undefined || cost === null) return "—";
  if (cost === 0) return "$0.00";
  if (cost < 0.01) return `$${cost.toFixed(4)}`;
  if (cost < 1) return `$${cost.toFixed(3)}`;
  return `$${cost.toFixed(2)}`;
}

export function formatDuration(minutes: number | undefined | null): string {
  if (minutes === undefined || minutes === null) return "—";
  if (minutes < 1) return "<1m";
  if (minutes < 60) return `${Math.round(minutes)}m`;
  const h = Math.floor(minutes / 60);
  const m = Math.round(minutes % 60);
  return m > 0 ? `${h}h ${m}m` : `${h}h`;
}

export function formatDate(dt: string | undefined | null): string {
  if (!dt) return "—";
  return new Date(dt).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export function formatDateTime(dt: string | undefined | null): string {
  if (!dt) return "—";
  return new Date(dt).toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function formatNumber(n: number | undefined): string {
  if (n === undefined || n === null) return "—";
  return n.toLocaleString();
}

export function truncateSessionId(id: string, length = 8): string {
  return id.slice(0, length);
}

export function modelDisplayName(model: string | null | undefined): string {
  if (!model) return "Unknown";
  if (model.includes("opus-4")) return "Opus 4";
  if (model.includes("sonnet-4-6")) return "Sonnet 4.6";
  if (model.includes("sonnet-4-5")) return "Sonnet 4.5";
  if (model.includes("sonnet-4")) return "Sonnet 4";
  if (model.includes("haiku-4-5")) return "Haiku 4.5";
  if (model.includes("haiku-4")) return "Haiku 4";
  if (model.includes("3-5-sonnet")) return "3.5 Sonnet";
  if (model.includes("3-5-haiku")) return "3.5 Haiku";
  if (model.includes("3-opus")) return "3 Opus";
  return model;
}
