"""Readable durations shared by report tables and figures."""


def readable_time(seconds: float) -> str:
    if seconds < 1:
        return f"{seconds:.3f} sec"
    if seconds < 59.95:
        return f"{seconds:.1f}".removesuffix(".0") + " sec"
    minutes, remainder = divmod(round(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    parts = [f"{hours} hr"] if hours else []
    if minutes:
        parts.append(f"{minutes} min")
    if remainder:
        parts.append(f"{remainder} sec")
    return " ".join(parts)
