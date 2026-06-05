'use client'

import { useState } from 'react'
import ClaimForm from '@/components/ClaimForm'
import DecisionDisplay from '@/components/DecisionDisplay'
import TestRunner from '@/components/TestRunner'

export default function Home() {
  const [decision, setDecision] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState<'submit' | 'test'>('submit')

  const handleClaimSubmit = async (formData: any) => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/adjudicate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': 'local-dev',
        },
        body: JSON.stringify(formData),
      })

      const result = await response.json()
      setDecision(result)
    } catch (error) {
      console.error('Error:', error)
      alert('Error submitting claim. Make sure the API is running on localhost:8000')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="mb-6">
        <div className="sm:hidden">
          <select
            value={activeTab}
            onChange={(e) => setActiveTab(e.target.value as 'submit' | 'test')}
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="submit">Submit Claim</option>
            <option value="test">Run Tests</option>
          </select>
        </div>
        <div className="hidden sm:block border-b border-gray-200">
          <nav className="-mb-px flex space-x-8" aria-label="Tabs">
            {[
              { id: 'submit', name: 'Submit Claim' },
              { id: 'test', name: 'Run Tests' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as 'submit' | 'test')}
                className={`${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
              >
                {tab.name}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {activeTab === 'submit' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Claim Submission</h2>
            <ClaimForm onSubmit={handleClaimSubmit} loading={loading} />
          </div>
          {decision && (
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Decision Result</h2>
              <DecisionDisplay decision={decision} />
            </div>
          )}
        </div>
      )}

      {activeTab === 'test' && (
        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Test Suite Runner</h2>
          <TestRunner />
        </div>
      )}
    </div>
  )
}
