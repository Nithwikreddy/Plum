'use client'

import { useState, useEffect } from 'react'

interface LineItem {
  type: string
  description: string
  amount: number
}

interface ClaimFormProps {
  onSubmit: (data: any) => void
  loading: boolean
}

export default function ClaimForm({ onSubmit, loading }: ClaimFormProps) {
  const STORAGE_KEY = 'opd_claim_form'

  const defaultData = {
    member_id: 'EMP001',
    member_name: 'John Doe',
    treatment_date: '2024-09-15',
    hospital: 'Apollo',
    is_network: true,
    cashless_requested: false,
    doctor_reg: 'KA/45678/2015',
    diagnosis: 'Viral fever',
    line_items: [
      { type: 'consultation', description: 'General Consultation', amount: 1000 },
      { type: 'diagnostic', description: 'CBC + Dengue', amount: 500 },
    ],
  }

  const loadInitial = () => {
    try {
      if (typeof window === 'undefined') return defaultData
      const raw = window.localStorage.getItem(STORAGE_KEY)
      if (!raw) return defaultData
      const parsed = JSON.parse(raw)
      // Ensure fallback values exist
      return { ...defaultData, ...parsed }
    } catch (e) {
      return defaultData
    }
  }

  const [formData, setFormData] = useState(() => loadInitial())

  const [lineItems, setLineItems] = useState<LineItem[]>(() => (loadInitial().line_items || defaultData.line_items))
  const [mounted, setMounted] = useState(false)

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value,
    })
  }

  const handleLineItemChange = (index: number, field: string, value: any) => {
    const newItems = [...lineItems]
    newItems[index] = { ...newItems[index], [field]: value }
    setLineItems(newItems)
  }

  const addLineItem = () => {
    setLineItems([...lineItems, { type: 'consultation', description: '', amount: 0 }])
  }

  const removeLineItem = (index: number) => {
    setLineItems(lineItems.filter((_, i) => i !== index))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const totalAmount = lineItems.reduce((sum, item) => sum + item.amount, 0)

    const submitData = {
      ...formData,
      line_items: lineItems,
      claim_amount: totalAmount,
      submission_date: new Date().toISOString().split('T')[0],
      prescription: {
        doctor_reg: formData.doctor_reg,
        diagnosis: formData.diagnosis,
        valid: true,
      },
    }

    onSubmit(submitData)
  }

  // Persist form state to localStorage so edits survive reloads
  useEffect(() => {
    try {
      if (typeof window === 'undefined') return
      const payload = { ...formData, line_items: lineItems }
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(payload))
    } catch (e) {
      // ignore storage errors
    }
  }, [formData, lineItems])

  // Mark component as mounted to avoid server/client rendering mismatches
  useEffect(() => {
    setMounted(true)
  }, [])

  const totalAmount = lineItems.reduce((sum, item) => sum + item.amount, 0)

  return (
    <form onSubmit={handleSubmit} className="space-y-6 bg-white p-6 rounded-lg shadow">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Member ID</label>
          <input
            type="text"
            name="member_id"
            value={formData.member_id}
            onChange={handleInputChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border px-3 py-2"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Member Name</label>
          <input
            type="text"
            name="member_name"
            value={formData.member_name}
            onChange={handleInputChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border px-3 py-2"
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Treatment Date</label>
          <input
            type="date"
            name="treatment_date"
            value={formData.treatment_date}
            onChange={handleInputChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border px-3 py-2"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Hospital</label>
          <select
            name="hospital"
            value={formData.hospital}
            onChange={handleInputChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border px-3 py-2"
          >
            <option value="Apollo">Apollo</option>
            <option value="Fortis">Fortis</option>
            <option value="Max">Max</option>
            <option value="Manipal">Manipal</option>
            <option value="Narayana">Narayana</option>
            <option value="Other">Other</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="flex items-center">
          <input
            type="checkbox"
            name="is_network"
            checked={formData.is_network}
            onChange={handleInputChange}
            className="h-4 w-4 text-blue-600"
          />
          <label className="ml-2 block text-sm text-gray-700">Network Hospital</label>
        </div>
        <div className="flex items-center">
          <input
            type="checkbox"
            name="cashless_requested"
            checked={formData.cashless_requested}
            onChange={handleInputChange}
            className="h-4 w-4 text-blue-600"
          />
          <label className="ml-2 block text-sm text-gray-700">Cashless Requested</label>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Doctor Registration</label>
          <input
            type="text"
            name="doctor_reg"
            placeholder="e.g., KA/45678/2015"
            value={formData.doctor_reg}
            onChange={handleInputChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border px-3 py-2"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Diagnosis</label>
          <input
            type="text"
            name="diagnosis"
            value={formData.diagnosis}
            onChange={handleInputChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border px-3 py-2"
          />
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Line Items</h3>
        <div className="space-y-3">
          {lineItems.map((item, index) => (
            <div key={index} className="flex gap-2 items-end">
              <select
                value={item.type}
                onChange={(e) => handleLineItemChange(index, 'type', e.target.value)}
                className="flex-1 rounded-md border-gray-300 shadow-sm border px-3 py-2"
              >
                <option value="consultation">Consultation</option>
                <option value="diagnostic">Diagnostic</option>
                <option value="pharmacy">Pharmacy</option>
                <option value="dental">Dental</option>
                <option value="alternative">Alternative</option>
                <option value="vision">Vision</option>
              </select>
              <input
                type="text"
                placeholder="Description"
                value={item.description}
                onChange={(e) => handleLineItemChange(index, 'description', e.target.value)}
                className="flex-1 rounded-md border-gray-300 shadow-sm border px-3 py-2"
              />
              <input
                type="number"
                placeholder="Amount"
                value={item.amount}
                onChange={(e) => handleLineItemChange(index, 'amount', parseFloat(e.target.value) || 0)}
                className="w-24 rounded-md border-gray-300 shadow-sm border px-3 py-2"
              />
              <button
                type="button"
                onClick={() => removeLineItem(index)}
                className="px-3 py-2 text-red-600 hover:text-red-800 font-medium"
              >
                Remove
              </button>
            </div>
          ))}
        </div>
        <button
          type="button"
          onClick={addLineItem}
          className="mt-3 px-4 py-2 bg-gray-200 text-gray-900 rounded-md hover:bg-gray-300 font-medium"
        >
          + Add Item
        </button>
      </div>

      <div className="bg-blue-50 p-4 rounded-md">
        <div className="text-lg font-semibold text-gray-900">
          Total Claim Amount: ₹{mounted ? totalAmount.toLocaleString('en-IN') : totalAmount}
        </div>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 font-medium"
      >
        {loading ? 'Processing...' : 'Submit Claim'}
      </button>
    </form>
  )
}
