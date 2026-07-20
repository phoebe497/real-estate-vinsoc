"""Seed danh mục chức năng (permissions) cho menu Phân quyền.

Admin mặc định có toàn quyền (không cần cấp). Sale nhận quyền qua bảng
user_permissions. Thêm quyền mới = thêm vào danh sách này; seeder upsert
theo `code` nên chạy lại an toàn ở mọi môi trường.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.entities import Permission

DEFAULT_PERMISSIONS: list[dict[str, str]] = [
    {"code": "customer.view_all", "name": "Xem tất cả khách", "group_name": "Khách hàng"},
    {"code": "customer.edit", "name": "Sửa khách", "group_name": "Khách hàng"},
    {"code": "customer.assign", "name": "Phân công khách", "group_name": "Khách hàng"},
    {"code": "customer.view_chat", "name": "Xem đoạn chat", "group_name": "Khách hàng"},
    {"code": "dashboard.view", "name": "Xem thống kê", "group_name": "Thống kê"},
    {"code": "sales.manage", "name": "Quản lý sale", "group_name": "Sale"},
    {"code": "permissions.manage", "name": "Quản lý phân quyền", "group_name": "Hệ thống"},
    {"code": "fallback.manage", "name": "Quản lý fallback rules", "group_name": "Hệ thống"},
    {"code": "report.export", "name": "Xuất báo cáo", "group_name": "Thống kê"},
]


def seed_permissions(session: Session) -> int:
    """Upsert danh mục quyền; trả về số quyền được thêm mới."""
    created = 0
    for item in DEFAULT_PERMISSIONS:
        permission = session.scalar(select(Permission).where(Permission.code == item["code"]))
        if permission is None:
            session.add(Permission(**item))
            created += 1
        else:
            permission.name = item["name"]
            permission.group_name = item["group_name"]
    session.commit()
    return created
