# OpenVIP - Open Voice Interaction Protocol

**OpenVIP** is an open standard for transmitting voice interaction messages between applications, devices, and services.

> *Voice interaction = voice input + voice output. OpenVIP handles the full loop.*

## Why OpenVIP?

Voice assistants are everywhere, but there's no open standard for voice interaction. OpenVIP fills this gap:

- **One format, many consumers** — Send voice messages to any compatible system
- **Transport agnostic** — HTTP, WebSockets, MQTT (v1.0 uses HTTP/SSE)
- **Simple core** — Minimal required fields, maximum extensibility
- **Best-effort** — Unidirectional, fire-and-forget, simple enough for constrained devices
- **Extensible** — Structured metadata via `x_` extension fields
- **Observable** — Built-in tracing via `trace_id`/`parent_id` (OpenTelemetry-style)

## Quick Start

```json
{
  "openvip": "1.0",
  "type": "transcription",
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-02-06T10:30:00Z",
  "text": "Turn on the kitchen light",
  "language": "en",
  "confidence": 0.95
}
```

## Specification

| Document | Description |
|----------|-------------|
| [Protocol v1.0](protocol/openvip-1.0.md) | Core message format |
| [HTTP Binding](bindings/http/) | REST + SSE transport |

## Message Types

| Type | Direction | Description |
|------|-----------|-------------|
| `transcription` | Engine → Agent | Transcribed text from speech-to-text |
| `speech` | Client → Engine | Text-to-speech request |

## Extension Fields

Messages can be enriched with `x_` extension fields — structured JSON objects
that carry metadata for domain-specific use cases.

### Standard Extensions

| Extension | Description |
|-----------|-------------|
| `x_input` | Text input behavior (submit, newline, trigger) |
| `x_agent_switch` | Agent routing (switch active agent) |

```json
{
  "openvip": "1.0",
  "type": "transcription",
  "id": "...",
  "timestamp": "...",
  "text": "fix the login bug",
  "x_input": {
    "submit": true,
    "trigger": "ok send",
    "confidence": 0.95
  }
}
```

Custom extensions use `x_<vendor_name>` prefix (e.g., `x_bticino`, `x_telegram`).
See the [protocol spec](protocol/openvip-1.0.md) for details.

## Tracing

Messages support OpenTelemetry-style tracing via optional fields:

| Field | Description |
|-------|-------------|
| `trace_id` | ID of the original message that started the chain |
| `parent_id` | ID of the message this one was derived from |

This enables full observability without external tooling.

## Examples

See the [examples/](examples/) directory for complete message samples.

## Schema

JSON Schema for validation: [schema/v1.0.json](schema/v1.0.json)

## Implementations

| Project | Language | Type | Description |
|---------|----------|------|-------------|
| [Dictare](https://github.com/dragfly/dictare) | Python | Engine + Client | Reference implementation — voice layer for AI coding agents |
| [openvip SDK](https://pypi.org/project/openvip/) | Python | Client SDK | Auto-generated from OpenAPI spec |

## Roadmap

### v1.0 (Current)
- Core message format (`transcription`, `speech`)
- HTTP binding with SSE
- Extension fields (`x_`) with standard extensions
- Built-in tracing (`trace_id`, `parent_id`)

### Planned
- Bidirectional communication
- WebSocket binding
- Authentication and authorization
- End-to-end encryption

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This specification is licensed under the [MIT License](LICENSE).

---

*OpenVIP is an open project. Contributions welcome!*
