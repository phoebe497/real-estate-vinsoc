"use client";

/** Đăng nhập nội bộ (P2) — theme public site, không điền sẵn dữ liệu mẫu. */

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { API_URL } from "@/lib/api";
import { setToken } from "@/lib/auth";

export default function AdminLoginPage() {
  const router = useRouter();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    const data = new FormData(event.currentTarget);
    try {
      const response = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(Object.fromEntries(data.entries())),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail ?? "Không thể đăng nhập");
      setToken(payload.access_token);
      router.replace("/admin/customers");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Không thể kết nối máy chủ");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen">
      {/* Panel giới thiệu — tông slate-950 giống hero public site */}
      <section className="hidden flex-1 flex-col justify-center bg-slate-950 px-14 text-white lg:flex">
        <p className="text-xs font-bold uppercase tracking-[0.25em] text-cyan-400">
          Vinhomes Ocean Park 1 · Bảng điều khiển bán hàng
        </p>
        <h1 className="mt-4 max-w-md text-4xl font-extrabold leading-tight">
          Nắm đúng nhu cầu.
          <br />
          <em className="not-italic text-cyan-400">Chạm đúng cơ hội.</em>
        </h1>
        <p className="mt-4 max-w-md text-slate-400">
          Không gian tập trung để đội Sale theo dõi khách hàng, xem hội thoại AI và làm chủ chất lượng tư vấn.
        </p>
        <div className="mt-10 flex items-center gap-4 rounded-xl border border-white/10 bg-white/5 px-5 py-4">
          <span className="text-4xl font-extrabold text-cyan-400">12</span>
          <span className="text-sm text-slate-300">
            phân khu trong một nguồn dữ liệu thống nhất, đồng bộ với chatbot AI
          </span>
        </div>
      </section>

      {/* Form đăng nhập */}
      <section className="flex flex-1 items-center justify-center bg-slate-50 px-6">
        <div className="w-full max-w-sm rounded-2xl border border-slate-200 bg-white p-8 shadow-lg">
          <div className="mb-6 text-center">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              alt="Ocean Park Advisor"
              className="mx-auto h-14 w-14 rounded-xl object-cover ring-2 ring-cyan-400/50"
              src="/media_files/advisor-avatar.jpg"
            />
            <h2 className="mt-4 text-xl font-extrabold text-slate-900">Chào mừng trở lại</h2>
            <p className="mt-1 text-sm text-slate-500">Đăng nhập bằng tài khoản nội bộ được cấp.</p>
          </div>

          <form className="space-y-4" onSubmit={submit}>
            <label className="block text-sm">
              <span className="mb-1 block font-semibold text-slate-700">Email</span>
              <input
                autoComplete="username"
                className="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none transition placeholder:text-slate-400 focus:border-cyan-500 focus:ring-2 focus:ring-cyan-100"
                name="email"
                placeholder="ten@congty.vn"
                required
                type="email"
              />
            </label>
            <label className="block text-sm">
              <span className="mb-1 block font-semibold text-slate-700">Mật khẩu</span>
              <input
                autoComplete="current-password"
                className="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none transition placeholder:text-slate-400 focus:border-cyan-500 focus:ring-2 focus:ring-cyan-100"
                name="password"
                placeholder="Nhập mật khẩu"
                required
                type="password"
              />
            </label>
            {error ? (
              <p className="rounded-lg bg-red-50 px-3 py-2 text-sm font-medium text-red-600">{error}</p>
            ) : null}
            <button
              className="w-full rounded-lg bg-cyan-500 py-2.5 text-sm font-bold text-slate-950 shadow-sm shadow-cyan-500/20 transition hover:bg-cyan-400 disabled:opacity-60"
              disabled={loading}
              type="submit"
            >
              {loading ? "Đang xác thực..." : "Đăng nhập"}
            </button>
          </form>
        </div>
      </section>
    </main>
  );
}
