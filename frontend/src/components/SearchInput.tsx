// The one search box every list toolbar uses: a controlled input with a
// magnifier and a caller-provided placeholder.
//
// It holds no debounce and no data on purpose. Panels that filter in memory
// (matchesQuery) re-render instantly, while server-search panels keep their
// own debounce around the fetch. Keeping the box dumb makes both flows
// explicit at the call site instead of hidden in the component.
export default function SearchInput({
  value,
  onChange,
  placeholder,
  className = "",
}: {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  className?: string;
}) {
  return (
    <div className={`relative ${className}`}>
      <svg
        viewBox="0 0 24 24"
        className="pointer-events-none absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        aria-hidden="true"
      >
        <circle cx="11" cy="11" r="7" />
        <path d="m21 21-4.3-4.3" />
      </svg>
      <input
        type="search"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        className="ui-input w-full pl-8 pr-3"
      />
    </div>
  );
}
