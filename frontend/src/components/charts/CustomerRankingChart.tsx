// Top customers by offer count, horizontal bars with the count printed at the
// end of every bar. The value label is the point of this chart: reading the
// ranking must not require hovering anything.
import { Bar, BarChart, LabelList, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { CHART_BLUE, TOOLTIP_STYLE } from "./chartTheme";

export type RankingBar = { label: string; count: number };

export default function CustomerRankingChart({ rows }: { rows: RankingBar[] }) {
  // One extra unit of headroom so the right-most label is not clipped.
  const max = rows.reduce((m, r) => Math.max(m, r.count), 0);

  return (
    <div className="h-32 mt-1">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={rows} layout="vertical" margin={{ top: 0, right: 22, bottom: 0, left: 0 }}>
          <XAxis type="number" domain={[0, max + 1]} hide />
          <YAxis type="category" dataKey="label" width={92} tick={{ fontSize: 9 }} interval={0} />
          <Tooltip contentStyle={TOOLTIP_STYLE} />
          <Bar dataKey="count" fill={CHART_BLUE} radius={[0, 2, 2, 0]}>
            <LabelList
              dataKey="count"
              position="right"
              offset={4}
              style={{ fontSize: 9, fill: "#374151", fontWeight: 600 }}
            />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
