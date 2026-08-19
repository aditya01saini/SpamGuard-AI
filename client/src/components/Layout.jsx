import { useState } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import Sidebar from './Sidebar.jsx'
import TopNav from './TopNav.jsx'

const TITLES = {
  '/': 'Dashboard',
  '/analyze': 'Email Analyzer',
  '/history': 'Scan History',
  '/analytics': 'Analytics',
  '/model': 'Model Performance',
}

export default function Layout() {
  const [open, setOpen] = useState(false)
  const { pathname } = useLocation()
  const title = pathname.startsWith('/result')
    ? 'Analysis Result'
    : TITLES[pathname] || 'SpamGuard AI'

  return (
    <div className="flex min-h-screen">
      <Sidebar open={open} onClose={() => setOpen(false)} />
      <div className="flex min-w-0 flex-1 flex-col">
        <TopNav title={title} onMenu={() => setOpen(true)} />
        <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-6 md:px-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
