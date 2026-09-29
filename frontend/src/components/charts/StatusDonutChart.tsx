// Status donut: how the whole portfolio splits across offer states.
// The legend is a real control, not decoration: clicking a row filters the
// offer table below, which is why it lives here and not in the chart itself.
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { statusColor, TOOLTIP_STYLE, TOOLTIP_WRAPPER_STYLE, type StatusCount } from "./chartTheme";

export default function StatusDonutChart({
  rows,
  selected,
  onSelect,
}: {
  rows: StatusCount[];
  selected: string;
  onSelect: (status: string) => void;
}) {
  const total = rows.reduce((sum, r) => sum + r.count, 0);
  return (
    <div className="flex h-44 items-center gap-2">
      <div className="h-44 w-[46%] shrink-0 overflow-hidden">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={rows}
              dataKey="count"
              nameKey="status"
              innerRadius="55%"
              outerRadius="88%"
              paddingAngle={2}
              stroke="none"
            >
              {rows.map((r) => (
                <Cell key={r.status} fill={statusColor(r.status)} />
              ))}
            </Pie>
            <Tooltip contentStyle={TOOLTIP_STYLE} wrapperStyle={TOOLTIP_WRAPPER_STYLE} />
          </PieChart>
        </ResponsiveContainer>
      </div>
      <ul className="min-w-0 flex-1 space-y-0.5 text-xs">
        {rows.map((r) => (
          <li key={r.status}>
            <button
              onClick={() => onSelect(r.status === selected ? "" : r.status)}
              className={`w-full flex items-center gap-1.5 px-1 py-0.5 rounded text-left hover:bg-blue-50 ${selected === r.status ? "bg-blue-100" : ""}`}
            >
              <span
                className="w-2.5 h-2.5 rounded-sm shrink-0"
                style={{ backgroundColor: statusColor(r.status) }}
              />
              <span className="min-w-0 flex-1 truncate text-gray-700">{r.status}</span>
              <span className="ml-auto font-mono font-semibold text-gray-900">{r.count}</span>
              <span className="font-mono text-gray-500 w-9 text-right">
                {total > 0 ? `${Math.round((r.count / total) * 100)}%` : "0%"}
              </span>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
