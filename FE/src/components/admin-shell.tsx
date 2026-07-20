"use client";

/** Khung admin (P2) — sidebar slate-950 + accent cyan, đồng bộ theme public site. */

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { ReactNode, useEffect, useState } from "react";
import Image from "next/image";

import { adminFetch, clearToken, hasPermission, MeInfo } from "@/lib/auth";
import { roleMeta } from "@/lib/crm-labels";

// Menu theo BAN_THIET_KE_V2 Mục 9.3: sale mặc định chỉ thấy Khách hàng + Hồ sơ,
// các menu khác hiện khi được cấp quyền tương ứng.
const navigation = [
  { href: "/admin", label: "Thống kê", icon: "📊", permission: "dashboard.view" },
  { href: "/admin/customers", label: "Khách hàng", icon: "👥", permission: null },
  { href: "/admin/sales", label: "Quản lý Sale", icon: "🧑‍💼", permission: "sales.manage" },
  { href: "/admin/permissions", label: "Phân quyền", icon: "🔐", permission: "permissions.manage" },
  { href: "/admin/fallback-rules", label: "Mẫu trả lời", icon: "💬", permission: "fallback.manage" },
  { href: "/admin/profile", label: "Hồ sơ cá nhân", icon: "⚙️", permission: null },
];

export function AdminShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [me, setMe] = useState<MeInfo | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    adminFetch("/auth/me")
      .then(async (response) => {
        if (response.ok) setMe(await response.json());
      })
      .finally(() => setReady(true));
  }, []);

  function logout() {
    clearToken();
    router.replace("/admin/login");
  }

  if (!ready) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50 text-sm text-slate-500">
        Đang xác thực phiên làm việc...
      </div>
    );
  }
  if (!me) return null;

  const visibleNavigation = navigation.filter(
    (item) => !item.permission || hasPermission(me, item.permission)
  );

  return (
    <div className="flex min-h-screen bg-slate-50">
      {/* Sidebar */}
      <aside className="fixed inset-y-0 left-0 flex w-60 flex-col bg-slate-950 text-slate-300">
        <Link className="flex items-center gap-3 px-5 py-5" href="/admin/customers">
          <Image
            src="/media_files/advisor-avatar.jpg"
            alt="Ocean Park Advisor"
            width={36}
            height={36}
            className="rounded-lg object-cover"
          />

          <span className="text-sm font-bold text-white">
            Ocean Park
            <span className="block text-[11px] font-medium text-slate-400">
              Bảng điều khiển bán hàng
            </span>
          </span>
        </Link>

        <nav className="mt-2 flex-1 space-y-1 px-3">
          {visibleNavigation.map((item) => {
            const active =
              pathname === item.href || (item.href !== "/admin" && pathname.startsWith(`${item.href}/`));
            return (
              <Link
                className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-semibold transition ${
                  active
                    ? "bg-cyan-500/15 text-cyan-300"
                    : "text-slate-400 hover:bg-white/5 hover:text-white"
                }`}
                href={item.href}
                key={item.href}
              >
                <span aria-hidden>{item.icon}</span>
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="border-t border-white/10 p-4">
          <div className="flex items-center gap-3">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              alt={me.user.full_name}
              className="h-9 w-9 rounded-full object-cover ring-2 ring-cyan-400/50"
              src={me.user.avatar_url || "/media_files/advisor-avatar.jpg"}
            />
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-semibold text-white">{me.user.full_name}</p>
              <p className="truncate text-xs text-slate-400">
                {me.user.title || roleMeta[me.user.role]?.label || me.user.role}
              </p>
            </div>
            <button
              className="rounded-lg p-1.5 text-slate-400 transition hover:bg-white/10 hover:text-white"
              onClick={logout}
              title="Đăng xuất"
              type="button"
            >
              ⎋
            </button>
          </div>
        </div>
      </aside>

      {/* Workspace */}
      <div className="ml-60 flex min-h-screen flex-1 flex-col">
        <header className="sticky top-0 z-10 flex items-center justify-between border-b border-slate-200 bg-white/90 px-6 py-3 backdrop-blur">
          <p className="text-sm font-semibold text-slate-700">Vinhomes Ocean Park 1 · Quản trị CRM</p>
          <Link
            className="text-sm font-semibold text-cyan-600 transition hover:text-cyan-500"
            href="/"
            target="_blank"
          >
            Xem website ↗
          </Link>
        </header>
        <main className="flex-1 px-6 py-6">{children}</main>
      </div>
    </div>
  );
}
