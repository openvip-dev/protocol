# Contributing to OpenVIP

Thank you for your interest in contributing to the Open Voice Interaction Protocol!

## Ways to Contribute

### Specification Feedback
- Open an [issue](https://github.com/openvip-dev/protocol/issues) for bugs or unclear sections
- Start a [discussion](https://github.com/openvip-dev/protocol/discussions) for feature requests or design questions

### Documentation
- Fix typos or improve clarity
- Add examples
- Translate to other languages

### Implementations
- Build an OpenVIP client or server in your language
- Add your implementation to the [implementations list](README.md#implementations)

## Pull Request Process

1. Fork the repository
2. Create a branch (`git checkout -b fix/typo-in-spec`)
3. Make your changes
4. Submit a pull request

## Specification Changes

Changes to the core protocol require discussion before implementation:

1. Open an issue describing the proposed change
2. Wait for maintainer feedback
3. If approved, submit a PR with the change

### What belongs in the spec vs. bindings

| Spec (protocol/) | Bindings (bindings/) |
|------------------|---------------------|
| Message format | Transport details |
| Required fields | Headers, encoding |
| Message types | Connection lifecycle |
| Extension mechanism | Error codes |
| Tracing fields | Keepalive behavior |

## Code of Conduct

Be respectful and constructive. We're all here to build something useful.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
