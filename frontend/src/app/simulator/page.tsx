import { DashboardSidebar, DashboardTopbar } from "@/components/dashboard-sidebar";
import { SimulatorPanel } from "@/components/simulator-panel";

export default function SimulatorPage() {
  return <main className="flex min-h-screen bg-[#0b0c10]"><DashboardSidebar /><div className="min-w-0 flex-1"><DashboardTopbar title="Simulator" subtitle="Prediction engine" /><div className="mx-auto max-w-7xl p-5 md:p-7"><SimulatorPanel /></div></div></main>;
}