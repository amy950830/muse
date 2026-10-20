"""Shared contracts for the Muse autonomous learning runner."""

ALLOWED_DOMAINS = ("frontend", "backend", "security")
CANDIDATE_TRACKS = ("stable", "emerging")
EVOLUTION_LEVELS = ("L0", "L1", "L2", "L3")
CONFIDENCE_VALUES = ("High", "Medium", "Exploratory")
KNOWLEDGE_STATES = ("CURRENT", "AGING", "STALE", "MISSING")
SIGNAL_LEVELS = ("LOW", "MEDIUM", "HIGH", "UNKNOWN")
ORDINARY_AUTO_WRITE_ROOTS = ("knowledge/", "evolution/")
PROTECTED_PATHS = (
    "IDENTITY.md",
    "AGENTS.md",
    "SKILLS.md",
    ".agents/",
    ".github/",
    "automation/",
)
SUPPORTED_SKILLS = (
    "frontend-development",
    "backend-development",
    "application-security",
    "database-engineering",
    "systematic-debugging",
    "continuous-learning",
)


def is_allowed_domain(value: str) -> bool:
    return value in ALLOWED_DOMAINS


def is_ordinary_auto_write_path(path: str) -> bool:
    normalized = path.replace("\\", "/").lstrip("./")
    return any(normalized.startswith(root) for root in ORDINARY_AUTO_WRITE_ROOTS)


def is_protected_path(path: str) -> bool:
    normalized = path.replace("\\", "/").lstrip("./")
    for protected in PROTECTED_PATHS:
        if protected.endswith("/"):
            if normalized.startswith(protected):
                return True
        elif normalized == protected:
            return True
    return False
