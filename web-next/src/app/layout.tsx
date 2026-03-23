import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SML AI Router",
  description: "AI Proxy Dashboard - ค้นหา ทดสอบ และจัดการ AI API ฟรี",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="th" className="dark h-full" suppressHydrationWarning>
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@300;400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="h-full flex flex-col overflow-hidden antialiased">{children}</body>
    </html>
  );
}
