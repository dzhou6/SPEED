from __future__ import annotations

"""
CourseCupid / StackMatch MVP ranking.

We prioritize role coverage first (fill missing roles in a 4-person pod),
then overlapping availability, then stack compatibility (shared tools and known
pairings like React + FastAPI), then recent activity. We also penalize near-
identical profiles so the feed isn't repetitive.

This file is wired into the backend:
- backend/app/main.py -> from .matching import rank_candidates
- /recommendations calls: rank_candidates(me, candidates, my_pod_roles)

So we KEEP that call signature.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union



# Transparent weights (points)

WEIGHTS = {
    "role": 50.0,          # highest
    "availability": 20.0,
    "skills": 20.0,
    "activity": 10.0,
    "diversity_penalty": 15.0,  # max penalty when profiles are near-identical
}

# MVP roles in this repo (see backend/app/models.py)
ALL_ROLES = ["Frontend", "Backend", "Matching", "Platform"]

# Skills: normalize tokens to lowercase alnum (e.g., "UI/UX" -> "uiux")
# Pairings for "medium boost for complement" (explicit + explainable)
SKILL_SYNERGY_PAIRS = {
    ("react", "fastapi"),
    ("react", "apis"),
    ("python", "fastapi"),
    ("fastapi", "mongodb"),
    ("docker", "aws"),
    ("docker", "azure"),
    ("ml", "data"),
    ("python", "ml"),
    ("security", "apis"),
    ("testing", "apis"),
}

# Availability blocks in this MVP (src/pages/ProfileBuilder.tsx):
# "Mon evening", "Sat morning", ...
# Convert to fixed week-minute intervals so overlap is measurable.
DAY_TO_IDX = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}
BLOCK_TO_RANGE = {
    "morning": (9 * 60, 12 * 60),
    "afternoon": (12 * 60, 17 * 60),
    "evening": (17 * 60, 21 * 60),
    "night": (21 * 60, 24 * 60),  # not currently used, but safe
}


@dataclass
class Ranked:
    userId: str
    score: float
    reasons: List[str]
    breakdown: Dict[str, float]


def rank_candidates(
    me: Dict[str, Any],
    candidates: List[Dict[str, Any]],
    my_pod_roles_or_state: Union[List[str], Dict[str, Any], None],
    prior_swipes: Optional[Sequence[Any]] = None,
    debug: bool = False,
    mode: str = "skillmatch",
) -> List[Dict[str, Any]]:
    """
    Returns a ranked list:
      {userId, score, reasons, breakdown}

    Compatibility:
    - Backend uses: rank_candidates(me, cand, my_pod_roles)
    - Prompt may use: rank_candidates(me, cand, myPodStateDict)

    prior_swipes is optional; /recommendations already filters swiped users,
    but this keeps the function usable elsewhere too.
    
    mode: "quickmatch" or "skillmatch"
    - quickmatch: Prioritize activity + availability (fast active people)
    - skillmatch: Prioritize roles + skills (targeted matching)
    """
    # Adjust weights based on mode
    if mode == "quickmatch":
        weights = {
            "role": 20.0,          # Lower priority
            "availability": 40.0,  # Higher priority
            "skills": 15.0,        # Lower priority
            "activity": 35.0,      # Higher priority
            "diversity_penalty": 15.0,
        }
    else:  # skillmatch (default)
        weights = {
            "role": 50.0,          # Highest priority
            "availability": 20.0,
            "skills": 20.0,
            "activity": 10.0,
            "diversity_penalty": 15.0,
        }
    
    now = datetime.now(timezone.utc)

    me_roles = _norm_roles(me.get("rolePrefs", []))
    me_primary = me_roles[0] if me_roles else ""
    me_skills = _norm_skills(me.get("skills", []))
    me_avail = _norm_availability(me.get("availability", []))

    pod_roles, member_count = _extract_pod_state(my_pod_roles_or_state)
    missing_roles = _missing_roles(pod_roles, member_count)

    swiped_ids = _extract_swiped_ids(prior_swipes)

    ranked: List[Ranked] = []

    for c in candidates:
        cid = c.get("userId") or c.get("id") or c.get("user_id") or c.get("_id")
        if cid is None:
            continue
        user_id = str(cid)

        if user_id in swiped_ids:
            continue

        c_roles = _norm_roles(c.get("rolePrefs", []))
        c_primary = c_roles[0] if c_roles else ""
        c_skills = _norm_skills(c.get("skills", []))
        c_avail = _norm_availability(c.get("availability", []))

        last_active = _parse_dt(
            c.get("lastActiveAt") or (c.get("presence") or {}).get("lastActiveAt"),
            now=now,
        )

        role_s, role_reason = _role_score_and_reason(
            me_primary=me_primary,
            cand_roles=c_roles,
            missing_roles=missing_roles,
            in_pod=bool(pod_roles),
        )
        skills_s, skills_meta = _skills_score(me_skills, c_skills)
        avail_s, avail_meta = _availability_score(me_avail, c_avail)
        activity_s, activity_reason = _activity_score(last_active, now)
        diversity_pen = _diversity_penalty(me_primary, me_skills, c_primary, c_skills)

        role_pts = weights["role"] * role_s
        skills_pts = weights["skills"] * skills_s
        avail_pts = weights["availability"] * avail_s
        activity_pts = weights["activity"] * activity_s
        penalty_pts = weights["diversity_penalty"] * diversity_pen

        total = role_pts + skills_pts + avail_pts + activity_pts - penalty_pts

        breakdown = {
            "role": round(role_pts, 2),
            "skills": round(skills_pts, 2),
            "availability": round(avail_pts, 2),
            "activity": round(activity_pts, 2),
            "diversityPenalty": round(-penalty_pts, 2),
        }

        reasons = _pick_top_reasons(
            role_reason=role_reason,
            role_pts=role_pts,
            skills_meta=skills_meta,
            skills_pts=skills_pts,
            avail_meta=avail_meta,
            avail_pts=avail_pts,
            activity_reason=activity_reason,
            activity_pts=activity_pts,
        )

        ranked.append(
            Ranked(
                userId=user_id,
                score=round(total, 2),
                reasons=reasons,
                breakdown=breakdown,
            )
        )

    # Deterministic sort (score desc, then userId asc)
    ranked.sort(key=lambda r: (-r.score, r.userId))

    if debug:
        _debug_print_top5(ranked)

    return [
        {"userId": r.userId, "score": r.score, "reasons": r.reasons, "breakdown": r.breakdown}
        for r in ranked
    ]



# Role scoring


def _extract_pod_state(my_pod_roles_or_state: Union[List[str], Dict[str, Any], None]) -> Tuple[List[str], int]:
    if my_pod_roles_or_state is None:
        return [], 0

    if isinstance(my_pod_roles_or_state, dict):
        roles = _norm_roles(my_pod_roles_or_state.get("memberRoles", []))
        count = int(my_pod_roles_or_state.get("memberCount", 0) or 0)
        return roles, count

    roles = _norm_roles(list(my_pod_roles_or_state))
    # Backend doesn't pass memberCount; we only need to know "in pod?"
    return roles, (1 if roles else 0)


def _missing_roles(pod_roles: List[str], member_count: int) -> List[str]:
    if member_count <= 0:
        return []
    covered = set(pod_roles)
    return [r for r in ALL_ROLES if r not in covered]


def _role_score_and_reason(
    me_primary: str,
    cand_roles: List[str],
    missing_roles: List[str],
    in_pod: bool,
) -> Tuple[float, str]:
    if not cand_roles:
        return 0.2, "role unspecified"

    cand_primary = cand_roles[0]

    # In a pod: filling missing role is king.
    if in_pod and missing_roles:
        for r in cand_roles:
            if r in missing_roles:
                return 1.0, f"fills missing {r} role"
        if me_primary and cand_primary != me_primary:
            return 0.55, f"adds complementary {cand_primary} role"
        return 0.25, "role is workable"

    # No pod: prefer complementary to my primary role.
    if me_primary and cand_primary == me_primary:
        return 0.25, f"same role ({cand_primary})"
    if me_primary and cand_primary != me_primary:
        return 0.85, f"complements your {me_primary} focus with {cand_primary}"
    return 0.55, f"different role ({cand_primary})"



# Skills scoring


def _skills_score(me_skills: set, c_skills: set) -> Tuple[float, Dict[str, Any]]:
    if not me_skills and not c_skills:
        return 0.0, {"shared": [], "synergy": []}

    inter = sorted(me_skills & c_skills)
    union = me_skills | c_skills
    jacc = (len(inter) / len(union)) if union else 0.0

    synergy_hits: List[Tuple[str, str]] = []
    for a, b in SKILL_SYNERGY_PAIRS:
        if (a in me_skills and b in c_skills) or (b in me_skills and a in c_skills):
            synergy_hits.append((a, b))

    overlap_component = 0.25 * jacc
    complement_component = 0.65 * min(1.0, len(synergy_hits) / 2.0)
    score = min(1.0, overlap_component + complement_component)

    return score, {
        "shared": inter[:5],
        "synergy": synergy_hits[:3],
        "jaccard": round(jacc, 3),
        "synergyCount": len(synergy_hits),
    }



# Availability scoring


def _availability_score(me_avail: List[Tuple[int, int]], c_avail: List[Tuple[int, int]]) -> Tuple[float, Dict[str, Any]]:
    if not me_avail or not c_avail:
        return 0.0, {"overlapMinutes": 0, "overlapBlocks": 0}

    overlap = _interval_overlap_minutes(me_avail, c_avail)
    denom = max(1, min(_total_minutes(me_avail), _total_minutes(c_avail)))
    ratio = max(0.0, min(1.0, overlap / denom))

    return ratio, {
        "overlapMinutes": int(overlap),
        "overlapBlocks": _rough_overlap_blocks(me_avail, c_avail),
    }


def _interval_overlap_minutes(a: List[Tuple[int, int]], b: List[Tuple[int, int]]) -> int:
    a = sorted(a)
    b = sorted(b)
    i = j = 0
    overlap = 0
    while i < len(a) and j < len(b):
        s1, e1 = a[i]
        s2, e2 = b[j]
        s = max(s1, s2)
        e = min(e1, e2)
        if e > s:
            overlap += e - s
        if e1 < e2:
            i += 1
        else:
            j += 1
    return overlap


def _total_minutes(intervals: List[Tuple[int, int]]) -> int:
    return sum(max(0, e - s) for s, e in intervals)


def _rough_overlap_blocks(me_avail: List[Tuple[int, int]], c_avail: List[Tuple[int, int]]) -> int:
    count = 0
    for s1, e1 in me_avail:
        for s2, e2 in c_avail:
            if min(e1, e2) > max(s1, s2):
                count += 1
    return count



# Activity scoring


def _activity_score(last_active: datetime | None, now: datetime) -> Tuple[float, str]:
    if not last_active:
        return 0.3, "activity unknown"

    if last_active.tzinfo is None:
        last_active = last_active.replace(tzinfo=timezone.utc)

    age_hours = (now - last_active).total_seconds() / 3600.0
    if age_hours <= 24:
        return 1.0, "active within 24h"
    if age_hours <= 72:
        return 0.7, "active within 3d"
    if age_hours <= 168:
        return 0.45, "active within 7d"
    return 0.2, "inactive recently"



# Diversity penalty


def _diversity_penalty(me_role: str, me_skills: set, c_role: str, c_skills: set) -> float:
    if not me_role or not c_role or me_role != c_role:
        return 0.0

    union = me_skills | c_skills
    skill_sim = (len(me_skills & c_skills) / len(union)) if union else 1.0
    if skill_sim >= 0.8:
        return min(1.0, (skill_sim - 0.8) / 0.2)
    return 0.0



# Reasons (top 2-3)


def _pick_top_reasons(
    role_reason: str,
    role_pts: float,
    skills_meta: Dict[str, Any],
    skills_pts: float,
    avail_meta: Dict[str, Any],
    avail_pts: float,
    activity_reason: str,
    activity_pts: float,
) -> List[str]:
    options: List[Tuple[float, str]] = []

    if role_pts > 10:
        options.append((role_pts, role_reason))

    if skills_pts > 6:
        if skills_meta.get("synergy"):
            a, b = skills_meta["synergy"][0]
            options.append((skills_pts, f"complementary stack: {a} + {b}"))
        elif skills_meta.get("shared"):
            shared = ", ".join(skills_meta["shared"][:3])
            options.append((skills_pts, f"shared tools: {shared}"))

    if avail_pts > 4:
        blocks = int(avail_meta.get("overlapBlocks", 0) or 0)
        if blocks > 0:
            options.append((avail_pts, f"overlapping availability ({blocks} block{'s' if blocks != 1 else ''})"))

    if activity_pts > 3:
        options.append((activity_pts, activity_reason))

    options.sort(key=lambda x: -x[0])
    reasons = [r for _, r in options[:3]]

    if not reasons:
        reasons = [role_reason, activity_reason][:2]

    return reasons



# Normalization helpers


def _norm_roles(roles: Sequence[Any]) -> List[str]:
    out: List[str] = []
    for r in roles or []:
        rr = r.get("role") if isinstance(r, dict) else str(r)
        rr = rr.strip()
        if rr in ALL_ROLES:
            out.append(rr)
        else:
            cap = rr.capitalize()
            if cap in ALL_ROLES:
                out.append(cap)
    return out


def _norm_skills(skills: Sequence[Any]) -> set:
    out = set()
    for sk in skills or []:
        v = sk.get("name") if isinstance(sk, dict) else sk
        s = str(v).strip().lower()
        if not s:
            continue
        s = "".join(ch for ch in s if ch.isalnum())
        out.add(s)
    return out


def _norm_availability(avail: Sequence[Any]) -> List[Tuple[int, int]]:
    intervals: List[Tuple[int, int]] = []

    for item in avail or []:
        s = str(item).strip()
        if not s:
            continue
        parts = s.split()
        if len(parts) != 2:
            continue

        day, block = parts[0], parts[1].lower()
        if day in DAY_TO_IDX and block in BLOCK_TO_RANGE:
            base = DAY_TO_IDX[day] * 1440
            s0, e0 = BLOCK_TO_RANGE[block]
            intervals.append((base + s0, base + e0))

    return _merge_intervals(sorted(intervals))


def _merge_intervals(intervals: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    if not intervals:
        return []
    merged = [intervals[0]]
    for s, e in intervals[1:]:
        ps, pe = merged[-1]
        if s <= pe:
            merged[-1] = (ps, max(pe, e))
        else:
            merged.append((s, e))
    return merged


def _parse_dt(v: Any, now: datetime) -> datetime | None:
    if v is None:
        return None
    if isinstance(v, datetime):
        return v if v.tzinfo else v.replace(tzinfo=timezone.utc)
    if isinstance(v, (int, float)) and v > 0:
        try:
            return datetime.fromtimestamp(float(v), tz=timezone.utc)
        except Exception:
            return None
    s = str(v).strip()
    if not s:
        return None
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        return None


def _extract_swiped_ids(prior_swipes: Optional[Sequence[Any]]) -> set:
    ids = set()
    for s in prior_swipes or []:
        if isinstance(s, dict):
            uid = s.get("userId") or s.get("id") or s.get("toUserId")
            if uid is not None:
                ids.add(str(uid))
        else:
            ids.add(str(s))
    return ids


def _debug_print_top5(ranked: List[Ranked]) -> None:
    print("\n=== CourseCupid ranker: TOP 5 ===")
    for i, r in enumerate(ranked[:5], start=1):
        print(f"{i}. userId={r.userId} score={r.score}")
        print(f"   reasons={r.reasons}")
        print(f"   breakdown={r.breakdown}")
    print("================================\n")
