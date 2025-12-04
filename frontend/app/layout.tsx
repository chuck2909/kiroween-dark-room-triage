export const metadata = {
  title: 'Dark Room Triage',
  description: 'Passive reconnaissance and security triage',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
