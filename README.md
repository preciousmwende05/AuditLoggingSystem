
# Immutable Audit Logging and Compliance System for a Healthcare Platform

Fourth year computer science project. An audit logging system for a company that supports elderly patients and their caregivers. Because the data is sensitive, every access and change to a patient record must be recorded in a log that cannot be altered or deleted after the fact, and that can be independently verified.

The system deals with elderly patients' and caregivers' data, which is sensitive. Design decisions made with that in mind so far: role is tracked on every audit event (`actor_role`), the audit table itself cannot be altered after the fact even by an administrator, and passwords are hashed with bcrypt, never stored or logged in plain text. It has role-based access control on the API itself (so only authorized roles can read or write specific resources).It deals with PostgreSQL, React, Python and anomaly detection.


