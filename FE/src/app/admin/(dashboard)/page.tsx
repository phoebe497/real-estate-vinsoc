"use client";

/** Thống kê (P2) — lưới card rõ ràng theo Mục 11 BAN_THIET_KE_V2, Chart.js. */

import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Tooltip,
} from "chart.js";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { Bar, Doughnut, Line } from "react-chartjs-2";

import { Card, EmptyState, PageHeader, StatCard } from "@/components/admin/ui";
import { adminFetch } from "@/lib/auth";
import { statusLabels, temperatureLabels, typeLabels } from "@/lib/crm-labels";

ChartJS.register(ArcElement, BarElement, CategoryScale, LinearScale, LineElement, PointElement, Legend, Tooltip);

type BreakdownItem = { label: string; count: number };
type SalePerformance = { id: number; name: string; assigned_count: number; sold_count: number };

type Stats = {
  total_customers: number;
  new_today: number;
  new_this_week: number;
  new_this_month: number;
  conversations: number;
  messages: number;
  captured_conversations: number;
  capture_rate: number;
  handover_customers: number;
  active_fallback_rules: number;
  customer_type_breakdown: BreakdownItem[];
  temperature_breakdown: BreakdownItem[];
  status_funnel: BreakdownItem[];
  top_subdivisions: BreakdownItem[];
  customer_trend: BreakdownItem[];
  sales_performance: SalePerformance[];
};

const PALETTE = ["#06b6d4", "#8b5cf6", "#10b981", "#f59e0b", "#ef4444", "#64748b"];
const CHART_OPTIONS = { maintainAspectRatio: false, plugins: { legend: { display: false } } } as const;

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [forbidden, setForbidden] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    adminFetch("/dashboard/stats?days=30")
      .then(async (r) => {
        if (r.status === 403) {
          setForbidden(true);
          return null;
        }
        return r.ok ? r.json() : null;
      })
      .then(setStats)
      .finally(() => setLoading(false));
  }, []);

  const cards = useMemo(
    () => [
      {
        label: "Tổng số khách hàng",
        value: stats?.total_customers ?? "—",
        caption: "Toàn bộ khách trong CRM",
      },
      {
        label: "Khách mới hôm nay",
        value: stats?.new_today ?? "—",
        caption: `Tuần này: ${stats?.new_this_week ?? "—"} · Tháng này: ${stats?.new_this_month ?? "—"}`,
      },
      {
        label: "Tỷ lệ để lại thông tin",
        value: stats ? `${Math.round(stats.capture_rate * 100)}%` : "—",
        caption: `${stats?.captured_conversations ?? 0}/${stats?.conversations ?? 0} phiên chat đã cho thông tin`,
      },
      {
        label: "Khách nóng cần chăm sóc",
        value: stats?.handover_customers ?? "—",
        caption: "Đã chuyển cho Sale phụ trách",
      },
    ],
    [stats]
  );

  if (forbidden) {
    return (
      <section>
        <EmptyState>
          Tài khoản của bạn chưa được cấp quyền <b>Xem thống kê</b>. Vào menu{" "}
          <Link className="font-semibold text-cyan-600" href="/admin/customers">
            Khách hàng
          </Link>{" "}
          để làm việc, hoặc liên hệ quản trị viên.
        </EmptyState>
      </section>
    );
  }

  if (loading) return <p className="text-sm text-slate-500">Đang tải thống kê...</p>;

  const doughnut = (items: BreakdownItem[], labelMap: Record<string, string>) => ({
    labels: items.map((i) => labelMap[i.label] ?? i.label),
    datasets: [
      {
        data: items.map((i) => i.count),
        backgroundColor: PALETTE.slice(0, Math.max(items.length, 1)),
        borderWidth: 0,
      },
    ],
  });

  return (
    <section>
      <PageHeader
        kicker="Tổng quan vận hành"
        title="Thống kê"
        description="Cơ cấu khách theo loại và mức độ quan tâm, phễu trạng thái, phân khu được quan tâm và hiệu suất đội Sale trong 30 ngày gần nhất."
        actions={
          <Link
            className="rounded-lg bg-cyan-500 px-4 py-2 text-sm font-bold text-slate-950 shadow-sm shadow-cyan-500/20 transition hover:bg-cyan-400"
            href="/admin/customers"
          >
            Danh sách khách hàng →
          </Link>
        }
      />

      {/* Hàng chỉ số tổng quan */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {cards.map((card) => (
          <StatCard caption={card.caption} key={card.label} label={card.label} value={card.value} />
        ))}
      </div>

      {/* Lưới chart */}
      <div className="mt-6 grid gap-4 lg:grid-cols-2 xl:grid-cols-3">
        <Card subtitle="Nhu cầu thật / Đầu tư / Khách ảo" title="Cơ cấu khách theo loại">
          <div className="h-56">
            {stats && stats.customer_type_breakdown.length > 0 ? (
              <Doughnut
                data={doughnut(stats.customer_type_breakdown, typeLabels)}
                options={{ maintainAspectRatio: false, plugins: { legend: { position: "bottom" } } }}
              />
            ) : (
              <EmptyState>Chưa có dữ liệu.</EmptyState>
            )}
          </div>
        </Card>

        <Card subtitle="Nóng / Ấm / Lạnh" title="Mức độ quan tâm của khách">
          <div className="h-56">
            {stats && stats.temperature_breakdown.length > 0 ? (
              <Doughnut
                data={doughnut(stats.temperature_breakdown, temperatureLabels)}
                options={{ maintainAspectRatio: false, plugins: { legend: { position: "bottom" } } }}
              />
            ) : (
              <EmptyState>Chưa có dữ liệu.</EmptyState>
            )}
          </div>
        </Card>

        <Card subtitle="Mới → Đã liên hệ → Đang tư vấn → Hẹn xem → Chốt" title="Phễu trạng thái chăm sóc">
          <div className="h-56">
            {stats ? (
              <Bar
                data={{
                  labels: stats.status_funnel.map((i) => statusLabels[i.label] ?? i.label),
                  datasets: [
                    { label: "Số khách", data: stats.status_funnel.map((i) => i.count), backgroundColor: "#06b6d4" },
                  ],
                }}
                options={CHART_OPTIONS}
              />
            ) : null}
          </div>
        </Card>

        <Card subtitle="Theo khách đã để lại thông tin" title="Phân khu được quan tâm nhất">
          <div className="h-56">
            {stats && stats.top_subdivisions.length > 0 ? (
              <Bar
                data={{
                  labels: stats.top_subdivisions.map((i) => i.label),
                  datasets: [
                    {
                      label: "Số khách quan tâm",
                      data: stats.top_subdivisions.map((i) => i.count),
                      backgroundColor: "#8b5cf6",
                    },
                  ],
                }}
                options={{ ...CHART_OPTIONS, indexAxis: "y" as const }}
              />
            ) : (
              <EmptyState>Chưa có dữ liệu.</EmptyState>
            )}
          </div>
        </Card>

        <Card className="lg:col-span-2" subtitle="Số khách mới mỗi ngày, 30 ngày gần nhất" title="Khách mới theo ngày">
          <div className="h-56">
            {stats && stats.customer_trend.length > 0 ? (
              <Line
                data={{
                  labels: stats.customer_trend.map((i) => i.label.slice(5)),
                  datasets: [
                    {
                      label: "Khách mới",
                      data: stats.customer_trend.map((i) => i.count),
                      borderColor: "#06b6d4",
                      backgroundColor: "rgba(6, 182, 212, 0.12)",
                      fill: true,
                      tension: 0.35,
                    },
                  ],
                }}
                options={CHART_OPTIONS}
              />
            ) : (
              <EmptyState>Chưa có khách mới trong 30 ngày.</EmptyState>
            )}
          </div>
        </Card>

        <Card
          className="lg:col-span-2"
          subtitle="Số khách được phân công và số căn đã bán theo từng Sale"
          title="Hiệu suất đội Sale"
        >
          <div className="h-56">
            {stats && stats.sales_performance.length > 0 ? (
              <Bar
                data={{
                  labels: stats.sales_performance.map((s) => s.name),
                  datasets: [
                    {
                      label: "Khách phụ trách",
                      data: stats.sales_performance.map((s) => s.assigned_count),
                      backgroundColor: "#06b6d4",
                    },
                    {
                      label: "Căn đã bán",
                      data: stats.sales_performance.map((s) => s.sold_count),
                      backgroundColor: "#10b981",
                    },
                  ],
                }}
                options={{ maintainAspectRatio: false, plugins: { legend: { position: "bottom" } } }}
              />
            ) : (
              <EmptyState>Chưa có tài khoản Sale nào.</EmptyState>
            )}
          </div>
        </Card>

        <Card subtitle="Toàn hệ thống" title="Hoạt động chat AI">
          <dl className="grid grid-cols-3 gap-3 text-center">
            {[
              ["Phiên chat", stats?.conversations ?? 0],
              ["Tin nhắn", stats?.messages ?? 0],
              ["Mẫu trả lời đang bật", stats?.active_fallback_rules ?? 0],
            ].map(([label, value]) => (
              <div className="rounded-lg bg-slate-50 px-2 py-4" key={String(label)}>
                <dt className="text-xs font-medium text-slate-500">{label}</dt>
                <dd className="mt-1 text-2xl font-extrabold text-slate-900">{value}</dd>
              </div>
            ))}
          </dl>
        </Card>
      </div>
    </section>
  );
}
