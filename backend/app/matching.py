from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

@dataclass
class Ranked:
    userId: str
    score: float
    reasons: List[str]

def _overlap_count(a: List[str], b: List[str]) -> int:
    return len(set(a) & set(b))

def _role_score(me_roles: List[str], cand_roles: List[str], missing_roles: List[str]) -> Tuple[float, List[str]]:
    reasons: List[str] = []
    score = 0.0

    for r in cand_roles:
        if r in missing_roles:
            score += 5.0
            reasons.append(f"Fills missing {r} role")
            break

    if score == 0 and me_roles and cand_roles:
        if cand_roles[0] != me_roles[0]:
            score += 2.0
            reasons.append("Complementary role")

    return score, reasons

def _activity_score(last_active: datetime | None) -> Tuple[float, List[str]]:
    if not last_active:
        return -0.5, ["No recent activity signal"]
    
    # Ensure both datetimes are timezone-aware (UTC)
    now = datetime.now(timezone.utc)
    
    # If last_active is naive (no timezone), assume it's UTC
    if last_active.tzinfo is None:
        last_active = last_active.replace(tzinfo=timezone.utc)
    # If it's aware but not UTC, convert to UTC
    elif last_active.tzinfo != timezone.utc:
        last_active = last_active.astimezone(timezone.utc)
    
    age_hours = (now - last_active).total_seconds() / 3600
    if age_hours <= 24:
        return 2.0, ["Active today"]
    if age_hours <= 72:
        return 1.0, ["Active this week"]
    return -0.5, ["Inactive recently"]

def rank_candidates(me: Dict[str, Any], candidates: List[Dict[str, Any]], my_pod_roles: List[str]) -> List[Dict[str, Any]]:
    ALL = ["Frontend", "Backend", "Matching", "Platform"]
    missing = [r for r in ALL if r not in set(my_pod_roles or [])]

    ranked: List[Ranked] = []
    for c in candidates:
        reasons: List[str] = []
        score = 0.0

        rs, rr = _role_score(me.get("rolePrefs", []), c.get("rolePrefs", []), missing)
        score += rs
        reasons += rr

        ov = _overlap_count(me.get("skills", []), c.get("skills", []))
        if ov > 0:
            score += min(2.0, 0.4 * ov)
            reasons.append("Shared skills")

        av = _overlap_count(me.get("availability", []), c.get("availability", []))
        if av > 0:
            score += min(3.0, 1.0 + 0.5 * av)
            reasons.append("Overlapping availability")

        ascore, areasons = _activity_score(c.get("lastActiveAt"))
        score += ascore
        reasons += areasons

        ranked.append(Ranked(userId=str(c["_id"]), score=score, reasons=reasons[:3]))

    ranked.sort(key=lambda x: x.score, reverse=True)
    return [{"userId": r.userId, "score": r.score, "reasons": r.reasons} for r in ranked]
