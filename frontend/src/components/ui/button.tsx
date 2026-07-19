import { type ButtonHTMLAttributes, type ReactNode } from "react";
import { cn } from "@/lib/utils";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & { children: ReactNode; variant?: "primary" | "secondary" | "ghost" };

export function Button({ children, className, variant = "primary", ...props }: ButtonProps) {
  const variants = { primary: "bg-[#a5f3c7] text-[#062316] hover:bg-[#d6ffe7] hover:shadow-[0_0_26px_rgba(148,247,197,.3)]", secondary: "border border-emerald-200/15 bg-emerald-300/[.06] text-emerald-50 hover:bg-emerald-300/[.12] hover:shadow-[0_0_20px_rgba(148,247,197,.14)]", ghost: "text-zinc-400 hover:text-emerald-50" };
  return <button className={cn("group relative isolate overflow-hidden inline-flex items-center justify-center rounded-xl px-4 py-2.5 text-sm font-medium transition duration-200 hover:-translate-y-px active:translate-y-0 active:scale-[.975] disabled:pointer-events-none", variants[variant], className)} {...props}><span className="absolute inset-0 -z-10 bg-gradient-to-r from-transparent via-white/20 to-transparent opacity-0 transition duration-500 group-hover:opacity-100" />{children}</button>;
}
