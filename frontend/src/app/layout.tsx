import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ECHO — Your Academic Digital Twin",
  description: "Understand your learning. Predict your future."
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
