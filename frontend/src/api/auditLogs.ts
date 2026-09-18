import { apiClient } from "./client";
import type { AuditChainVerification, AuditLog } from "../types/auditLog";

export async function fetchAuditLogs(limit = 50): Promise<AuditLog[]> {
  const { data } = await apiClient.get<AuditLog[]>("/audit-logs", {
    params: { limit },
  });
  return data;
}

export async function verifyAuditChain(): Promise<AuditChainVerification> {
  const { data } = await apiClient.get<AuditChainVerification>("/audit-logs/verify");
  return data;
}
