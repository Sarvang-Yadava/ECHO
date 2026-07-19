import { type HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) { return <section className={cn("surface rounded-2xl transition-all duration-300", className)} {...props} />; }
