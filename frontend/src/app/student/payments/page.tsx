"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { formatCurrency } from "@/lib/currency";
import { toast } from "@/components/ui/Toast";

interface PaymentItem {
  id: string;
  course_title: string;
  course_id: string;
  amount: number;
  currency: string;
  status: string;
  created_at: string | null;
  reviewed_at: string | null;
  review_notes: string | null;
  payment_plan?: string;
  expected_amount?: number;
  monthly_amount?: number;
  full_amount?: number;
}

const STATUS_BADGE: Record<string, { cls: string; label: string }> = {
  pending: { cls: "badge-warning", label: "En revisión" },
  approved: { cls: "badge-success", label: "Aprobado" },
  approved_pending_class: { cls: "badge-info", label: "Aprobado — sin clase" },
  rejected: { cls: "badge-error", label: "Rechazado" },
};

function planLabel(plan?: string) {
  if (!plan) return "—";
  return plan === "monthly" ? "Mensual" : plan === "full" ? "Completo" : plan;
}

export default function StudentPaymentsPage() {
  const [payments, setPayments] = useState<PaymentItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get<{ items: PaymentItem[] }>("/payments/my-payments")
      .then((data) => setPayments(data.items || []))
      .catch(() => {
        toast.error("No se pudieron cargar los pagos");
        setPayments([]);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <>
      <div className="page-header">
        <h1>Pagos</h1>
        <p>Historial y estado de tus pagos.</p>
      </div>

      {loading ? (
        <div className="card" style={{ textAlign: "center", padding: "40px", color: "var(--color-text-muted)" }}>
          Cargando pagos...
        </div>
      ) : payments.length === 0 ? (
        <div className="card" style={{ textAlign: "center", padding: "48px" }}>
          <div style={{ fontSize: "3rem", marginBottom: "16px" }}>💳</div>
          <h3 style={{ fontWeight: 600, marginBottom: "8px" }}>Sin pagos</h3>
          <p style={{ color: "var(--color-text-muted)", marginBottom: "24px" }}>
            No has realizado ningún pago aún.
          </p>
          <a href="/courses" className="btn btn-primary">Explorar cursos</a>
        </div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Curso</th>
                <th>Plan</th>
                <th>Monto esperado</th>
                <th>Monto</th>
                <th>Estado</th>
                <th>Fecha</th>
                <th>Notas</th>
              </tr>
            </thead>
            <tbody>
              {payments.map((p) => {
                const badge = STATUS_BADGE[p.status] || { cls: "", label: p.status };
                return (
                  <tr key={p.id}>
                    <td style={{ fontWeight: 500 }}>{p.course_title}</td>
                    <td>{planLabel(p.payment_plan)}</td>
                    <td>
                      {p.expected_amount != null
                        ? formatCurrency(p.expected_amount, p.currency)
                        : "—"}
                    </td>
                    <td>{formatCurrency(p.amount, p.currency)}</td>
                    <td>
                      <span className={`badge ${badge.cls}`}>{badge.label}</span>
                    </td>
                    <td style={{ fontSize: "0.8125rem" }}>
                      {p.created_at ? new Date(p.created_at).toLocaleDateString("es-MX") : "—"}
                    </td>
                    <td style={{ fontSize: "0.8125rem", color: "var(--color-text-muted)", maxWidth: "200px" }}>
                      {p.review_notes || "—"}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
