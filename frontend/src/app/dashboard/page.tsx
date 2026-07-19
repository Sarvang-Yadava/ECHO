import { DashboardSidebar, DashboardTopbar } from "@/components/dashboard-sidebar";
import { LiveDashboard } from "@/components/live-dashboard";

export default function DashboardPage() {
  return <main className="flex min-h-screen bg-[#0b0c10]"><DashboardSidebar /><div className="min-w-0 flex-1"><DashboardTopbar title="Dashboard" subtitle="Live overview" /><div className="mx-auto max-w-7xl p-5 md:p-7"><LiveDashboard /></div></div></main>;
}
