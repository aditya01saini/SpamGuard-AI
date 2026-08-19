import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Analyzer from './pages/Analyzer.jsx'
import Result from './pages/Result.jsx'
import History from './pages/History.jsx'
import Analytics from './pages/Analytics.jsx'
import ModelPerformance from './pages/ModelPerformance.jsx'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/analyze" element={<Analyzer />} />
        <Route path="/result/:id" element={<Result />} />
        <Route path="/history" element={<History />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/model" element={<ModelPerformance />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}
