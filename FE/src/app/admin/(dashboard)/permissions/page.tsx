"use client";

/**
 * Phân quyền (P2) — ma trận: hàng = chức năng (nhóm theo `group_name`),
 * cột = tài khoản sale, checkbox căn giữa, sticky header + sticky cột đầu.
 */

import { Fragment, useEffect, useState } from "react";

import { EmptyState, PageHeader } from "@/components/admin/ui";
import { adminFetch } from "@/lib/auth";

type Permission = { id: number; code: string; name: string; group_name: string };
type Sale = { id: number; full_name: string; role: string; is_active: boolean };

export default function PermissionsPage() {
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [sales, setSales] = useState<Sale[]>([]);
  const [granted, setGranted] = useState<Record<number, Set<string>>>({});
  const [saving, setSaving] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  async function load() {
    const [permissionsRes, salesRes] = await Promise.all([adminFetch("/permissions"), adminFetch("/sales")]);
    const permissionList: Permission[] = permissionsRes.ok ? await permissionsRes.json() : [];
    const saleList: Sale[] = (salesRes.ok ? await salesRes.json() : []).filter((s: Sale) => s.role === "sale");
    setPermissions(permissionList);
    setSales(saleList);

    const grantedMap: Record<number, Set<string>> = {};
    await Promise.all(
      saleList.map(async (sale) => {
        const response = await adminFetch(`/sales/${sale.id}/permissions`);
        const list: Permission[] = response.ok ? await response.json() : [];
        grantedMap[sale.id] = new Set(list.map((p) => p.code));
      })
    );
    setGranted(grantedMap);
    setLoading(false);
  }

  useEffect(() => {
    load();
  }, []);

  async function toggle(sale: Sale, code: string) {
    const current = new Set(granted[sale.id] ?? []);
    if (current.has(code)) current.delete(code);
    else current.add(code);
    setSaving(sale.id);
    const response = await adminFetch(`/sales/${sale.id}/permissions`, {
      method: "PUT",
      body: JSON.stringify({ codes: [...current] }),
    });
    if (response.ok) {
      setGranted((prev) => ({ ...prev, [sale.id]: current }));
    }
    setSaving(null);
  }

  const groups = [...new Set(permissions.map((p) => p.group_name))];

  return (
    <section>
      <PageHeader
        kicker="Phân quyền hệ thống"
        title="Phân quyền"
        description="Tick vào ô để cấp hoặc thu quyền cho từng Sale. Tài khoản Quản trị mặc định có toàn quyền, không cần cấp."
      />

      {loading ? (
        <p className="text-sm text-slate-500">Đang tải ma trận phân quyền...</p>
      ) : sales.length === 0 ? (
        <EmptyState>
          Chưa có tài khoản Sale nào. Hãy tạo Sale ở menu <b>Quản lý Sale</b> trước.
        </EmptyState>
      ) : (
        <div className="max-h-[70vh] overflow-auto rounded-xl border border-slate-200 bg-white shadow-sm">
          <table className="w-full border-collapse text-sm">
            <thead className="sticky top-0 z-20">
              <tr className="bg-slate-950 text-xs uppercase tracking-wide text-slate-300">
                <th className="sticky left-0 z-30 min-w-[240px] bg-slate-950 px-4 py-3 text-left font-semibold">
                  Chức năng
                </th>
                {sales.map((sale) => (
                  <th className="min-w-[130px] px-4 py-3 text-center font-semibold" key={sale.id}>
                    {sale.full_name}
                    {saving === sale.id ? <span className="ml-1 animate-pulse">⏳</span> : null}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {groups.map((group) => (
                <Fragment key={group}>
                  <tr>
                    <td
                      className="sticky left-0 z-10 bg-cyan-50 px-4 py-2 text-xs font-extrabold uppercase tracking-wide text-cyan-700"
                      colSpan={sales.length + 1}
                    >
                      {group}
                    </td>
                  </tr>
                  {permissions
                    .filter((p) => p.group_name === group)
                    .map((permission) => (
                      <tr className="border-t border-slate-100 hover:bg-cyan-50/40" key={permission.code}>
                        <td className="sticky left-0 z-10 bg-white px-4 py-3">
                          <p className="font-semibold text-slate-800">{permission.name}</p>
                        </td>
                        {sales.map((sale) => (
                          <td className="px-4 py-3 text-center" key={sale.id}>
                            <input
                              checked={granted[sale.id]?.has(permission.code) ?? false}
                              className="h-4 w-4 cursor-pointer accent-cyan-500"
                              disabled={saving === sale.id}
                              onChange={() => toggle(sale, permission.code)}
                              type="checkbox"
                            />
                          </td>
                        ))}
                      </tr>
                    ))}
                </Fragment>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
