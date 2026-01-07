import "./globals.css";

export const metadata = {
  title: "Agentic Job Copilot",
  description: "Tiny UI for the Agentic Job Application Copilot"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen">{children}</body>
    </html>
  );
}
