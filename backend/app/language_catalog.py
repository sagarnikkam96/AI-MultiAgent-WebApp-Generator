"""Supported output languages and their native names."""

LANGUAGE_NAMES: dict[str, str] = {
    "en": "English",
    "hi": "Hindi",
    "kn": "Kannada",
    "mr": "Marathi",
    "te": "Telugu",
    "bn": "Bengali",
    "ta": "Tamil",
    "gu": "Gujarati",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "or": "Odia",
    "as": "Assamese",
    "ur": "Urdu",
    "sa": "Sanskrit",
    "ne": "Nepali",
    "kok": "Konkani",
    "sd": "Sindhi",
    "ks": "Kashmiri",
    "mni": "Manipuri (Meitei)",
    "mai": "Maithili",
}

RTL_LANGUAGES = frozenset({"ur", "sd", "ks"})


def output_language_instruction(language: str) -> str:
    """Build a strict, explicit instruction for user-facing generated content."""
    language_name = LANGUAGE_NAMES.get(language)
    if language_name is None:
        raise ValueError(f"Unsupported output language code: {language}")

    return (
        f"OUTPUT LANGUAGE: {language_name} (language code: {language}). "
        f"Write every user-facing phrase in {language_name}, including navigation, "
        "buttons, headings, form labels, placeholders, validation messages, empty states, "
        "sample records, accessibility labels, and generated documentation. Do not mix "
        "in English or another natural language. Keep product and personal names, "
        "programming identifiers, framework names, API paths, and standard technical "
        "acronyms unchanged where translation would break their meaning."
    )
