import type { Metadata } from "next";
import { Inter, Outfit } from "next/font/google";
import "./globals.css";
import { TooltipProvider } from "@/components/ui/tooltip";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const outfit = Outfit({
  variable: "--font-outfit",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AI Virtual Film Studio — 24/7 Autonomous Movie & Series Production",
  description:
    "Real-time command center orchestrating 24 specialized Hollywood AI agents: Concept, Story, Directing, Art, Audio, Generation, and Quality Control.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`dark ${inter.variable} ${outfit.variable} h-full antialiased`}>
      <body className="min-h-full bg-[#07080d] text-slate-100 flex flex-col font-sans selection:bg-amber-500/30 selection:text-amber-200">
        <TooltipProvider>
          {children}
        </TooltipProvider>
      </body>
    </html>
  );
}
