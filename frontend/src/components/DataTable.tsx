import {
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  useReactTable,
  type ColumnDef,
  type SortingState,
} from "@tanstack/react-table";
import { Fragment, useState, type ReactNode } from "react";

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

  // Minimum width of the inner table; wide tables scroll horizontally.
  tableClassName?: string;

  // The rounded frame + border belongs to standalone tables. Inside a card
  // that already draws its own frame, pass false: otherwise the blue header
  // gets its own 10px radius inside the card and a seam is visible.
  bordered?: boolean;
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
  tableClassName = "min-w-[850px]",
  bordered = true,
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
        <p className="text-sm text-muted">{loadingText}</p>
      </div>
    );
  }

  return (
    <div
      className={`${bordered ? "ui-tw" : ""} min-h-0 flex-1 overflow-auto ${className}`}
    >
      <table className={`w-full text-sm ${tableClassName}`}>
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
                    className="border-b border-weber-blue px-3 py-2 text-[11.5px] font-semibold"
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
                            : "",
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
          {table.getRowModel().rows.map((row) => {
            const selected = selectedRowId === row.id;

            return (
              <Fragment key={row.id}>
                <tr
                  onClick={() => onRowClick?.(row.original)}
                  className={[
                    "border-b border-soft last:border-0",
                    onRowClick ? "cursor-pointer" : "",
                    selected ? "bg-chip-1" : "bg-white",
                    "hover:bg-canvas",
                  ].join(" ")}
                >
                  {row.getVisibleCells().map((cell) => (
                    <td
                      key={cell.id}
                      className="px-3 py-2"
                    >
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext(),
                      )}
                    </td>
                  ))}
                </tr>

                {selected && renderExpandedRow && (
                  <tr className="border-b border-soft bg-canvas">
                    <td
                      colSpan={row.getVisibleCells().length}
                      className="px-3 py-3"
                    >
                      {renderExpandedRow(row.original)}
                    </td>
                  </tr>
                )}
              </Fragment>
            );
          })}

          {data.length === 0 && (
            <tr>
              <td
                colSpan={columns.length}
                className="px-3 py-8 text-center text-muted"
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
