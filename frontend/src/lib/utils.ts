/**
 * CodeAcademy Pro — General Utilities
 */

/** Format price with currency symbol */
export function formatPrice(amount: number, currency = "USD"): string {
  return new Intl.NumberFormat("es", { style: "currency", currency }).format(amount);
}

/** Format date to localized string */
export function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("es", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

/** Format relative time (e.g., "hace 5 min") */
export function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60_000);
  if (mins < 1) return "Ahora";
  if (mins < 60) return `Hace ${mins} min`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `Hace ${hours}h`;
  const days = Math.floor(hours / 24);
  return `Hace ${days}d`;
}

/** Clsx-like utility for conditional class names */
export function cn(...classes: (string | false | null | undefined)[]): string {
  return classes.filter(Boolean).join(" ");
}

/** Truncate text */
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + "...";
}

/** Level label in Spanish */
export function levelLabel(level: string): string {
  const labels: Record<string, string> = {
    beginner: "Principiante",
    intermediate: "Intermedio",
    advanced: "Avanzado",
  };
  return labels[level] || level;
}
