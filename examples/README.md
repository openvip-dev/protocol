# OpenVIP Message Examples

Example OpenVIP v1.0 messages for reference and testing.

## Files

| File | Description |
|------|-------------|
| `basic-message.json` | Minimal complete transcription |
| `message-with-extension.json` | Transcription with `x_input` standard extension |
| `message-with-tracing.json` | Transcription with tracing fields |
| `partial-transcription.json` | Partial (incomplete) transcription |
| `speech-request.json` | Text-to-speech request |

## Required Fields

All messages require:
- `openvip` - Protocol version (`"1.0"`)
- `type` - Message type (`"transcription"` or `"speech"`)
- `id` - Unique message identifier (UUID v4)
- `timestamp` - ISO 8601 timestamp
- `text` - The transcribed or synthesized text

## Optional Fields

- `origin` - Producer identifier (e.g., `"myapp/1.0.0"`)
- `language` - BCP 47 language tag (e.g., `"en"`, `"it"`)
- `confidence` - Transcription confidence (0.0–1.0)
- `partial` - If `true`, this is an incomplete transcription in progress
- `trace_id` - ID of the original message in the chain
- `parent_id` - ID of the immediate predecessor message

## Extension Fields

Any field prefixed with `x_` is an extension. Extension values
are structured JSON objects with their own schema defined by the extension
designer.

### Standard Extensions

| Extension | Description |
|-----------|-------------|
| `x_input` | Text input behavior (submit, newline) |
| `x_agent_switch` | Agent routing (switch active agent) |

```json
{
  "x_input": {
    "submit": true,
    "newline": false,
    "trigger": "ok send",
    "confidence": 0.95
  }
}
```

See [protocol/openvip-1.0.md](../protocol/openvip-1.0.md) for full specification.

## Validation

Validate examples against the JSON Schema:

```bash
# Using ajv-cli
npx ajv validate -s ../schema/v1.0.json -d basic-message.json

# Using Python jsonschema
python -c "
import json
from jsonschema import validate
schema = json.load(open('../schema/v1.0.json'))
message = json.load(open('basic-message.json'))
validate(message, schema)
print('Valid!')
"
```

## Usage in Code

### Python

```python
import json

with open("basic-message.json") as f:
    message = json.load(f)

print(f"Type: {message['type']}")
print(f"Text: {message['text']}")
print(f"ID: {message['id']}")

# Check for extension fields
for key, value in message.items():
    if key.startswith("x_"):
        print(f"Extension: {key} = {value}")
```

### JavaScript

```javascript
import message from './basic-message.json';

console.log(`Type: ${message.type}`);
console.log(`Text: ${message.text}`);
console.log(`ID: ${message.id}`);

// Check for extension fields
Object.entries(message)
  .filter(([key]) => key.startsWith('x_'))
  .forEach(([key, value]) => console.log(`Extension: ${key}`, value));
```
