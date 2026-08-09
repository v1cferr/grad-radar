import type { Metadata } from "next";
import type { ReactNode } from "react";
import { Inter } from "next/font/google";

import { TooltipProvider } from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";

import "./globals.css";

// `display: swap` so text is readable while the font loads; `variable` feeds
// --font-sans in globals.css, which is what Tailwind's font-sans resolves to.
const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: "GradRadar",
  description: "Discover, compare, and track graduate opportunities.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="pt-BR" className={cn(inter.variable)} suppressHydrationWarning>
      <body className="min-h-screen antialiased">
        {/* One provider at the root: every Tooltip below shares its timing, so
            hovering across cells feels continuous instead of re-arming.
            shadcn ships Base UI here, not Radix — the prop is `delay`. */}
        <TooltipProvider delay={150}>
          {children}
        </TooltipProvider>
      </body>
    </html>
  );
}
