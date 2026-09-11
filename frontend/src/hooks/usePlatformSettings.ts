/**
 * CodeAcademy Pro — Platform Settings Hook
 * Loads public platform settings once and caches them.
 */
"use client";

import { useEffect, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api/v1";
const CACHE_KEY = "platform_settings";
const CACHE_TTL_MS = 5 * 60 * 1000; // 5 minutes

export interface PlatformSettings {
  platform_name: string;
  default_currency: string;
  currency_symbol: string;
  global_max_students_per_class: number;
}

const DEFAULTS: PlatformSettings = {
  platform_name: "CodeAcademy Pro",
  default_currency: "USD",
  currency_symbol: "US$",
  global_max_students_per_class: 100,
};

function getCached(): PlatformSettings | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem(CACHE_KEY);
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw);
    if (Date.now() - parsed.ts < CACHE_TTL_MS) {
      return parsed.data;
    }
  } catch {
    /* ignore */
  }
  return null;
}

function setCached(data: PlatformSettings) {
  if (typeof window === "undefined") return;
  localStorage.setItem(CACHE_KEY, JSON.stringify({ ts: Date.now(), data }));
}

export function usePlatformSettings() {
  const [settings, setSettings] = useState<PlatformSettings>(DEFAULTS);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const cached = getCached();
    if (cached) {
      setSettings(cached);
      setLoaded(true);
    }

    fetch(`${API_BASE}/settings/public`)
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => {
        if (data) {
          const merged: PlatformSettings = {
            platform_name: data.platform_name ?? DEFAULTS.platform_name,
            default_currency: data.default_currency ?? DEFAULTS.default_currency,
            currency_symbol: data.currency_symbol ?? DEFAULTS.currency_symbol,
            global_max_students_per_class:
              data.global_max_students_per_class ?? DEFAULTS.global_max_students_per_class,
          };
          setSettings(merged);
          setCached(merged);
        }
      })
      .catch(() => {})
      .finally(() => setLoaded(true));
  }, []);

  return { settings, loaded };
}
