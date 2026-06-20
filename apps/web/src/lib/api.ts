import axios from "axios";
import type {
  CostResponse,
  CostsParams,
  InsightsResponse,
  ModelStat,
  OverviewResponse,
  PaginatedSessionList,
  ProjectDetail,
  ProjectSummary,
  SessionDetail,
  SessionsParams,
  SyncResponse,
  ToolStat,
} from "@/types/api";

const client = axios.create({
  baseURL: typeof window !== "undefined" ? "" : (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"),
  timeout: 60_000,
});

export const api = {
  sync: () => client.post<SyncResponse>("/api/sync"),

  overview: () => client.get<OverviewResponse>("/api/overview"),

  projects: () => client.get<ProjectSummary[]>("/api/projects"),
  project: (id: number) => client.get<ProjectDetail>(`/api/projects/${id}`),

  sessions: (params?: SessionsParams) =>
    client.get<PaginatedSessionList>("/api/sessions", { params }),
  session: (id: number) => client.get<SessionDetail>(`/api/sessions/${id}`),

  tools: (params?: { project_id?: number; provider?: string }) =>
    client.get<ToolStat[]>("/api/tools", { params }),

  costs: (params?: CostsParams) =>
    client.get<CostResponse>("/api/costs", { params }),

  insights: () => client.get<InsightsResponse>("/api/insights"),

  models: () => client.get<ModelStat[]>("/api/models"),
};
