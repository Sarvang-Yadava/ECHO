"use client";
import { motion } from "framer-motion";

export function ProgressRing({ value, label, size = 112 }: { value: number; label: string; size?: number }) {
  const stroke = 8; const radius = (size - stroke) / 2; const circumference = radius * 2 * Math.PI;
  return <div className="relative grid place-items-center" style={{ width: size, height: size }}><svg className="-rotate-90" width={size} height={size}><circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke="rgba(255,255,255,.09)" strokeWidth={stroke} /><motion.circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke="url(#echoGradient)" strokeLinecap="round" strokeWidth={stroke} strokeDasharray={circumference} initial={{ strokeDashoffset: circumference }} animate={{ strokeDashoffset: circumference - value / 100 * circumference }} transition={{ duration: 1.4, ease: "easeOut" }} /><defs><linearGradient id="echoGradient"><stop stopColor="#8b5cf6" /><stop offset="1" stopColor="#34d399" /></linearGradient></defs></svg><div className="absolute text-center"><p className="text-2xl font-semibold tracking-tight">{value}</p><p className="text-[10px] uppercase tracking-wider text-zinc-500">{label}</p></div></div>;
}
