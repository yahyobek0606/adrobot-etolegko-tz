import { Link, Outlet } from 'react-router'

import { paths } from '@/app/paths'

export function AppLayout() {
  return (
    <div className="min-h-svh bg-background text-foreground">
      <header className="border-b">
        <div className="mx-auto flex h-14 max-w-6xl items-center px-4">
          <Link to={paths.campaigns} className="font-semibold">
            Keitaro Campaign Manager
          </Link>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-8">
        <Outlet />
      </main>
    </div>
  )
}
