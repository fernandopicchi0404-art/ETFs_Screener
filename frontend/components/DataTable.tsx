"use client";

import { useRouter } from "next/navigation";

export interface Column<T> {
  key: string;
  label: string;
  sortable?: boolean;
  align?: "left" | "right";
  render?: (row: T) => React.ReactNode;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  rows: T[];
  sortBy?: string;
  sortDir?: "asc" | "desc";
  onSort?: (key: string) => void;
  rowHref?: (row: T) => string | null;
  emptyMessage?: string;
}

export default function DataTable<T extends object>({
  columns,
  rows,
  sortBy,
  sortDir = "asc",
  onSort,
  rowHref,
  emptyMessage = "Nenhum registro encontrado.",
}: DataTableProps<T>) {
  const router = useRouter();

  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="bg-slate-50 text-left text-slate-600">
            <tr>
              {columns.map((column) => (
                <th
                  key={column.key}
                  className={`px-4 py-3 font-medium ${column.align === "right" ? "text-right" : ""}`}
                >
                  {column.sortable && onSort ? (
                    <button
                      type="button"
                      onClick={() => onSort(column.key)}
                      className="inline-flex items-center gap-1 hover:text-brand-700"
                    >
                      {column.label}
                      {sortBy === column.key ? (
                        <span>{sortDir === "asc" ? "↑" : "↓"}</span>
                      ) : null}
                    </button>
                  ) : (
                    column.label
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="px-4 py-8 text-center text-slate-500">
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              rows.map((row, index) => {
                const href = rowHref?.(row);
                return (
                  <tr
                    key={index}
                    className={`border-t border-slate-100 ${href ? "cursor-pointer hover:bg-brand-50" : ""}`}
                    onClick={href ? () => router.push(href) : undefined}
                  >
                    {columns.map((column) => (
                      <td
                        key={column.key}
                        className={`px-4 py-3 text-slate-800 ${column.align === "right" ? "text-right" : ""}`}
                      >
                        {column.render
                          ? column.render(row)
                          : String((row as Record<string, unknown>)[column.key] ?? "—")}
                      </td>
                    ))}
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
