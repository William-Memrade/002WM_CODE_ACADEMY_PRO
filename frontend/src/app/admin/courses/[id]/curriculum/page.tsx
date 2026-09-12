/**
 * CodeAcademy Pro — Administración: editar el temario de un curso
 *
 * Mismo editor que usa el docente (`components/curriculum/CurriculumEditor`): el backend
 * autoriza a administración con `ensure_course_manager`, así que administración puede
 * crear, editar, borrar y reordenar módulos y lecciones sin pasar por el docente.
 */
"use client";

import { useParams } from "next/navigation";
import CurriculumEditor from "@/components/curriculum/CurriculumEditor";

export default function AdminCourseCurriculumPage() {
  const params = useParams();
  const courseId = params.id as string;

  return (
    <CurriculumEditor
      courseId={courseId}
      backHref="/admin/courses"
      backLabel="← Cursos"
      hint="Editando como administración: los cambios afectan al curso que ven docentes y alumnos."
    />
  );
}
