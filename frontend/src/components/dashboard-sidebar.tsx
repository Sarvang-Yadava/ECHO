"use client";
"use client";

import { Bell, BrainCircuit, FileText, Gauge, Settings, Sparkles } from "lucide-react";
import { motion } from "framer-motion";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const items = [
	{ label: "Dashboard", icon: Gauge, href: "/dashboard" },
	{ label: "Twin", icon: BrainCircuit, href: "/twin" },
	{ label: "Documents", icon: FileText, href: "/documents" },
	{ label: "Simulator", icon: Sparkles, href: "/simulator" },
];
export function DashboardSidebar() { const pathname = usePathname(); return <aside className="hidden w-64 shrink-0 border-r border-white/[.08] bg-[#0b0c10] p-5 lg:flex lg:flex-col"><a className="mb-12 text-xl font-semibold tracking-tight" href="/">ECHO<span className="text-violet-400">.</span></a><nav className="space-y-1">{items.map(({ label, icon: Icon, href }) => { const active = pathname === href; return <a key={label} href={href} className={cn("relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition duration-200", active ? "text-white" : "text-zinc-500 hover:bg-white/[.05] hover:text-zinc-200")}>{active && <motion.span layoutId="sidebar-active" transition={{ duration: .22 }} className="absolute inset-0 rounded-xl bg-white/[.08]" />}<Icon className="relative" size={18} /><span className="relative">{label}</span></a>; })}</nav><div className="mt-auto space-y-2"><button className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-zinc-500 hover:bg-white/[.05]"><Settings size={18} />Settings</button><div className="surface mt-5 rounded-xl p-3"><p className="text-xs font-medium">ECHO Pro</p><p className="mt-1 text-xs leading-5 text-zinc-500">Unlock deeper future simulations.</p></div></div></aside>; }

export function DashboardTopbar({ title = "Good evening, Aria.", subtitle = "Live academic twin" }: { title?: string; subtitle?: string }) { return <header className="flex items-center justify-between border-b border-white/[.08] px-6 py-4"><div><p className="text-sm text-zinc-500">{subtitle}</p><h1 className="mt-1 text-xl font-semibold">{title}</h1></div><button className="relative rounded-xl border border-white/[.09] p-2.5 text-zinc-400"><Bell size={18} /><span className="absolute right-2 top-2 size-1.5 rounded-full bg-violet-400" /></button></header>; }
