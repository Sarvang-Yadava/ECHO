"use client";

import Link from "next/link";
import { ArrowRight, BrainCircuit, FileSearch, Gauge, Sparkles } from "lucide-react";
import { LandingNav } from "@/components/landing-nav";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

const features = [
  [BrainCircuit, "Digital Twin", "Build a student model from your uploaded syllabus."],
  [FileSearch, "Document Intelligence", "Extract text from PDF, DOCX, and TXT files."],
  [Gauge, "Prediction Engine", "Simulate outcomes from study habits and attendance."],
] as const;

function Hero() {
  return <div className="mx-auto mt-14 max-w-6xl rounded-[2rem] border border-emerald-100/[.12] bg-white/[.025] p-2 shadow-2xl shadow-black/30"><div className="grid gap-3 lg:grid-cols-[1.15fr_.85fr]"><Card className="p-7 sm:p-9"><p className="eyebrow">Your living academic system</p><h1 className="mt-4 text-5xl font-semibold leading-[.95] tracking-[-.05em] text-white sm:text-7xl">Academic intelligence from real documents.</h1><p className="mt-5 max-w-2xl text-base leading-7 text-zinc-400 sm:text-lg">Upload a syllabus, let ECHO structure it into courses and topics, and use the resulting twin, simulator, and mentor immediately.</p><div className="mt-8 flex flex-wrap gap-3"><Link href="/documents"><Button className="gap-2">Upload syllabus <ArrowRight size={16} /></Button></Link><Link href="/dashboard"><Button variant="secondary">Open dashboard</Button></Link></div></Card><Card className="p-7 sm:p-9"><p className="font-medium">What happens next</p><div className="mt-5 space-y-3 text-sm text-zinc-400"><div className="flex items-center gap-3"><Sparkles size={16} className="text-violet-300" />Text is extracted and stored in your academic workspace.</div><div className="flex items-center gap-3"><Sparkles size={16} className="text-violet-300" />The syllabus becomes structured course intelligence.</div><div className="flex items-center gap-3"><Sparkles size={16} className="text-violet-300" />Twin, forecast, and mentor update from the same source.</div></div></Card></div></div>;
}

export default function Home() {
  return <main className="overflow-hidden"><div className="aurora-orb -left-32 top-20 size-[32rem] bg-emerald-400"/><div className="aurora-orb right-0 top-56 size-[24rem] bg-teal-300 [animation-delay:-7s]"/><LandingNav /><section className="relative mx-auto px-6 pb-20 pt-12 text-center"><p className="eyebrow mx-auto flex w-fit items-center gap-2 rounded-full border border-emerald-200/20 bg-emerald-300/[.07] px-3 py-1.5"><Sparkles size={12} /> Academic intelligence, reimagined</p><Hero /></section><section className="mx-auto max-w-6xl px-6 py-10"><div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">{features.map(([Icon, title, description]) => <Card key={title} className="p-5"><Icon className="text-violet-300" size={20} /><h3 className="mt-4 text-lg font-semibold">{title}</h3><p className="mt-2 text-sm leading-6 text-zinc-400">{description}</p></Card>)}</div></section></main>;
}
