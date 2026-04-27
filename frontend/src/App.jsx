import React, { useState, useEffect } from 'react'
import { Toaster } from 'react-hot-toast'
import Dashboard from './components/Dashboard'
import PayoutForm from './components/PayoutForm'
import PayoutHistory from './components/PayoutHistory'
import api from './api'

function App() {
  const [refreshTrigger, setRefreshTrigger] = useState(0)
  const [merchant, setMerchant] = useState(null)

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const email = 'merchant3@example.com'   // 👈 change here to test different merchants
        localStorage.setItem('merchant_email', email)

        const response = await api.get('/dashboard/')
        setMerchant(response.data)

      } catch (error) {
        console.error('Failed to fetch dashboard:', error)
      }
    }

    fetchDashboard()
  }, [refreshTrigger])

  const refreshDashboard = () => {
    setRefreshTrigger(prev => prev + 1)
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <Toaster position="top-right" />

      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">
                Playto Pay Dashboard
              </h1>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {merchant ? (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              <Dashboard
                balance={merchant.balance}
                heldBalance={merchant.held_balance}
              />
              <PayoutForm onSuccess={refreshDashboard} />
            </div>

            <PayoutHistory
              payouts={merchant.recent_payouts}
              refreshTrigger={refreshTrigger}
            />
          </>
        ) : (
          <p className="text-gray-500">Loading dashboard...</p>
        )}
      </main>
    </div>
  )
}

export default App
