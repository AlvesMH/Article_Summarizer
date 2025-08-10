export const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

export async function postJSON(path, body) {
  const res = await fetch(`${API_BASE}/api/${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

export async function postForm(path, formData) {
  const res = await fetch(`${API_BASE}/api/${path}`, {
    method: 'POST',
    body: formData
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}
