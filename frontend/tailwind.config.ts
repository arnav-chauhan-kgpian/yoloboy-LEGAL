import type { Config } from "tailwindcss";

export default {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink:     "#0F172A",
        surface: "#EEF1F8",
        shell:   "#0B0D14",
        accent:  "#6366F1",
        gap:     "#E11D48",
        gapBg:   "#FFF0F3",
        ok:      "#10B981",
        okBg:    "#ECFDF5",
        warn:    "#F59E0B",
        warnBg:  "#FFFBEB",
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "-apple-system"],
        mono: ["ui-monospace", "SFMono-Regular", "Menlo"],
      },
    },
  },
  plugins: [],
} satisfies Config;
