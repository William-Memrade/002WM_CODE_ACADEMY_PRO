/**
 * CodeAcademy Pro — Currency helpers
 * Centralised formatting for all price displays.
 */

/** Currency code → disambiguated display symbol (LATAM-safe) */
export const CURRENCY_SYMBOLS: Record<string, string> = {
  USD: "US$",
  EUR: "€",
  MXN: "MX$",
  COP: "COP$",
  GTQ: "Q",
  HNL: "L",
  NIO: "C$",
  CRC: "₡",
  SVC: "$",
};

/** Return symbol for a currency code, falling back to the code itself. */
export function getCurrencySymbol(code: string): string {
  return CURRENCY_SYMBOLS[code.toUpperCase()] ?? code.toUpperCase();
}

/**
 * Format a numeric amount with the platform currency symbol.
 * Output: "US$29.99", "MX$499.00", "€29.99", etc.
 */
export function formatCurrency(
  amount: number,
  currencyCode: string = "USD"
): string {
  const symbol = getCurrencySymbol(currencyCode);
  // Always show 2 decimals for consistency
  const formatted = amount.toLocaleString("es", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
  return `${symbol}${formatted}`;
}
