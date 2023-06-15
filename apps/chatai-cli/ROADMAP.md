# Roadmap

## Features to Add

- [x] Add support for prompts when using ask command
- [x] Add support for indicator to show it is working on a request
- [x] Add conversation command to attach files to conversations
- [x] Add conversation command to delete messages and responses from conversations
- [x] Add conversation command for copying messages and responses to the clipboard
- [x] Add conversation command to snapshot a specific state of a conversation
- [x] Add command/ability that shows token info (using model and response.usage.{prompt_tokens,completion_tokens,total_tokens})
- [x] Add support to apply responses from the send command
- [x] Add support for autocomplete of conversation commands
- [x] Add support for autosuggest in conversation input
- [x] Add support for analyzing and performing tasks on files, and after each task the user can choose to apply or discard the proposed changes
- [x] Add support for exporting conversations to a prompt file
- [x] Improve separation of messages and responses with dividers
- [x] Add support for multiple selector types in the delete coversation command (same syntaxes as copy)
- [x] Add ability to show existing conversation
- [x] Only show the prompt name, aliases, model, and system role's content, when listing prompts
- [ ] Add support for editing previous messages and responses in conversations
- [ ] Add support for named snapshots
- [ ] Add support for **only** copying code block from responses
- [ ] Add support for providing URLs for prompts
- [ ] Add CLI command for generating new prompts (locally and globally)
- [ ] Add setting that enables logging for raw entries and responses for app
- [ ] Add documentation via README
- [ ] Add CLI commands for managing settings in the global settings file (CRUDL operations)
- [ ] Add support for functions
- [ ] Cleanup snapshots on conversation deletion
- [ ] Refactor file organization and format of conversations

## Known Bugs

- [ ] Delete doesn't automatically detect model when only one model exists for the name

## Features to Consider

- [ ] Add support for layouts
- [ ] Add ability to switch models in conversations?
- [ ] Add support for gpt-4-32k model and any other larger context models
- [ ] Add integration with Jupyter Notebooks
