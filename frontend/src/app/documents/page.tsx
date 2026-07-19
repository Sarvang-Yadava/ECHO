import { DashboardSidebar, DashboardTopbar } from "@/components/dashboard-sidebar";
import { DocumentManager } from "@/components/document-manager";

export default function DocumentsPage() {
  return <main className="flex min-h-screen bg-[#0b0c10]"><DashboardSidebar /><div className="min-w-0 flex-1"><DashboardTopbar title="Documents" subtitle="Upload and analysis" /><div className="mx-auto max-w-7xl p-5 md:p-7"><DocumentManager /></div></div></main>;
}