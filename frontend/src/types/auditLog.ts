export interface AuditLog {
  id: string;
  sequence: number;
  actor_id: string | null;
  actor_role: string;
  action: string;
  resource_type: string;
  resource_id: string | null;
  metadata_json: Record<string, unknown> | null;
  ip_address: string | null;
  previous_hash: string | null;
  record_hash: string;
  created_at: string;
}

export interface AuditChainVerification {
  is_valid: boolean;
  records_checked: number;
  first_broken_record_id: string | null;
}
