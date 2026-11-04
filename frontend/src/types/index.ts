export interface User {
  id: number;
  email: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Detection {
  id: number;
  class_name: string;
  confidence: number;
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface DiagnosisResult {
  id: number;
  original_image_url: string;
  result_image_url: string | null;
  status: 'detected' | 'no_detection';
  inference_time: number | null;
  created_at: string;
  detections: Detection[];
  summary: string;
}

export interface DiagnosisListItem {
  id: number;
  original_image_url: string;
  result_image_url: string | null;
  status: string;
  inference_time: number | null;
  created_at: string;
  detection_count: number;
  primary_disease: string | null;
  max_confidence: number | null;
}

export interface Disease {
  id: number;
  class_name: string;
  display_name: string;
  description: string | null;
  symptoms: string | null;
  prevention: string | null;
  treatment: string | null;
  treatment_steps: string | null;
  recovery_info: string | null;
  image_path: string | null;
}

export interface RecentDiagnosisItem {
  id: number;
  status: string;
  created_at: string;
  detection_count: number;
  primary_disease: string | null;
  original_image_url: string;
}

export interface DashboardStats {
  total_diagnoses: number;
  detected_count: number;
  no_detection_count: number;
  disease_distribution: Record<string, number>;
  recent_diagnoses: RecentDiagnosisItem[];
}
