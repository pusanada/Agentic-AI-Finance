import type { Metadata } from "next";
import "./globals.css";
import Navbar from "@/components/Navbar";
import ChatWidget from "@/components/ChatWidget";

export const metadata: Metadata = {
  title: "ThaiESG Portfolio Allocator & Compliance Guard",
  description: "High-fidelity modern Fintech dashboard for personal tax optimization and investment compliance.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="th" className="dark h-full scroll-smooth" style={{ colorScheme: 'light dark' }}>
      <head>
        {/* Anti-flash script for theme toggles defaulting to dark */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              try {
                const theme = localStorage.getItem('app-theme') || 'dark';
                if (theme === 'dark') {
                  document.documentElement.classList.add('dark');
                } else {
                  document.documentElement.classList.remove('dark');
                }
              } catch (e) {}
            `,
          }}
        />
      </head>
      <body className="min-h-full flex flex-col bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 transition-colors duration-300 font-sans">
        <Navbar />
        <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {children}
        </main>
        
        {/* Floating AI Tax Assistant Chat Widget */}
        <ChatWidget />
      </body>
    </html>
  );
}
