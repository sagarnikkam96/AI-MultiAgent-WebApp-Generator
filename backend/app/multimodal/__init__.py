"""Multimodal input support for the generator.

Allows a requirements prompt to be augmented with text, image, audio, video,
and document inputs. Extraction is additive and never affects the core text
pipeline: any optional parsing library that isn't installed results in a
graceful note instead of an error.
"""

from .extractor import ExtractedAttachment, extract_attachment

__all__ = ["ExtractedAttachment", "extract_attachment"]
