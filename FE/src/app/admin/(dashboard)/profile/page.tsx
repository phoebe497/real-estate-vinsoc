"use client";

/** Hồ sơ cá nhân (P2) — sale/admin tự sửa thông tin của mình. */

import { FormEvent, useEffect, useState } from "react";

import { Badge, Button, Card, ErrorText, Field, PageHeader, TextInput } from "@/components/admin/ui";
import { adminFetch, MeInfo } from "@/lib/auth";
import { formatDateOnly, metaOf, roleMeta } from "@/lib/crm-labels";

export default function ProfilePage() {
  const [me, setMe] = useState<MeInfo | null>(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  function load() {
    adminFetch("/auth/me")
      .then((r) => (r.ok ? r.json() : null))
      .then(setMe);
  }

  useEffect(load, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("");
    setError("");
    const data = Object.fromEntries(new FormData(event.currentTarget).entries());
    const patch: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(data)) {
      if (value) patch[key] = value;
    }
    const response = await adminFetch("/auth/me", { method: "PATCH", body: JSON.stringify(patch) });
    if (response.ok) {
      setMessage("Đã lưu thay đổi.");
      load();
    } else {
      const detail = await response.json().catch(() => null);
      setError(detail?.detail ?? "Không lưu được thay đổi.");
    }
  }

  if (!me) return <p className="text-sm text-slate-500">Đang tải hồ sơ...</p>;

  const role = metaOf(roleMeta, me.user.role);

  return (
    <section>
      <PageHeader kicker="Tài khoản" title="Hồ sơ cá nhân" description="Cập nhật thông tin hiển thị và mật khẩu đăng nhập của bạn." />

      <div className="grid gap-4 lg:grid-cols-[280px_1fr]">
        <Card>
          <div className="flex flex-col items-center py-4 text-center">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              alt={me.user.full_name}
              className="h-20 w-20 rounded-full object-cover ring-4 ring-cyan-400/40"
              src={me.user.avatar_url || "/media_files/advisor-avatar.jpg"}
            />
            <p className="mt-3 font-bold text-slate-900">{me.user.full_name}</p>
            <p className="text-sm text-slate-500">{me.user.email}</p>
            <div className="mt-2 flex gap-2">
              <Badge tone={role.tone}>{role.label}</Badge>
              {me.user.title ? <Badge tone="cyan">{me.user.title}</Badge> : null}
            </div>
            {me.user.join_date ? (
              <p className="mt-3 text-xs text-slate-500">Vào làm: {formatDateOnly(me.user.join_date)}</p>
            ) : null}
          </div>
        </Card>

        <Card title="Chỉnh sửa thông tin">
          <form className="grid gap-3 sm:grid-cols-2" onSubmit={submit}>
            <Field label="Họ và tên">
              <TextInput defaultValue={me.user.full_name} name="full_name" />
            </Field>
            <Field label="Số điện thoại">
              <TextInput defaultValue={me.user.phone ?? ""} name="phone" placeholder="09xxxxxxxx" />
            </Field>
            <Field label="Chức danh">
              <TextInput defaultValue={me.user.title ?? ""} name="title" placeholder="VD: Chuyên viên kinh doanh" />
            </Field>
            <Field label="Ảnh đại diện (đường dẫn)">
              <TextInput defaultValue={me.user.avatar_url ?? ""} name="avatar_url" placeholder="https://..." />
            </Field>
            <Field className="sm:col-span-2" label="Mật khẩu mới (bỏ trống nếu không đổi)">
              <TextInput minLength={8} name="password" placeholder="Tối thiểu 8 ký tự" type="password" />
            </Field>
            <div className="sm:col-span-2">
              {message ? <p className="text-sm font-medium text-emerald-600">{message}</p> : null}
              <ErrorText>{error}</ErrorText>
              <Button className="mt-1" type="submit" variant="primary">
                Lưu thay đổi
              </Button>
            </div>
          </form>
        </Card>
      </div>
    </section>
  );
}
