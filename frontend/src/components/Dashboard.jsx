import React from 'react'

const Dashboard = ({ balance, heldBalance }) => {
  const formatINR = (paise) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2
    }).format(paise / 100)
  }
  
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-medium text-gray-900 mb-4">Account Balance</h2>
      <div className="space-y-3">
        <div className="flex justify-between items-baseline">
          <span className="text-gray-600">Available Balance:</span>
          <span className="text-2xl font-bold text-green-600">{formatINR(balance)}</span>
        </div>
        <div className="flex justify-between items-baseline">
          <span className="text-gray-600">Held Balance:</span>
          <span className="text-lg text-yellow-600">{formatINR(heldBalance)}</span>
        </div>
        <div className="border-t pt-3 mt-3">
          <div className="flex justify-between items-baseline">
            <span className="text-gray-800 font-medium">Total Value:</span>
            <span className="text-xl font-bold text-gray-900">{formatINR(balance + heldBalance)}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard