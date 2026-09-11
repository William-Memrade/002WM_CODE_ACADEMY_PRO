"use client";

import { useEffect, useRef, useState, useCallback } from "react";

const SITE_KEY = process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY || "";

let scriptPromise: Promise<void> | null = null;

function loadRecaptchaScript(): Promise<void> {
  if (typeof window === "undefined") return Promise.resolve();
  if ((window as any).grecaptcha) return Promise.resolve();
  if (scriptPromise) return scriptPromise;
  scriptPromise = new Promise<void>((resolve) => {
    const s = document.createElement("script");
    s.src = `https://www.google.com/recaptcha/api.js?render=explicit`;
    s.async = true;
    s.defer = true;
    s.onload = () => resolve();
    s.onerror = () => resolve();
    document.head.appendChild(s);
  });
  return scriptPromise;
}

interface CaptchaProps {
  onVerify: (token: string) => void;
  onExpire?: () => void;
}

export function isCaptchaEnabled(): boolean {
  return !!SITE_KEY;
}

export default function Captcha({ onVerify, onExpire }: CaptchaProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const widgetIdRef = useRef<number | null>(null);
  const onVerifyRef = useRef(onVerify);
  const onExpireRef = useRef(onExpire);
  const [loaded, setLoaded] = useState(false);

  // Keep latest callbacks in refs without re-rendering the widget.
  useEffect(() => {
    onVerifyRef.current = onVerify;
    onExpireRef.current = onExpire;
  }, [onVerify, onExpire]);

  useEffect(() => {
    if (!SITE_KEY) return;
    let cancelled = false;

    const renderWidget = () => {
      if (cancelled || !containerRef.current || !(window as any).grecaptcha) return;
      const grecaptcha = (window as any).grecaptcha;
      try {
        widgetIdRef.current = grecaptcha.render(containerRef.current!, {
          sitekey: SITE_KEY,
          callback: (token: string) => onVerifyRef.current(token),
          "expired-callback": () => onExpireRef.current?.(),
        });
        setLoaded(true);
      } catch {
        // grecaptcha may be available but not fully ready yet; retry once.
        setTimeout(() => {
          if (cancelled || !containerRef.current) return;
          try {
            widgetIdRef.current = (window as any).grecaptcha.render(containerRef.current!, {
              sitekey: SITE_KEY,
              callback: (token: string) => onVerifyRef.current(token),
              "expired-callback": () => onExpireRef.current?.(),
            });
            setLoaded(true);
          } catch { /* give up silently */ }
        }, 500);
      }
    };

    // Expose callbacks globally for potential explicit-reset usage.
    (window as any).__captchaReset = () => {
      if (widgetIdRef.current !== null && (window as any).grecaptcha) {
        (window as any).grecaptcha.reset(widgetIdRef.current);
      }
    };

    loadRecaptchaScript().then(() => {
      if ((window as any).grecaptcha?.render) {
        renderWidget();
      } else if ((window as any).grecaptcha) {
        // grecaptcha loaded but render not ready: wait for the ready cb.
        (window as any).grecaptcha.ready(renderWidget);
      }
    });

    return () => {
      cancelled = true;
    };
  }, []);

  if (!SITE_KEY) {
    // No site key configured (dev): render a neutral hint instead of a widget.
    return (
      <div
        style={{
          padding: "10px 12px",
          borderRadius: "8px",
          background: "rgba(99,102,241,0.08)",
          border: "1px dashed rgba(99,102,241,0.3)",
          fontSize: "0.8rem",
          color: "var(--color-text-muted)",
        }}
      >
        Captcha deshabilitado (sin NEXT_PUBLIC_RECAPTCHA_SITE_KEY)
      </div>
    );
  }

  return <div ref={containerRef} style={{ minHeight: 78 }} aria-busy={!loaded} />;
}

export function resetCaptcha() {
  if (typeof window !== "undefined" && (window as any).__captchaReset) {
    (window as any).__captchaReset();
  }
}