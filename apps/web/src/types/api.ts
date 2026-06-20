export interface SyncResponse {
  files_checked: number;
  files_processed: number;
  sessions_upserted: number;
  providers: { name: string; processed: number }[];
  synced_at: string;
}

export interface DailyTokenPoint {
  date: string;
  input_tokens: number;
  output_tokens: number;
  cache_creation_tokens: number;
  cache_read_tokens: number;
  total_tokens: number;
}

export interface DailyCostPoint {
  date: string;
  estimated_cost: number;
  input_cost: number;
  output_cost: number;
  cache_cost: number;
}

export interface OverviewResponse {
  total_sessions: number;
  total_projects: number;
  total_input_tokens: number;
  total_output_tokens: number;
  total_cache_tokens: number;
  total_tokens: number;
  cost_all_time: number;
  cost_30d: number;
  cost_7d: number;
  active_projects_30d: number;
  token_trend: DailyTokenPoint[];
  cost_trend: DailyCostPoint[];
  most_active_project: string | null;
  most_used_model: string | null;
}

export interface ProjectSummary {
  id: number;
  name: string;
  slug: string;
  path: string;
  total_sessions: number;
  sessions_30d: number;
  total_input_tokens: number;
  total_output_tokens: number;
  total_tokens: number;
  estimated_cost: number;
  last_active: string | null;
  most_used_model: string | null;
}

export interface ProjectDetail extends ProjectSummary {
  total_messages: number;
  total_tool_calls: number;
  avg_session_duration_minutes: number | null;
}

export interface SessionSummary {
  id: number;
  session_id: string;
  provider: string;
  project_id: number;
  project_name: string;
  model: string | null;
  started_at: string | null;
  ended_at: string | null;
  duration_minutes: number | null;
  message_count: number;
  tool_call_count: number;
  total_input_tokens: number;
  total_output_tokens: number;
  total_tokens: number;
  estimated_cost: number;
  has_compaction: boolean;
}

export interface MessageDetail {
  id: number;
  role: string;
  content_summary: string | null;
  input_tokens: number;
  output_tokens: number;
  cache_creation_tokens: number;
  cache_read_tokens: number;
  model: string | null;
  timestamp: string | null;
}

export interface ToolUsageDetail {
  tool_name: string;
  execution_count: number;
  is_error_count: number;
}

export interface SessionDetail extends SessionSummary {
  messages: MessageDetail[];
  tool_usages: ToolUsageDetail[];
}

export interface PaginatedSessionList {
  items: SessionSummary[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface ToolStat {
  tool_name: string;
  execution_count: number;
  is_error_count: number;
  error_rate: number;
  session_count: number;
}

export interface CostDataPoint {
  period: string;
  input_cost: number;
  output_cost: number;
  cache_cost: number;
  total_cost: number;
  input_tokens: number;
  output_tokens: number;
}

export interface ModelCostBreakdown {
  model: string;
  input_tokens: number;
  output_tokens: number;
  estimated_cost: number;
  percentage: number;
}

export interface CostResponse {
  granularity: string;
  total_cost: number;
  total_input_cost: number;
  total_output_cost: number;
  total_cache_cost: number;
  data_points: CostDataPoint[];
  model_breakdown: ModelCostBreakdown[];
}

export interface InsightsResponse {
  peak_day_of_week: string | null;
  most_active_hour: number | null;
  avg_session_duration_minutes: number;
  longest_session_id: string | null;
  longest_session_duration_minutes: number;
  most_used_tool: string | null;
  most_used_tool_count: number;
  busiest_project: string | null;
  cache_hit_rate: number;
  avg_messages_per_session: number;
  total_tool_calls: number;
  total_sessions: number;
  total_messages: number;
}

export interface ModelStat {
  model: string;
  session_count: number;
  message_count: number;
  input_tokens: number;
  output_tokens: number;
  cache_creation_tokens: number;
  cache_read_tokens: number;
  estimated_cost: number;
}

export interface SessionsParams {
  page?: number;
  page_size?: number;
  project_id?: number;
  provider?: string;
  model?: string;
  search?: string;
  sort_by?: string;
  sort_order?: string;
}

export interface CostsParams {
  granularity?: "day" | "week" | "month";
  days?: number;
  project_id?: number;
}
