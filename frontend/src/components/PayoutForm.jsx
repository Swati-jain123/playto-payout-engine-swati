import React, { useState } from 'react'
import toast from 'react-hot-toast'
import api from '../api'

const PayoutForm = ({ onSuccess }) => {
  const [amount, setAmount] = useState('')
  const [bankAccountId, setBankAccountId] = useState('')
  const [loading, setLoading] = useState(false)
  
  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!amount || amount <= 0) {
      toast.error('Please enter a valid amount')
      return
    }
    
    if (!bankAccountId) {
      toast.error('Please enter bank account ID')
      return
    }
    
    setLoading(true)
    const amountPaise = Math.round(parseFloat(amount) * 100)
    
    try {
      const response = await api.post('/payouts/', {
        amount_paise: amountPaise,
        bank_account_id: bankAccountId
      })
      
      toast.success(`Payout request created! Status: ${response.data.status}`)
      setAmount('')
      setBankAccountId('')
      onSuccess()
    } catch (error) {
      const message = error.response?.data?.error || 'Failed to create payout'
      toast.error(message)
      console.error('Payout error:', error)
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-medium text-gray-900 mb-4">Request Payout</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Amount (INR)
          </label>
          <input
            type="number"
            step="0.01"
            min="0.01"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter amount in INR"
            disabled={loading}
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Bank Account ID
          </label>
          <input
            type="text"
            value={bankAccountId}
            onChange={(e) => setBankAccountId(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter bank account ID"
            disabled={loading}
          />
        </div>
        
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors disabled:bg-blue-300"
        >
          {loading ? 'Processing...' : 'Request Payout'}
        </button>
      </form>
    </div>
  )
}

export default PayoutForm