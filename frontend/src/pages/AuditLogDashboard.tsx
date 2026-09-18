import { useEffect, useState } from "react";
import { fetchAuditLogs, verifyAuditChain } from "../api/auditLogs";
import type { AuditChainVerification, AuditLog } from "../types/auditLog";

/**
 * Sprint 1 placeholder screen: proves the frontend can reach the
 * FastAPI backend and render real audit records plus the chain
 * integrity check. Styling, pagination, filtering, and RBAC-gated
 * views are intentionally deferred to later sprints.
 */
export function AuditLogDashboard() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [verification, setVerification] = useState<AuditChainVerification | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [logData, verifyData] = await Promise.all([
          fetchAuditLogs(),
          verifyAuditChain(),
        ]);
        setLogs(logData);
        setVerification(verifyData);
      } catch (err) {
        setError(
          "Could not reach the audit log API. Is the backend running? " +
            (err instanceof Error ? err.message : String(err)),
        );
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return <p>Loading audit logs...</p>;
  if (error) return <p style={{ color: "crimson" }}>{error}</p>;

  return (
    <div>
      <h1>Audit Log Dashboard</h1>

      {verification && (
        <p>
          Chain integrity:{" "}
          <strong style={{ color: verification.is_valid ? "green" : "crimson" }}>
            {verification.is_valid ? "VALID" : "TAMPERED"}
          </strong>{" "}
          ({verification.records_checked} records checked)
        </p>
      )}

      <table cellPadding={6} style={{ borderCollapse: "collapse", width: "100%" }}>
        <thead>
          <tr style={{ textAlign: "left", borderBottom: "1px solid #ccc" }}>
            <th>Seq</th>
            <th>Time</th>
            <th>Actor role</th>
            <th>Action</th>
            <th>Resource</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log) => (
            <tr key={log.id} style={{ borderBottom: "1px solid #eee" }}>
              <td>{log.sequence}</td>
              <td>{new Date(log.created_at).toLocaleString()}</td>
              <td>{log.actor_role}</td>
              <td>{log.action}</td>
              <td>
                {log.resource_type}
                {log.resource_id ? ` / ${log.resource_id}` : ""}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {logs.length === 0 && <p>No audit events recorded yet.</p>}
    </div>
  );
}
