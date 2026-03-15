# OpenVIP Protocol v1.0

**Open Voice Interaction Protocol** — A lightweight, unidirectional, best-effort
protocol for transmitting voice interaction messages between applications,
devices, and services.

Voice interaction is inherently non-deterministic: speech recognition is
imperfect, commands may be misheard, and real-time audio processing introduces
latency and uncertainty. Rather than fighting this with complex reliability
mechanisms (acknowledgments, retries, ordering guarantees), OpenVIP embraces
it: messages flow in one direction without protocol-level confirmation, and
the cost of a lost message is simply repeating a voice command.

This deliberate simplicity makes OpenVIP easy to implement on any platform —
from IoT devices and microcontrollers to desktop applications and cloud
services — while providing a standard way to evolve voice interaction
semantics through extensions.

## Status

**v1.0** — Published specification.

## Scope

### This version defines

- Protocol identity (`openvip` field on every JSON payload)
- Message format (JSON)
- Message types (`transcription`, `speech`)
- Extension fields (`x_`) for structured metadata
- Standard extensions (`x_input`, `x_agent_switch`)
- Message tracing (`trace_id`, `parent_id`)
- Control, response, and error payloads
- HTTP binding with SSE for message delivery and status streaming

### Not covered (planned for future versions)

- Bidirectional communication (protocol-level request/response semantics)
- WebSocket binding
- Authentication and authorization
- End-to-end encryption

## Binding

| Binding | Use Case | Status |
|---------|----------|--------|
| [HTTP](../bindings/http/) | Local and network | v1.0 |
| WebSocket | Real-time bidirectional | Planned |

---

## Architecture

### Roles

| Role | Description | Examples |
|------|-------------|----------|
| **Engine** | Produces and receives voice interaction messages | STT engine, voice assistant |
| **Agent** | Sends and receives messages | Claude Code, Cursor, IDE plugin |

### Data Flow

```
┌────────┐  transcription  ┌───────┐
│ Engine │ ──────────────►  │ Agent │
│        │  ◄──────────────  │       │
└────────┘     speech       └───────┘
```

- **Engine → Agent**: `transcription` messages (speech-to-text results)
- **Agent → Engine**: `speech` messages (text-to-speech requests)

---

## Protocol Identity

**Every JSON payload** in the OpenVIP protocol — messages, status responses,
control requests, responses, and errors — MUST include the `openvip`
field with the protocol version. This ensures that every piece of data
exchanged is unambiguously identifiable as an OpenVIP payload.

```json
{"openvip": "1.0", ...}
```

Implementations MUST reject payloads missing the `openvip` field or carrying
an unsupported version.

---

## Message Format

All OpenVIP messages are JSON objects.

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `openvip` | string | Protocol version. Must be `"1.0"` |
| `type` | string | Message type (e.g., `"transcription"`, `"speech"`) |
| `id` | string | Unique message identifier (UUID v4) |
| `timestamp` | string | ISO 8601 timestamp with timezone |
| `text` | string | The transcribed or synthesized text |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `origin` | string | Producer identifier (e.g., `"myapp/1.0.0"`) |
| `language` | string | BCP 47 language tag (e.g., `"en"`, `"it"`) |
| `confidence` | float | Transcription confidence, 0.0–1.0 (only meaningful on `transcription`) |
| `partial` | boolean | If `true`, this is an incomplete transcription in progress (only on `transcription`) |
| `trace_id` | string | ID of the original message that started this chain |
| `parent_id` | string | ID of the message this one was derived from |

### Message Tracing

Messages support OpenTelemetry-style tracing for observability:

| Field | OpenTelemetry equivalent | Purpose |
|-------|--------------------------|---------|
| `id` | `span_id` | Identifies this specific message |
| `trace_id` | `trace_id` | Groups all messages from one utterance |
| `parent_id` | `parent_span_id` | Links to the immediate predecessor |

**Rules:**

- When a message passes through unchanged, `id` stays the same
- When a message is modified, a new `id` is generated
- `trace_id` always points to the original message
- `parent_id` points to the message this one was derived from

**Tracing fields are optional but coupled**: if one is present, both must be.
This is enforced by the JSON schema (`dependentRequired`).

- **Origin message** (first in chain): no `trace_id`, no `parent_id`
- **Derived message** (2nd onwards): both `trace_id` and `parent_id` present

A single message is not a trace — it's just a message. A trace begins when
a second message is derived from the first. The derived message creates the
trace retroactively by pointing to the original.

### Forward Compatibility

Receivers MUST ignore unknown fields. This allows processors to augment
messages with additional metadata and future extensions without breaking
existing agents.

---

## Message Types

### `transcription`

**Direction**: Engine → Agent
**Transport**: HTTP SSE (see [HTTP Binding](../bindings/http/))

Transcribed text from speech-to-text.

```json
{
  "openvip": "1.0",
  "type": "transcription",
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-02-06T10:30:00Z",
  "text": "fix the login bug",
  "language": "en",
  "confidence": 0.95,
  "origin": "myapp/1.0.0"
}
```

#### Partial transcriptions

When `partial` is `true`, the message contains an incomplete transcription
that is still in progress. This is useful for real-time feedback (e.g.,
subtitles, live transcription displays).

Consumers that act on final text (e.g., text injection, command execution)
SHOULD ignore messages with `partial: true`.

```json
{
  "openvip": "1.0",
  "type": "transcription",
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "timestamp": "2026-02-06T10:30:00Z",
  "text": "Turn on the",
  "partial": true,
  "origin": "myapp/1.0.0"
}
```

### `speech`

**Direction**: Client → Engine
**Transport**: HTTP POST (see [HTTP Binding](../bindings/http/))

Request text-to-speech synthesis.

```json
{
  "openvip": "1.0",
  "type": "speech",
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "timestamp": "2026-02-06T10:30:05Z",
  "text": "The bug has been fixed",
  "language": "en",
  "voice": "af_sky"
}
```

Optional fields:
- `language` — BCP 47 language tag (e.g. `"en"`, `"it"`)
- `voice` — voice identifier, engine-specific (e.g. `"af_sky"` for Kokoro)

---

## Extension Fields

Any field prefixed with `x_` is an **extension**. The protocol defines the
mechanism; extension designers define the semantics.

### Structure

Extension values are **structured JSON objects** with their own schema defined
by the extension designer. The protocol treats them as opaque.

```json
{
  "openvip": "1.0",
  "type": "transcription",
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-02-06T10:30:00Z",
  "text": "ok terminal 3",
  "language": "it",
  "x_shortcut": {
    "keys": "cmd+3",
    "trigger": "ok terminal",
    "confidence": 0.97
  }
}
```

### Receiver behavior

Receivers MUST ignore `x_` fields they do not recognize. This ensures that
extensions can be added without breaking existing consumers.

### Naming convention

Custom extensions use `x_<vendor_name>` as prefix:

- `x_bticino` — BTicino home automation
- `x_philips_hue` — Philips Hue lighting
- `x_telegram` — Telegram messaging

### Confidence

Voice interaction is inherently non-deterministic. Extensions that interpret
voice text should include a `confidence` score (0.0–1.0) in their value:

```json
{
  "x_shortcut": {
    "keys": "cmd+3",
    "confidence": 0.97
  }
}
```

---

## Standard Extensions

The protocol defines a set of **standard extensions** — officially documented,
optional extensions with well-defined schemas. Implementations MAY support any
subset of standard extensions.

Standard extensions follow the same `x_` mechanism as custom extensions. The
difference is that their schema is defined in this specification.

### `x_input` — Text input behavior

Controls how transcribed text should be delivered to a text-based interface
(e.g., text box, terminal, chat input). This extension is relevant when the
consumer operates a text entry area.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ops` | array of strings | **yes** | Ordered list of input operations to perform. Values: `"submit"` (press Enter), `"newline"` (Shift+Enter) |
| `trigger` | string | no | The voice phrase that triggered this action |
| `confidence` | float | no | Confidence score for the trigger (0.0–1.0) |
| `source` | string | no | Generator identifier — free-form string identifying the component that produced this extension (e.g., `"my-submit-filter/1.2"`, `"GestureKit/2.1"`) |

`ops` is an ordered list — operations are applied in sequence. A single message
can request multiple operations (e.g., `["newline", "submit"]`).

```json
{
  "openvip": "1.0",
  "type": "transcription",
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-02-06T10:30:00Z",
  "text": "fix the login bug",
  "x_input": {
    "ops": ["submit"],
    "trigger": "ok send",
    "confidence": 0.95,
    "source": "my-submit-filter/1.2"
  }
}
```

Consumers that do not operate a text input (e.g., smart home devices) SHOULD
ignore this extension.

### `x_agent_switch` — Agent routing

Requests switching the active agent. This extension is relevant in multi-agent
environments where voice commands can redirect input to a different consumer.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `target` | string | **yes** | Identifier of the agent to switch to |
| `confidence` | float | no | Confidence score (0.0–1.0) |
| `source` | string | no | Generator identifier (same convention as `x_input.source`) |

```json
{
  "openvip": "1.0",
  "type": "transcription",
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-02-06T10:30:00Z",
  "text": "",
  "x_agent_switch": {
    "target": "claude",
    "confidence": 0.92,
    "source": "my-agent-filter/1.0"
  }
}
```

---

## Status Endpoint

The `/status` endpoint provides information about the running engine.

### Protocol-level fields

| Field | Type | Description |
|-------|------|-------------|
| `openvip` | string | Protocol version. Must be `"1.0"` |
| `stt` | object | Speech-to-text service status |
| `stt.enabled` | boolean | STT service available on this engine |
| `stt.active` | boolean | Microphone is currently listening |
| `tts` | object | Text-to-speech service status |
| `tts.enabled` | boolean | TTS service available on this engine |
| `connected_agents` | array of strings | List of currently connected agent identifiers |
| `platform` | object | Implementation-specific details (opaque to protocol) |

### Example

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

The `stt` and `tts` objects provide protocol-level information about engine
capabilities. Generic clients can use these to discover available services
without parsing implementation-specific `platform` data.

The `platform` object is entirely implementation-specific. Each engine puts
whatever operational details are relevant to its consumers. The protocol does
not define its content.

## Status Stream

The `/status/stream` endpoint provides **push-based** status updates via
Server-Sent Events (SSE). Instead of polling `/status`, clients can subscribe
to this stream and receive notifications only when state changes occur.

### Behavior

- The engine sends an event whenever `stt`, `tts`, `connected_agents`, or
  other protocol-level fields change.
- Fields that change continuously (e.g., `uptime_seconds`) SHOULD NOT trigger
  events. Only discrete state transitions are relevant.
- The payload of each event is a `Status` object — the same schema as the
  `/status` endpoint response.
- Keepalive comments (`: keepalive`) are sent periodically if no events occur,
  to prevent connection timeouts.
- Clients that cannot use SSE SHOULD fall back to polling `/status`.

### Example stream

```
data: {"openvip":"1.0","stt":{"enabled":true,"active":true},"tts":{"enabled":true},"connected_agents":["claude"],"platform":{...}}

data: {"openvip":"1.0","stt":{"enabled":true,"active":false},"tts":{"enabled":true},"connected_agents":["claude"],"platform":{...}}

: keepalive

data: {"openvip":"1.0","stt":{"enabled":true,"active":true},"tts":{"enabled":true},"connected_agents":["claude","cursor"],"platform":{...}}
```

### Design rationale

Polling `/status` is simple and works for all HTTP clients, but it introduces
latency proportional to the poll interval. The status stream eliminates this
latency for clients that support SSE, while the polling endpoint remains
available as a universal fallback.

---

## Control Requests

Control requests are sent by agents to the engine to trigger operational
commands. Standard commands: `stt.start`, `stt.stop`, `ping`.
Implementations may define additional commands.

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `openvip` | string | Protocol version. Must be `"1.0"` |
| `id` | string | Unique request identifier (UUID v4) |
| `command` | string | Command to execute |

Control commands mutate engine state and MUST carry an `id` for traceability.

### Example

```json
{
  "openvip": "1.0",
  "id": "770e8400-e29b-41d4-a716-446655440000",
  "command": "stt.stop"
}
```

---

## Response Payloads

All HTTP responses from the engine carry the `openvip` field.

### Optional Fields

Response and error payloads support two optional fields for traceability:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier for this response/error (UUID v4, assigned by the engine) |
| `ref` | string | ID of the request that triggered this response/error |

Both fields are optional. `id` allows the engine to tag its own responses for
logging. `ref` links the response back to the originating request.

### Response

Returned on successful operations (message delivery, control commands).

```json
{
  "openvip": "1.0",
  "status": "ok",
  "ref": "770e8400-e29b-41d4-a716-446655440000"
}
```

### Error

Returned when an operation fails.

```json
{
  "openvip": "1.0",
  "error": "Agent not connected",
  "code": "NOT_FOUND",
  "ref": "770e8400-e29b-41d4-a716-446655440000"
}
```

### Speech Response

Returned after successful text-to-speech synthesis.

```json
{
  "openvip": "1.0",
  "status": "ok",
  "duration_ms": 2100,
  "ref": "660e8400-e29b-41d4-a716-446655440001"
}
```

---

## Implementation Guidelines

### For Engines (Producers)

Engines produce messages and MUST:

1. Generate unique `id` (UUID v4) for each message
2. Include `timestamp` on all messages
3. Include `text` with the transcribed content

Engines SHOULD:

1. Include `language` when detected
2. Include `confidence` when available
3. Include `origin` for identification
4. Set `partial: true` on incomplete transcriptions

### For Agents (Consumers)

Agents consume messages and MUST:

1. Process `transcription` type
2. Ignore unknown message types (forward compatibility)
3. Ignore unknown fields and `x_` extensions (forward compatibility)

**Agent types:**
- **Text Agent**: Injects text (keyboard, clipboard, stdin)
- **Audio Agent**: Speaks text (TTS)
- **Action Agent**: Executes commands (smart home, API calls)

---

## Security Considerations

OpenVIP v1.0 is designed for **local-first** use — engines running on the same
machine or trusted local network as their agents. The protocol does not include
authentication or authorization mechanisms.

### Known exposure

- `/status` exposes `connected_agents` to any client that can reach the engine
- Any client can send messages to any connected agent
- No authentication or authorization is enforced at the protocol level

### Mitigation

This is by design for v1.0, which targets local engine use (e.g., a
speech-to-text engine running on the user's workstation). For deployments on
untrusted networks, implementations SHOULD use a reverse proxy or firewall to
restrict access to the engine's HTTP endpoints.

Future versions may introduce authentication and authorization mechanisms.

---

## Design Principles

### Unidirectional, best-effort delivery

OpenVIP v1.0 is a **unidirectional** protocol: messages flow from producer to
consumer without protocol-level responses, acknowledgments, or delivery
guarantees. This is a deliberate design choice, not a limitation.

Voice interaction is inherently non-deterministic — speech recognition is
imperfect, and the natural recovery from a missed command is to repeat it.
Building complex reliability mechanisms (ACKs, retries, ordering, exactly-once
delivery) into the protocol would add significant implementation cost without
meaningful benefit for the voice interaction use case.

- **Fire-and-forget**: messages flow without protocol-level confirmation.
- **No retry**: if a message is lost, the user repeats the command.
- **Transport-level reliability**: HTTP and TCP already provide connection-level
  guarantees. The protocol does not duplicate them.

> **Note**: HTTP responses (200, 400, 404) are transport-level confirmations,
> not protocol-level acknowledgments. They confirm that the server received
> and processed the HTTP request, not that the voice interaction succeeded.

Future versions may introduce bidirectional semantics where warranted, but
v1.0 prioritizes simplicity and broad adoption.

### Minimal protocol

The protocol defines the minimum required for interoperability:

- Message format and required fields
- Two message types (`transcription`, `speech`)
- Extension mechanism (`x_` fields)
- Tracing mechanism (`trace_id`, `parent_id`)

Everything else (what goes inside extensions, how pipelines work, what
actions executors perform) is outside the protocol scope.

### Simple enough for constrained devices

An IoT device, a Raspberry Pi, or a microcontroller should be able to produce
and consume OpenVIP messages with minimal overhead. The protocol uses flat JSON
with few required fields.

### Mechanism, not policy

The protocol provides mechanisms; users define policies:

- **Extension mechanism**: `x_` fields. The protocol doesn't define content.
- **Tracing mechanism**: ID triad. Usage is optional.
- **Standard extensions**: officially defined but optional to implement.

---

## Validation

Messages can be validated against the JSON Schema:

See [schema/v1.0.json](../schema/v1.0.json) for the full schema.

---

## References

- [HTTP Binding Specification](../bindings/http/)
- [JSON Schema](../schema/v1.0.json)

---

## License

This specification is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
