"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { toast } from "@/components/ui/Toast";
import Modal from "@/components/ui/Modal";
import type { CourseClass } from "@/types";

interface TeacherClass extends CourseClass {
  course?: { title: string } | null;
}

export default function TeacherDashboard() {
  const [classes, setClasses] = useState<TeacherClass[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedClass, setSelectedClass] = useState<TeacherClass | null>(null);
  const [meetingPlatform, setMeetingPlatform] = useState("");
  const [meetingUrl, setMeetingUrl] = useState("");
  const [savingLink, setSavingLink] = useState(false);

  useEffect(() => {
    api
      .get<TeacherClass[]>("/teachers/me/classes")
      .then((data) => {
        setClasses(Array.isArray(data) ? data : []);
      })
      .catch(() => {
        toast.error("No se pudieron cargar las clases");
        setClasses([]);
      })
      .finally(() => setLoading(false));
  }, []);

  const totalStudents = classes.reduce((sum, c) => sum + (c.enrolled_count || 0), 0);

  const openLinkModal = (cls: TeacherClass) => {
    setSelectedClass(cls);
    setMeetingPlatform(cls.meeting_platform || "");
    setMeetingUrl(cls.meeting_url || "");
    setModalOpen(true);
  };

  const saveMeetingLink = async () => {
    if (!selectedClass) return;
    setSavingLink(true);
    try {
      await api.patch(`/course-classes/${selectedClass.id}/meeting-link`, {
        meeting_platform: meetingPlatform,
        meeting_url: meetingUrl,
      });
      toast.success("Enlace actualizado correctamente");
      setClasses((prev) =>
        prev.map((c) =>
          c.id === selectedClass.id
            ? { ...c, meeting_platform: meetingPlatform, meeting_url: meetingUrl }
            : c
        )
      );
      setModalOpen(false);
    } catch {
      toast.error("Error al actualizar el enlace");
    } finally {
      setSavingLink(false);
    }
  };

  if (loading) {
    return (
      <>
        <div className="page-header">
          <h1>Dashboard</h1>
          <p>Resumen de tus cursos y alumnos.</p>
        </div>
        <div className="card" style={{ textAlign: "center", padding: "40px", color: "var(--color-text-muted)" }}>
          Cargando...
        </div>
      </>
    );
  }

  return (
    <>
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Resumen de tus cursos y alumnos.</p>
      </div>

      <div className="grid-stats">
        <div className="stats-card">
          <div className="stats-icon" style={{ background: "#eef2ff", color: "#6366f1" }}>
            📚
          </div>
          <div>
            <div className="stats-value">{classes.length}</div>
            <div className="stats-label">Clases asignadas</div>
          </div>
        </div>
        <div className="stats-card">
          <div className="stats-icon" style={{ background: "#ecfdf5", color: "#10b981" }}>
            👥
          </div>
          <div>
            <div className="stats-value">{totalStudents}</div>
            <div className="stats-label">Total alumnos</div>
          </div>
        </div>
      </div>

      <h2 style={{ fontSize: "1.25rem", fontWeight: 600, marginBottom: "16px" }}>Mis Clases</h2>

      {classes.length === 0 ? (
        <div className="card" style={{ textAlign: "center", padding: "48px" }}>
          <div style={{ fontSize: "3rem", marginBottom: "16px" }}>📚</div>
          <h3 style={{ fontWeight: 600, marginBottom: "8px" }}>Sin clases asignadas</h3>
          <p style={{ color: "var(--color-text-muted)" }}>No tienes clases asignadas actualmente.</p>
        </div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Curso</th>
                <th>Alumnos inscritos</th>
                <th>Horario</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {classes.map((cls) => (
                <tr key={cls.id}>
                  <td style={{ fontWeight: 500 }}>{cls.name}</td>
                  <td>{cls.course?.title || "—"}</td>
                  <td>{cls.enrolled_count ?? 0}</td>
                  <td>{cls.schedule_info || "—"}</td>
                  <td>
                    <span className={`badge ${cls.status === "active" ? "badge-success" : "badge-neutral"}`}>
                      {cls.status}
                    </span>
                  </td>
                  <td>
                    <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", alignItems: "center" }}>
                      <span style={{ fontSize: "0.8125rem", color: "var(--color-text-muted)" }}>
                        {cls.enrolled_count ?? 0} alumnos
                      </span>
                      <Link href={`/teacher/classes/${cls.id}/attendance`} className="btn btn-secondary btn-sm">
                        Asistencia
                      </Link>
                      <button className="btn btn-primary btn-sm" onClick={() => openLinkModal(cls)}>
                        Enlace clase
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="Enlace de clase">
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          <div>
            <label className="label">Plataforma</label>
            <input
              type="text"
              className="input"
              value={meetingPlatform}
              onChange={(e) => setMeetingPlatform(e.target.value)}
              placeholder="Zoom, Google Meet, etc."
            />
          </div>
          <div>
            <label className="label">URL de la reunión</label>
            <input
              type="url"
              className="input"
              value={meetingUrl}
              onChange={(e) => setMeetingUrl(e.target.value)}
              placeholder="https://..."
            />
          </div>
          <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px" }}>
            <button className="btn btn-secondary" onClick={() => setModalOpen(false)} disabled={savingLink}>
              Cancelar
            </button>
            <button className="btn btn-primary" onClick={saveMeetingLink} disabled={savingLink}>
              {savingLink ? "Guardando..." : "Guardar"}
            </button>
          </div>
        </div>
      </Modal>
    </>
  );
}
