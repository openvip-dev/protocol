# Voice Input Standards: Market Research & Gap Analysis

*Research conducted January 2026*

---

## Executive Summary

The voice technology landscape has mature standards for **speech synthesis** (SSML), **speech recognition** (W3C Web Speech API), and **LLM output** (OpenResponses, Chat Completions). However, there is a critical gap: **no open standard exists for structured voice input messages** that can be consumed by diverse systems (LLM agents, home automation, voice assistants, custom applications).

OpenVIP (Open Voice Interaction Protocol) aims to fill this gap by providing a transport-agnostic, privacy-aware standard for voice input messages.

---

## 1. Existing Voice Standards

### 1.1 W3C Web Speech API

**Purpose**: Browser-based speech recognition and synthesis

**Scope**:
- `SpeechRecognition` interface for voice-to-text
- `SpeechSynthesis` interface for text-to-speech
- JavaScript API, browser-only

**Limitations**:
- Browser-confined, not suitable for server-side or CLI applications
- No structured output format beyond raw transcription
- No metadata (confidence, timing, language detection)
- No standard for delivery to external systems

**Relevance to OpenVIP**: Defines what browsers expose, but not how voice input travels between systems.

### 1.2 VoiceXML

**Purpose**: IVR (Interactive Voice Response) systems for telephony

**Scope**:
- Dialog flow definition for phone systems
- Grammar definitions for expected inputs
- Legacy standard from W3C (2004)

**Limitations**:
- Telephony-focused, not suited for modern voice interfaces
- Overly complex for simple transcription delivery
- No support for streaming or real-time updates
- Essentially obsolete for modern use cases

**Relevance to OpenVIP**: Historical precedent, but not a viable foundation.

### 1.3 SSML (Speech Synthesis Markup Language)

**Purpose**: Controlling text-to-speech output

**Scope**:
- Pronunciation, emphasis, breaks, prosody
- Widely adopted (Alexa, Google, Azure, Polly)

**Limitations**:
- Output-focused (TTS), not input (STT)
- No relevance to voice input delivery

**Relevance to OpenVIP**: Complementary (SSML for output, OpenVIP for input).

### 1.4 MRCP (Media Resource Control Protocol)

**Purpose**: Controlling speech recognition/synthesis servers

**Scope**:
- Server-side ASR/TTS resource management
- Used in enterprise telephony (Nuance, Genesys)

**Limitations**:
- Complex, enterprise-focused
- Session management, not message format
- Requires dedicated infrastructure

**Relevance to OpenVIP**: Infrastructure protocol, not a message format standard.

### 1.5 OVTS (Open Voice Transcription Standard)

**Status**: Proposed but not widely adopted

**Scope**:
- Attempted to standardize transcription formats
- Never gained significant traction

**Relevance to OpenVIP**: Demonstrates market need, but execution gap.

---

## 2. Voice Assistant Protocols

### 2.1 Amazon Alexa

**Input Format**: Proprietary JSON to Alexa Voice Service (AVS)

```json
{
  "directive": {
    "header": {
      "namespace": "SpeechRecognizer",
      "name": "Recognize"
    },
    "payload": {
      "format": "AUDIO_L16_RATE_16000_CHANNELS_1"
    }
  }
}
```

**Output to Skills**: Intent-based JSON

```json
{
  "request": {
    "type": "IntentRequest",
    "intent": {
      "name": "TurnOnLight",
      "slots": {
        "room": { "value": "kitchen" }
      }
    }
  }
}
```

**Limitations**:
- Locked to Alexa ecosystem
- Requires Alexa Skills Kit certification
- No direct transcription access for third parties

### 2.2 Google Assistant

**Input Format**: gRPC streams to Google Cloud

**Output**: Actions on Google JSON format

```json
{
  "queryResult": {
    "queryText": "turn on kitchen lights",
    "intent": {
      "displayName": "lights.on"
    },
    "parameters": {
      "room": "kitchen"
    }
  }
}
```

**Limitations**:
- Google Cloud dependency
- Actions on Google deprecated for consumer devices (2023)
- Dialogflow required for custom intents

### 2.3 Apple Siri

**Input Format**: Completely proprietary

**Output**: SiriKit intents (iOS only)

**Limitations**:
- Most closed ecosystem
- No third-party voice input integration outside Apple devices
- SiriKit limited to predefined domains

### 2.4 Summary: Voice Assistant Gap

| Platform | Open Input Format | Open Output Format | Third-Party Access |
|----------|------------------|-------------------|-------------------|
| Alexa | No | Partial (Skills) | Limited |
| Google | No | Partial (Actions) | Deprecated |
| Siri | No | No | Very Limited |

**Key Finding**: All major voice assistants use proprietary formats and restrict third-party access to voice input streams.

---

## 3. LLM Voice Integration

### 3.1 OpenAI Whisper API

**Input**: Raw audio (mp3, wav, webm, etc.)

**Output**: Simple JSON

```json
{
  "text": "Hello, how are you?"
}
```

With verbose_json format:
```json
{
  "task": "transcribe",
  "language": "en",
  "duration": 2.5,
  "text": "Hello, how are you?",
  "segments": [...]
}
```

**Limitations**:
- REST API only, no streaming transcription delivery
- No standard for forwarding to other systems
- Verbose format is Whisper-specific

### 3.2 OpenAI Realtime API

**Format**: WebSocket-based, proprietary event format

```json
{
  "type": "input_audio_buffer.append",
  "audio": "base64..."
}
```

**Limitations**:
- Tightly coupled to OpenAI's realtime model
- Audio-in, audio/text-out, not transcription delivery
- No standard for interoperability

### 3.3 Anthropic Claude

**Voice Support**: None currently

**Chat Format**: Messages API with text content

```json
{
  "messages": [
    {"role": "user", "content": "Turn on the lights"}
  ]
}
```

**Opportunity**: OpenVIP could define how voice input reaches Claude.

### 3.4 OpenResponses Standard

**Purpose**: Standardize LLM **output** format

**Scope**:
- Response streaming
- Tool calls
- Multi-modal outputs

**Relevance**: OpenVIP is the **input** complement to OpenResponses' output standard.

---

## 4. Home Automation Protocols

### 4.1 Home Assistant

**Voice Input**: Wyoming protocol (local, Home Assistant-specific)

**Intents**: YAML-based intent definitions

```yaml
intents:
  HassLightSet:
    slots:
      name:
        - "kitchen"
      brightness:
        - 100
```

**Automation Triggers**:
```yaml
trigger:
  platform: conversation
  command: "turn on {area} lights"
```

**Limitations**:
- No standard format for receiving external voice input
- Wyoming protocol is Home Assistant-specific
- No webhook/SSE standardization

### 4.2 Matter Protocol

**Purpose**: IoT device interoperability

**Voice**: Not addressed (Matter is device control, not voice input)

**Relevance**: OpenVIP could bridge voice input to Matter devices.

### 4.3 MQTT

**Purpose**: Lightweight messaging for IoT

**Voice Convention**: None standardized

**Opportunity**: OpenVIP messages could travel over MQTT topics.

---

## 5. Gap Analysis

### 5.1 The Missing Layer

```
┌─────────────────────────────────────────────────────────────┐
│                    VOICE INPUT JOURNEY                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   [Microphone] → [STT Engine] → [???] → [Consumer System]   │
│                                    ↑                         │
│                              NO STANDARD                     │
│                                                              │
│   Consumers:                                                 │
│   • LLM Agents (Claude, GPT, local models)                  │
│   • Home Automation (Home Assistant, OpenHAB)               │
│   • Custom Applications                                      │
│   • Voice Assistants                                         │
│   • Accessibility Tools                                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 What's Missing

| Capability | Current State | OpenVIP Solution |
|------------|---------------|------------------|
| Structured transcription format | Each STT has own format | Universal JSON schema |
| Transport agnostic delivery | Varies by system | File, webhook, SSE, WebSocket |
| Privacy controls | Rarely considered | Metadata-only mode |
| Language/locale metadata | Optional, inconsistent | Required fields |
| Timing information | Whisper-specific | Standardized fields |
| Streaming partial results | No standard | Event types defined |
| Intent hints | Not standardized | Optional intent field |

### 5.3 Why This Gap Exists

1. **Voice assistants want lock-in**: Alexa, Google, Siri compete on ecosystem
2. **STT engines focus on accuracy**: Whisper, DeepSpeech care about transcription quality, not delivery
3. **No market pressure**: Until LLM agents needed voice input, raw text was sufficient
4. **Privacy concerns**: Standardizing voice data raises questions vendors avoid

### 5.4 Why Now

1. **LLM agent explosion**: Every AI assistant wants voice input
2. **Local STT maturity**: Whisper, MLX Whisper, faster-whisper enable local transcription
3. **MCP precedent**: Model Context Protocol proved open standards get adopted
4. **Privacy awareness**: Users want local processing, vendors want compliance

---

## 6. Potential Adopters

### 6.1 Voice-to-Text Tools

| Tool | Language | Current Output | OpenVIP Fit |
|------|----------|----------------|-------------|
| example-engine | Python | Custom JSONL | Reference implementation |
| whisper.cpp | C++ | Raw text | Easy wrapper |
| faster-whisper | Python | Python objects | Natural fit |
| Vosk | Multi | JSON | Compatible |
| Mozilla DeepSpeech | Multi | Text | Needs wrapper |

### 6.2 LLM Frameworks

| Framework | Voice Support | OpenVIP Opportunity |
|-----------|---------------|---------------------|
| LangChain | None native | Input source |
| LlamaIndex | None native | Document loader |
| Semantic Kernel | Limited | Input handler |
| Claude Code | None | Direct integration |

### 6.3 Home Automation

| Platform | Current Voice | OpenVIP Opportunity |
|----------|---------------|---------------------|
| Home Assistant | Wyoming | Alternative input source |
| OpenHAB | Limited | Voice input standard |
| Node-RED | Custom | Input node |
| Hubitat | Cloud-only | Local voice option |

### 6.4 Agent Frameworks

| Framework | Voice Input | OpenVIP Opportunity |
|-----------|-------------|---------------------|
| AutoGPT | None | Input source |
| BabyAGI | None | Input source |
| AgentGPT | Browser mic | Backend integration |
| Claude MCP | File-based | Native support |

---

## 7. Competitive Analysis

### 7.1 Why Not Extend Existing Standards?

| Standard | Extension Possible? | Why Not |
|----------|--------------------|---------|
| W3C Web Speech | No | Browser-only, wrong scope |
| VoiceXML | No | Obsolete, wrong paradigm |
| MRCP | No | Infrastructure, not messages |
| Whisper format | Partial | Vendor-specific, limited metadata |

### 7.2 Why a New Standard?

1. **Clean slate**: No legacy baggage
2. **Modern requirements**: LLM-era needs
3. **Privacy-first**: Designed for local processing
4. **Transport agnostic**: Not tied to HTTP or WebSocket
5. **Minimal viable**: Simple core, optional extensions

---

## 8. OpenVIP Design Principles

Based on this research, OpenVIP should:

### 8.1 Core Principles

1. **Simple core**: A transcription message is just text + metadata
2. **Transport agnostic**: Works over files, HTTP, SSE, WebSocket, MQTT
3. **Privacy aware**: Metadata-only mode for sensitive contexts
4. **Extensible**: Optional fields for intents, confidence, timing
5. **Version tolerant**: Consumers ignore unknown fields

### 8.2 Minimum Viable Message

```json
{
  "openvip": "1.0",
  "type": "message",
  "text": "turn on the lights in the kitchen"
}
```

### 8.3 Full Message

```json
{
  "openvip": "1.0",
  "type": "message",
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "text": "turn on the lights in the kitchen",
  "metadata": {
    "timestamp": "2026-01-24T10:30:00.000Z",
    "language": "en",
    "confidence": 0.95,
    "audio_duration_ms": 2500,
    "transcription_ms": 150,
    "source": "myapp/2.0.0",
    "device": "default"
  },
  "intent": {
    "action": "lights.on",
    "parameters": {
      "location": "kitchen"
    }
  }
}
```

### 8.4 Event Types

| Type | Purpose |
|------|---------|
| `message` | Complete transcription |
| `partial` | Streaming partial result |
| `start` | Recording started |
| `end` | Recording ended |
| `error` | Error occurred |
| `state` | State change notification |

---

## 9. Transport Methods

### 9.1 File-Based

```
~/.myengine/messages.jsonl
```

Append-only JSONL for agent consumption (MCP file resources pattern).

### 9.2 Webhooks

```http
POST /openvip/messages HTTP/1.1
Content-Type: application/json

{"openvip": "1.0", "type": "message", "text": "..."}
```

### 9.3 Server-Sent Events

```
event: message
data: {"openvip": "1.0", "type": "message", "text": "..."}

event: partial
data: {"openvip": "1.0", "type": "partial", "text": "turn on the..."}
```

### 9.4 WebSocket (Future)

Bidirectional for acknowledgments and commands.

---

## 10. Privacy Considerations

### 10.1 Metadata-Only Mode

For privacy-sensitive deployments:

```json
{
  "openvip": "1.0",
  "type": "message",
  "text": null,
  "metadata": {
    "timestamp": "2026-01-24T10:30:00.000Z",
    "language": "en",
    "audio_duration_ms": 2500,
    "char_count": 35,
    "word_count": 7
  }
}
```

### 10.2 Local-First Design

- No cloud requirement
- All processing can be local
- Transport is user's choice

---

## 11. Adoption Strategy

### 11.1 Phase 1: Reference Implementation

- example-engine implements OpenVIP output
- File-based + webhook + SSE transports
- Documentation and examples

### 11.2 Phase 2: Ecosystem

- Libraries for common languages (Python, TypeScript, Rust)
- Home Assistant integration
- MCP server for Claude

### 11.3 Phase 3: Adoption

- Partner with STT projects (whisper.cpp, Vosk)
- Home automation integrations
- LLM framework support

---

## 12. Success Metrics

1. **Adoption**: 10+ projects implementing OpenVIP within 1 year
2. **Transport diversity**: 4+ transport methods in active use
3. **Cross-platform**: Implementations in 5+ languages
4. **Home automation**: At least 2 major platforms supporting OpenVIP

---

## 13. Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Low adoption | Keep spec minimal, provide libraries |
| Competing standard | Move fast, build community |
| Over-engineering | Strict "minimal viable" principle |
| Privacy concerns | Metadata-only mode, local-first |

---

## 14. Related Standards

| Standard | Relationship |
|----------|--------------|
| OpenResponses | Complementary (output vs input) |
| JSON Schema | Used for validation |
| JSON Lines | File format |
| SSE | Transport method |
| WebSocket | Future transport |

---

## 15. Conclusion

The voice input space lacks a standard that:
- Is **open** and **transport-agnostic**
- Supports **modern use cases** (LLM agents, home automation)
- Respects **privacy** (metadata-only mode)
- Is **simple** enough for quick adoption

OpenVIP fills this gap. With the precedent set by MCP's rapid adoption and the explosion of LLM agents needing voice input, the timing is right for an open standard.

---

## References

- W3C Web Speech API: https://w3c.github.io/speech-api/
- VoiceXML 2.0: https://www.w3.org/TR/voicexml20/
- SSML 1.1: https://www.w3.org/TR/speech-synthesis11/
- MRCP v2: https://tools.ietf.org/html/rfc6787
- OpenAI Whisper API: https://platform.openai.com/docs/guides/speech-to-text
- Home Assistant Voice: https://www.home-assistant.io/voice_control/
- Matter Protocol: https://csa-iot.org/all-solutions/matter/
- Model Context Protocol: https://modelcontextprotocol.io/

---

*This research document is part of the OpenVIP specification project.*
*License: CC BY 4.0*
