"use client";

/** Quản lý Sale (P2): card từng sale — thông tin, ca làm, phân khu, số căn bán, giải thưởng. */

import { FormEvent, useEffect, useState } from "react";

import { Badge, Button, Card, EmptyState, ErrorText, Field, PageHeader, Select, TextInput } from "@/components/admin/ui";
import { adminFetch } from "@/lib/auth";
import { formatDateOnly, metaOf, roleMeta } from "@/lib/crm-labels";

type SubdivisionBrief = { id: number; slug: string; name: string };
type Award = { id: number; award_name: string; awarded_at: string; note: string | null };
type Sale = {
  id: number;
  email: string;
  full_name: string;
  phone: string | null;
  role: string;
  is_active: boolean;
  title: string | null;
  work_shift_start: string | null;
  work_shift_end: string | null;
  join_date: string | null;
  subdivisions: SubdivisionBrief[];
  awards: Award[];
  assigned_customer_count: number;
  sold_count: number;
};

function shiftLabel(sale: Sale) {
  if (!sale.work_shift_start) return "Chưa thiết lập";
  return `${sale.work_shift_start.slice(0, 5)} – ${(sale.work_shift_end ?? "").slice(0, 5)}`;
}

export default function SalesPage() {
  const [sales, setSales] = useState<Sale[]>([]);
  const [subdivisions, setSubdivisions] = useState<SubdivisionBrief[]>([]);
  const [openCreate, setOpenCreate] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [error, setError] = useState("");

  function load() {
    adminFetch("/sales")
      .then((r) => (r.ok ? r.json() : []))
      .then(setSales);
  }

  useEffect(() => {
    load();
    adminFetch("/subdivisions")
      .then((r) => (r.ok ? r.json() : []))
      .then((items: SubdivisionBrief[]) => setSubdivisions(items))
      .catch(() => setSubdivisions([]));
  }, []);

  async function createSale(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    const form = event.currentTarget;
    const data = Object.fromEntries(new FormData(form).entries());
    const payload: Record<string, unknown> = { ...data };
    for (const key of ["phone", "title", "work_shift_start", "work_shift_end", "join_date"]) {
      if (!payload[key]) delete payload[key];
    }
    const response = await adminFetch("/sales", { method: "POST", body: JSON.stringify(payload) });
    if (response.ok) {
      form?.reset();
      setOpenCreate(false);
      load();
    } else {
      const detail = await response.json().catch(() => null);
      setError(detail?.detail ?? "Không thể tạo tài khoản");
    }
  }

  async function updateSale(saleId: number, patch: Record<string, unknown>) {
    const response = await adminFetch(`/sales/${saleId}`, { method: "PATCH", body: JSON.stringify(patch) });
    if (response.ok) load();
  }

  async function removeSale(sale: Sale) {
    if (!window.confirm(`Xóa tài khoản ${sale.full_name}? Khách đã phân công sẽ về trạng thái chưa phân công.`)) return;
    const response = await adminFetch(`/sales/${sale.id}`, { method: "DELETE" });
    if (response.ok) load();
  }

  async function addAward(sale: Sale, event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = Object.fromEntries(new FormData(form).entries());
    const response = await adminFetch(`/sales/${sale.id}/awards`, { method: "POST", body: JSON.stringify(data) });
    if (response.ok) {
      form?.reset();
      load();
    }
  }

  async function removeAward(sale: Sale, awardId: number) {
    const response = await adminFetch(`/sales/${sale.id}/awards/${awardId}`, { method: "DELETE" });
    if (response.ok) load();
  }

  async function toggleSubdivision(sale: Sale, subdivisionId: number) {
    const current = sale.subdivisions.map((s) => s.id);
    const next = current.includes(subdivisionId)
      ? current.filter((id) => id !== subdivisionId)
      : [...current, subdivisionId];
    const response = await adminFetch(`/sales/${sale.id}/subdivisions`, {
      method: "PUT",
      body: JSON.stringify({ subdivision_ids: next }),
    });
    if (response.ok) load();
  }

  return (
    <section>
      <PageHeader
        kicker="Đội ngũ kinh doanh"
        title="Quản lý Sale"
        description="Thông tin cá nhân, giờ làm việc, phân khu phụ trách, số căn đã bán và giải thưởng của từng nhân viên."
        actions={
          <Button onClick={() => setOpenCreate(!openCreate)} variant="primary">
            ＋ Thêm nhân viên
          </Button>
        }
      />

      {openCreate ? (
        <Card className="mb-5" title="Tạo tài khoản mới">
          <form className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3" onSubmit={createSale}>
            <Field label="Họ và tên">
              <TextInput name="full_name" placeholder="Nguyễn Văn A" required />
            </Field>
            <Field label="Email đăng nhập">
              <TextInput name="email" placeholder="ten@congty.vn" required type="email" />
            </Field>
            <Field label="Mật khẩu ban đầu">
              <TextInput minLength={8} name="password" placeholder="Tối thiểu 8 ký tự" required type="password" />
            </Field>
            <Field label="Vai trò">
              <Select defaultValue="sale" name="role">
                <option value="sale">Sale</option>
                <option value="admin">Quản trị</option>
              </Select>
            </Field>
            <Field label="Số điện thoại">
              <TextInput name="phone" placeholder="09xxxxxxxx" />
            </Field>
            <Field label="Chức danh">
              <TextInput name="title" placeholder="VD: Chuyên viên kinh doanh" />
            </Field>
            <Field label="Giờ làm việc từ">
              <TextInput name="work_shift_start" type="time" />
            </Field>
            <Field label="Đến">
              <TextInput name="work_shift_end" type="time" />
            </Field>
            <Field label="Ngày vào làm">
              <TextInput name="join_date" type="date" />
            </Field>
            <div className="sm:col-span-2 lg:col-span-3">
              <ErrorText>{error}</ErrorText>
              <Button className="mt-1" type="submit" variant="primary">
                Tạo tài khoản
              </Button>
            </div>
          </form>
        </Card>
      ) : null}

      {sales.length === 0 ? <EmptyState>Chưa có tài khoản nào.</EmptyState> : null}

      <div className="grid gap-4 xl:grid-cols-2">
        {sales.map((sale) => {
          const role = metaOf(roleMeta, sale.role);
          return (
            <Card key={sale.id}>
              {/* Header card */}
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div className="flex items-center gap-3">
                  <div className="flex h-11 w-11 items-center justify-center rounded-full bg-cyan-500/15 text-base font-extrabold text-cyan-600">
                    {sale.full_name.slice(0, 1).toUpperCase()}
                  </div>
                  <div>
                    <p className="font-bold text-slate-900">
                      {sale.full_name}
                      {sale.title ? <span className="font-medium text-slate-500"> — {sale.title}</span> : null}
                    </p>
                    <p className="text-xs text-slate-500">
                      {sale.email}
                      {sale.phone ? ` · ${sale.phone}` : ""}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge tone={role.tone}>{role.label}</Badge>
                  <Badge tone={sale.is_active ? "green" : "slate"}>
                    {sale.is_active ? "Đang hoạt động" : "Đã khóa"}
                  </Badge>
                </div>
              </div>

              {/* Chỉ số */}
              <dl className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
                {[
                  ["Khách phụ trách", sale.assigned_customer_count],
                  ["Căn đã bán", sale.sold_count],
                  ["Giờ làm việc", shiftLabel(sale)],
                  ["Ngày vào làm", sale.join_date ? formatDateOnly(sale.join_date) : "—"],
                ].map(([label, value]) => (
                  <div className="rounded-lg bg-slate-50 px-3 py-2.5" key={String(label)}>
                    <dt className="text-[11px] font-medium uppercase tracking-wide text-slate-500">{label}</dt>
                    <dd className="mt-0.5 text-sm font-bold text-slate-900">{value}</dd>
                  </div>
                ))}
              </dl>

              {/* Phân khu phụ trách */}
              {sale.role === "sale" ? (
                <div className="mt-4">
                  <p className="mb-2 text-xs font-bold uppercase tracking-wide text-slate-500">
                    Phân khu phụ trách ({sale.subdivisions.length})
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {subdivisions.map((sub) => {
                      const active = sale.subdivisions.some((s) => s.id === sub.id);
                      return (
                        <button
                          className={`rounded-full px-3 py-1 text-xs font-semibold ring-1 ring-inset transition ${
                            active
                              ? "bg-cyan-500 text-slate-950 ring-cyan-500"
                              : "bg-white text-slate-500 ring-slate-200 hover:ring-cyan-300"
                          }`}
                          key={sub.id}
                          onClick={() => toggleSubdivision(sale, sub.id)}
                          type="button"
                        >
                          {sub.name}
                        </button>
                      );
                    })}
                  </div>
                </div>
              ) : null}

              {/* Giải thưởng */}
              <div className="mt-4">
                <p className="mb-2 text-xs font-bold uppercase tracking-wide text-slate-500">
                  Giải thưởng ({sale.awards.length})
                </p>
                <div className="space-y-1.5">
                  {sale.awards.map((award) => (
                    <div
                      className="flex items-center justify-between rounded-lg bg-amber-50 px-3 py-1.5 text-sm"
                      key={award.id}
                    >
                      <span className="text-amber-800">
                        🏆 {award.award_name} · {formatDateOnly(award.awarded_at)}
                      </span>
                      <button
                        className="text-xs font-bold text-amber-500 hover:text-red-600"
                        onClick={() => removeAward(sale, award.id)}
                        title="Xóa giải thưởng"
                        type="button"
                      >
                        ✕
                      </button>
                    </div>
                  ))}
                </div>
                <form className="mt-2 flex flex-wrap gap-2" onSubmit={(e) => addAward(sale, e)}>
                  <TextInput className="!w-auto flex-1" name="award_name" placeholder="Tên giải thưởng" required />
                  <TextInput className="!w-auto" name="awarded_at" required type="date" />
                  <Button type="submit">＋ Thêm</Button>
                </form>
              </div>

              {/* Hành động */}
              <div className="mt-4 flex flex-wrap gap-2 border-t border-slate-100 pt-3">
                <Button onClick={() => setEditingId(editingId === sale.id ? null : sale.id)}>✏️ Sửa</Button>
                <Button onClick={() => updateSale(sale.id, { is_active: !sale.is_active })}>
                  {sale.is_active ? "🔒 Khóa" : "🔓 Mở lại"}
                </Button>
                <Button onClick={() => removeSale(sale)} variant="danger">
                  🗑 Xóa
                </Button>
              </div>

              {editingId === sale.id ? (
                <form
                  className="mt-3 grid gap-3 rounded-lg bg-slate-50 p-4 sm:grid-cols-2 lg:grid-cols-3"
                  onSubmit={async (e) => {
                    e.preventDefault();
                    const data = Object.fromEntries(new FormData(e.currentTarget).entries());
                    const patch: Record<string, unknown> = {};
                    for (const [key, value] of Object.entries(data)) {
                      if (value) patch[key] = value;
                    }
                    await updateSale(sale.id, patch);
                    setEditingId(null);
                  }}
                >
                  <Field label="Họ và tên">
                    <TextInput defaultValue={sale.full_name} name="full_name" />
                  </Field>
                  <Field label="Số điện thoại">
                    <TextInput defaultValue={sale.phone ?? ""} name="phone" placeholder="09xxxxxxxx" />
                  </Field>
                  <Field label="Chức danh">
                    <TextInput defaultValue={sale.title ?? ""} name="title" placeholder="VD: Chuyên viên kinh doanh" />
                  </Field>
                  <Field label="Giờ làm việc từ">
                    <TextInput defaultValue={sale.work_shift_start ?? ""} name="work_shift_start" type="time" />
                  </Field>
                  <Field label="Đến">
                    <TextInput defaultValue={sale.work_shift_end ?? ""} name="work_shift_end" type="time" />
                  </Field>
                  <Field label="Ngày vào làm">
                    <TextInput defaultValue={sale.join_date ?? ""} name="join_date" type="date" />
                  </Field>
                  <div className="sm:col-span-2 lg:col-span-3">
                    <Button type="submit" variant="primary">
                      Lưu thay đổi
                    </Button>
                  </div>
                </form>
              ) : null}
            </Card>
          );
        })}
      </div>
    </section>
  );
}
