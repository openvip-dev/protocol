# OpenVIP HTTP Binding v1.0

This document specifies how OpenVIP messages are transported over HTTP.

## Overview

The HTTP binding uses REST-style endpoints with Server-Sent Events (SSE) for
message delivery. Agents connect via SSE to receive messages — the SSE
connection itself acts as registration.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/agents/{agent_id}/messages` | Subscribe to messages (SSE) |
| `POST` | `/agents/{agent_id}/messages` | Send a message to an agent |
| `POST` | `/speech` | Text-to-speech request |
| `GET` | `/status` | Engine status |
| `GET` | `/status/stream` | Subscribe to status changes (SSE) |
| `POST` | `/control` | Control commands |

## Content Types

| Type | Usage |
|------|-------|
| `application/json` | Request/response bodies |
| `text/event-stream` | SSE subscriptions |

## Agent Lifecycle

Agents are **ephemeral**. An agent exists only while its SSE connection is open:

1. Agent connects via `GET /agents/{agent_id}/messages`
2. Server creates an internal queue for this agent
3. Messages are delivered as SSE events
4. When the client disconnects, the agent is automatically de-registered

No explicit registration endpoint is needed — the SSE connection **is** the
registration.

## Examples

### Subscribe to Messages (SSE)

The agent connects and stays connected. Messages arrive as SSE events.

```bash
curl http://localhost:8770/agents/550e8400-e29b-41d4-a716-446655440000/messages
```

Response (SSE stream, connection stays open):
```
data: {"openvip":"1.0","type":"transcription","id":"...","text":"turn on the light","language":"en"}

data: {"openvip":"1.0","type":"transcription","id":"...","text":"hello world"}
```

Keepalive (sent every 30s if no data):
```
: keepalive
```

### Send a Message to an Agent

```bash
curl -X POST http://localhost:8770/agents/550e8400-e29b-41d4-a716-446655440000/messages \
  -H "Content-Type: application/json" \
  -d '{
    "openvip": "1.0",
    "type": "transcription",
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2026-02-06T10:30:00Z",
    "text": "turn on the light",
    "language": "en"
  }'
```

Response:
```json
{"openvip": "1.0", "status": "ok", "ref": "550e8400-e29b-41d4-a716-446655440000"}
```

### Text-to-Speech Request

```bash
curl -X POST http://localhost:8770/speech \
  -H "Content-Type: application/json" \
  -d '{
    "openvip": "1.0",
    "type": "speech",
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "timestamp": "2026-02-06T10:30:05Z",
    "text": "Light turned on",
    "language": "en"
  }'
```

Response:
```json
{"openvip": "1.0", "status": "ok", "duration_ms": 1250, "ref": "660e8400-e29b-41d4-a716-446655440001"}
```

### Get Status

```bash
curl http://localhost:8770/status
```

Response:
```json
{
  "openvip": "1.0",
  "stt": { "enabled": true, "active": true },
  "tts": { "enabled": true },
  "connected_agents": ["claude", "terminal"],
  "platform": {
    "name": "MyEngine",
    "version": "0.1.0",
    "uptime_seconds": 3600
  }
}
```

### Subscribe to Status Changes (SSE)

```bash
curl http://localhost:8770/status/stream
```

Response (SSE stream, connection stays open):
```
data: {"openvip":"1.0","stt":{"enabled":true,"active":true},"tts":{"enabled":true},"connected_agents":["claude"],"platform":{...}}

data: {"openvip":"1.0","stt":{"enabled":true,"active":false},"tts":{"enabled":true},"connected_agents":["claude"],"platform":{...}}
```

Events are sent only on state transitions (`stt`, `tts`, `connected_agents`, etc.).
Keepalive comments (`: keepalive`) are sent every 30s if no events.

Clients that cannot use SSE should fall back to polling `GET /status`.

### Control Commands

```bash
curl -X POST http://localhost:8770/control \
  -H "Content-Type: application/json" \
  -d '{"openvip": "1.0", "id": "770e8400-e29b-41d4-a716-446655440000", "command": "stt.stop"}'
```

Response:
```json
{"openvip": "1.0", "status": "ok", "ref": "770e8400-e29b-41d4-a716-446655440000"}
```

Available commands:
- `stt.start` — Start speech-to-text
- `stt.stop` — Stop speech-to-text
- `engine.shutdown` — Graceful shutdown

## Error Responses

```json
{
  "openvip": "1.0",
  "error": "Agent not found",
  "code": "NOT_FOUND",
  "ref": "550e8400-e29b-41d4-a716-446655440000"
}
```

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_FORMAT` | 400 | Malformed request |
| `MISSING_FIELD` | 400 | Required field missing |
| `NOT_FOUND` | 404 | Agent not connected |
| `CONFLICT` | 409 | Agent ID already connected |
| `INTERNAL_ERROR` | 500 | Server error |

## Reconnection

If the SSE connection drops, the client should reconnect. Upon reconnection,
a new queue is created. Messages sent while disconnected are lost (ephemeral
model).

## References

- [OpenVIP Protocol v1.0](../../protocol/openvip-1.0.md)
- [OpenAPI Specification](./openapi.yaml)
