import {
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  useReactTable,
  type ColumnDef,
  type SortingState,
} from "@tanstack/react-table";
import { useState, type ReactNode } from "react";

type DataTableProps<TData> = {
  data: TData[];
  columns: ColumnDef<TData, any>[];
  loading?: boolean;
  loadingText?: ReactNode;
  emptyText?: ReactNode;

  onRowClick?: (row: TData) => void;

  getRowId?: (row: TData) => string;

  selectedRowId?: string | null;

  renderExpandedRow?: (row: TData) => ReactNode;

  className?: string;
};

export default function DataTable<TData>({
  data,
  columns,
  loading = false,
  loadingText = "Loading...",
  emptyText = "—",
  onRowClick,
  getRowId,
  selectedRowId,
  renderExpandedRow,
  className = "",
}: DataTableProps<TData>) {
  const [sorting, setSorting] = useState<SortingState>([]);

  const table = useReactTable({
    data,
    columns,
    state: {
      sorting,
    },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getRowId,
  });

  if (loading) {
    return (
      <div
        className={`flex min-h-0 flex-1 items-center justify-center ${className}`}
      >
        <p className="text-sm text-gray-500">{loadingText}</p>
      </div>
    );
  }

  return (
    <div
      className={`min-h-0 flex-1 overflow-auto border ${className}`}
    >
      <table className="w-full min-w-[850px] text-sm">
        <thead className="sticky top-0 z-10">
          {table.getHeaderGroups().map((headerGroup) => (
            <tr
              key={headerGroup.id}
              className="bg-weber-blue text-left text-white"
            >
              {headerGroup.headers.map((header) => {
                const canSort = header.column.getCanSort();
                const sorted = header.column.getIsSorted();

                return (
                  <th
                    key={header.id}
                    className="px-3 py-1.5 font-semibold"
                  >
                    {header.isPlaceholder ? null : (
                      <button
                        type="button"
                        disabled={!canSort}
                        onClick={header.column.getToggleSortingHandler()}
                        className={[
                          "flex items-center gap-1",
                          canSort
                            ? "cursor-pointer select-none hover:opacity-80"
                            : "cursor-default",
                        ].join(" ")}
                      >
                        {flexRender(
                          header.column.columnDef.header,
                          header.getContext(),
                        )}

                        {sorted === "asc" && <span>↑</span>}
                        {sorted === "desc" && <span>↓</span>}
                      </button>
                    )}
                  </th>
                );
              })}
            </tr>
          ))}
        </thead>

        <tbody>
          {table.getRowModel().rows.map((row, index) => {
            const selected = selectedRowId === row.id;

            return (
              <>
                <tr
                  key={row.id}
                  onClick={() => onRowClick?.(row.original)}
                  className={[
                    "border-b last:border-0",
                    onRowClick ? "cursor-pointer" : "",
                    selected
                      ? "bg-blue-100"
                      : index % 2
                        ? "bg-gray-50"
                        : "bg-white",
                    "hover:bg-blue-50",
                  ].join(" ")}
                >
                  {row.getVisibleCells().map((cell) => (
                    <td
                      key={cell.id}
                      className="px-3 py-1.5"
                    >
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext(),
                      )}
                    </td>
                  ))}
                </tr>

                {selected && renderExpandedRow && (
                  <tr className="border-b bg-blue-50/40">
                    <td
                      colSpan={row.getVisibleCells().length}
                      className="px-3 py-3"
                    >
                      {renderExpandedRow(row.original)}
                    </td>
                  </tr>
                )}
              </>
            );
          })}

          {data.length === 0 && (
            <tr>
              <td
                colSpan={columns.length}
                className="px-3 py-8 text-center text-gray-400"
              >
                {emptyText}
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}