const DEFAULT_API_URL = process.env.NODE_ENV === "development"
  ? "http://localhost:8000/api/v1"
  : "/api/v1";

const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? DEFAULT_API_URL).replace(/\/$/, "");

export type DocumentListItem = {
  id: string;
  filename: string;
  course: string | null;
  status: "uploaded" | "processing" | "ready" | "failed";
  uploaded_date: string;
  page_count: number;
  size_bytes: number;
  error_message: string | null;
};

export type DocumentDetailResponse = DocumentListItem & {
  mime_type: string;
  size_bytes: number;
  storage_key: string;
  extracted_text: string;
  analysis: {
    course_name: string | null;
    topics: string[];
    modules: string[];
    important_concepts: string[];
    assignments_mentioned: string[];
    exam_dates: string[];
    recommended_study_priority: string;
    subject_code: string | null;
    instructor: string | null;
    semester: string | null;
    academic_year: string | null;
    learning_outcomes: string[];
    references: string[];
    topic_hierarchy: Array<{ name: string; topics: string[] }>;
    timeline_events: Array<{ event: string; date: string; priority: string; kind: string }>;
  };
  updated_at: string;
};

export type DashboardResponse = {
  has_data: boolean;
  student_profile: { display_name: string; email: string; timezone: string; documents_uploaded: number; active_courses: number };
  detected_courses: Array<{ id: string; name: string; code: string | null; confidence: number; topic_count: number; assignment_count: number; exam_count: number }>;
  knowledge_graph: { nodes: Array<{ id: string; label: string; type: string; value: number | null }>; edges: Array<{ source: string; target: string; relation: string }> };
  current_confidence: number;
  weak_topics: Array<{ name: string; course: string; confidence: number; importance: number }>;
  strong_topics: Array<{ name: string; course: string; confidence: number; importance: number }>;
  revision_timeline: Array<{ label: string; date: string; detail: string; kind: string }>;
  upcoming_deadlines: Array<{ title: string; due_date: string; priority: string; source: string }>;
  academic_health: number;
  recommended_study_load: number;
  learning_dna: Record<string, number>;
  memory_decay: Array<{ topic: string; course: string; today: number; tomorrow: number; three_days: number; one_week: number; two_weeks: number }>;
  future_timeline: Array<{ label: string; date: string; detail: string; kind: string }>;
  academic_health_factors: Array<{ label: string; value: number; detail: string }>;
  onboarding_message: string | null;
  recent_documents: DocumentListItem[];
};

export type TwinResponse = Omit<DashboardResponse, "onboarding_message" | "recent_documents">;

export type DocumentUploadResponse = {
  filename: string;
  page_count: number;
  extracted_text: string;
  analysis: {
    course_name: string | null;
    topics: string[];
    modules: string[];
    important_concepts: string[];
    assignments_mentioned: string[];
    exam_dates: string[];
    recommended_study_priority: string;
  };
  document_id: string;
  status: DocumentListItem["status"];
};

export type SimulationRequest = {
  study_hours_per_day: number;
  days_skipped: number;
  attendance: number;
  exam_date: string | null;
  sleep_hours: number;
  revision_frequency: number;
};

export type SimulationPrediction = {
  knowledge_score: number;
  confidence: number;
  academic_health: number;
  recommended_study_load: number;
  explanation: string;
  model_version: string;
  expected_exam_score: number;
  memory_retention: number;
  stress: number;
};

function buildHeaders(initHeaders?: HeadersInit, token?: string, hasBody = false) {
  return {
    ...(hasBody ? { "Content-Type": "application/json" } : {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...initHeaders,
  };
}

export async function apiFetch<T>(path: string, init: RequestInit = {}, token?: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, { ...init, headers: buildHeaders(init.headers, token, !(init.body instanceof FormData)) });
  if (!response.ok) throw new Error((await response.json().catch(() => null))?.detail ?? "Request failed");
  if (response.status === 204) return undefined as T;
  const contentType = response.headers.get("content-type") ?? "";
  if (!contentType.includes("application/json")) return undefined as T;
  return response.json() as Promise<T>;
}

export async function fetchDashboard(token?: string) {
  return apiFetch<DashboardResponse>("/dashboard", { method: "GET" }, token);
}

export async function fetchTwin(token?: string) {
  return apiFetch<TwinResponse>("/twin", { method: "GET" }, token);
}

export async function fetchDocuments(token?: string) {
  return apiFetch<DocumentListItem[]>("/documents", { method: "GET" }, token);
}

export async function fetchDocumentDetail(documentId: string, token?: string) {
  return apiFetch<DocumentDetailResponse>(`/documents/${documentId}`, { method: "GET" }, token);
}

export function uploadDocument(file: File, subjectId?: string, token?: string, onProgress?: (progress: number) => void) {
  const form = new FormData();
  form.append("file", file);
  if (subjectId) form.append("subject_id", subjectId);
  return new Promise<DocumentUploadResponse>((resolve, reject) => {
    const request = new XMLHttpRequest();
    request.open("POST", `${API_URL}/documents/upload`);
    if (token) request.setRequestHeader("Authorization", `Bearer ${token}`);
    request.upload.onprogress = (event) => { if (event.lengthComputable) onProgress?.(Math.round((event.loaded / event.total) * 100)); };
    request.onload = () => {
      const body = request.responseText ? JSON.parse(request.responseText) : null;
      if (request.status >= 200 && request.status < 300) resolve(body);
      else reject(new Error(body?.detail ?? "Upload failed"));
    };
    request.onerror = () => reject(new Error("Network error during upload"));
    request.send(form);
  });
}

export async function reprocessDocument(documentId: string, token?: string) {
  return apiFetch<DocumentUploadResponse>(`/documents/${documentId}/reprocess`, { method: "POST" }, token);
}

export async function addManualTopic(documentId: string, name: string, module?: string, token?: string) {
  return apiFetch<DocumentDetailResponse>(`/documents/${documentId}/topics`, { method: "POST", body: JSON.stringify({ name, module }) }, token);
}

export async function deleteDocument(documentId: string, token?: string) {
  return apiFetch<void>(`/documents/${documentId}`, { method: "DELETE" }, token);
}

export async function simulateScenario(payload: SimulationRequest, token?: string) {
  return apiFetch<SimulationPrediction>("/simulate", { method: "POST", body: JSON.stringify(payload) }, token);
}
