"use client";

/**
 * Chat Widget V2 — BAN_THIET_KE_V2 Mục 9.1.
 *
 * - Bubble góc phải dưới trên mọi trang public (ẩn ở /admin).
 * - Khách chat ẩn danh qua session_id (localStorage).
 * - Nút "Tạo đơn tư vấn" luôn hiển thị; khi backend trả require_lead_capture=true
 *   → tự bung form và khóa ô nhập cho tới khi submit thành công.
 */

import { usePathname } from "next/navigation";
import { FormEvent, useEffect, useRef, useState } from "react";

import { ChatMarkdown } from "@/components/chat-markdown";
import { API_URL } from "@/lib/api";
import type { SubdivisionSummary } from "@/lib/types";

const ADVISOR_AVATAR = "/media_files/advisor-avatar.jpg";

const AGENT_URL = API_URL.replace(/\/api\/v1$/, "");
const SESSION_KEY = "op_chat_session_id";
const MESSAGES_KEY = "op_chat_messages";
const CAPTURED_KEY = "op_chat_captured";

type ChatMessage = { role: "user" | "ai"; content: string };

type ChatApiResponse = {
  response: string;
  reply?: string;
  require_lead_capture?: boolean;
  trigger_handover?: boolean;
  session_id: string;
};

const QUICK_ACTIONS = [
  "Tư vấn căn 2PN khoảng 3-4 tỷ",
  "So sánh The Zenpark và The Sapphire",
  "Phân khu nào phù hợp gia đình có con nhỏ?",
];

const BUDGET_OPTIONS = [
  { label: "Chưa xác định", min: null, max: null },
  { label: "Dưới 2 tỷ", min: null, max: 2_000_000_000 },
  { label: "2 - 3 tỷ", min: 2_000_000_000, max: 3_000_000_000 },
  { label: "3 - 5 tỷ", min: 3_000_000_000, max: 5_000_000_000 },
  { label: "Trên 5 tỷ", min: 5_000_000_000, max: null },
];

const UNIT_TYPES = ["", "Studio", "1PN", "1PN+1", "2PN", "2PN+1", "3PN", "Duplex", "Penthouse"];

function newSessionId() {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) return crypto.randomUUID();
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export function ChatWidget() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [locked, setLocked] = useState(false);
  const [captured, setCaptured] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [subdivisions, setSubdivisions] = useState<SubdivisionSummary[]>([]);
  const [formError, setFormError] = useState("");
  const [formSubmitting, setFormSubmitting] = useState(false);
  const sessionRef = useRef<string>("");
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let sessionId = localStorage.getItem(SESSION_KEY);
    if (!sessionId) {
      sessionId = newSessionId();
      localStorage.setItem(SESSION_KEY, sessionId);
    }
    sessionRef.current = sessionId;
    try {
      const stored = localStorage.getItem(MESSAGES_KEY);
      if (stored) setMessages(JSON.parse(stored));
    } catch {
      /* bỏ qua dữ liệu hỏng */
    }
    const captureState = localStorage.getItem(CAPTURED_KEY);
    setLocked(captureState === "locked");
    setCaptured(captureState === "captured");
  }, []);

  useEffect(() => {
    if (messages.length) localStorage.setItem(MESSAGES_KEY, JSON.stringify(messages));
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight });
  }, [messages, open, showForm]);

  useEffect(() => {
    if (open && subdivisions.length === 0) {
      fetch(`${API_URL}/subdivisions`)
        .then((r) => (r.ok ? r.json() : []))
        .then(setSubdivisions)
        .catch(() => setSubdivisions([]));
    }
  }, [open, subdivisions.length]);

  if (pathname?.startsWith("/admin")) return null;

  async function send(text: string) {
    const content = text.trim();
    if (!content || sending || locked) return;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content }]);
    setSending(true);
    try {
      const response = await fetch(`${AGENT_URL}/agent/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionRef.current,
          messages: [{ role: "user", content }],
        }),
      });
      const data: ChatApiResponse = await response.json();
      setMessages((prev) => [...prev, { role: "ai", content: data.reply || data.response }]);
      if (data.require_lead_capture && !captured) {
        // Bị chặn vì chưa để lại thông tin → bắt buộc bung form + khóa chat.
        setLocked(true);
        setShowForm(true);
        localStorage.setItem(CAPTURED_KEY, "locked");
      } else if (data.trigger_handover && !captured) {
        // Chỉ tự mở form khi khách CHƯA tạo đơn. Đã có thông tin rồi thì
        // không làm phiền lại — khách có thể tự bấm "Tạo đơn tư vấn" nếu muốn.
        setShowForm(true);
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "ai", content: "Xin lỗi, hệ thống đang gián đoạn. Anh/Chị vui lòng thử lại sau ít phút." },
      ]);
    } finally {
      setSending(false);
    }
  }

  async function submitCapture(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFormError("");
    const form = new FormData(event.currentTarget);
    const fullName = String(form.get("full_name") || "").trim();
    const phone = String(form.get("phone") || "").trim();
    if (!fullName || !phone) {
      setFormError("Vui lòng nhập họ tên và số điện thoại.");
      return;
    }
    const budget = BUDGET_OPTIONS[Number(form.get("budget") || 0)] ?? BUDGET_OPTIONS[0];
    const payload: Record<string, unknown> = {
      full_name: fullName,
      phone,
      session_id: sessionRef.current,
      consent_contact: form.get("consent") === "on",
      purpose: String(form.get("purpose") || "unknown"),
    };
    const email = String(form.get("email") || "").trim();
    if (email) payload.email = email;
    const subdivision = String(form.get("subdivision") || "");
    if (subdivision) payload.interested_subdivision_slug = subdivision;
    const unitType = String(form.get("unit_type") || "");
    if (unitType) payload.preferred_unit_type = unitType;
    if (budget.min) payload.budget_min = budget.min;
    if (budget.max) payload.budget_max = budget.max;
    const contactTime = String(form.get("contact_time") || "").trim();
    if (contactTime) payload.contact_time = contactTime;
    const note = String(form.get("note") || "").trim();
    if (note) payload.note = note;

    setFormSubmitting(true);
    try {
      const response = await fetch(`${API_URL}/customers/capture`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        const detail = await response.json().catch(() => null);
        setFormError(
          Array.isArray(detail?.detail)
            ? "Số điện thoại chưa đúng định dạng Việt Nam."
            : detail?.detail || "Không gửi được thông tin. Vui lòng thử lại."
        );
        return;
      }
      setLocked(false);
      setShowForm(false);
      setCaptured(true);
      localStorage.setItem(CAPTURED_KEY, "captured");
      setMessages((prev) => [
        ...prev,
        {
          role: "ai",
          content:
            "Cảm ơn Anh/Chị đã để lại thông tin! Sales phụ trách sẽ liên hệ sớm nhất. Anh/Chị có thể tiếp tục đặt câu hỏi cho em ngay tại đây ạ.",
        },
      ]);
    } catch {
      setFormError("Không gửi được thông tin. Vui lòng thử lại.");
    } finally {
      setFormSubmitting(false);
    }
  }

  return (
    <>
      {/* Bubble — avatar trợ lý */}
      <button
        aria-label={open ? "Đóng chat" : "Chat với AI tư vấn"}
        className="fixed bottom-5 right-5 z-50 flex h-16 w-16 items-center justify-center overflow-hidden rounded-full shadow-xl ring-2 ring-cyan-400/70 transition hover:scale-105"
        onClick={() => setOpen((v) => !v)}
        type="button"
      >
        {open ? (
          <span className="flex h-full w-full items-center justify-center bg-slate-900 text-2xl text-cyan-300">✕</span>
        ) : (
          // eslint-disable-next-line @next/next/no-img-element
          <img alt="Trợ lý AI Ocean Park" className="h-full w-full object-cover" src={ADVISOR_AVATAR} />
        )}
      </button>

      {open ? (
        <div className="fixed bottom-24 right-5 z-50 flex h-[900px] max-h-[calc(100vh-120px)] w-[660px] max-w-[calc(100vw-40px)] flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-2xl">
          {/* Header — avatar + tên trợ lý */}
          <div className="flex items-center justify-between bg-slate-900 px-4 py-3 text-white">
            <div className="flex items-center gap-3">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                alt="Trợ lý AI"
                className="h-10 w-10 rounded-full object-cover ring-2 ring-cyan-400/60"
                src={ADVISOR_AVATAR}
              />
              <div>
                <strong className="block text-sm">Trợ lý AI Ocean Park</strong>
                <span className="flex items-center gap-1.5 text-xs text-slate-300">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                  Vinhomes Ocean Park 1 · Gia Lâm
                </span>
              </div>
            </div>
            <button
              className="rounded border border-cyan-400/60 px-3 py-1.5 text-xs font-semibold text-cyan-300 transition hover:bg-cyan-400 hover:text-slate-900"
              onClick={() => setShowForm((v) => !v)}
              type="button"
            >
              Tạo đơn tư vấn
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 space-y-3 overflow-y-auto bg-slate-50 p-4" ref={scrollRef}>
            {messages.length === 0 ? (
              <div className="space-y-3">
                <div className="flex items-start gap-2">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    alt="Trợ lý AI"
                    className="mt-1 h-7 w-7 shrink-0 rounded-full object-cover ring-1 ring-slate-200"
                    src={ADVISOR_AVATAR}
                  />
                  <p className="rounded-2xl rounded-bl-sm border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700 shadow-sm">
                    Chào Anh/Chị! Em là trợ lý AI của <b>Vinhomes Ocean Park 1</b>. Anh/Chị cần tư vấn
                    phân khu, loại căn hay khoảng giá nào ạ?
                  </p>
                </div>
                <div className="space-y-2 pl-9">
                  {QUICK_ACTIONS.map((action) => (
                    <button
                      className="block w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-left text-sm text-slate-700 transition hover:border-cyan-400 hover:text-cyan-700"
                      key={action}
                      onClick={() => send(action)}
                      type="button"
                    >
                      {action}
                    </button>
                  ))}
                </div>
              </div>
            ) : null}
            {messages.map((message, index) =>
              message.role === "user" ? (
                <div
                  className="ml-auto max-w-[80%] whitespace-pre-wrap rounded-2xl rounded-br-sm bg-cyan-500 px-4 py-2.5 text-sm text-white shadow-sm"
                  key={index}
                >
                  {message.content}
                </div>
              ) : (
                <div className="mr-auto flex max-w-[88%] items-start gap-2" key={index}>
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    alt="AI"
                    className="mt-1 h-7 w-7 shrink-0 rounded-full object-cover ring-1 ring-slate-200"
                    src={ADVISOR_AVATAR}
                  />
                  <div className="rounded-2xl rounded-bl-sm border border-slate-200 bg-white px-4 py-3 text-slate-800 shadow-sm">
                    <ChatMarkdown content={message.content} />
                  </div>
                </div>
              )
            )}
            {sending ? (
              <div className="mr-auto flex items-center gap-2">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  alt="AI"
                  className="h-7 w-7 rounded-full object-cover ring-1 ring-slate-200"
                  src={ADVISOR_AVATAR}
                />
                <span className="rounded-2xl border border-slate-200 bg-white px-4 py-2.5 text-xs text-slate-400">
                  Đang soạn câu trả lời…
                </span>
              </div>
            ) : null}
          </div>

          {/* Lead capture form */}
          {showForm ? (
            <form className="max-h-[480px] space-y-2 overflow-y-auto border-t border-slate-200 bg-white p-3" onSubmit={submitCapture}>
              <p className="text-xs font-semibold text-slate-700">
                {locked
                  ? "Anh/Chị vui lòng để lại thông tin để tiếp tục được tư vấn:"
                  : "Để lại thông tin để Sales hỗ trợ nhanh nhất:"}
              </p>
              <div className="grid grid-cols-2 gap-2">
                <input className="form-input !py-2 text-sm" name="full_name" placeholder="Họ tên *" required />
                <input className="form-input !py-2 text-sm" name="phone" placeholder="Số điện thoại *" required />
              </div>
              <input className="form-input !py-2 text-sm" name="email" placeholder="Email (tuỳ chọn)" type="email" />
              <div className="grid grid-cols-2 gap-2">
                <select className="form-input !py-2 text-sm" defaultValue="" name="subdivision">
                  <option value="">Phân khu quan tâm</option>
                  {subdivisions.map((s) => (
                    <option key={s.slug} value={s.slug}>
                      {s.name}
                    </option>
                  ))}
                </select>
                <select className="form-input !py-2 text-sm" defaultValue="" name="unit_type">
                  {UNIT_TYPES.map((t) => (
                    <option key={t} value={t}>
                      {t || "Loại căn hộ"}
                    </option>
                  ))}
                </select>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <select className="form-input !py-2 text-sm" defaultValue={0} name="budget">
                  {BUDGET_OPTIONS.map((b, i) => (
                    <option key={b.label} value={i}>
                      {b.label}
                    </option>
                  ))}
                </select>
                <select className="form-input !py-2 text-sm" defaultValue="unknown" name="purpose">
                  <option value="unknown">Mục đích</option>
                  <option value="to_live">Mua để ở</option>
                  <option value="to_invest">Đầu tư</option>
                </select>
              </div>
              <input className="form-input !py-2 text-sm" name="contact_time" placeholder="Thời gian tiện liên hệ (tuỳ chọn)" />
              <textarea className="form-input !py-2 text-sm" name="note" placeholder="Ghi chú (tuỳ chọn)" rows={2} />
              <label className="flex items-center gap-2 text-xs text-slate-600">
                <input defaultChecked name="consent" type="checkbox" />
                Tôi đồng ý để Vinhomes Ocean Park liên hệ tư vấn.
              </label>
              {formError ? <p className="text-xs text-red-600">{formError}</p> : null}
              <div className="flex gap-2">
                <button className="btn-primary flex-1 !py-2 text-sm" disabled={formSubmitting} type="submit">
                  {formSubmitting ? "Đang gửi…" : "Gửi thông tin"}
                </button>
                {!locked ? (
                  <button
                    className="rounded border border-slate-300 px-3 text-sm text-slate-600"
                    onClick={() => setShowForm(false)}
                    type="button"
                  >
                    Đóng
                  </button>
                ) : null}
              </div>
            </form>
          ) : null}

          {/* Input */}
          <form
            className="flex gap-2 border-t border-slate-200 bg-white p-3"
            onSubmit={(e) => {
              e.preventDefault();
              send(input);
            }}
          >
            <input
              className="form-input !py-2 text-sm disabled:bg-slate-100"
              disabled={locked || sending}
              onChange={(e) => setInput(e.target.value)}
              placeholder={locked ? "Vui lòng gửi thông tin ở form phía trên…" : "Nhập câu hỏi…"}
              value={input}
            />
            <button
              className="rounded-lg bg-cyan-500 px-5 text-sm font-bold text-slate-950 transition hover:bg-cyan-400 disabled:opacity-50"
              disabled={locked || sending || !input.trim()}
              type="submit"
            >
              Gửi
            </button>
          </form>
        </div>
      ) : null}
    </>
  );
}
