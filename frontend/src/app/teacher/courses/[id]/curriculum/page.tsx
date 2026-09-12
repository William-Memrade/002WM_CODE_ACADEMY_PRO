/**
 * CodeAcademy Pro — Panel docente: editor de temario
 *
 * El editor vive en `components/curriculum/CurriculumEditor` porque lo comparten el
 * docente y administración (mismos endpoints, misma mecánica de orden).
 */
"use client";

import { useParams } from "next/navigation";
import CurriculumEditor from "@/components/curriculum/CurriculumEditor";

export default function TeacherCurriculumPage() {
  const params = useParams();
  const courseId = params.id as string;

  return (
    <CurriculumEditor
      courseId={courseId}
      backHref="/teacher/courses"
      backLabel="← Mis cursos"
    />
  );
}
