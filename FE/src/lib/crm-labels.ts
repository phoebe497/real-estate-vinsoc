/**
 * Dictionary label tiếng Việt cho toàn bộ field CRM (P2).
 *
 * Quy tắc: KHÔNG hiển thị tên field kỹ thuật (snake_case/enum nội bộ) ra UI —
 * mọi giá trị enum đi qua các map này; thêm field mới = thêm vào đây,
 * không hard-code rải rác trong component.
 */

export type BadgeTone = "slate" | "cyan" | "green" | "amber" | "red" | "violet" | "blue";

type LabeledValue = { label: string; tone: BadgeTone };

// ── Trạng thái pipeline CRM ──────────────────────────────────────────────────
export const statusMeta: Record<string, LabeledValue> = {
  new: { label: "Mới", tone: "cyan" },
  contacted: { label: "Đã liên hệ", tone: "blue" },
  consulting: { label: "Đang tư vấn", tone: "violet" },
  visiting: { label: "Hẹn xem nhà", tone: "amber" },
  won: { label: "Đã chốt", tone: "green" },
  lost: { label: "Không phù hợp", tone: "slate" },
};

// ── Loại khách (AI phân loại) ────────────────────────────────────────────────
export const typeMeta: Record<string, LabeledValue> = {
  real_need: { label: "Nhu cầu thật", tone: "green" },
  investor: { label: "Đầu tư", tone: "violet" },
  ghost: { label: "Khách ảo", tone: "slate" },
  unknown: { label: "Chưa rõ", tone: "slate" },
};

// ── Nhiệt độ lead ────────────────────────────────────────────────────────────
export const temperatureMeta: Record<string, LabeledValue> = {
  hot: { label: "🔥 Nóng", tone: "red" },
  warm: { label: "Ấm", tone: "amber" },
  cold: { label: "Lạnh", tone: "blue" },
  unknown: { label: "—", tone: "slate" },
};

// ── Mục đích mua ─────────────────────────────────────────────────────────────
export const purposeMeta: Record<string, LabeledValue> = {
  to_live: { label: "Mua để ở", tone: "green" },
  to_invest: { label: "Đầu tư", tone: "violet" },
  unknown: { label: "Chưa rõ", tone: "slate" },
};

// ── Nguồn khách ──────────────────────────────────────────────────────────────
export const sourceMeta: Record<string, LabeledValue> = {
  chat: { label: "Chat AI", tone: "cyan" },
  contact_form: { label: "Form liên hệ", tone: "blue" },
  manual: { label: "Nhập tay", tone: "slate" },
};

// ── Trạng thái giao dịch mua nhà ─────────────────────────────────────────────
export const purchaseStatusMeta: Record<string, LabeledValue> = {
  deposit: { label: "Đặt cọc", tone: "amber" },
  contract: { label: "Đã ký HĐ", tone: "blue" },
  handed_over: { label: "Đã bàn giao", tone: "green" },
};

// ── Vai trò tài khoản nội bộ ─────────────────────────────────────────────────
export const roleMeta: Record<string, LabeledValue> = {
  admin: { label: "Quản trị", tone: "violet" },
  sale: { label: "Sale", tone: "cyan" },
};

// Backward-compatible plain-label maps (một số trang chỉ cần text)
export const statusLabels = Object.fromEntries(Object.entries(statusMeta).map(([k, v]) => [k, v.label]));
export const typeLabels = Object.fromEntries(Object.entries(typeMeta).map(([k, v]) => [k, v.label]));
export const temperatureLabels = Object.fromEntries(
  Object.entries(temperatureMeta).map(([k, v]) => [k, v.label])
);
export const purposeLabels = Object.fromEntries(Object.entries(purposeMeta).map(([k, v]) => [k, v.label]));
export const purchaseStatusLabels = Object.fromEntries(
  Object.entries(purchaseStatusMeta).map(([k, v]) => [k, v.label])
);

export function metaOf(map: Record<string, LabeledValue>, key: string | null | undefined): LabeledValue {
  return map[key ?? ""] ?? { label: key || "—", tone: "slate" };
}

export function formatVnd(value: number | null | undefined) {
  if (value == null) return "—";
  if (value >= 1_000_000_000) return `${(value / 1_000_000_000).toFixed(1).replace(/\.0$/, "")} tỷ`;
  if (value >= 1_000_000) return `${Math.round(value / 1_000_000)} triệu`;
  return value.toLocaleString("vi-VN");
}

export function formatDate(value?: string | null) {
  if (!value) return "—";
  return new Date(value).toLocaleString("vi-VN", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function formatDateOnly(value?: string | null) {
  if (!value) return "—";
  return new Date(value).toLocaleDateString("vi-VN");
}
