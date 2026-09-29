// Offers issued per month. Grouped by the business date (offer_date) on the
// server, so this chart always agrees with the date column and the PDF.
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { CHART_BLUE, TOOLTIP_STYLE, type MonthCount } from "./chartTheme";

export default function MonthlyOffersChart({ rows }: { rows: MonthCount[] }) {
  return (
    <div className="h-32 mt-1">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={rows} margin={{ top: 4, right: 4, bottom: 0, left: -18 }}>
          {/* Months arrive as yyyy-mm; the axis only has room for yy-mm. */}
          <XAxis
            dataKey="month"
            tickFormatter={(month: string) => month.slice(2)}
            tick={{ fontSize: 9 }}
            interval="preserveStartEnd"
          />
          <YAxis allowDecimals={false} tick={{ fontSize: 9 }} width={38} />
          <Tooltip contentStyle={TOOLTIP_STYLE} />
          <Bar dataKey="count" fill={CHART_BLUE} radius={[2, 2, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
