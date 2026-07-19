import { DashboardSidebar, DashboardTopbar } from "@/components/dashboard-sidebar";
import { TwinView } from "@/components/twin-view";

export default function TwinPage() {
  return <main className="flex min-h-screen bg-[#0b0c10]"><DashboardSidebar /><div className="min-w-0 flex-1"><DashboardTopbar title="Digital Twin" subtitle="Profile and knowledge graph" /><div className="mx-auto max-w-7xl p-5 md:p-7"><TwinView /></div></div></main>;
}