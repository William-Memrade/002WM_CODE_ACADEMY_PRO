/**
 * CodeAcademy Pro — Teacher Data Hooks
 * Hooks del panel docente: cursos asignados, temario (módulos/lecciones) y
 * progreso de los alumnos de sus clases.
 *
 * Endpoints (ver docs/architecture/API_ENDPOINTS.md):
 *   GET    /teachers/me/courses
 *   GET    /teachers/me/students
 *   GET    /courses/{course_id}/modules
 *   POST   /courses/{course_id}/modules          POST /courses/modules/{id}/lessons
 *   PUT    /courses/modules/{id}                 PUT  /courses/lessons/{id}
 *   DELETE /courses/modules/{id}                 DELETE /courses/lessons/{id}
 *   PATCH  /courses/{course_id}/modules/order    (orden del temario, 0..n-1)
 *   PATCH  /courses/modules/{module_id}/lessons/order
 *   PATCH  /course-classes/{class_id}/students/{student_id}/progress
 */
"use client";

import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import { toast } from "@/components/ui/Toast";

// ── Types ─────────────────────────────────────────────────────────────────────

export interface TeacherCourse {
  id: string;
  title: string;
  slug: string;
  level: string;
  is_active: boolean;
  /** true si es el docente titular del curso; false si sólo imparte una clase. */
  is_teacher_owner: boolean;
  modules_count: number;
  lessons_count: number;
  classes_count: number;
  students_count: number;
  avg_progress: number;
}

export interface TeacherLesson {
  id: string;
  title: string;
  description: string | null;
  content: string | null;
  sort_order: number;
  is_published: boolean;
  duration_minutes: number | null;
  is_free: boolean;
}

export interface TeacherModule {
  id: string;
  title: string;
  description: string | null;
  sort_order: number;
  is_published: boolean;
  lessons: TeacherLesson[];
}

export interface TeacherStudentRow {
  enrollment_id: string;
  student_id: string;
  student_name: string;
  student_email: string;
  course_id: string;
  course_title: string;
  course_class_id: string | null;
  course_class_name: string | null;
  progress_percentage: number;
  completed_at: string | null;
  status: string;
}

// ── useTeacherCourses ─────────────────────────────────────────────────────────

export function useTeacherCourses() {
  const [data, setData] = useState<TeacherCourse[]>([]);
  const [loading, setLoading] = useState(true);

  const fetch_ = useCallback(async () => {
    try {
      setLoading(true);
      const res = await api.get<{ items: TeacherCourse[] }>("/teachers/me/courses");
      setData(res.items ?? []);
    } catch {
      toast.error("Error al cargar tus cursos");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetch_();
  }, [fetch_]);

  return { data, loading, refresh: fetch_ };
}

// ── useTeacherStudents ────────────────────────────────────────────────────────

export function useTeacherStudents() {
  const [data, setData] = useState<TeacherStudentRow[]>([]);
  const [loading, setLoading] = useState(true);

  const fetch_ = useCallback(async () => {
    try {
      setLoading(true);
      const res = await api.get<{ items: TeacherStudentRow[] }>("/teachers/me/students");
      setData(res.items ?? []);
    } catch {
      toast.error("Error al cargar tus alumnos");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetch_();
  }, [fetch_]);

  /**
   * Guarda el progreso de un alumno en una clase concreta.
   * El backend sólo acepta la escritura del docente que imparte esa clase.
   */
  const updateProgress = async (classId: string, studentId: string, progress: number) => {
    const res = await api.patch<{ progress_percentage: number; completed_at: string | null }>(
      `/course-classes/${classId}/students/${studentId}/progress`,
      { progress_percentage: progress }
    );
    await fetch_();
    return res;
  };

  return { data, loading, refresh: fetch_, updateProgress };
}

// ── useCourseCurriculum ───────────────────────────────────────────────────────

export function useCourseCurriculum(courseId: string) {
  const [modules, setModules] = useState<TeacherModule[]>([]);
  const [loading, setLoading] = useState(true);

  const fetch_ = useCallback(async () => {
    if (!courseId) return;
    try {
      setLoading(true);
      const res = await api.get<{ items: TeacherModule[] }>(`/courses/${courseId}/modules`);
      setModules(res.items ?? []);
    } catch {
      toast.error("Error al cargar el temario");
    } finally {
      setLoading(false);
    }
  }, [courseId]);

  useEffect(() => {
    fetch_();
  }, [fetch_]);

  const createModule = async (title: string, description?: string) => {
    await api.post(`/courses/${courseId}/modules`, {
      course_id: courseId,
      title,
      description: description || null,
      sort_order: modules.length,
    });
    toast.success("Módulo añadido");
    await fetch_();
  };

  const updateModule = async (moduleId: string, payload: Partial<TeacherModule>) => {
    await api.put(`/courses/modules/${moduleId}`, payload);
    toast.success("Módulo actualizado");
    await fetch_();
  };

  const deleteModule = async (moduleId: string) => {
    await api.delete(`/courses/modules/${moduleId}`);
    toast.success("Módulo eliminado con sus lecciones");
    await fetch_();
  };

  const createLesson = async (
    moduleId: string,
    payload: {
      title: string;
      description?: string | null;
      content?: string | null;
      duration_minutes?: number | null;
      is_free?: boolean;
      sort_order?: number;
    }
  ): Promise<string | null> => {
    const created = await api.post<{ id: string }>(`/courses/modules/${moduleId}/lessons`, {
      module_id: moduleId,
      ...payload,
    });
    toast.success("Lección añadida");
    await fetch_();
    return created?.id ?? null;
  };

  const updateLesson = async (lessonId: string, payload: Partial<TeacherLesson>) => {
    await api.put(`/courses/lessons/${lessonId}`, payload);
    toast.success("Lección actualizada");
    await fetch_();
  };

  const deleteLesson = async (lessonId: string) => {
    await api.delete(`/courses/lessons/${lessonId}`);
    toast.success("Lección eliminada");
    await fetch_();
  };

  /**
   * Reordena los módulos del curso. `ordered_ids` va en el orden final; el backend
   * reescribe `sort_order` como 0..n-1 y devuelve el temario ya ordenado.
   *
   * Se pinta en local antes de la respuesta para que el arrastre no dé tirones; si la
   * llamada falla se recarga el orden real.
   */
  const reorderModules = async (orderedIds: string[]) => {
    const byId = new Map(modules.map((m) => [m.id, m]));
    setModules(orderedIds.map((id) => byId.get(id)).filter(Boolean) as TeacherModule[]);
    try {
      const res = await api.patch<{ items: TeacherModule[] }>(
        `/courses/${courseId}/modules/order`,
        { ordered_ids: orderedIds }
      );
      setModules(res.items ?? []);
    } catch {
      toast.error("No se pudo guardar el orden de los módulos");
      await fetch_();
    }
  };

  /** Reordena las lecciones de un módulo (misma mecánica que los módulos). */
  const reorderLessons = async (moduleId: string, orderedIds: string[]) => {
    setModules((prev) =>
      prev.map((m) =>
        m.id === moduleId
          ? {
              ...m,
              lessons: [...m.lessons].sort(
                (a, b) => orderedIds.indexOf(a.id) - orderedIds.indexOf(b.id)
              ),
            }
          : m
      )
    );
    try {
      const res = await api.patch<{ items: TeacherModule[] }>(
        `/courses/modules/${moduleId}/lessons/order`,
        { ordered_ids: orderedIds }
      );
      setModules(res.items ?? []);
    } catch {
      toast.error("No se pudo guardar el orden de las lecciones");
      await fetch_();
    }
  };

  return {
    modules,
    loading,
    refresh: fetch_,
    createModule,
    updateModule,
    deleteModule,
    createLesson,
    updateLesson,
    deleteLesson,
    reorderModules,
    reorderLessons,
  };
}
