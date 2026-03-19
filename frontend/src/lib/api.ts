const API_BASE = import.meta.env.PROD
  ? 'https://progenx-api.onrender.com/api'
  : '/api'

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('pf_token')
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...((options.headers as Record<string, string>) || {}),
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers })

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(error.detail || `Request failed: ${res.status}`)
  }

  return res.json()
}

// Auth
export const auth = {
  signup: (email: string, password: string, name: string) =>
    request<AuthResponse>('/auth/signup', { method: 'POST', body: JSON.stringify({ email, password, name }) }),
  login: (email: string, password: string) =>
    request<AuthResponse>('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),
  me: () => request<UserProfile>('/auth/me'),
}

// Designs
export const designs = {
  generate: (data: DesignRequest) =>
    request<DesignResponse>('/designs/generate', { method: 'POST', body: JSON.stringify(data) }),
  refine: (designId: string, message: string) =>
    request<DesignResponse>(`/designs/${designId}/refine`, { method: 'POST', body: JSON.stringify({ message }) }),
  history: () => request<DesignResponse[]>('/designs/history'),
  get: (id: string) => request<DesignResponse>(`/designs/${id}`),
  chat: (id: string) => request<ChatMessage[]>(`/designs/${id}/chat`),
  share: (id: string) => request<{ is_public: boolean }>(`/designs/${id}/share`, { method: 'POST' }),
}

// Billing
export const billing = {
  checkout: () =>
    request<{ checkout_url: string }>('/billing/checkout', { method: 'POST' }),
  portal: () =>
    request<{ portal_url: string }>('/billing/portal', { method: 'POST' }),
}

// Explore (public gallery)
export const explore = {
  list: () => request<DesignResponse[]>('/designs/explore'),
  get: (id: string) => request<DesignResponse>(`/designs/explore/${id}`),
}

// Stats (public, no auth)
export const stats = {
  get: () => request<{ users: number; designs: number }>('/stats'),
}

// Challenges
export const challenges = {
  daily: () => request<Challenge>('/challenges/daily'),
  random: () => request<Challenge>('/challenges/random'),
  all: () => request<Challenge[]>('/challenges/all'),
}

// Types
export interface AuthResponse {
  token: string; user_id: string; email: string; name: string; tier: string
}

export interface UserProfile {
  id: string; email: string; name: string; tier: string
  designs_this_month: number; monthly_limit: number
}

export interface DesignRequest {
  prompt: string; environment: string; safety_level: number; complexity: number
}

export interface DesignResponse {
  id: string
  status: string
  design_name: string
  host_organism: string
  organism_summary: string
  gene_circuit: GeneCircuit
  gene_sequences: Record<string, GeneSequenceResult>
  codon_optimized: Record<string, CodonOptResult>
  dna_sequence: string
  fasta_content: string
  genbank_content?: string
  plasmid_map_data: PlasmidMapData
  fba_results: FBAResults
  assembly_plan: AssemblyPlan
  safety_score: number
  safety_flags: string[]
  dual_use_assessment: string
  simulated_yield: string
  estimated_cost: string
  target_product: string
  generation_time_sec: number
  model_used: string
  is_public: boolean
  disclaimer: string
  is_conceptual?: boolean
  conceptual_banner?: string
  non_registry_genes?: string[]
  conceptual_genes?: string[]
}

export interface GeneCircuit {
  genes: { name: string; function: string; source_organism: string; size_bp?: number }[]
  promoters: string[]
  terminators: string[]
  regulatory_elements: string[]
}

export interface GeneSequenceResult {
  raw_sequence: string
  accession: string
  length: number
  source: string
  type: string
  description: string
  function_validation?: { score: number; match: boolean; reason: string }
  conceptual_only?: boolean
  warning?: string
  confidence?: 'high' | 'medium' | 'low' | 'none' | 'unknown'
  confidence_reason?: string
  variant_predictions?: {
    beneficial_mutations: { position: number; wild_type: string; mutant: string; score: number; notation: string }[]
    total_beneficial: number
    total_scored: number
    model_used: string
    method: string
    note: string
  }
}

export interface CodonOptResult {
  optimized_dna: string
  length_bp: number
  chassis: string
  cai_score: number | null
  gc_content: number
}

export interface PlasmidMapData {
  png_base64: string
  features: { start: number; end: number; label: string; type: string; color: string }[]
  feature_data: { name: string; start: number; end: number; size_bp: number; function: string }[]
  total_length_bp: number
}

export interface FBAResults {
  wild_type_growth_rate: number
  burdened_growth_rate: number
  growth_reduction_pct: number
  adjusted_growth_rate: number
  environment: string
  theoretical_product_yield_g_per_g_substrate: number
  estimated_titer_g_per_L: number
  model_used: string
  model_genes: number
  model_reactions: number
  heterologous_genes: number
  metabolic_burden_estimate: string
  summary: string
  source: string
}

export interface AssemblyPlan {
  origin_of_replication: { name: string; copy_number: string; rationale: string; alternative: string }
  selection_marker: { name: string; gene: string; rationale: string }
  assembly_method: { name: string; description: string; steps: string[]; cost_note: string }
  kill_switch: { name: string; mechanism: string; rationale: string }
  rbs_notes: { strategy: string; details: string[]; tool_note: string }
  estimated_total_size_bp: number
  summary: string
  primers?: {
    gene: string
    forward: { sequence: string; length: number; tm: number; gc: number }
    reverse: { sequence: string; length: number; tm: number; gc: number }
    expected_product_bp: number
    note: string
  }[]
}

export interface ChatMessage {
  role: string; content: string; created_at: string
}

export interface Challenge {
  id: string; title: string; prompt: string; category: string; difficulty: string; impact: string
}
