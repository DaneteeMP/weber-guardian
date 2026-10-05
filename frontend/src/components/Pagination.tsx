type PaginationProps = {
  page: number;
  pageSize: number;
  total: number;
  onPageChange: (page: number) => void;
};

export default function Pagination({
  page,
  pageSize,
  total,
  onPageChange,
}: PaginationProps) {
  const start = total === 0 ? 0 : page * pageSize + 1;
  const end = Math.min((page + 1) * pageSize, total);

  const hasPrevious = page > 0;
  const hasNext = end < total;

  return (
    <div className="flex items-center justify-between text-sm">
      <button
        disabled={!hasPrevious}
        onClick={() => onPageChange(page - 1)}
        className="px-3 py-1.5 rounded bg-gray-200 hover:bg-gray-300 disabled:opacity-40"
      >
        ←
      </button>

      <span className="text-gray-500">
        {start}–{end} / {total.toLocaleString()}
      </span>

      <button
        disabled={!hasNext}
        onClick={() => onPageChange(page + 1)}
        className="px-3 py-1.5 rounded bg-gray-200 hover:bg-gray-300 disabled:opacity-40"
      >
        →
      </button>
    </div>
  );
}