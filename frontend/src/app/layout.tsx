import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { Layout } from "@/components/layout/layout";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "WanderWise - AI-Powered Travel Planner",
  description: "Plan your perfect trip with AI-powered intelligence. Get personalized travel itineraries, hotel recommendations, and local insights.",
  keywords: "travel planner, AI travel, itinerary generator, vacation planner, trip planner",
  authors: [{ name: "WanderWise Team" }],
  openGraph: {
    title: "WanderWise - AI-Powered Travel Planner",
    description: "Plan your perfect trip with AI-powered intelligence",
    type: "website",
    locale: "en_US",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={inter.variable} suppressHydrationWarning>
      <body className="font-sans antialiased" suppressHydrationWarning>
        <Layout>
          {children}
        </Layout>
      </body>
    </html>
  );
}
