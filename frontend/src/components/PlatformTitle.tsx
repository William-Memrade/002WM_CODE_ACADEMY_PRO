"use client";

import { useEffect, useState } from "react";

const DEFAULT_NAME = "CodeAcademy Pro";
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api/v1";

export function PlatformTitle() {
  const [name, setName] = useState(DEFAULT_NAME);

  useEffect(() => {
    fetch(`${API_BASE}/settings/public`)
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => {
        if (data?.platform_name) {
          setName(data.platform_name);
          document.title = `${data.platform_name} — Academia Virtual de Programación`;
        }
      })
      .catch(() => {});
  }, []);

  return null;
}