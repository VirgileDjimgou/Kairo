"""Authorized domain context providers for the private assistant (Sprint 112).

`ChatService` asks the registry for structured context; each provider checks the
capability-derived domain policy before it queries its domain, so authorization
always happens before context assembly and the LLM never decides access.
"""
