/**
 * CodeAcademy Pro — Editor de temario (compartido por docente y administración)
 *
 * Módulos y lecciones del curso: alta, edición, borrado y ORDEN por arrastre.
 *
 * El orden vive en `sort_order`, que es un orden lógico (0..n-1) y no la clave:
 * se guarda con `PATCH /courses/{course_id}/modules/order` y
 * `PATCH /courses/modules/{module_id}/lessons/order`, que reescriben la secuencia
 * completa. Por eso insertar una lección al principio no obliga a renumerar nada
 * a mano: se arrastra y el backend recoloca el resto.
 *
 * Lo usan /teacher/courses/[id]/curriculum y /admin/courses/[id]/curriculum.
 */
"use client";

import { useState } from "react";
import Modal from "@/components/ui/Modal";
import { toast } from "@/components/ui/Toast";
import {
  TeacherLesson,
  TeacherModule,
  useCourseCurriculum,
} from "@/hooks/useTeacherData";

const emptyModuleForm = { title: "", description: "" };
const emptyLessonForm = {
  title: "",
  description: "",
  content: "",
  duration_minutes: "",
  is_free: false,
  is_published: true,
};

interface CurriculumEditorProps {
  courseId: string;
  /** Botón de vuelta del encabezado. */
  backHref: string;
  backLabel: string;
  /** Aviso opcional bajo el encabezado (p. ej. cuando edita administración). */
  hint?: string;
}

export default function CurriculumEditor({
  courseId,
  backHref,
  backLabel,
  hint,
}: CurriculumEditorProps) {
  const {
    modules,
    loading,
    createModule,
    updateModule,
    deleteModule,
    createLesson,
    updateLesson,
    deleteLesson,
    reorderModules,
    reorderLessons,
  } = useCourseCurriculum(courseId);

  const [saving, setSaving] = useState(false);
  const [moduleForm, setModuleForm] = useState(emptyModuleForm);
  const [moduleModal, setModuleModal] = useState<{ module: TeacherModule | null } | null>(null);
  const [lessonModal, setLessonModal] = useState<{ moduleId: string; lesson: TeacherLesson | null } | null>(null);
  const [lessonForm, setLessonForm] = useState(emptyLessonForm);
  const [confirm, setConfirm] = useState<
    { kind: "module" | "lesson"; id: string; label: string } | null
  >(null);

  // Arrastre: origen y destino se guardan como índices para no depender de ids
  // duplicados ni de plataformas raras de drag & drop.
  const [draggingModule, setDraggingModule] = useState<number | null>(null);
  const [moduleOver, setModuleOver] = useState<number | null>(null);
  const [draggingLesson, setDraggingLesson] = useState<{ moduleId: string; index: number } | null>(null);
  const [lessonOver, setLessonOver] = useState<{ moduleId: string; index: number } | null>(null);

  const totalLessons = modules.reduce((acc, m) => acc + m.lessons.length, 0);

  // ── Módulos ───────────────────────────────────────────────────────────────

  const openModuleModal = (module: TeacherModule | null) => {
    setModuleForm(
      module
        ? { title: module.title, description: module.description ?? "" }
        : emptyModuleForm
    );
    setModuleModal({ module });
  };

  const saveModule = async () => {
    if (moduleForm.title.trim().length < 2) {
      toast.error("El título del módulo necesita al menos 2 caracteres");
      return;
    }
    setSaving(true);
    try {
      if (moduleModal?.module) {
        await updateModule(moduleModal.module.id, {
          title: moduleForm.title,
          description: moduleForm.description || null,
        });
      } else {
        await createModule(moduleForm.title, moduleForm.description);
      }
      setModuleModal(null);
    } catch {
      toast.error("No se pudo guardar el módulo");
    } finally {
      setSaving(false);
    }
  };

  // ── Lecciones ─────────────────────────────────────────────────────────────

  const openLessonModal = (moduleId: string, lesson: TeacherLesson | null) => {
    setLessonForm(
      lesson
        ? {
            title: lesson.title,
            description: lesson.description ?? "",
            content: lesson.content ?? "",
            duration_minutes: lesson.duration_minutes ? String(lesson.duration_minutes) : "",
            is_free: lesson.is_free,
            is_published: lesson.is_published,
          }
        : emptyLessonForm
    );
    setLessonModal({ moduleId, lesson });
  };

  const saveLesson = async () => {
    if (!lessonModal) return;
    if (lessonForm.title.trim().length < 2) {
      toast.error("El título de la lección necesita al menos 2 caracteres");
      return;
    }
    const payload = {
      title: lessonForm.title,
      description: lessonForm.description || null,
      content: lessonForm.content || null,
      duration_minutes: lessonForm.duration_minutes ? Number(lessonForm.duration_minutes) : null,
      is_free: lessonForm.is_free,
      is_published: lessonForm.is_published,
    };
    setSaving(true);
    try {
      if (lessonModal.lesson) {
        await updateLesson(lessonModal.lesson.id, payload);
      } else {
        const module = modules.find((m) => m.id === lessonModal.moduleId);
        const lessonId = await createLesson(lessonModal.moduleId, {
          ...payload,
          sort_order: module?.lessons.length ?? 0,
        });
        // `is_published` no viaja en el POST: si se creó como borrador hay que
        // despublicarla en un segundo paso.
        if (lessonId && lessonForm.is_published === false) {
          await updateLesson(lessonId, { is_published: false });
        }
      }
      setLessonModal(null);
    } catch {
      toast.error("No se pudo guardar la lección");
    } finally {
      setSaving(false);
    }
  };

  const runDelete = async () => {
    if (!confirm) return;
    setSaving(true);
    try {
      if (confirm.kind === "module") await deleteModule(confirm.id);
      else await deleteLesson(confirm.id);
      setConfirm(null);
    } catch {
      toast.error("No se pudo eliminar");
    } finally {
      setSaving(false);
    }
  };

  // ── Orden (arrastre y botones ↑ ↓) ────────────────────────────────────────

  const moveInList = <T,>(list: T[], from: number, to: number): T[] => {
    const next = [...list];
    const [moved] = next.splice(from, 1);
    next.splice(to, 0, moved);
    return next;
  };

  const applyModuleOrder = async (from: number, to: number) => {
    if (from === to || to < 0 || to >= modules.length) return;
    await reorderModules(moveInList(modules, from, to).map((m) => m.id));
  };

  const applyLessonOrder = async (moduleId: string, from: number, to: number) => {
    const module = modules.find((m) => m.id === moduleId);
    if (!module || from === to || to < 0 || to >= module.lessons.length) return;
    await reorderLessons(moduleId, moveInList(module.lessons, from, to).map((l) => l.id));
  };

  const dropModule = async (index: number) => {
    const from = draggingModule;
    setDraggingModule(null);
    setModuleOver(null);
    if (from === null || from === index) return;
    await applyModuleOrder(from, index);
  };

  const dropLesson = async (moduleId: string, index: number) => {
    const from = draggingLesson;
    setDraggingLesson(null);
    setLessonOver(null);
    if (!from || from.moduleId !== moduleId || from.index === index) return;
    await applyLessonOrder(moduleId, from.index, index);
  };

  return (
    <>
      <div className="page-header">
        <div>
          <h1>Temario del curso</h1>
          <p>
            {modules.length} módulos · {totalLessons} lecciones. Puedes crear, editar y
            borrar módulos y lecciones, y reordenarlos arrastrando (o con ↑ ↓).
          </p>
          {hint && (
            <p style={{ color: "var(--color-text-muted)", fontSize: "0.8125rem", marginTop: "4px" }}>
              {hint}
            </p>
          )}
        </div>
        <div style={{ display: "flex", gap: "8px" }}>
          <a href={backHref} className="btn btn-secondary btn-sm">
            {backLabel}
          </a>
          <button className="btn btn-primary btn-sm" onClick={() => openModuleModal(null)}>
            + Añadir módulo
          </button>
        </div>
      </div>

      {loading ? (
        <div className="card" style={{ textAlign: "center", padding: "40px", color: "var(--color-text-muted)" }}>
          Cargando temario…
        </div>
      ) : modules.length === 0 ? (
        <div className="card" style={{ textAlign: "center", padding: "48px" }}>
          <div style={{ fontSize: "3rem", marginBottom: "16px" }}>📦</div>
          <h3 style={{ fontWeight: 600, marginBottom: "8px" }}>Curso sin temario</h3>
          <p style={{ color: "var(--color-text-muted)", marginBottom: "20px" }}>
            Crea el primer módulo y ve añadiendo sus lecciones.
          </p>
          <button className="btn btn-primary" onClick={() => openModuleModal(null)}>
            + Añadir módulo
          </button>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          {modules.map((module, index) => (
            <div
              key={module.id}
              className="card"
              onDragOver={(e) => {
                if (draggingModule === null) return;
                e.preventDefault();
                setModuleOver(index);
              }}
              onDrop={(e) => {
                if (draggingModule === null) return;
                e.preventDefault();
                void dropModule(index);
              }}
              style={
                moduleOver === index && draggingModule !== null && draggingModule !== index
                  ? { outline: "2px dashed var(--color-primary, #6366f1)", outlineOffset: "-2px" }
                  : undefined
              }
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "flex-start",
                  gap: "12px",
                  flexWrap: "wrap",
                }}
              >
                <div style={{ display: "flex", gap: "10px", alignItems: "flex-start" }}>
                  <span
                    draggable
                    onDragStart={() => setDraggingModule(index)}
                    onDragEnd={() => {
                      setDraggingModule(null);
                      setModuleOver(null);
                    }}
                    title="Arrastra para cambiar el orden de los módulos"
                    style={{ cursor: "grab", userSelect: "none", fontSize: "1.1rem", lineHeight: 1.4 }}
                  >
                    ⠿
                  </span>
                  <div>
                    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                      <span className="badge badge-neutral">Módulo {index + 1}</span>
                      <h3 style={{ fontWeight: 600, fontSize: "1.05rem" }}>{module.title}</h3>
                      {!module.is_published && <span className="badge badge-warning">Borrador</span>}
                    </div>
                    {module.description && (
                      <p style={{ color: "var(--color-text-muted)", fontSize: "0.875rem", marginTop: "4px" }}>
                        {module.description}
                      </p>
                    )}
                  </div>
                </div>
                <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={() => void applyModuleOrder(index, index - 1)}
                    disabled={index === 0}
                    title="Subir módulo"
                  >
                    ↑
                  </button>
                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={() => void applyModuleOrder(index, index + 1)}
                    disabled={index === modules.length - 1}
                    title="Bajar módulo"
                  >
                    ↓
                  </button>
                  <button className="btn btn-secondary btn-sm" onClick={() => openLessonModal(module.id, null)}>
                    + Lección
                  </button>
                  <button className="btn btn-secondary btn-sm" onClick={() => openModuleModal(module)}>
                    Editar
                  </button>
                  <button
                    className="btn btn-danger btn-sm"
                    onClick={() => setConfirm({ kind: "module", id: module.id, label: module.title })}
                  >
                    Eliminar
                  </button>
                </div>
              </div>

              <div className="table-container" style={{ marginTop: "16px" }}>
                {module.lessons.length === 0 ? (
                  <p style={{ padding: "16px", color: "var(--color-text-muted)", fontSize: "0.875rem" }}>
                    Este módulo no tiene lecciones todavía.
                  </p>
                ) : (
                  <table>
                    <thead>
                      <tr>
                        <th style={{ width: "96px" }} title="Arrastra ⠿ o usa ↑ ↓: el orden se guarda solo">Posición</th>
                        <th>Lección</th>
                        <th style={{ width: "110px" }}>Duración</th>
                        <th style={{ width: "150px" }}>Estado</th>
                        <th style={{ width: "150px" }}>Acciones</th>
                      </tr>
                    </thead>
                    <tbody>
                      {module.lessons.map((lesson, lessonIndex) => (
                        <tr
                          key={lesson.id}
                          onDragOver={(e) => {
                            if (!draggingLesson || draggingLesson.moduleId !== module.id) return;
                            e.preventDefault();
                            setLessonOver({ moduleId: module.id, index: lessonIndex });
                          }}
                          onDrop={(e) => {
                            if (!draggingLesson || draggingLesson.moduleId !== module.id) return;
                            e.preventDefault();
                            void dropLesson(module.id, lessonIndex);
                          }}
                          style={
                            lessonOver?.moduleId === module.id &&
                            lessonOver.index === lessonIndex &&
                            draggingLesson?.index !== lessonIndex
                              ? { outline: "2px dashed var(--color-primary, #6366f1)", outlineOffset: "-2px" }
                              : undefined
                          }
                        >
                          <td>
                            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                              <span
                                draggable
                                onDragStart={() => setDraggingLesson({ moduleId: module.id, index: lessonIndex })}
                                onDragEnd={() => {
                                  setDraggingLesson(null);
                                  setLessonOver(null);
                                }}
                                title="Arrastra para cambiar el orden de las lecciones"
                                style={{ cursor: "grab", userSelect: "none" }}
                              >
                                ⠿
                              </span>
                              <span style={{ color: "var(--color-text-muted)", fontSize: "0.875rem" }}>{lessonIndex + 1}</span>
                            </div>
                          </td>
                          <td>
                            <div style={{ fontWeight: 500 }}>{lesson.title}</div>
                            {lesson.description && (
                              <div style={{ fontSize: "0.8125rem", color: "var(--color-text-muted)" }}>
                                {lesson.description}
                              </div>
                            )}
                          </td>
                          <td>{lesson.duration_minutes ? `${lesson.duration_minutes} min` : "—"}</td>
                          <td>
                            {lesson.is_published ? (
                              <span className="badge badge-success">Publicada</span>
                            ) : (
                              <span className="badge badge-warning">Borrador</span>
                            )}
                            {lesson.is_free && <span className="badge badge-info">Gratis</span>}
                          </td>
                          <td>
                            <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
                              <button
                                className="btn btn-secondary btn-sm"
                                onClick={() => void applyLessonOrder(module.id, lessonIndex, lessonIndex - 1)}
                                disabled={lessonIndex === 0}
                                title="Subir lección"
                              >
                                ↑
                              </button>
                              <button
                                className="btn btn-secondary btn-sm"
                                onClick={() => void applyLessonOrder(module.id, lessonIndex, lessonIndex + 1)}
                                disabled={lessonIndex === module.lessons.length - 1}
                                title="Bajar lección"
                              >
                                ↓
                              </button>
                              <button className="btn btn-secondary btn-sm" onClick={() => openLessonModal(module.id, lesson)}>
                                Editar
                              </button>
                              <button
                                className="btn btn-danger btn-sm"
                                onClick={() => setConfirm({ kind: "lesson", id: lesson.id, label: lesson.title })}
                              >
                                Eliminar
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Módulo: alta y edición */}
      <Modal
        open={!!moduleModal}
        onClose={() => setModuleModal(null)}
        title={moduleModal?.module ? "Editar módulo" : "Nuevo módulo"}
      >
        <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
          <div className="form-group">
            <label className="label">Título</label>
            <input
              className="input"
              value={moduleForm.title}
              onChange={(e) => setModuleForm({ ...moduleForm, title: e.target.value })}
              placeholder="Módulo 1: Fundamentos"
            />
          </div>
          <div className="form-group">
            <label className="label">Descripción (opcional)</label>
            <textarea
              className="input"
              rows={3}
              value={moduleForm.description}
              onChange={(e) => setModuleForm({ ...moduleForm, description: e.target.value })}
            />
          </div>
          <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px" }}>
            <button className="btn btn-secondary" onClick={() => setModuleModal(null)} disabled={saving}>
              Cancelar
            </button>
            <button className="btn btn-primary" onClick={saveModule} disabled={saving}>
              {saving ? "Guardando…" : "Guardar"}
            </button>
          </div>
        </div>
      </Modal>

      {/* Lección: alta y edición */}
      <Modal
        open={!!lessonModal}
        onClose={() => setLessonModal(null)}
        title={lessonModal?.lesson ? "Editar lección" : "Nueva lección"}
        width="640px"
      >
        <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
          <div className="form-group">
            <label className="label">Título</label>
            <input
              className="input"
              value={lessonForm.title}
              onChange={(e) => setLessonForm({ ...lessonForm, title: e.target.value })}
              placeholder="Lección 1: Variables y tipos"
            />
          </div>
          <div className="form-group">
            <label className="label">Descripción (opcional)</label>
            <input
              className="input"
              value={lessonForm.description}
              onChange={(e) => setLessonForm({ ...lessonForm, description: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label className="label">Contenido</label>
            <textarea
              className="input"
              rows={8}
              value={lessonForm.content}
              onChange={(e) => setLessonForm({ ...lessonForm, content: e.target.value })}
              placeholder="Material de la lección (markdown o texto)"
            />
          </div>
          <div className="form-row" style={{ display: "flex", gap: "12px" }}>
            <div className="form-group" style={{ flex: 1 }}>
              <label className="label">Duración (minutos)</label>
              <input
                className="input"
                type="number"
                min={0}
                value={lessonForm.duration_minutes}
                onChange={(e) => setLessonForm({ ...lessonForm, duration_minutes: e.target.value })}
              />
            </div>
            <div className="form-group" style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <label className="label" style={{ marginBottom: 0 }}>
                <input
                  type="checkbox"
                  checked={lessonForm.is_published}
                  onChange={(e) => setLessonForm({ ...lessonForm, is_published: e.target.checked })}
                />{" "}
                Publicada
              </label>
              <label className="label" style={{ marginBottom: 0 }}>
                <input
                  type="checkbox"
                  checked={lessonForm.is_free}
                  onChange={(e) => setLessonForm({ ...lessonForm, is_free: e.target.checked })}
                />{" "}
                Gratis
              </label>
            </div>
          </div>
          <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px" }}>
            <button className="btn btn-secondary" onClick={() => setLessonModal(null)} disabled={saving}>
              Cancelar
            </button>
            <button className="btn btn-primary" onClick={saveLesson} disabled={saving}>
              {saving ? "Guardando…" : "Guardar"}
            </button>
          </div>
        </div>
      </Modal>

      {/* Confirmación de borrado */}
      <Modal
        open={!!confirm}
        onClose={() => setConfirm(null)}
        title="Confirmar eliminación"
        width="440px"
      >
        {confirm && (
          <div style={{ textAlign: "center" }}>
            <p style={{ marginBottom: "16px" }}>
              ¿Eliminar <strong>&quot;{confirm.label}&quot;</strong>?
            </p>
            <p style={{ fontSize: "0.875rem", color: "var(--color-text-muted)", marginBottom: "24px" }}>
              {confirm.kind === "module"
                ? "Se borran también todas sus lecciones. No se puede deshacer."
                : "No se puede deshacer."}
            </p>
            <div style={{ display: "flex", gap: "12px", justifyContent: "center" }}>
              <button className="btn btn-secondary" onClick={() => setConfirm(null)} disabled={saving}>
                Cancelar
              </button>
              <button className="btn btn-danger" onClick={runDelete} disabled={saving}>
                {saving ? "Eliminando…" : "Sí, eliminar"}
              </button>
            </div>
          </div>
        )}
      </Modal>
    </>
  );
}
