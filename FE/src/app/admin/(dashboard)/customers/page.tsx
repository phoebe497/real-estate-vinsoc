"use client";

/** Khách hàng (P2) — TanStack Table, cột tiếng Việt, badge màu theo enum. */

import { ColumnDef } from "@tanstack/react-table";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useMemo, useState } from "react";

import { DataTable } from "@/components/admin/data-table";
import { Badge, Button, Field, PageHeader, Select, TextInput } from "@/components/admin/ui";
import { adminFetch } from "@/lib/auth";
import { formatDateOnly, metaOf, statusMeta, temperatureMeta, typeMeta } from "@/lib/crm-labels";

type UserBrief = { id: number; full_name: string };
type SubdivisionBrief = { id: number; slug: string; name: string };
type Customer = {
  id: number;
  full_name: string | null;
  phone: string;
  email: string | null;
  customer_type: string;
  temperature: string;
  lead_score: number | null;
  status: string;
  interested_subdivision: SubdivisionBrief | null;
  preferred_unit_type: string | null;
  assigned_sale: UserBrief | null;
  source: string;
  created_at: string;
};

const FETCH_LIMIT = 200;

export default function CustomersPage() {
  const router = useRouter();
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [typeFilter, setTypeFilter] = useState("");
  const [temperatureFilter, setTemperatureFilter] = useState("");
  const [loading, setLoading] = useState(true);

  function load(filters?: { status?: string; type?: string; temperature?: string }) {
    const status = filters?.status ?? statusFilter;
    const type = filters?.type ?? typeFilter;
    const temperature = filters?.temperature ?? temperatureFilter;
    const params = new URLSearchParams({ limit: String(FETCH_LIMIT) });
    if (search.trim()) params.set("search", search.trim());
    if (status) params.set("status", status);
    if (type) params.set("customer_type", type);
    if (temperature) params.set("temperature", temperature);
    setLoading(true);
    adminFetch(`/customers?${params.toString()}`)
      .then((r) => (r.ok ? r.json() : []))
      .then(setCustomers)
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const columns = useMemo<ColumnDef<Customer, unknown>[]>(
    () => [
      {
        header: "Họ tên",
        accessorKey: "full_name",
        cell: ({ row }) => (
          <div>
            <p className="font-semibold text-slate-900">
              {row.original.full_name || "Khách chưa cung cấp tên"}
            </p>
            <p className="text-xs text-slate-500">{row.original.phone}</p>
          </div>
        ),
      },
      {
        header: "Loại khách",
        accessorKey: "customer_type",
        cell: ({ getValue }) => {
          const meta = metaOf(typeMeta, String(getValue()));
          return <Badge tone={meta.tone}>{meta.label}</Badge>;
        },
      },
      {
        header: "Mức độ quan tâm",
        accessorKey: "lead_score",
        cell: ({ row }) => {
          const meta = metaOf(temperatureMeta, row.original.temperature);
          return (
            <div className="flex items-center gap-2">
              <Badge tone={meta.tone}>{meta.label}</Badge>
              {row.original.lead_score != null ? (
                <span className="text-xs text-slate-500">{row.original.lead_score}/100</span>
              ) : null}
            </div>
          );
        },
      },
      {
        header: "Phân khu quan tâm",
        accessorFn: (row) => row.interested_subdivision?.name ?? "",
        id: "subdivision",
        cell: ({ getValue }) => (getValue() ? String(getValue()) : <span className="text-slate-400">—</span>),
      },
      {
        header: "Sale phụ trách",
        accessorFn: (row) => row.assigned_sale?.full_name ?? "",
        id: "sale",
        cell: ({ getValue }) =>
          getValue() ? String(getValue()) : <span className="text-slate-400">Chưa phân công</span>,
      },
      {
        header: "Trạng thái",
        accessorKey: "status",
        cell: ({ getValue }) => {
          const meta = metaOf(statusMeta, String(getValue()));
          return <Badge tone={meta.tone}>{meta.label}</Badge>;
        },
      },
      {
        header: "Ngày tạo",
        accessorKey: "created_at",
        cell: ({ getValue }) => (
          <span className="whitespace-nowrap text-slate-500">{formatDateOnly(String(getValue()))}</span>
        ),
      },
    ],
    []
  );

  function submitSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    load();
  }

  return (
    <section>
      <PageHeader
        kicker="CRM"
        title="Khách hàng"
        description="Danh sách khách đã để lại thông tin từ chat AI và form liên hệ. Bấm vào một dòng để xem hội thoại, nhu cầu và lịch sử mua."
      />

      {/* Bộ lọc */}
      <form
        className="mb-4 grid gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm sm:grid-cols-2 lg:grid-cols-5"
        onSubmit={submitSearch}
      >
        <Field className="lg:col-span-2" label="Tìm kiếm">
          <TextInput
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Nhập tên, số điện thoại hoặc email..."
            value={search}
          />
        </Field>
        <Field label="Trạng thái">
          <Select
            onChange={(e) => {
              setStatusFilter(e.target.value);
              load({ status: e.target.value });
            }}
            value={statusFilter}
          >
            <option value="">Tất cả</option>
            {Object.entries(statusMeta).map(([value, meta]) => (
              <option key={value} value={value}>
                {meta.label}
              </option>
            ))}
          </Select>
        </Field>
        <Field label="Loại khách">
          <Select
            onChange={(e) => {
              setTypeFilter(e.target.value);
              load({ type: e.target.value });
            }}
            value={typeFilter}
          >
            <option value="">Tất cả</option>
            {Object.entries(typeMeta).map(([value, meta]) => (
              <option key={value} value={value}>
                {meta.label}
              </option>
            ))}
          </Select>
        </Field>
        <div className="flex items-end gap-2">
          <Field className="flex-1" label="Mức độ quan tâm">
            <Select
              onChange={(e) => {
                setTemperatureFilter(e.target.value);
                load({ temperature: e.target.value });
              }}
              value={temperatureFilter}
            >
              <option value="">Tất cả</option>
              {Object.entries(temperatureMeta).map(([value, meta]) => (
                <option key={value} value={value}>
                  {meta.label}
                </option>
              ))}
            </Select>
          </Field>
          <Button className="mb-px" type="submit" variant="primary">
            Tìm
          </Button>
        </div>
      </form>

      <DataTable
        columns={columns}
        data={customers}
        emptyMessage="Chưa có khách hàng phù hợp với bộ lọc."
        loading={loading}
        onRowClick={(customer) => router.push(`/admin/customers/${customer.id}`)}
      />
    </section>
  );
}
