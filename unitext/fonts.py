"""Unicode typography transforms used by Unitext."""

from __future__ import annotations

import random
import unicodedata
from collections.abc import Callable


def _translate(
    text: str,
    *,
    upper_start: int | None = None,
    lower_start: int | None = None,
    digit_start: int | None = None,
    exceptions: dict[str, str] | None = None,
) -> str:
    """Translate ASCII letters/digits into a contiguous Unicode alphabet."""
    exceptions = exceptions or {}
    out: list[str] = []

    for char in text:
        if char in exceptions:
            out.append(exceptions[char])
        elif upper_start is not None and "A" <= char <= "Z":
            out.append(chr(upper_start + ord(char) - ord("A")))
        elif lower_start is not None and "a" <= char <= "z":
            out.append(chr(lower_start + ord(char) - ord("a")))
        elif digit_start is not None and "0" <= char <= "9":
            out.append(chr(digit_start + ord(char) - ord("0")))
        else:
            out.append(char)

    return "".join(out)


# Mathematical alphanumeric symbols. Some alphabets contain intentionally
# non-contiguous characters, so their exceptional glyphs are specified below.
BOLD = lambda s: _translate(s, upper_start=0x1D400, lower_start=0x1D41A, digit_start=0x1D7CE)

ITALIC = lambda s: _translate(
    s,
    upper_start=0x1D434,
    lower_start=0x1D44E,
    exceptions={"h": "ℎ"},
)

BOLD_ITALIC = lambda s: _translate(
    s,
    upper_start=0x1D468,
    lower_start=0x1D482,
    digit_start=None,
    exceptions={"h": "𝒉"},
)

SCRIPT = lambda s: _translate(
    s,
    upper_start=0x1D49C,
    lower_start=0x1D4B6,
    exceptions={
        "B": "ℬ", "E": "ℰ", "F": "ℱ", "H": "ℋ", "I": "ℐ",
        "L": "ℒ", "M": "ℳ", "R": "ℛ", "e": "ℯ", "g": "ℊ",
        "o": "ℴ",
    },
)

FRAKTUR = lambda s: _translate(
    s,
    upper_start=0x1D504,
    lower_start=0x1D51E,
    exceptions={
        "C": "ℭ", "H": "ℌ", "I": "ℑ", "R": "ℜ", "Z": "ℨ",
    },
)

DOUBLE = lambda s: _translate(
    s,
    upper_start=0x1D538,
    lower_start=0x1D552,
    digit_start=0x1D7D8,
    exceptions={
        "C": "ℂ", "H": "ℍ", "N": "ℕ", "P": "ℙ", "Q": "ℚ",
        "R": "ℝ", "Z": "ℤ",
    },
)

MONOSPACE = lambda s: _translate(
    s,
    upper_start=0x1D670,
    lower_start=0x1D68A,
    digit_start=0x1D7F6,
)

BOLD_SCRIPT = lambda s: _translate(s, upper_start=0x1D4D0, lower_start=0x1D4EA)

BOLD_FRAKTUR = lambda s: _translate(s, upper_start=0x1D56C, lower_start=0x1D586)

SANS = lambda s: _translate(
    s, upper_start=0x1D5A0, lower_start=0x1D5BA, digit_start=0x1D7E2
)

SANS_BOLD = lambda s: _translate(
    s, upper_start=0x1D5D4, lower_start=0x1D5EE, digit_start=0x1D7EC
)

SANS_ITALIC = lambda s: _translate(s, upper_start=0x1D608, lower_start=0x1D622)

SANS_BOLD_ITALIC = lambda s: _translate(s, upper_start=0x1D63C, lower_start=0x1D656)

CIRCLED_UPPER = {chr(ord("A") + i): chr(0x24B6 + i) for i in range(26)}
CIRCLED_LOWER = {chr(ord("a") + i): chr(0x24D0 + i) for i in range(26)}
CIRCLED_DIGITS = {str(i): ("⓪" if i == 0 else chr(0x2460 + i - 1)) for i in range(10)}
CIRCLED = lambda s: "".join(
    CIRCLED_UPPER.get(c, CIRCLED_LOWER.get(c, CIRCLED_DIGITS.get(c, c))) for c in s
)

NEGATIVE_CIRCLED_UPPER = {chr(ord("A") + i): chr(0x1F150 + i) for i in range(26)}
NEGATIVE_CIRCLED_LOWER = {chr(ord("a") + i): chr(0x1F150 + i) for i in range(26)}
NEGATIVE_CIRCLED = lambda s: "".join(NEGATIVE_CIRCLED_UPPER.get(c, c) for c in s)

SUPERSCRIPT = str.maketrans({
    "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
    "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹",
    "+": "⁺", "-": "⁻", "=": "⁼", "(": "⁽", ")": "⁾",
    "a": "ᵃ", "b": "ᵇ", "c": "ᶜ", "d": "ᵈ", "e": "ᵉ",
    "f": "ᶠ", "g": "ᵍ", "h": "ʰ", "i": "ⁱ", "j": "ʲ",
    "k": "ᵏ", "l": "ˡ", "m": "ᵐ", "n": "ⁿ", "o": "ᵒ",
    "p": "ᵖ", "r": "ʳ", "s": "ˢ", "t": "ᵗ", "u": "ᵘ",
    "v": "ᵛ", "w": "ʷ", "x": "ˣ", "y": "ʸ", "z": "ᶻ",
})

SUBSCRIPT = str.maketrans({
    "0": "₀", "1": "₁", "2": "₂", "3": "₃", "4": "₄",
    "5": "₅", "6": "₆", "7": "₇", "8": "₈", "9": "₉",
    "+": "₊", "-": "₋", "=": "₌", "(": "₍", ")": "₎",
    "a": "ₐ", "e": "ₑ", "h": "ₕ", "i": "ᵢ", "j": "ⱼ",
    "k": "ₖ", "l": "ₗ", "m": "ₘ", "n": "ₙ", "o": "ₒ",
    "p": "ₚ", "r": "ᵣ", "s": "ₛ", "t": "ₜ", "u": "ᵤ",
    "v": "ᵥ", "x": "ₓ",
})

SMALL_CAPS = {
    "a": "ᴀ", "b": "ʙ", "c": "ᴄ", "d": "ᴅ", "e": "ᴇ", "f": "ꜰ",
    "g": "ɢ", "h": "ʜ", "i": "ɪ", "j": "ᴊ", "k": "ᴋ", "l": "ʟ",
    "m": "ᴍ", "n": "ɴ", "o": "ᴏ", "p": "ᴘ", "q": "ǫ", "r": "ʀ",
    "s": "s", "t": "ᴛ", "u": "ᴜ", "v": "ᴠ", "w": "ᴡ", "x": "x",
    "y": "ʏ", "z": "ᴢ",
}

GREEK = {
    "A": "Α", "B": "Β", "C": "Ϲ", "D": "Δ", "E": "Ε", "F": "Φ",
    "G": "Γ", "H": "Η", "I": "Ι", "J": "Ϳ", "K": "Κ", "L": "Λ",
    "M": "Μ", "N": "Ν", "O": "Ο", "P": "Ρ", "Q": "Θ", "R": "Ρ",
    "S": "Σ", "T": "Τ", "U": "Υ", "V": "Ѵ", "W": "Ω", "X": "Χ",
    "Y": "Υ", "Z": "Ζ",
    "a": "α", "b": "β", "c": "ϲ", "d": "δ", "e": "ε", "f": "φ",
    "g": "ɡ", "h": "η", "i": "ι", "j": ";", "k": "κ", "l": "λ",
    "m": "μ", "n": "ν", "o": "ο", "p": "ρ", "q": "θ", "r": "ρ",
    "s": "σ", "t": "τ", "u": "υ", "v": "ν", "w": "ω", "x": "χ",
    "y": "γ", "z": "ζ",
}

FULLWIDTH = str.maketrans(
    {chr(i): chr(0xFF01 + i - 0x21) for i in range(0x21, 0x7F)} | {" ": "　"}
)

SQUARED_UPPER = {chr(ord("A") + i): chr(0x1F130 + i) for i in range(26)}
SQUARED = lambda s: "".join(SQUARED_UPPER.get(c.upper(), c) for c in s)

NEGATIVE_SQUARED_UPPER = {chr(ord("A") + i): chr(0x1F170 + i) for i in range(26)}
NEGATIVE_SQUARED = lambda s: "".join(NEGATIVE_SQUARED_UPPER.get(c.upper(), c) for c in s)

PARENTHESIZED_LOWER = {chr(ord("a") + i): chr(0x249C + i) for i in range(26)}
PARENTHESIZED_UPPER = {chr(ord("A") + i): chr(0x1F110 + i) for i in range(26)}
PARENTHESIZED = lambda s: "".join(
    PARENTHESIZED_UPPER.get(c, PARENTHESIZED_LOWER.get(c, c)) for c in s
)

REGIONAL_INDICATOR = {chr(ord("A") + i): chr(0x1F1E6 + i) for i in range(26)}
REGIONAL = lambda s: "".join(
    REGIONAL_INDICATOR.get(c.upper(), c) if c != " " else "  " for c in s
)

# Forcing U+FE0F (variation selector-16) on the negative-squared letters
# makes Discord render them with full emoji presentation (colored tiles)
# instead of the plain black-and-white glyph. Keycap digits are "real"
# multi-codepoint emoji already (digit + FE0F + combining enclosing keycap).
EMOJI_LETTER = {chr(ord("A") + i): chr(0x1F170 + i) + "️" for i in range(26)}
EMOJI_DIGIT = {str(d): str(d) + "️⃣" for d in range(10)}
EMOJI = lambda s: "".join(
    EMOJI_LETTER.get(c.upper(), EMOJI_DIGIT.get(c, c)) for c in s
)

# Combining diacritical marks, grouped by where they stack relative to the
# base character. Zalgo deliberately "breaks" text by piling several of
# these onto every character; the per-character cap keeps output from
# exploding past Discord's message-length limits on longer input.
_ZALGO_ABOVE = [chr(c) for c in range(0x0300, 0x0315)]
_ZALGO_BELOW = [chr(c) for c in range(0x0316, 0x0333)]
_ZALGO_MID = [chr(c) for c in (0x0334, 0x0335, 0x0336, 0x0337, 0x0338)]


def _zalgo(text: str, *, intensity: int = 3) -> str:
    out: list[str] = []

    for char in text:
        out.append(char)

        if char.isspace():
            continue

        for pool in (_ZALGO_ABOVE, _ZALGO_BELOW, _ZALGO_MID):
            out.extend(random.choices(pool, k=intensity))

    return "".join(out)


UPSIDE_DOWN = str.maketrans({
    "a": "ɐ", "b": "q", "c": "ɔ", "d": "p", "e": "ǝ", "f": "ɟ",
    "g": "ƃ", "h": "ɥ", "i": "ᴉ", "j": "ɾ", "k": "ʞ", "l": "ʃ",
    "m": "ɯ", "n": "u", "o": "o", "p": "d", "q": "b", "r": "ɹ",
    "s": "s", "t": "ʇ", "u": "n", "v": "ʌ", "w": "ʍ", "x": "x",
    "y": "ʎ", "z": "z",
    "A": "∀", "B": "B", "C": "Ↄ", "D": "◖", "E": "Ǝ", "F": "Ⅎ",
    "G": "פ", "H": "H", "I": "I", "J": "ſ", "K": "⋊", "L": "Γ",
    "M": "W", "N": "N", "O": "O", "P": "Ԁ", "Q": "Ό", "R": "ᴚ",
    "S": "S", "T": "⊥", "U": "∩", "V": "Λ", "W": "M", "X": "X",
    "Y": "⅄", "Z": "Z",
    "1": "Ɩ", "2": "ᄅ", "3": "Ɛ", "4": "ㄣ", "5": "ϛ", "6": "9",
    "7": "L", "8": "8", "9": "6", "0": "0",
})


def _small_caps(text: str) -> str:
    return "".join(SMALL_CAPS.get(c, c) for c in text.lower())


def _superscript(text: str) -> str:
    return text.translate(SUPERSCRIPT)


def _subscript(text: str) -> str:
    return text.translate(SUBSCRIPT)


def _upside_down(text: str) -> str:
    # Reverse grapheme-unaware text after mapping. This is deliberately simple
    # because Unitext is intended for normal Discord messages, not complex
    # script shaping.
    return text.translate(UPSIDE_DOWN)[::-1]


STYLES: dict[str, tuple[str, Callable[[str], str]]] = {
    "bold": ("Bold", BOLD),
    "italic": ("Italic", ITALIC),
    "bold_italic": ("Bold Italic", BOLD_ITALIC),
    "script": ("Script", SCRIPT),
    "fraktur": ("Fraktur", FRAKTUR),
    "double": ("Double-struck", DOUBLE),
    "monospace": ("Monospace", MONOSPACE),
    "bold_script": ("Bold Script", BOLD_SCRIPT),
    "bold_fraktur": ("Bold Fraktur", BOLD_FRAKTUR),
    "sans": ("Sans-serif", SANS),
    "sans_bold": ("Sans-serif Bold", SANS_BOLD),
    "sans_italic": ("Sans-serif Italic", SANS_ITALIC),
    "sans_bold_italic": ("Sans-serif Bold Italic", SANS_BOLD_ITALIC),
    "circled": ("Circled", CIRCLED),
    "negative_circled": ("Negative circled", NEGATIVE_CIRCLED),
    "squared": ("Squared", SQUARED),
    "negative_squared": ("Negative squared", NEGATIVE_SQUARED),
    "parenthesized": ("Parenthesized", PARENTHESIZED),
    "fullwidth": ("Fullwidth", lambda s: s.translate(FULLWIDTH)),
    "regional": ("Regional indicator (flags)", REGIONAL),
    "emoji": ("Emoji", EMOJI),
    "small_caps": ("Small caps", _small_caps),
    "superscript": ("Superscript", _superscript),
    "subscript": ("Subscript", _subscript),
    "upside_down": ("Upside-down", _upside_down),
    "greek": ("Greek-ish", lambda s: "".join(GREEK.get(c, c) for c in s)),
    "zalgo": ("Zalgo", _zalgo),
}

ALIASES = {
    "bolditalic": "bold_italic",
    "bold-italic": "bold_italic",
    "double-struck": "double",
    "double_struck": "double",
    "smallcaps": "small_caps",
    "small-caps": "small_caps",
    "upside-down": "upside_down",
    "boldscript": "bold_script",
    "bold-script": "bold_script",
    "boldfraktur": "bold_fraktur",
    "bold-fraktur": "bold_fraktur",
    "sans-serif": "sans",
    "sansserif": "sans",
    "sans-bold": "sans_bold",
    "sansbold": "sans_bold",
    "sans-italic": "sans_italic",
    "sansitalic": "sans_italic",
    "sans-bold-italic": "sans_bold_italic",
    "sansbolditalic": "sans_bold_italic",
    "negativecircled": "negative_circled",
    "negative-circled": "negative_circled",
    "negativesquared": "negative_squared",
    "negative-squared": "negative_squared",
    "parens": "parenthesized",
    "full-width": "fullwidth",
    "full_width": "fullwidth",
    "flags": "regional",
    "regional-indicator": "regional",
    "regional_indicator": "regional",
    # Short, casual forms for the `!style text` chat trigger — the names
    # people actually type from memory, not the internal snake_case keys.
    "b": "bold",
    "i": "italic",
    "bi": "bold_italic",
    "ib": "bold_italic",
    "caps": "small_caps",
    "mono": "monospace",
    "wide": "fullwidth",
    "aesthetic": "fullwidth",
    "tiny": "superscript",
    "flip": "upside_down",
    "gothic": "fraktur",
    "cursive": "script",
    "bubble": "circled",
    "outline": "double",
    "glitch": "zalgo",
    "corrupted": "zalgo",
}


def normalize_style(name: str) -> str | None:
    key = "_".join(name.strip().lower().replace("-", " ").split())
    key = ALIASES.get(key, key)
    return key if key in STYLES else None


def transform(text: str, style: str) -> str:
    """Transform text using a named style, raising ValueError for unknown styles."""
    key = normalize_style(style)
    if key is None:
        raise ValueError(f"Unknown style: {style}")
    return STYLES[key][1](text)


def style_names() -> list[str]:
    return list(STYLES)


def visible_name(style: str) -> str:
    key = normalize_style(style)
    if key is None:
        raise ValueError(f"Unknown style: {style}")
    return STYLES[key][0]
