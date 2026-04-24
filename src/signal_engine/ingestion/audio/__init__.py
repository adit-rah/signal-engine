"""Audio pipeline (Pipeline B): webcast audio + WhisperX ASR.

Fallback path for issuers who do not publish PDF transcripts. Heavier
investment: requires yt-dlp, WhisperX, and Hugging Face tokens for
pyannote speaker diarization.
"""
