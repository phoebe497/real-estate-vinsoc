"use client";

/**
 * DataTable — wrapper TanStack Table theo thiết kế P2:
 * header nổi bật, hover từng dòng, padding thoáng, phân trang, sort client-side.
 */

import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  SortingState,
  useReactTable,
} from "@tanstack/react-table";
import { ReactNode, useState } from "react";

import { Button, EmptyState } from "./ui";

export function DataTable<T>({
  columns,
  data,
  loading = false,
  emptyMessage = "Chưa có dữ liệu.",
  pageSize = 15,
  onRowClick,
}: {
  columns: ColumnDef<T, unknown>[];
  data: T[];
  loading?: boolean;
  emptyMessage?: ReactNode;
  pageSize?: number;
  onRowClick?: (row: T) => void;
}) {
  const [sorting, setSorting] = useState<SortingState>([]);

  const table = useReactTable({
    data,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: { pagination: { pageSize } },
  });

  if (!loading && data.length === 0) {
    return <EmptyState>{emptyMessage}</EmptyState>;
  }

  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-left text-sm">
          <thead className="bg-slate-950 text-xs uppercase tracking-wide text-slate-300">
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <th
                    className={`px-4 py-3 font-semibold ${
                      header.column.getCanSort() ? "cursor-pointer select-none hover:text-cyan-300" : ""
                    }`}
                    key={header.id}
                    onClick={header.column.getToggleSortingHandler()}
                  >
                    <span className="inline-flex items-center gap-1">
                      {flexRender(header.column.columnDef.header, header.getContext())}
                      {{ asc: "▲", desc: "▼" }[header.column.getIsSorted() as string] ?? ""}
                    </span>
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody className="divide-y divide-slate-100">
            {loading ? (
              <tr>
                <td className="px-4 py-8 text-center text-slate-400" colSpan={columns.length}>
                  Đang tải dữ liệu...
                </td>
              </tr>
            ) : (
              table.getRowModel().rows.map((row) => (
                <tr
                  className={`transition hover:bg-cyan-50/60 ${onRowClick ? "cursor-pointer" : ""}`}
                  key={row.id}
                  onClick={onRowClick ? () => onRowClick(row.original) : undefined}
                >
                  {row.getVisibleCells().map((cell) => (
                    <td className="px-4 py-3 align-middle text-slate-700" key={cell.id}>
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {table.getPageCount() > 1 ? (
        <div className="flex items-center justify-between border-t border-slate-200 px-4 py-2.5 text-sm text-slate-500">
          <span>
            Trang {table.getState().pagination.pageIndex + 1} / {table.getPageCount()} ·{" "}
            {data.length} bản ghi
          </span>
          <div className="flex gap-2">
            <Button disabled={!table.getCanPreviousPage()} onClick={() => table.previousPage()}>
              ← Trước
            </Button>
            <Button disabled={!table.getCanNextPage()} onClick={() => table.nextPage()}>
              Sau →
            </Button>
          </div>
        </div>
      ) : null}
    </div>
  );
}
