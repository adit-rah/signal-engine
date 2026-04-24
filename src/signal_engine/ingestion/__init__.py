"""Ingestion (ARCHITECTURE.md component 1).

Three V1 pipelines:

* edgar/     — SEC 8-K filings and the press-release exhibits within
* pdf/       — issuer-published FactSet PDF transcripts (NVDA, INTC, META)
* audio/     — webcast audio + WhisperX ASR (fallback path)

Each pipeline preserves the Raw artifact as received and writes per-artifact
provenance (DATA_MODEL.md Raw layer). Normalization into canonical
Utterances / Segments is a downstream stage (DOCUMENT_PROCESSING.md).
"""
