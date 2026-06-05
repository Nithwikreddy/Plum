import type { Metadata } from "next"
import "./globals.css"

export const metadata: Metadata = {
  title: "Plum OPD Advantage - Claim Adjudication",
  description: "AI-powered OPD claim adjudication system",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50">
        <nav className="bg-white shadow">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <h1 className="text-2xl font-bold text-gray-900">Plum OPD Advantage</h1>
            <p className="text-sm text-gray-600">Claim Adjudication System</p>
          </div>
        </nav>
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
        <footer className="bg-white shadow mt-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 text-center text-sm text-gray-600">
            <p>&copy; 2024 Plum OPD Advantage. All rights reserved.</p>
          </div>
        </footer>
      </body>
    </html>
  )
}
