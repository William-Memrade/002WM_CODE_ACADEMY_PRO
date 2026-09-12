/**
 * CodeAcademy Pro — Student Progress Hook
 * El progreso del alumno es de sólo lectura: lo escribe el docente de su clase
 * (PATCH /course-classes/{class_id}/students/{student_id}/progress).
 */
"use client";

import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import { toast } from "@/components/ui/Toast";

export interface StudentProgressRow {
  enrollment_id: string;
  course_id: string;
  course_title: string | null;
  course_class_id: string | null;
  course_class_name: string | null;
  progress_percentage: number;
  completed_at: string | null;
  status: string;
  course_slug?: string | null;
  enrolled_at?: string | null;
}

export function useStudentProgress() {
  const [data, setData] = useState<StudentProgressRow[]>([]);
  const [loading, setLoading] = useState(true);

  const fetch_ = useCallback(async () => {
    try {
      setLoading(true);
      const res = await api.get<{ items: StudentProgressRow[] }>("/students/me/progress");
      setData(res.items ?? []);
    } catch {
      toast.error("No se pudo cargar tu progreso");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetch_();
  }, [fetch_]);

  /** Mapa por curso para pintar el progreso junto a cada curso inscrito. */
  const byCourse: Record<string, StudentProgressRow> = {};
  data.forEach((row) => {
    byCourse[row.course_id] = row;
  });

  return { data, byCourse, loading, refresh: fetch_ };
}
