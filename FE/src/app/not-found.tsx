import Link from "next/link";

export default function NotFound() {
  return (
    <section className="empty-page">
      <span>404</span>
      <h1>Chưa tìm thấy phân khu</h1>
      <p>Dữ liệu có thể đang được đồng bộ hoặc đường dẫn chưa chính xác.</p>
      <Link className="primary-button" href="/phan-khu">
        Quay lại danh sách
      </Link>
    </section>
  );
}
