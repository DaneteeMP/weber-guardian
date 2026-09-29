// Top customers by offer count, horizontal bars with the count printed at the
// end of every bar. The value label is the point of this chart: reading the
// ranking must not require hovering anything.
//
// Horizontal bars because the label is a company name. On a vertical bar chart
// the names have to share the width of the category axis and every one of them
// turns into an unreadable stub; here the name owns a fixed, wide column and the
// bar takes whatever is left.
import { Bar, BarChart, LabelList, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { CHART_BLUE, shortName, TOOLTIP_STYLE, TOOLTIP_WRAPPER_STYLE } from "./chartTheme";

export type RankingBar = { label: string; count: number };

type NameTickProps = {
  x?: number;
  y?: number;
  payload?: { value?: string | number };
  textAnchor?: "inherit" | "start" | "middle" | "end";
};

// Axis tick that shows a shortened name but keeps the full one in a native
// tooltip, so a long legal name is never lost, only deferred to hover.
function NameTick({ x = 0, y = 0, payload, textAnchor }: NameTickProps) {
  const value = String(payload?.value ?? "");
  return (
    <text x={x} y={y} dy={4} textAnchor={textAnchor} fontSize={12} fill="#374151">
      <title>{value}</title>
      {shortName(value)}
    </text>
  );
}

export default function CustomerRankingChart({ rows }: { rows: RankingBar[] }) {
  // One extra unit of headroom so the right-most label is not clipped.
  const max = rows.reduce((m, r) => Math.max(m, r.count), 0);

  return (
    <div className="h-44 mt-1 overflow-hidden">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={rows} layout="vertical" margin={{ top: 0, right: 28, bottom: 0, left: 0 }}>
          <XAxis type="number" domain={[0, max + 1]} hide />
          <YAxis
            type="category"
            dataKey="label"
            width={240}
            interval={0}
            tick={<NameTick />}
          />
          <Tooltip contentStyle={TOOLTIP_STYLE} wrapperStyle={TOOLTIP_WRAPPER_STYLE} />
          <Bar dataKey="count" fill={CHART_BLUE} radius={[0, 2, 2, 0]} barSize={14}>
            <LabelList
              dataKey="count"
              position="right"
              offset={6}
              style={{ fontSize: 12, fill: "#374151", fontWeight: 600 }}
            />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
