import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "LexGraph AI",
  description: "Find what is missing from a contract.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body suppressHydrationWarning>{children}</body>
    </html>
  );
}
