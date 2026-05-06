"""
Template Engine safety filter.

Validates rendered output for dangerous shell patterns before
returning scripts to the client. This is a hard safety gate —
no script passes without this validation.
"""
import re

FORBIDDEN_PATTERNS: list[tuple[str, str]] = [
    # Pattern, Description
    (r"rm\s+-[rRf]{1,3}\s+/", "Recursive delete of root filesystem"),
    (r"rm\s+-[rRf]{1,3}\s+\$HOME", "Recursive delete of home directory"),
    (r"rm\s+-[rRf]{1,3}\s+~", "Recursive delete of home directory (tilde)"),
    (r"mkfs\.", "Filesystem format command"),
    (r"format\s+[A-Za-z]:", "Windows drive format command"),
    (r":(\s*)\(\s*\)\s*\{.*\|.*&", "Fork bomb pattern"),
    (r"dd\s+if=", "Raw disk write command"),
    (r">\s*/dev/sd[a-z]", "Direct disk write"),
    (r"shutdown\s+(/s|/r|-h|-r)", "System shutdown/reboot"),
    (r"DROP\s+DATABASE", "SQL database destruction"),
    (r"DROP\s+TABLE", "SQL table destruction"),
    (r"TRUNCATE\s+TABLE", "SQL table truncation"),
    (r"curl\s+.*\|\s*(ba)?sh", "Curl-pipe-to-shell (untrusted exec)"),
    (r"wget\s+.*-O-\s*\|\s*(ba)?sh", "Wget-pipe-to-shell (untrusted exec)"),
    (r"eval\s+\$\(", "Eval of subshell output"),
    (r"base64\s+--decode\s*\|.*sh", "Base64 decode pipe to shell"),
]

_COMPILED: list[tuple[re.Pattern, str]] = [
    (re.compile(pattern, re.IGNORECASE | re.DOTALL), desc)
    for pattern, desc in FORBIDDEN_PATTERNS
]


class SafetyViolationError(Exception):
    """Raised when rendered template output contains a forbidden pattern."""

    def __init__(self, pattern: str, description: str, context: str = "") -> None:
        self.pattern = pattern
        self.description = description
        self.context = context
        super().__init__(
            f"Safety violation detected: {description} "
            f"(pattern: {pattern!r})"
        )


def validate_rendered_output(content: str, template_name: str = "") -> str:
    """
    Scan rendered template output for forbidden patterns.

    Args:
        content: The rendered script content to validate
        template_name: Template name for error context

    Returns:
        The original content unchanged (if safe)

    Raises:
        SafetyViolationError: If any forbidden pattern is found
    """
    for compiled_pattern, description in _COMPILED:
        if compiled_pattern.search(content):
            raise SafetyViolationError(
                pattern=compiled_pattern.pattern,
                description=description,
                context=f"Template: {template_name}",
            )
    return content
