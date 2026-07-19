import type { Config } from "tailwindcss";

export default {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#09090b",
        panel: "#111113",
        line: "#27272a",
        echo: "#a3e635"
      }
    }
  },
  plugins: []
} satisfies Config;
