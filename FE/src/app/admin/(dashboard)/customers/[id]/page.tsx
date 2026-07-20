"use client";

/** Chi tiết khách hàng (P2): hồ sơ, hội thoại, lịch sử mua, ghi chú, phân công. */

import Link from "next/link";
import { FormEvent, use, useEffect, useState } from "react";

import { Badge, Button, Card, EmptyState, Field, PageHeader, Select, TextArea } from "@/components/admin/ui";
import { ChatMarkdown } from "@/components/chat-markdown";
import { adminFetch, hasPermission, MeInfo } from "@/lib/auth";
import {
  formatDate,
  formatDateOnly,
  formatVnd,
  metaOf,
  purchaseStatusMeta,
  purposeMeta,
  sourceMeta,
  statusMeta,
  temperatureMeta,
  typeMeta,
} from "@/lib/crm-labels";

type UserBrief = { id: number; full_name: string };
type SubdivisionBrief = { id: number; slug: string; name: string };
type Note = { id: number; content: string; created_at: string; author: UserBrief | null };
type Purchase = {
  id: number;
  subdivision: SubdivisionBrief;
  unit_type: string;
  purchase_date: string;
  price: number;
  responsible_sale: UserBrief | null;
  status: string;
  note: string | null;
};
type Message = { id: number; role: string; content: string; created_at: string };
type ConversationSummary = {
  id: number;
  session_id: string;
  user_message_count: number;
  is_lead_captured: boolean;
  started_at: string;
  last_message_at: string;
};
type ConversationDetail = ConversationSummary & { messages: Message[] };
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
  budget_min: number | null;
  budget_max: number | null;
  purpose: string;
  needs_summary: string | null;
  assigned_sale: UserBrief | null;
  source: string;
  created_at: string;
  notes: Note[];
  purchases: Purchase[];
};

export default function CustomerDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id: customerId } = use(params);
  const [me, setMe] = useState<MeInfo | null>(null);
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [selectedConversation, setSelectedConversation] = useState<ConversationDetail | null>(null);
  const [sales, setSales] = useState<UserBrief[]>([]);
  const [loading, setLoading] = useState(true);

  async function loadCustomer() {
    const response = await adminFetch(`/customers/${customerId}`);
    if (response.ok) setCustomer(await response.json());
  }

  async function loadConversations(openFirst = false) {
    const response = await adminFetch(`/customers/${customerId}/conversations`);
    if (!response.ok) return;
    const payload: ConversationSummary[] = await response.json();
    setConversations(payload);
    if (openFirst && payload.length > 0) openConversation(payload[0]);
  }

  async function openConversation(conversation: ConversationSummary) {
    const response = await adminFetch(`/customers/${customerId}/conversations/${conversation.id}`);
    if (response.ok) setSelectedConversation(await response.json());
  }

  async function updateCustomer(patch: Record<string, unknown>) {
    const response = await adminFetch(`/customers/${customerId}`, {
      method: "PATCH",
      body: JSON.stringify(patch),
    });
    if (response.ok) loadCustomer();
  }

  async function assignSale(saleId: number | null) {
    const response = await adminFetch(`/customers/${customerId}/assign`, {
      method: "POST",
      body: JSON.stringify({ sale_id: saleId }),
    });
    if (response.ok) loadCustomer();
  }

  async function addNote(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const content = String(new FormData(form).get("content") || "");
    const response = await adminFetch(`/customers/${customerId}/notes`, {
      method: "POST",
      body: JSON.stringify({ content }),
    });
    if (response.ok) {
      form?.reset();
      loadCustomer();
    }
  }

  useEffect(() => {
    adminFetch("/auth/me")
      .then((r) => (r.ok ? r.json() : null))
      .then((meInfo: MeInfo | null) => {
        setMe(meInfo);
        if (meInfo && hasPermission(meInfo, "sales.manage")) {
          adminFetch("/sales")
            .then((r) => (r.ok ? r.json() : []))
            .then((list: (UserBrief & { role: string })[]) =>
              setSales(list.filter((s) => s.role === "sale"))
            );
        }
      });
    Promise.all([loadCustomer(), loadConversations(true)]).finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [customerId]);

  if (loading) return <p className="text-sm text-slate-500">Đang tải thông tin khách hàng...</p>;

  if (!customer) {
    return (
      <section>
        <Link className="text-sm font-semibold text-cyan-600" href="/admin/customers">
          ← Quay lại danh sách khách hàng
        </Link>
        <div className="mt-4">
          <EmptyState>Không tìm thấy khách hàng.</EmptyState>
        </div>
      </section>
    );
  }

  const canEdit = hasPermission(me, "customer.edit");
  const canAssign = hasPermission(me, "customer.assign");
  const typeInfo = metaOf(typeMeta, customer.customer_type);
  const temperatureInfo = metaOf(temperatureMeta, customer.temperature);
  const sourceInfo = metaOf(sourceMeta, customer.source);

  return (
    <section>
      <Link className="text-sm font-semibold text-cyan-600 transition hover:text-cyan-500" href="/admin/customers">
        ← Khách hàng
      </Link>

      <PageHeader
        kicker={`Khách hàng #${customer.id}`}
        title={customer.full_name || "Khách chưa cung cấp tên"}
        description={customer.needs_summary || "Chưa có tóm tắt nhu cầu."}
      />

      {/* Hồ sơ nhanh */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Card title="Liên hệ">
          <a className="text-lg font-bold text-cyan-600" href={`tel:${customer.phone}`}>
            {customer.phone}
          </a>
          <p className="mt-1 text-sm text-slate-500">{customer.email || "Chưa có email"}</p>
          <div className="mt-2">
            <Badge tone={sourceInfo.tone}>Nguồn: {sourceInfo.label}</Badge>
          </div>
        </Card>

        <Card title="Đánh giá của AI">
          <div className="flex flex-wrap items-center gap-2">
            <Badge tone={typeInfo.tone}>{typeInfo.label}</Badge>
            <Badge tone={temperatureInfo.tone}>{temperatureInfo.label}</Badge>
          </div>
          <p className="mt-2 text-sm text-slate-600">
            Điểm quan tâm:{" "}
            <b className="text-slate-900">
              {customer.lead_score != null ? `${customer.lead_score}/100` : "Chưa chấm"}
            </b>
          </p>
        </Card>

        <Card title="Nhu cầu">
          <p className="text-sm text-slate-700">
            <b>{customer.interested_subdivision?.name ?? "Chưa rõ phân khu"}</b>
            {customer.preferred_unit_type ? ` · ${customer.preferred_unit_type}` : ""}
          </p>
          <p className="mt-1 text-sm text-slate-500">
            {metaOf(purposeMeta, customer.purpose).label} · Ngân sách{" "}
            {customer.budget_min || customer.budget_max
              ? `${formatVnd(customer.budget_min)} – ${formatVnd(customer.budget_max)}`
              : "chưa rõ"}
          </p>
        </Card>

        <Card title="Chăm sóc">
          {canEdit ? (
            <Field label="Trạng thái">
              <Select onChange={(e) => updateCustomer({ status: e.target.value })} value={customer.status}>
                {Object.entries(statusMeta).map(([value, meta]) => (
                  <option key={value} value={value}>
                    {meta.label}
                  </option>
                ))}
              </Select>
            </Field>
          ) : (
            <p className="text-sm">
              Trạng thái: <Badge tone={metaOf(statusMeta, customer.status).tone}>{metaOf(statusMeta, customer.status).label}</Badge>
            </p>
          )}
          {canAssign && sales.length > 0 ? (
            <Field className="mt-3" label="Sale phụ trách">
              <Select
                onChange={(e) => assignSale(e.target.value ? Number(e.target.value) : null)}
                value={customer.assigned_sale?.id ?? ""}
              >
                <option value="">Chưa phân công</option>
                {sales.map((sale) => (
                  <option key={sale.id} value={sale.id}>
                    {sale.full_name}
                  </option>
                ))}
              </Select>
            </Field>
          ) : (
            <p className="mt-3 text-sm text-slate-600">
              Sale phụ trách: <b>{customer.assigned_sale?.full_name ?? "Chưa phân công"}</b>
            </p>
          )}
        </Card>
      </div>

      {/* Hội thoại */}
      <div className="mt-6 grid gap-4 lg:grid-cols-[300px_1fr]">
        <Card subtitle={`${conversations.length} phiên`} title="Phiên chat">
          {conversations.length === 0 ? (
            <EmptyState>Chưa xem được phiên chat (cần quyền “Xem đoạn chat”).</EmptyState>
          ) : (
            <div className="space-y-2">
              {conversations.map((conversation) => (
                <button
                  className={`w-full rounded-lg border px-3 py-2.5 text-left text-sm transition ${
                    selectedConversation?.id === conversation.id
                      ? "border-cyan-400 bg-cyan-50"
                      : "border-slate-200 hover:border-cyan-300"
                  }`}
                  key={conversation.id}
                  onClick={() => openConversation(conversation)}
                  type="button"
                >
                  <p className="font-semibold text-slate-900">Phiên #{conversation.id}</p>
                  <p className="text-xs text-slate-500">{formatDate(conversation.last_message_at)}</p>
                  <p className="mt-1 text-xs text-slate-600">{conversation.user_message_count} tin của khách</p>
                </button>
              ))}
            </div>
          )}
        </Card>

        <Card
          subtitle={selectedConversation ? `Bắt đầu ${formatDate(selectedConversation.started_at)}` : undefined}
          title={selectedConversation ? `Nội dung hội thoại — Phiên #${selectedConversation.id}` : "Nội dung hội thoại"}
        >
          {selectedConversation ? (
            <div className="max-h-[420px] space-y-3 overflow-y-auto pr-1">
              {selectedConversation.messages.map((message) =>
                message.role === "user" ? (
                  <div
                    className="ml-auto max-w-[80%] rounded-2xl rounded-br-sm bg-cyan-500/90 px-3.5 py-2.5 text-sm text-white"
                    key={message.id}
                  >
                    <p className="mb-1 text-[11px] font-bold uppercase tracking-wide opacity-70">Khách hàng</p>
                    <p className="whitespace-pre-wrap">{message.content}</p>
                    <p className="mt-1 text-right text-[10px] opacity-60">{formatDate(message.created_at)}</p>
                  </div>
                ) : (
                  <div className="mr-auto flex max-w-[85%] items-start gap-2" key={message.id}>
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      alt="Trợ lý AI"
                      className="mt-1 h-7 w-7 shrink-0 rounded-full object-cover ring-1 ring-slate-200"
                      src="/media_files/advisor-avatar.jpg"
                    />
                    <div className="rounded-2xl rounded-bl-sm bg-slate-100 px-3.5 py-2.5 text-slate-800">
                      <p className="mb-1 text-[11px] font-bold uppercase tracking-wide opacity-70">Trợ lý AI</p>
                      <ChatMarkdown content={message.content} />
                      <p className="mt-1 text-right text-[10px] opacity-60">{formatDate(message.created_at)}</p>
                    </div>
                  </div>
                )
              )}
            </div>
          ) : (
            <EmptyState>Chọn một phiên chat để xem nội dung.</EmptyState>
          )}
        </Card>
      </div>

      {/* Lịch sử mua nhà */}
      <div className="mt-6">
        <Card subtitle="Phân khu, loại căn, thời gian, giá và Sale phụ trách giao dịch" title="Lịch sử mua nhà">
          {customer.purchases.length === 0 ? (
            <EmptyState>Chưa có giao dịch nào.</EmptyState>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-slate-950 text-xs uppercase tracking-wide text-slate-300">
                  <tr>
                    <th className="rounded-l-lg px-4 py-2.5">Phân khu</th>
                    <th className="px-4 py-2.5">Loại căn</th>
                    <th className="px-4 py-2.5">Ngày mua</th>
                    <th className="px-4 py-2.5">Giá</th>
                    <th className="px-4 py-2.5">Sale phụ trách</th>
                    <th className="rounded-r-lg px-4 py-2.5">Trạng thái</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {customer.purchases.map((purchase) => {
                    const purchaseStatus = metaOf(purchaseStatusMeta, purchase.status);
                    return (
                      <tr className="hover:bg-cyan-50/60" key={purchase.id}>
                        <td className="px-4 py-3 font-semibold text-slate-900">{purchase.subdivision.name}</td>
                        <td className="px-4 py-3">{purchase.unit_type}</td>
                        <td className="px-4 py-3">{formatDateOnly(purchase.purchase_date)}</td>
                        <td className="px-4 py-3 font-semibold">{formatVnd(purchase.price)}</td>
                        <td className="px-4 py-3">{purchase.responsible_sale?.full_name ?? "—"}</td>
                        <td className="px-4 py-3">
                          <Badge tone={purchaseStatus.tone}>{purchaseStatus.label}</Badge>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      </div>

      {/* Ghi chú CRM */}
      <div className="mt-6">
        <Card subtitle="Lịch sử chăm sóc của đội Sale" title="Ghi chú CRM">
          <div className="space-y-3">
            {customer.notes.map((note) => (
              <div className="rounded-lg border border-slate-200 bg-slate-50 px-4 py-3" key={note.id}>
                <p className="text-sm text-slate-800">{note.content}</p>
                <p className="mt-1 text-xs text-slate-500">
                  {note.author?.full_name ?? "Hệ thống"} · {formatDate(note.created_at)}
                </p>
              </div>
            ))}
          </div>
          <form className="mt-4 space-y-2" onSubmit={addNote}>
            <TextArea name="content" placeholder="Ghi chú sau cuộc gọi, hẹn xem nhà..." required rows={2} />
            <Button type="submit" variant="primary">
              Thêm ghi chú
            </Button>
          </form>
        </Card>
      </div>
    </section>
  );
}
