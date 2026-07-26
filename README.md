# nwn-message

Message definitions and websocket client for the Neverwinter Nights networking protocol.

This library has the full message index from the game binary, and can encode
and decode messages in a simplified wire format as implemented by
[NWNX_WSNetLayer](https://github.com/niv/NWNX_WSNetLayer).

It also ships a fully functional async websocket client that can connect to a server
running the plugin, log in as a player, and send/receive messages as structured Python
objects.

This message library can only connect to servers that run the NWNX_WSNetLayer plugin.
The decision not to expose the current UDP-based transport was made to reduce the
likelyhood of abuse for existing servers. Thus, any server that wishes to allow custom
clients is required to run the NWNX plugin.

## Requirements

- Python 3.14+
- NWN:EE 37.17

## Version compatibility

This package only speaks with 8193-37.17; which is the latest official stable version of
NWN:EE as of this writing. Earlier (or later) versions are not supported.

The library has some base scaffolding for supporting past or future versions; however the
divergences are not implemented to reduce the testing surface.

## Message definitions

The source of truth for this library is a registry of Python dataclasses in
`src/nwn_message/messages/`, indexed by the NWN protocol's ``(major, minor, direction)``
tuple. Each dataclass uses annotated type hints to describe its wire format: field types,
sizes, conditional guards, tagged unions, and size prefixes are all expressed declaratively
through Python's ``typing.Annotated`` and custom metadata types.

Most messages are fully declarative: their on-wire layout can be determined entirely from
their type annotations. A handful of messages with highly irregular or context-dependent
formats define custom ``read``/``write`` methods instead. These are the exception, not the
rule.

Because the message definitions are plain Python dataclasses, they serve as both the
runtime encoding/decoding layer and the schema for code generation. Any tool that wants
to speak the WSNetLayer protocol can use these same types as its source of truth.

## Client Usage

The supplied client library is fully async and meant to be wired up using the popular
`blinker` library. It will emit signals for each message type received, and you can
register handlers for those signals to process messages as they arrive. You can also
register for sub-messages (such as specific game object updates); complex messages are
decomposed inside the library for this purpose.

The example client at `examples/client.py` walks through the full connect-flow. It is
meant to be copied out into your own parent project and changed there.

This library uses the standard logging framework to emit debug informations. Use the
python builtin logging getters to mute the subsystems you don't care about.

## Usage in other languages

Codegen to other languages will be added in the future. Peliminary targets for Godot,
Typescript, and C(++) are implemented, but not yet ready for publication.

## Stability

The message definitions and wire format are, while complete, not yet API-stable. All
messages should be (!) implemented, but some types are stubs (e.g. a int might be a
stand-in for a missing enum type, or some nested classes are needlessly complex). These
will be filled in or amended as we go.

Changes to the message spec will necessitate changes to any client code that uses this
library. If you do build on this library, you will need to watch for updates to message
definitions.

The wire format (WSNetLayer) might also see changes but is at least major-versioned.

## Contributing

There is no formal contribution process yet. All contributions will require to be
licenced under the GPLv3. If in doubt, just open a discussion/issue.

## License

This project is licensed under the GPLv3.

The spirit of this license choice is: if you build on this work, share it back. The NWN
ecosystem thrives on open tools, not closed ones.

Whether you're building a custom client, a bot, or a whole new server, we hope you'll
open-source your work too. And even if you can't open everything, come tell us what
you're building anyway. We'd love to hear about it.

## Get in touch

- Join the community chat: https://nwn.zulipchat.com/
- Open a new issue or discussion thread here on GitHub.
