"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowRight, BookOpen, BrainCircuit, CalendarDays, FileText, Gauge, Sparkles, UploadCloud } from "lucide-react";
import { fetchDashboard, type DashboardResponse } from "@/lib/api";
import { Card } from "@/components/ui/card";

function Metric({ label, value, detail, icon: Icon }: { label: string; value: string; detail: string; icon: typeof Gauge }) {
  return <Card className="p-5"><div className="flex items-start justify-between"><div><p className="text-sm text-zinc-500">{label}</p><p className="mt-2 text-3xl font-semibold tracking-tight">{value}</p></div><Icon size={18} className="text-violet-300" /></div><p className="mt-4 text-xs text-emerald-400">{detail}</p></Card>;
}

export function LiveDashboard() {
  const [data, setData] = useState<DashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    fetchDashboard()
      .then((payload) => {
        if (active) setData(payload);
      })
      .catch((reason: Error) => {
        if (active) setError(reason.message);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => { active = false; };
  }, []);

  if (loading) {
    return <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4"><Card className="h-32 animate-pulse bg-white/[.03]" /><Card className="h-32 animate-pulse bg-white/[.03]" /><Card className="h-32 animate-pulse bg-white/[.03]" /><Card className="h-32 animate-pulse bg-white/[.03]" /></div>;
  }

  if (error) {
    return <Card className="border-rose-500/30 bg-rose-500/10 p-6 text-rose-100">Could not load dashboard: {error}</Card>;
  }

  if (!data) {
    return null;
  }

  const profile = data.student_profile;
  const emptyState = !data.has_data;

  return <div className="space-y-4"><div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4"><Card className="flex items-center gap-5 p-5"><div className="grid size-20 place-items-center rounded-2xl bg-violet-400/10 text-violet-200"><BrainCircuit size={30} /></div><div><p className="text-sm text-zinc-500">Academic health</p><p className="mt-1 text-3xl font-semibold">{data.academic_health.toFixed(1)}%</p><p className="mt-1 text-xs text-emerald-400">Recommended load {data.recommended_study_load.toFixed(1)} h/day</p></div></Card><Metric label="Uploaded syllabi" value={`${profile.documents_uploaded}`} detail="Real documents powering the twin" icon={UploadCloud} /><Metric label="Courses detected" value={`${profile.active_courses}`} detail="Detected from uploaded content" icon={BookOpen} /><Metric label="Current confidence" value={`${data.current_confidence.toFixed(1)}%`} detail="Derived from topic confidence" icon={Gauge} /></div>{emptyState ? <Card className="surface p-8"><p className="eyebrow">Onboarding</p><h2 className="mt-4 text-3xl font-semibold">Upload your first syllabus to create your Digital Twin.</h2><p className="mt-3 max-w-2xl text-zinc-400">ECHO will extract text, build structured course data, populate your knowledge graph, and enable the simulator from the same source.</p><div className="mt-6 flex flex-wrap gap-3"><Link href="/documents" className="inline-flex items-center gap-2 rounded-xl bg-white px-4 py-2.5 text-sm font-medium text-zinc-950"><UploadCloud size={16} /> Upload document</Link><Link href="/twin" className="inline-flex items-center gap-2 rounded-xl border border-white/10 px-4 py-2.5 text-sm text-white">Open twin <ArrowRight size={16} /></Link></div></Card> : null}<div className="grid gap-4 xl:grid-cols-[1.2fr_.8fr]"><Card className="p-5"><div className="flex items-center justify-between"><div><p className="font-medium">Detected courses</p><p className="mt-1 text-sm text-zinc-500">Structured from uploaded syllabi</p></div><span className="rounded-full bg-violet-400/10 px-3 py-1 text-xs text-violet-200">Live</span></div><div className="mt-5 space-y-3">{data.detected_courses.length ? data.detected_courses.map((course) => <div key={course.id} className="rounded-2xl border border-white/8 bg-white/[.03] p-4"><div className="flex items-start justify-between gap-4"><div><p className="font-medium">{course.name}</p><p className="mt-1 text-xs text-zinc-500">{course.topic_count} topics · {course.assignment_count} assignments · {course.exam_count} exams</p></div><p className="text-sm text-emerald-300">{course.confidence.toFixed(1)}%</p></div></div>) : <p className="text-sm text-zinc-500">No courses yet.</p>}</div></Card><Card className="p-5"><p className="font-medium">Upcoming deadlines</p><div className="mt-5 space-y-3">{data.upcoming_deadlines.length ? data.upcoming_deadlines.map((deadline) => <div key={`${deadline.title}-${deadline.due_date}`} className="rounded-2xl bg-white/[.03] p-4"><p className="text-sm font-medium">{deadline.title}</p><p className="mt-1 text-xs text-zinc-500">{deadline.due_date}</p><p className="mt-2 text-xs text-violet-300">{deadline.priority}</p></div>) : <p className="text-sm text-zinc-500">No upcoming deadlines detected.</p>}</div></Card></div><div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3"><Card className="p-5"><p className="font-medium">Weak topics</p><div className="mt-4 space-y-3">{data.weak_topics.length ? data.weak_topics.map((topic) => <div key={`${topic.course}-${topic.name}`} className="rounded-2xl bg-rose-500/10 p-3"><p className="text-sm font-medium">{topic.name}</p><p className="mt-1 text-xs text-rose-200">{topic.course} · {topic.confidence.toFixed(1)}%</p></div>) : <p className="text-sm text-zinc-500">No weak topics yet.</p>}</div></Card><Card className="p-5"><p className="font-medium">Strong topics</p><div className="mt-4 space-y-3">{data.strong_topics.map((topic) => <div key={`${topic.course}-${topic.name}`} className="rounded-2xl bg-emerald-500/10 p-3"><p className="text-sm font-medium">{topic.name}</p><p className="mt-1 text-xs text-emerald-200">{topic.course} · {topic.confidence.toFixed(1)}%</p></div>)}</div></Card><Card className="p-5"><p className="font-medium">Recent documents</p><div className="mt-4 space-y-3">{data.recent_documents.length ? data.recent_documents.map((document) => <div key={document.id} className="rounded-2xl bg-white/[.03] p-3"><p className="text-sm font-medium">{document.filename}</p><p className="mt-1 text-xs text-zinc-500">{document.course ?? "Unassigned"} · {document.status} · {new Date(document.uploaded_date).toLocaleDateString()}</p></div>) : <p className="text-sm text-zinc-500">Upload a document to populate this list.</p>}</div></Card></div></div>;
}
