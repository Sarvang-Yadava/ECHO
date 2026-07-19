"use client";
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const confidence = [{ day: "Mon", value: 54 }, { day: "Tue", value: 61 }, { day: "Wed", value: 58 }, { day: "Thu", value: 72 }, { day: "Fri", value: 70 }, { day: "Sat", value: 78 }, { day: "Sun", value: 82 }];
const decay = [{ day: "Now", value: 82 }, { day: "+2d", value: 76 }, { day: "+4d", value: 65 }, { day: "+6d", value: 57 }, { day: "+8d", value: 52 }];

export function ConfidenceChart({ decayChart = false, values }: { decayChart?: boolean; values?: Array<{ day: string; value: number }> }) {
  const data = values ?? (decayChart ? decay : confidence);
  return <div className="h-44 w-full"><ResponsiveContainer><AreaChart data={data} margin={{ top: 10, left: -20, right: 4, bottom: 0 }}><defs><linearGradient id={decayChart ? "decay" : "confidence"} x1="0" x2="0" y1="0" y2="1"><stop offset="0" stopColor={decayChart ? "#fb7185" : "#8b5cf6"} stopOpacity={.38} /><stop offset="1" stopColor={decayChart ? "#fb7185" : "#8b5cf6"} stopOpacity={0} /></linearGradient></defs><XAxis dataKey="day" tickLine={false} axisLine={false} tick={{ fill: "#71717a", fontSize: 11 }} /><YAxis hide domain={[0, 100]} /><Tooltip contentStyle={{ background: "#17171c", border: "1px solid #3f3f46", borderRadius: 10 }} /><Area isAnimationActive animationDuration={240} animationEasing="ease-out" type="monotone" dataKey="value" stroke={decayChart ? "#fb7185" : "#a78bfa"} strokeWidth={2.5} fill={`url(#${decayChart ? "decay" : "confidence"})`} /></AreaChart></ResponsiveContainer></div>;
}
