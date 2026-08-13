# Third-party service adapters used by the portal.
#
# * ``services.openrouter`` — OpenRouter chat-completions client backing the
#   Academic Research & Thesis Assistant (/research-ai/), with automatic
#   free-model fallback on 429/503.
# * ``services.parser``    — plain-text extraction for reference PDF/DOCX
#   uploads (feeds the extracted text into the LLM system prompt).
# * ``services.attendance_email`` — Attendance module email dispatch: class-QR
#   PNG generation (qrcode) + per-session report (HTML/CSV) sent to the
#   assigned course teacher (``Teacher``).
