"use client";

/** Mẫu trả lời tự động (P2): bảng rule rõ ràng — từ khóa, mẫu trả lời, ưu tiên, bật/tắt. */

import { FormEvent, useEffect, useState } from "react";

import { Badge, Button, Card, EmptyState, ErrorText, Field, PageHeader, TextArea, TextInput } from "@/components/admin/ui";
import { adminFetch } from "@/lib/auth";

type Rule = {
  id: number;
  keyword: string;
  response_message: string;
  priority: number;
  is_active: boolean;
};

export default function FallbackRulesPage() {
  const [rules, setRules] = useState<Rule[]>([]);
  const [open, setOpen] = useState(false);
  const [error, setError] = useState("");

  function load() {
    adminFetch("/fallback-rules")
      .then((r) => (r.ok ? r.json() : []))
      .then(setRules);
  }

  useEffect(load, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    const form = event.currentTarget;
    const data = new FormData(form);
    const response = await adminFetch("/fallback-rules", {
      method: "POST",
      body: JSON.stringify({
        keyword: data.get("keyword"),
        response_message: data.get("response_message"),
        priority: Number(data.get("priority")),
        is_active: true,
      }),
    });
    if (response.ok) {
      setOpen(false);
      load();
      form?.reset();
    } else {
      const payload = await response.json().catch(() => null);
      setError(payload?.detail ?? "Không thể tạo mẫu trả lời");
    }
  }

  async function toggleActive(rule: Rule) {
    const response = await adminFetch(`/fallback-rules/${rule.id}`, {
      method: "PATCH",
      body: JSON.stringify({
        keyword: rule.keyword,
        response_message: rule.response_message,
        priority: rule.priority,
        is_active: !rule.is_active,
      }),
    });
    if (response.ok) load();
  }

  async function remove(rule: Rule) {
    if (!window.confirm(`Xóa mẫu trả lời cho từ khóa "${rule.keyword}"?`)) return;
    const response = await adminFetch(`/fallback-rules/${rule.id}`, { method: "DELETE" });
    if (response.ok) load();
  }

  return (
    <section>
      <PageHeader
        kicker="Kiểm soát phản hồi AI"
        title="Mẫu trả lời tự động"
        description="Khi tin nhắn của khách chứa từ khóa cấu hình ở đây, hệ thống dùng mẫu trả lời soạn sẵn thay vì hỏi AI — dùng cho thông tin chưa có trong cơ sở tri thức."
        actions={
          <Button onClick={() => setOpen(!open)} variant="primary">
            ＋ Thêm mẫu trả lời
          </Button>
        }
      />

      {open ? (
        <Card className="mb-5" title="Tạo mẫu trả lời mới">
          <form className="grid gap-3 sm:grid-cols-2" onSubmit={submit}>
            <Field label="Từ khóa kích hoạt">
              <TextInput name="keyword" placeholder="VD: thú cưng, gửi xe, phí dịch vụ..." required />
            </Field>
            <Field label="Độ ưu tiên (lớn = ưu tiên trước)">
              <TextInput defaultValue={10} max={1000} min={0} name="priority" type="number" />
            </Field>
            <Field className="sm:col-span-2" label="Nội dung trả lời">
              <TextArea
                name="response_message"
                placeholder="Câu trả lời hệ thống sẽ gửi cho khách khi gặp từ khóa này..."
                required
                rows={3}
              />
            </Field>
            <div className="sm:col-span-2">
              <ErrorText>{error}</ErrorText>
              <Button className="mt-1" type="submit" variant="primary">
                Lưu mẫu trả lời
              </Button>
            </div>
          </form>
        </Card>
      ) : null}

      {rules.length === 0 ? (
        <EmptyState>Chưa có mẫu trả lời nào. Hãy tạo mẫu đầu tiên cho các câu hỏi thường gặp.</EmptyState>
      ) : (
        <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-950 text-xs uppercase tracking-wide text-slate-300">
              <tr>
                <th className="px-4 py-3 font-semibold">Từ khóa</th>
                <th className="px-4 py-3 font-semibold">Mẫu trả lời</th>
                <th className="px-4 py-3 text-center font-semibold">Ưu tiên</th>
                <th className="px-4 py-3 text-center font-semibold">Trạng thái</th>
                <th className="px-4 py-3 text-right font-semibold">Thao tác</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {rules.map((rule) => (
                <tr className="hover:bg-cyan-50/60" key={rule.id}>
                  <td className="px-4 py-3 font-semibold text-slate-900">{rule.keyword}</td>
                  <td className="max-w-md px-4 py-3 text-slate-600">
                    <p className="line-clamp-2">{rule.response_message}</p>
                  </td>
                  <td className="px-4 py-3 text-center font-semibold text-slate-700">{rule.priority}</td>
                  <td className="px-4 py-3 text-center">
                    <Badge tone={rule.is_active ? "green" : "slate"}>
                      {rule.is_active ? "Đang bật" : "Đang tắt"}
                    </Badge>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex justify-end gap-2">
                      <Button onClick={() => toggleActive(rule)}>
                        {rule.is_active ? "⏸ Tắt" : "▶ Bật"}
                      </Button>
                      <Button onClick={() => remove(rule)} variant="danger">
                        🗑 Xóa
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
