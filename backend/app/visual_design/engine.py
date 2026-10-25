"""Prompt-aware, accessible visual direction for generated React projects."""

from __future__ import annotations

import hashlib
import json
import logging
import re
from typing import Any

from ..code_generator.website_spec import detect_website_key

logger = logging.getLogger(__name__)


class PremiumDesignEngine:
    """Select a visual personality and produce a CSS-only enhancement."""

    PERSONALITIES = (
        "futuristic",
        "luxury",
        "cinematic",
        "creative",
        "editorial",
        "organic",
        "minimalist",
        "glassmorphism",
        "bold",
    )

    _PALETTES: dict[str, dict[str, str]] = {
        "futuristic": {
            "page": "#07111f", "card": "#0d1c2e", "inner": "#11283c",
            "accent": "#55e6d2", "action": "#006e68", "secondary": "#6fa8ff", "text": "#edf7ff",
            "muted": "#9ab0c4", "border": "rgba(111, 168, 255, .2)",
        },
        "luxury": {
            "page": "#11100e", "card": "#1b1915", "inner": "#252118",
            "accent": "#d7b978", "action": "#806022", "secondary": "#f0dfb6", "text": "#f7f1e5",
            "muted": "#b8ad99", "border": "rgba(215, 185, 120, .22)",
        },
        "cinematic": {
            "page": "#10101a", "card": "#1a1928", "inner": "#252337",
            "accent": "#ff8a66", "action": "#9d3f26", "secondary": "#a394ff", "text": "#f8f4f3",
            "muted": "#b3adbd", "border": "rgba(163, 148, 255, .2)",
        },
        "creative": {
            "page": "#17111a", "card": "#241a29", "inner": "#302137",
            "accent": "#ff7e67", "action": "#ac3d30", "secondary": "#c49bff", "text": "#fff7f1",
            "muted": "#c4b3c7", "border": "rgba(255, 126, 103, .2)",
        },
        "editorial": {
            "page": "#f3f0e8", "card": "#fffdf7", "inner": "#ebe7dc",
            "accent": "#315c4b", "action": "#315c4b", "secondary": "#b16c46", "text": "#1b2922",
            "muted": "#66736b", "border": "rgba(38, 58, 45, .17)",
        },
        "organic": {
            "page": "#eef1e8", "card": "#fbfcf7", "inner": "#e4eadc",
            "accent": "#557b56", "action": "#426a42", "secondary": "#ba7956", "text": "#202d22",
            "muted": "#687568", "border": "rgba(72, 104, 73, .18)",
        },
        "minimalist": {
            "page": "#f4f5f3", "card": "#ffffff", "inner": "#eef0ed",
            "accent": "#334f70", "action": "#334f70", "secondary": "#7388a0", "text": "#1c2731",
            "muted": "#6f7c87", "border": "rgba(41, 57, 72, .14)",
        },
        "glassmorphism": {
            "page": "#0c1324", "card": "rgba(23, 35, 59, .82)", "inner": "rgba(35, 51, 79, .72)",
            "accent": "#89a8ff", "action": "#465da8", "secondary": "#69e1d2", "text": "#f2f5ff",
            "muted": "#a8b3cb", "border": "rgba(184, 202, 255, .22)",
        },
        "bold": {
            "page": "#111111", "card": "#1c1c1c", "inner": "#292929",
            "accent": "#d9ff43", "action": "#56691c", "secondary": "#ff6b55", "text": "#f7f7f2",
            "muted": "#b4b4ac", "border": "rgba(217, 255, 67, .22)",
        },
    }

    _FONT_STACKS = {
        "editorial": "Georgia, 'Times New Roman', serif",
        "luxury": "Georgia, 'Times New Roman', serif",
        "organic": "'Trebuchet MS', Arial, sans-serif",
        "default": "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    }

    _LAYOUT_TOKENS = {
        "futuristic": {"sidebar": "264px", "gap": "20px", "space": "22px", "hero": "230px"},
        "luxury": {"sidebar": "250px", "gap": "28px", "space": "34px", "hero": "270px"},
        "cinematic": {"sidebar": "280px", "gap": "24px", "space": "28px", "hero": "300px"},
        "creative": {"sidebar": "260px", "gap": "20px", "space": "22px", "hero": "250px"},
        "editorial": {"sidebar": "238px", "gap": "30px", "space": "36px", "hero": "280px"},
        "organic": {"sidebar": "270px", "gap": "26px", "space": "30px", "hero": "260px"},
        "minimalist": {"sidebar": "240px", "gap": "16px", "space": "18px", "hero": "210px"},
        "glassmorphism": {"sidebar": "280px", "gap": "22px", "space": "24px", "hero": "260px"},
        "bold": {"sidebar": "250px", "gap": "18px", "space": "20px", "hero": "240px"},
    }

    _STYLE_HINTS = {
        "futuristic": ("futuristic", "future", "sci-fi", "cyber", "technology", "tech", "ai", "innovation"),
        "luxury": ("luxury", "premium", "elegant", "high-end", "jewelry", "boutique", "exclusive"),
        "cinematic": ("cinematic", "film", "movie", "storytelling", "immersive", "dramatic"),
        "creative": ("creative", "portfolio", "agency", "art", "playful", "experimental"),
        "editorial": ("editorial", "magazine", "publication", "news", "journal", "reading"),
        "organic": ("organic", "nature", "garden", "wellness", "eco", "sustainable", "food", "farm"),
        "minimalist": ("minimal", "minimalist", "clean", "simple", "clinical", "health", "medical"),
        "glassmorphism": ("glassmorphism", "glass", "translucent", "frosted"),
        "bold": ("bold", "energetic", "sport", "fitness", "campaign", "streetwear"),
    }

    def __init__(self, model_client: Any | None = None) -> None:
        self.model_client = model_client

    def create_art_direction(self, prompt: str, requested_style: str = "auto") -> dict[str, Any]:
        """Return constrained art direction; prefer a local model, with transparent fallback."""
        style = requested_style
        rationale = ""
        imagery = ""
        source = "user_selected"
        fallback_reason: str | None = None

        if requested_style == "auto":
            model_result = self._model_direction(prompt)
            if model_result:
                style, rationale, imagery = model_result
                source = "local_model"
            else:
                style = self._infer_style(prompt)
                rationale = self._rationale(style, prompt)
                imagery = self._imagery_guidance(style, prompt)
                source = "prompt_rules"
                fallback_reason = (
                    "No local art-direction model was configured; prompt-aware style rules selected this direction."
                    if self.model_client is None
                    else "The local art-direction model was unavailable or returned an unsupported style; prompt-aware rules were used."
                )
        else:
            rationale = self._rationale(style, prompt)
            imagery = self._imagery_guidance(style, prompt)

        return {
            "personality": style,
            "source": source,
            "fallback_reason": fallback_reason,
            "rationale": rationale,
            "palette": self._palette_for_prompt(style, prompt),
            "typography": self._FONT_STACKS.get(style, self._FONT_STACKS["default"]),
            "layout_direction": self._layout_direction(style),
            "imagery_direction": imagery,
            "motion_direction": "Subtle entrance and hover transitions; disabled when reduced motion is requested.",
            "accessibility": [
                "Visible keyboard focus rings",
                "Reduced-motion preference is respected",
                "Existing controls, forms, navigation, and application logic are not modified",
            ],
        }

    def _model_direction(self, prompt: str) -> tuple[str, str, str] | None:
        if not self.model_client:
            return None
        request = (
            "Choose visual art direction for an existing web application. "
            f"User request: {prompt[:3000]}\n"
            f"Return JSON only with personality (one of {', '.join(self.PERSONALITIES)}), "
            "rationale (one short sentence), and imagery (one short image art-direction sentence). "
            "Do not suggest external image URLs, functionality changes, or code."
        )
        try:
            response = self.model_client.generate(request)
            if not isinstance(response, str):
                return None
            match = re.search(r"\{.*\}", response, flags=re.DOTALL)
            if not match:
                return None
            parsed = json.loads(match.group(0))
            style = parsed.get("personality")
            if style not in self.PERSONALITIES:
                return None
            rationale = parsed.get("rationale")
            imagery = parsed.get("imagery")
            if not isinstance(rationale, str) or not isinstance(imagery, str):
                return None
            return style, rationale[:300], imagery[:300]
        except (RuntimeError, TypeError, AttributeError) as error:
            logger.warning("Local art direction unavailable; using prompt rules: %s", error)
            return None
        except ValueError as error:
            logger.warning("Local art direction returned invalid JSON; using prompt rules: %s", error)
            return None

    def _infer_style(self, prompt: str) -> str:
        normalized = prompt.casefold()
        scores = {
            style: sum(1 for hint in hints if hint in normalized)
            for style, hints in self._STYLE_HINTS.items()
        }
        maximum = max(scores.values(), default=0)
        if maximum:
            winners = [style for style, score in scores.items() if score == maximum]
            digest = hashlib.sha256(prompt.strip().casefold().encode("utf-8")).digest()
            return winners[int.from_bytes(digest[:2], "big") % len(winners)]
        domain_styles = {
            "hospital": "minimalist",
            "ecommerce": "bold",
            "food_delivery": "organic",
            "education": "editorial",
            "finance": "minimalist",
            "inventory": "futuristic",
            "real_estate": "luxury",
            "hospitality": "luxury",
            "railway": "futuristic",
            "travel": "cinematic",
            "fitness": "bold",
            "task": "minimalist",
        }
        domain_style = domain_styles.get(detect_website_key(prompt))
        if domain_style:
            return domain_style
        digest = hashlib.sha256(prompt.strip().casefold().encode("utf-8")).digest()
        return self.PERSONALITIES[int.from_bytes(digest[:4], "big") % len(self.PERSONALITIES)]

    def _palette_for_prompt(self, style: str, prompt: str) -> dict[str, str]:
        palette = dict(self._PALETTES[style])
        if detect_website_key(prompt) == "railway":
            palette.update({
                "page": "#101820",
                "card": "#1b2731",
                "inner": "#263540",
                "accent": "#e3a83b",
                "action": "#805516",
                "secondary": "#8fb6c8",
                "text": "#f5f2e9",
                "muted": "#b6c0c4",
                "border": "rgba(227, 168, 59, .24)",
            })
        return palette

    def _rationale(self, style: str, prompt: str) -> str:
        domain = prompt.strip().splitlines()[0][:100].strip() if prompt.strip() else "this application"
        descriptions = {
            "futuristic": "A precise, high-contrast interface with cool luminous accents suits the forward-looking product.",
            "luxury": "Restrained warm metallic accents, generous spacing, and refined serif headings create a considered premium feel.",
            "cinematic": "A layered dark palette, focused lighting, and editorial scale create a more immersive presentation.",
            "creative": "Expressive color contrast and asymmetrical rhythm add personality while retaining a clear interface.",
            "editorial": "A paper-toned canvas, restrained ink palette, and typographic hierarchy emphasize readable content.",
            "organic": "Natural greens, warm neutrals, and softer surfaces create a calm, human visual language.",
            "minimalist": "Quiet neutrals, clear hierarchy, and deliberate whitespace keep attention on the product and its tasks.",
            "glassmorphism": "Layered translucent surfaces and soft ambient light add depth while keeping controls legible.",
            "bold": "A confident accent, crisp edges, and strong typographic contrast make key information easy to scan.",
        }
        return f"{descriptions[style]} Art direction is tailored for {domain}."

    def _imagery_guidance(self, style: str, prompt: str) -> str:
        guidance = {
            "futuristic": "Use real product or interface imagery with cool, directional light; avoid decorative stock imagery.",
            "luxury": "Prefer authentic detail photography, warm highlights, and generous negative space; do not add stock assets.",
            "cinematic": "Favor existing project imagery with controlled contrast and a clear focal point; avoid autoplay media.",
            "creative": "Use the project's own content as the visual subject and preserve its existing media sources.",
            "editorial": "Favor existing photography with natural light, strong crops, and a clear editorial focal point.",
            "organic": "Use existing nature or material imagery with natural light; do not introduce external image dependencies.",
            "minimalist": "Keep imagery sparse and purposeful, retaining the project's existing media only.",
            "glassmorphism": "Let existing imagery provide subtle background context; preserve contrast behind translucent surfaces.",
            "bold": "Use existing high-quality imagery with strong subject separation; avoid adding external assets.",
        }
        return guidance[style]

    def _layout_direction(self, style: str) -> str:
        directions = {
            "futuristic": "Compact navigation, a focused luminous masthead, and crisp information panels.",
            "luxury": "Airy content rhythm, warm focal header, and understated layered surfaces.",
            "cinematic": "A broad atmospheric masthead, deliberate content framing, and layered panels.",
            "creative": "Flexible modular cards and a vivid focal header with clear actions.",
            "editorial": "Typography-led masthead, generous margins, and clear section sequencing.",
            "organic": "Softly rounded surfaces, relaxed spacing, and a calm vertical reading flow.",
            "minimalist": "Quiet navigation, reduced visual noise, and consistent content alignment.",
            "glassmorphism": "Translucent navigation and cards over a restrained ambient background.",
            "bold": "Strong masthead, confident section divisions, and high-contrast action controls.",
        }
        return directions[style]

    def create_css(self, direction: dict[str, Any]) -> str:
        """Create additive CSS that styles existing generated components only."""
        palette = direction["palette"]
        personality = direction["personality"]
        layout = self._LAYOUT_TOKENS[personality]
        color_scheme = "light" if personality in ("editorial", "organic", "minimalist") else "dark"
        radius = "18px" if personality in ("minimalist", "editorial", "futuristic", "bold") else "26px"
        blur = "blur(18px)" if personality == "glassmorphism" else "none"
        card_background = palette["card"]
        if personality == "glassmorphism":
            card_background = "rgba(23, 35, 59, .72)"

        return f"""
/* Premium visual direction: {personality}. Generated as an additive, CSS-only layer. */
/* PREMIUM_DESIGN_BEGIN */
:root {{
  color-scheme: {color_scheme};
  --bg-page: {palette["page"]};
  --bg-card: {card_background};
  --bg-inner: {palette["inner"]};
  --accent-primary: {palette["accent"]};
  --secondary-accent: {palette["secondary"]};
  --accent-glow: color-mix(in srgb, {palette["accent"]} 24%, transparent);
  --accent-gradient: linear-gradient(125deg, {palette["action"]}, {palette["action"]});
  --border-color: {palette["border"]};
  --text-main: {palette["text"]};
  --text-muted: {palette["muted"]};
  --premium-radius: {radius};
  --premium-sidebar-width: {layout["sidebar"]};
  --premium-layout-gap: {layout["gap"]};
  --premium-content-space: {layout["space"]};
  --premium-hero-height: {layout["hero"]};
  font-family: {direction["typography"]};
  scroll-behavior: smooth;
}}
.app-shell:not(.light-mode) {{
  color-scheme: {color_scheme};
  --bg-page: {palette["page"]};
  --bg-card: {card_background};
  --bg-inner: {palette["inner"]};
  --accent-primary: {palette["accent"]};
  --secondary-accent: {palette["secondary"]};
  --accent-glow: color-mix(in srgb, {palette["accent"]} 24%, transparent);
  --accent-gradient: linear-gradient(125deg, {palette["action"]}, {palette["action"]});
  --border-color: {palette["border"]};
  --text-main: {palette["text"]};
  --text-muted: {palette["muted"]};
  --premium-sidebar-width: {layout["sidebar"]};
  --premium-layout-gap: {layout["gap"]};
  --premium-content-space: {layout["space"]};
  --premium-hero-height: {layout["hero"]};
}}
.app-shell.light-mode {{
  color-scheme: light;
  --bg-page: color-mix(in srgb, {palette["page"]} 5%, #ffffff);
  --bg-card: color-mix(in srgb, {palette["accent"]} 3%, #ffffff);
  --bg-inner: color-mix(in srgb, {palette["accent"]} 8%, #ffffff);
  --accent-primary: {palette["accent"]};
  --accent-glow: color-mix(in srgb, {palette["accent"]} 18%, transparent);
  --accent-gradient: linear-gradient(125deg, {palette["action"]}, {palette["action"]});
  --border-color: {palette["border"]};
  --text-main: #1d2933;
  --text-muted: #586775;
}}
body {{
  background:
    radial-gradient(ellipse at 86% -18%, color-mix(in srgb, {palette["accent"]} 12%, transparent), transparent 44%),
    var(--bg-page);
}}
.app-shell {{
  grid-template-columns: var(--premium-sidebar-width) minmax(0, 1fr);
  gap: var(--premium-layout-gap);
  padding: clamp(14px, 2.6vw, 36px);
}}
.sidebar {{
  align-self: start;
  position: sticky;
  top: 18px;
  max-height: calc(100vh - 36px);
  overflow-y: auto;
  border-radius: var(--premium-radius);
  padding: var(--premium-content-space);
  background: var(--bg-card);
  border-color: var(--border-color);
  box-shadow: 0 18px 48px rgba(0, 0, 0, .14);
  backdrop-filter: {blur};
}}
.brand-name, .topbar h1, .section-head-row h2 {{
  letter-spacing: -.045em;
}}
.topbar {{
  min-height: 0;
  padding: 18px 8px 22px;
  border-radius: 0;
  border: 0;
  border-bottom: 1px solid var(--border-color);
  background: transparent;
  box-shadow: none;
}}
.topbar h1 {{ font-size: clamp(1.6rem, 3vw, 2.65rem); line-height: 1.08; max-width: 20ch; }}
.topbar-subtitle {{ max-width: 58ch; line-height: 1.7; }}
.topbar-heading {{ min-width: 0; }}
.top-actions {{ max-width: 560px; justify-content: flex-end; gap: 10px; }}
.top-actions > * {{ min-width: 0; }}
.domain-hero-banner {{
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(210px, .85fr) minmax(132px, .52fr);
  gap: 20px;
  align-items: center;
  padding: clamp(20px, 2.5vw, 32px);
  border: 1px solid var(--border-color);
  border-radius: calc(var(--premium-radius) + 8px);
  background:
    linear-gradient(112deg, color-mix(in srgb, var(--bg-card) 88%, var(--accent-primary)), var(--bg-card) 70%),
    var(--bg-card);
  box-shadow: 0 22px 48px rgba(0, 0, 0, .15);
}}
.domain-hero-left {{ min-width: 0; gap: 12px; }}
.domain-hero-title {{ font-size: clamp(1.65rem, 2.65vw, 2.45rem); line-height: 1.08; max-width: 16ch; }}
.domain-hero-desc {{ max-width: 48ch; font-size: 1rem; }}
.domain-hero-badge {{ border-color: color-mix(in srgb, var(--accent-primary) 55%, transparent); }}
.domain-hero-visual {{ width: 100%; max-width: 430px; min-width: 0; height: clamp(190px, 20vw, 250px); grid-template-rows: repeat(2, minmax(0, 1fr)); justify-self: center; gap: 10px; }}
.domain-hero-image {{ height: clamp(140px, 17vw, 205px); border-radius: 14px; box-shadow: 0 14px 28px rgba(0, 0, 0, .2); }}
.domain-hero-image:first-child {{ grid-row: span 2; height: 100%; min-height: 0; }}
.domain-hero-image:last-child {{ height: 100%; min-height: 0; }}
.domain-hero-art {{ grid-template-columns: repeat(2, minmax(0, 1fr)); grid-template-rows: repeat(2, minmax(0, 1fr)); }}
.domain-hero-art-card {{ display: flex; flex-direction: column; justify-content: space-between; min-width: 0; padding: 16px; border: 1px solid var(--border-color); border-radius: 14px; background: color-mix(in srgb, var(--bg-card) 92%, var(--accent-primary)); box-shadow: 0 12px 24px rgba(0, 0, 0, .12); }}
.domain-hero-art-card:first-child {{ grid-row: span 2; }}
.domain-hero-art-card span {{ color: var(--text-muted); font-size: .68rem; font-weight: 700; letter-spacing: .1em; }}
.domain-hero-art-card strong {{ overflow-wrap: anywhere; font-size: clamp(1rem, 1.5vw, 1.35rem); }}
.domain-hero-art-card i {{ width: 38px; height: 3px; border-radius: 4px; background: var(--accent-primary); }}
.domain-hero-actions {{ display: flex; align-items: center; flex-wrap: wrap; gap: 10px; margin-top: 6px; }}
.domain-hero-actions a {{ display: inline-flex; align-items: center; min-height: 42px; padding: 9px 16px; border-radius: 11px; color: var(--text-main); text-decoration: none; }}
.domain-hero-stats {{
  grid-column: auto;
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 10px;
  padding: 0;
  border-top: 0;
}}
.domain-stat-card {{ display: grid; gap: 5px; padding: 13px; border: 1px solid var(--border-color); border-radius: 14px; background: color-mix(in srgb, var(--bg-inner) 82%, var(--accent-primary)); }}
.domain-stat-card:first-child {{ padding-left: 13px; }}
.domain-stat-card:last-child {{ border: 1px solid var(--border-color); }}
.domain-stat-val {{ font-size: 1.3rem; line-height: 1.2; font-weight: 750; }}
.domain-stat-lbl {{ display: block; margin-top: 2px; color: var(--text-muted); font-size: .72rem; line-height: 1.35; }}
.content-block {{
  border: 0;
  border-radius: 0;
  padding: 8px 0;
  background: transparent;
  box-shadow: none;
}}
.dashboard-card, .resource-card, .panel {{
  border-radius: calc(var(--premium-radius) - 4px);
  border-color: var(--border-color);
  background: var(--bg-card);
  box-shadow: 0 8px 24px rgba(0, 0, 0, .08);
  transition: transform 180ms ease, border-color 180ms ease, box-shadow 180ms ease;
}}
.dashboard-card:hover, .resource-card:hover {{
  transform: translateY(-2px);
  border-color: color-mix(in srgb, {palette["accent"]} 45%, var(--border-color));
  box-shadow: 0 14px 30px rgba(0, 0, 0, .13);
}}
.dashboard-card {{ border-top: 3px solid var(--accent-primary); background: linear-gradient(145deg, color-mix(in srgb, var(--bg-card) 76%, var(--accent-primary)), var(--bg-card)); }}
.dashboard-card:nth-child(even) {{ border-top-color: var(--secondary-accent, var(--accent-primary)); background: linear-gradient(145deg, color-mix(in srgb, var(--bg-card) 78%, var(--secondary-accent, var(--accent-primary))), var(--bg-card)); }}
.resource-card {{ overflow: hidden; }}
.resource-card .section-head-row {{ align-items: flex-start; }}
.resource-card input {{ min-width: 180px; }}
.table-wrap {{ border: 1px solid var(--border-color); background: var(--bg-card); }}
table {{ min-width: 620px; }}
th {{ background: var(--bg-inner); letter-spacing: .035em; text-transform: uppercase; font-size: .72rem; }}
td {{ vertical-align: middle; }}
tbody tr:last-child td {{ border-bottom: 0; }}
.section-head-row {{ padding-bottom: 12px; border-bottom: 1px solid var(--border-color); }}
button, .nav-list a, input, select, textarea {{ transition-duration: 180ms; }}
button:hover {{ transform: translateY(-2px); filter: saturate(1.08) brightness(1.04); }}
button:focus-visible, a:focus-visible, input:focus-visible, select:focus-visible, textarea:focus-visible {{
  outline: 3px solid {palette["accent"]};
  outline-offset: 3px;
}}
input, select, textarea {{ border-color: var(--border-color); }}
input:focus, select:focus, textarea:focus {{
  border-color: {palette["accent"]};
  box-shadow: 0 0 0 3px color-mix(in srgb, {palette["accent"]} 20%, transparent);
}}
.table-wrap {{ border-radius: 14px; }}
@media (max-width: 980px) {{
  .app-shell {{ grid-template-columns: 1fr; gap: 16px; }}
  .sidebar {{ position: static; max-height: none; }}
  .domain-hero-banner {{ grid-template-columns: minmax(0, 1.1fr) minmax(200px, .9fr); }}
  .domain-hero-stats {{ grid-column: 1 / -1; grid-template-columns: repeat(3, minmax(0, 1fr)); }}
  .domain-hero-visual {{ justify-self: stretch; max-width: none; height: 190px; }}
  .domain-hero-image:first-child, .domain-hero-image:last-child {{ height: 100%; min-height: 0; }}
}}
@media (max-width: 1100px) {{
  .topbar {{ align-items: flex-start; flex-direction: column; }}
  .top-actions {{ width: 100%; max-width: none; justify-content: flex-start; }}
}}
@media (max-width: 640px) {{
  .app-shell {{ grid-template-columns: minmax(0, 1fr); padding: 12px; gap: 12px; }}
  .sidebar {{ padding: 14px; border-radius: 16px; gap: 12px; }}
  .content-block {{ padding: 18px; border-radius: 18px; }}
  .nav-list {{ flex-direction: row; gap: 6px; overflow-x: auto; padding-bottom: 3px; }}
  .nav-list a {{ flex: 0 0 auto; white-space: nowrap; padding: 9px 12px; }}
  .sidebar-action-box {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; margin-top: 0; padding-top: 10px; }}
  .sidebar-action-box button {{ min-height: 42px; padding: 8px; font-size: .8rem; }}
  .sidebar-user {{ padding-top: 8px; }}
  .topbar {{ align-items: flex-start; flex-direction: column; gap: 20px; }}
  .top-actions {{ width: 100%; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; }}
  .top-actions button {{ min-height: 42px; padding: 8px; font-size: .8rem; }}
  .top-actions > a {{ display: flex; align-items: center; justify-content: center; min-height: 42px; }}
  .topbar-user-badge {{ grid-column: 1 / -1; }}
  .content-block {{ padding: 6px 0; }}
  .domain-hero-banner {{ grid-template-columns: minmax(0, 1fr); padding: 22px; gap: 18px; }}
  .domain-hero-stats {{ grid-column: auto; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; }}
  .domain-stat-card, .domain-stat-card:first-child {{ padding: 10px; border: 1px solid var(--border-color); }}
  .domain-stat-val {{ font-size: 1.05rem; }}
  .domain-stat-lbl {{ font-size: .68rem; line-height: 1.3; }}
  .domain-hero-actions {{ width: 100%; }}
  .domain-hero-actions button, .domain-hero-actions a {{ flex: 1 1 auto; justify-content: center; }}
  .dashboard-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }}
  .dashboard-card {{ padding: 16px; }}
  .table-wrap {{ overflow-x: auto; -webkit-overflow-scrolling: touch; }}
}}
@media (max-width: 400px) {{
  .dashboard-grid {{ grid-template-columns: minmax(0, 1fr); }}
}}
@media (prefers-reduced-motion: no-preference) {{
  .content-block {{ animation: premium-arrive 420ms cubic-bezier(.2, .65, .25, 1) both; }}
  .content-block:nth-of-type(2) {{ animation-delay: 35ms; }}
  .content-block:nth-of-type(3) {{ animation-delay: 70ms; }}
}}
@keyframes premium-arrive {{
  from {{ opacity: .84; transform: translateY(8px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}
@media (prefers-reduced-motion: reduce) {{
  :root {{ scroll-behavior: auto; }}
  *, *::before, *::after {{
    animation-duration: .01ms !important;
    animation-iteration-count: 1 !important;
    scroll-behavior: auto !important;
    transition-duration: .01ms !important;
  }}
}}
/* PREMIUM_DESIGN_END */
""".strip() + "\n"

    def replace_css(self, current_css: str, new_css: str) -> str:
        """Replace the owned premium style block without discarding custom CSS around it."""
        pattern = re.compile(
            r"/\* Premium visual direction: [a-z]+\. Generated as an additive, CSS-only layer\. \*/"
            r"\s*/\* PREMIUM_DESIGN_BEGIN \*/.*?/\* PREMIUM_DESIGN_END \*/",
            flags=re.DOTALL,
        )
        matches = list(pattern.finditer(current_css))
        if len(matches) > 1:
            raise ValueError("Multiple premium design blocks were found; refusing to overwrite ambiguous custom CSS.")
        if matches:
            return pattern.sub(lambda _: new_css.rstrip(), current_css, count=1)
        return f"{current_css.rstrip()}\n\n{new_css}"

    def active_premium_css(self, stylesheet: str) -> str | None:
        """Extract this engine's managed style block for isolated validation."""
        pattern = re.compile(
            r"/\* Premium visual direction: [a-z]+\. Generated as an additive, CSS-only layer\. \*/"
            r"\s*/\* PREMIUM_DESIGN_BEGIN \*/.*?/\* PREMIUM_DESIGN_END \*/",
            flags=re.DOTALL,
        )
        match = pattern.search(stylesheet)
        return match.group(0) if match else None

    def validate_css(self, css: str) -> list[str]:
        """Validate the key responsive, accessible, and performance constraints."""
        errors: list[str] = []
        required = (
            "prefers-reduced-motion: reduce",
            "focus-visible",
            "max-width: 640px",
            "max-width: 980px",
            "Premium visual direction:",
        )
        for token in required:
            if token not in css:
                errors.append(f"Missing visual requirement: {token}")
        if "@import" in css or "url(" in css:
            errors.append("Premium styles must not add remote fonts, imports, or image assets.")
        if css.count("{") != css.count("}"):
            errors.append("Unbalanced CSS blocks.")
        return errors
