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
  const button =
    "inline-flex h-8 w-8 items-center justify-center rounded-lg border border-line-strong bg-white text-ink transition hover:bg-canvas disabled:opacity-40";

  return (
    <div className="flex items-center justify-between text-sm">
      <button
        disabled={!hasPrevious}
        onClick={() => onPageChange(page - 1)}
        className={button}
      >
        ←
      </button>

      <span className="text-muted">
        {start}–{end} / {total.toLocaleString()}
      </span>

      <button
        disabled={!hasNext}
        onClick={() => onPageChange(page + 1)}
        className={button}
      >
        →
      </button>
    </div>
  );
}
