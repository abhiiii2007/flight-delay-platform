import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "FlightPulse | U.S. Flight Delay Intelligence",
  description: "Explore official U.S. flight-delay patterns and evaluate delay risk.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
