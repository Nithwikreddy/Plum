'use client'

interface Decision {
  claim_id: string
  decision: string
  approved_amount: number
  rejection_reasons?: string[]
  deductions?: {
    copay?: number
    network_discount?: number
  }
  flags?: string[]
  cashless_approved?: boolean
  notes: string
  confidence_score: number
  next_steps: string
}

export default function DecisionDisplay({ decision }: { decision: Decision }) {
  const getDecisionColor = (decision: string) => {
    switch (decision) {
      case 'APPROVED':
        return 'bg-green-50 border-green-200'
      case 'REJECTED':
        return 'bg-red-50 border-red-200'
      case 'PARTIAL':
        return 'bg-yellow-50 border-yellow-200'
      case 'MANUAL_REVIEW':
        return 'bg-blue-50 border-blue-200'
      default:
        return 'bg-gray-50 border-gray-200'
    }
  }

  const getDecisionBadgeColor = (decision: string) => {
    switch (decision) {
      case 'APPROVED':
        return 'bg-green-100 text-green-800'
      case 'REJECTED':
        return 'bg-red-100 text-red-800'
      case 'PARTIAL':
        return 'bg-yellow-100 text-yellow-800'
      case 'MANUAL_REVIEW':
        return 'bg-blue-100 text-blue-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className={`border rounded-lg p-6 ${getDecisionColor(decision.decision)}`}>
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <p className="text-sm text-gray-600">Claim ID</p>
            <p className="text-lg font-semibold text-gray-900">{decision.claim_id}</p>
          </div>
          <span className={`px-4 py-2 rounded-full font-semibold text-lg ${getDecisionBadgeColor(decision.decision)}`}>
            {decision.decision}
          </span>
        </div>
      </div>

      {/* Approved Amount */}
      {decision.decision === 'APPROVED' || decision.decision === 'PARTIAL' ? (
        <div className="bg-white rounded-lg p-4 mb-6">
          <p className="text-sm text-gray-600">Approved Amount</p>
          <p className="text-3xl font-bold text-green-600">₹{decision.approved_amount.toLocaleString('en-IN')}</p>
        </div>
      ) : null}

      {/* Deductions */}
      {decision.deductions && Object.keys(decision.deductions).length > 0 ? (
        <div className="bg-white rounded-lg p-4 mb-6">
          <h3 className="font-semibold text-gray-900 mb-3">Deductions</h3>
          <div className="space-y-2">
            {decision.deductions.copay ? (
              <div className="flex justify-between">
                <span className="text-gray-700">Co-pay</span>
                <span className="text-gray-900 font-medium">₹{decision.deductions.copay.toLocaleString('en-IN')}</span>
              </div>
            ) : null}
            {decision.deductions.network_discount ? (
              <div className="flex justify-between">
                <span className="text-gray-700">Network Discount</span>
                <span className="text-gray-900 font-medium">-₹{decision.deductions.network_discount.toLocaleString('en-IN')}</span>
              </div>
            ) : null}
          </div>
        </div>
      ) : null}

      {/* Rejection Reasons */}
      {decision.rejection_reasons && decision.rejection_reasons.length > 0 ? (
        <div className="bg-white rounded-lg p-4 mb-6">
          <h3 className="font-semibold text-gray-900 mb-3">Rejection Reasons</h3>
          <ul className="space-y-2">
            {decision.rejection_reasons.map((reason, idx) => (
              <li key={idx} className="flex items-start text-gray-700">
                <span className="text-red-600 mr-2">•</span>
                <span>{reason}</span>
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      {/* Flags */}
      {decision.flags && decision.flags.length > 0 ? (
        <div className="bg-white rounded-lg p-4 mb-6">
          <h3 className="font-semibold text-gray-900 mb-3">Alerts</h3>
          <ul className="space-y-2">
            {decision.flags.map((flag, idx) => (
              <li key={idx} className="flex items-start text-gray-700">
                <span className="text-orange-600 mr-2">⚠</span>
                <span>{flag}</span>
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      {/* Notes */}
      <div className="bg-white rounded-lg p-4 mb-6">
        <h3 className="font-semibold text-gray-900 mb-2">Notes</h3>
        <p className="text-gray-700">{decision.notes}</p>
      </div>

      {/* Cashless Status */}
      {decision.cashless_approved ? (
        <div className="bg-white rounded-lg p-4 mb-6">
          <h3 className="font-semibold text-gray-900 mb-2">Cashless Approval</h3>
          <p className="text-green-600 font-medium">✓ Cashless claim approved at network hospital</p>
        </div>
      ) : null}

      {/* Confidence Score */}
      <div className="bg-white rounded-lg p-4 mb-6">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-gray-900">Confidence Score</h3>
          <div className="flex items-center">
            <div className="w-32 bg-gray-200 rounded-full h-2 mr-3">
              <div
                className={`h-2 rounded-full transition-all ${
                  decision.confidence_score > 0.8
                    ? 'bg-green-600'
                    : decision.confidence_score > 0.6
                    ? 'bg-yellow-600'
                    : 'bg-red-600'
                }`}
                style={{ width: `${decision.confidence_score * 100}%` }}
              ></div>
            </div>
            <span className="text-lg font-semibold text-gray-900">
              {(decision.confidence_score * 100).toFixed(0)}%
            </span>
          </div>
        </div>
      </div>

      {/* Next Steps */}
      <div className="bg-white rounded-lg p-4">
        <h3 className="font-semibold text-gray-900 mb-2">Next Steps</h3>
        <p className="text-gray-700">{decision.next_steps}</p>
      </div>

      {/* Raw JSON */}
      <div className="mt-6 pt-6 border-t">
        <details className="cursor-pointer">
          <summary className="text-sm font-medium text-gray-600 hover:text-gray-900">
            View Raw JSON
          </summary>
          <pre className="mt-3 bg-gray-100 p-4 rounded-md text-xs overflow-auto">
            {JSON.stringify(decision, null, 2)}
          </pre>
        </details>
      </div>
    </div>
  )
}
