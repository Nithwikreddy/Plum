'use client'

import { useState } from 'react'

interface TestResult {
  test_id: string
  passed: boolean
  expected: any
  actual: any
  error?: string
}

export default function TestRunner() {
  const [results, setResults] = useState<TestResult[] | null>(null)
  const [loading, setLoading] = useState(false)

  const runTests = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/run-tests', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': 'local-dev',
        },
      })

      const data = await response.json()
      setResults(data.results || [])
    } catch (error) {
      console.error('Error running tests:', error)
      alert('Error running tests. Make sure the API is running on localhost:8000')
    } finally {
      setLoading(false)
    }
  }

  const passedTests = results ? results.filter((r) => r.passed).length : 0
  const totalTests = results ? results.length : 0

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="mb-6">
        <button
          onClick={runTests}
          disabled={loading}
          className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 font-medium"
        >
          {loading ? 'Running Tests...' : 'Run Test Suite'}
        </button>
      </div>

      {results && (
        <div>
          {/* Summary */}
          <div className="mb-6 p-4 rounded-lg bg-blue-50 border border-blue-200">
            <div className="flex justify-between items-center">
              <div>
                <p className="text-sm text-gray-600">Test Results</p>
                <p className="text-2xl font-bold text-gray-900">
                  {passedTests} / {totalTests} Passed
                </p>
              </div>
              <div className={`text-4xl font-bold ${passedTests === totalTests ? 'text-green-600' : 'text-red-600'}`}>
                {passedTests === totalTests ? '✓' : '✗'}
              </div>
            </div>
          </div>

          {/* Test Results */}
          <div className="space-y-4">
            {results.map((result) => (
              <div
                key={result.test_id}
                className={`border rounded-lg p-4 ${
                  result.passed ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
                }`}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center">
                    <span className={`mr-3 text-xl ${result.passed ? 'text-green-600' : 'text-red-600'}`}>
                      {result.passed ? '✓' : '✗'}
                    </span>
                    <h3 className="text-lg font-semibold text-gray-900">{result.test_id}</h3>
                  </div>
                </div>

                {!result.passed && (
                  <div className="mt-3 space-y-2">
                    {result.error && (
                      <div>
                        <p className="text-sm font-medium text-gray-700">Error:</p>
                        <p className="text-sm text-red-600 font-mono">{result.error}</p>
                      </div>
                    )}
                    <details className="cursor-pointer">
                      <summary className="text-sm font-medium text-gray-600">View Details</summary>
                      <div className="mt-2 space-y-2 text-xs font-mono">
                        <div>
                          <p className="font-semibold text-gray-700">Expected:</p>
                          <pre className="bg-gray-100 p-2 rounded overflow-auto">
                            {JSON.stringify(result.expected, null, 2)}
                          </pre>
                        </div>
                        <div>
                          <p className="font-semibold text-gray-700">Actual:</p>
                          <pre className="bg-gray-100 p-2 rounded overflow-auto">
                            {JSON.stringify(result.actual, null, 2)}
                          </pre>
                        </div>
                      </div>
                    </details>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
