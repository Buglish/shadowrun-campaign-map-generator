"""
Utility functions for Shadowrun dice rolling mechanics.

Shadowrun 5th Edition dice rules:
- Roll pools of D6 dice
- Each 5 or 6 is a "hit"
- Rule of Six: 6s can explode (add extra dice)
- Glitch: More than half the original dice show 1
- Critical Glitch: Glitch with zero hits
"""

import random
from typing import Tuple, List, Dict


def roll_d6() -> int:
    """Roll a single six-sided die."""
    return random.randint(1, 6)


def roll_shadowrun_dice(
    pool_size: int,
    use_rule_of_six: bool = True,
    edge_used: bool = False
) -> Dict[str, any]:
    """
    Roll a pool of Shadowrun dice and calculate results.

    Args:
        pool_size: Number of dice to roll
        use_rule_of_six: If True, 6s explode and add additional dice
        edge_used: If True, all 6s explode (even if rule_of_six is False)

    Returns:
        Dictionary containing:
            - dice_results: List of all die results
            - original_dice: List of the first pool_size dice (for glitch detection)
            - total_hits: Number of hits (5s and 6s)
            - ones_count: Number of 1s in original dice
            - is_glitch: True if more than half original dice are 1s
            - is_critical_glitch: True if glitch and zero hits
    """
    if pool_size < 1:
        pool_size = 1
    if pool_size > 50:
        pool_size = 50

    dice_results = []
    original_dice = []

    # Roll initial pool
    for i in range(pool_size):
        roll = roll_d6()
        dice_results.append(roll)
        original_dice.append(roll)

    # Handle Rule of Six (exploding 6s)
    if use_rule_of_six or edge_used:
        exploding_dice = [d for d in dice_results if d == 6]
        max_explosions = 100  # Safety limit to prevent infinite loops

        while exploding_dice and max_explosions > 0:
            new_exploding = []
            for _ in exploding_dice:
                roll = roll_d6()
                dice_results.append(roll)
                if roll == 6:
                    new_exploding.append(roll)
            exploding_dice = new_exploding
            max_explosions -= 1

    # Count hits (5s and 6s)
    total_hits = sum(1 for d in dice_results if d >= 5)

    # Count 1s in ORIGINAL dice only (for glitch detection)
    ones_count = sum(1 for d in original_dice if d == 1)

    # Detect glitch (more than half of ORIGINAL dice are 1s)
    is_glitch = ones_count > (len(original_dice) / 2)

    # Critical glitch = glitch + zero hits
    is_critical_glitch = is_glitch and total_hits == 0

    return {
        'dice_results': dice_results,
        'original_dice': original_dice,
        'total_hits': total_hits,
        'ones_count': ones_count,
        'is_glitch': is_glitch,
        'is_critical_glitch': is_critical_glitch,
    }


def check_success(hits: int, threshold: int = None) -> bool:
    """
    Check if a roll succeeded based on hits vs threshold.

    Args:
        hits: Number of hits rolled
        threshold: Number of hits needed (None if not applicable)

    Returns:
        True if hits >= threshold, None if no threshold set
    """
    if threshold is None:
        return None
    return hits >= threshold


def format_dice_results(dice_results: List[int], original_count: int = None) -> str:
    """
    Format dice results for display, highlighting hits and ones.

    Args:
        dice_results: List of die results
        original_count: Number of original dice (to separate explosions)

    Returns:
        Formatted string representation
    """
    if not dice_results:
        return ""

    result_parts = []
    for i, die in enumerate(dice_results):
        # Mark separation point if original_count provided
        if original_count and i == original_count:
            result_parts.append("|")

        # Format based on result
        if die >= 5:
            result_parts.append(f"[{die}]")  # Hit
        elif die == 1:
            result_parts.append(f"({die})")  # One (potential glitch)
        else:
            result_parts.append(f"{die}")    # Normal

    return " ".join(result_parts)


def calculate_opposed_test(
    attacker_hits: int,
    defender_hits: int
) -> Dict[str, any]:
    """
    Calculate results of an opposed test.

    In Shadowrun, opposed tests compare hits:
    - If attacker hits > defender hits, attacker wins
    - Net hits = attacker_hits - defender_hits
    - Tie goes to defender

    Args:
        attacker_hits: Number of hits the attacker rolled
        defender_hits: Number of hits the defender rolled

    Returns:
        Dictionary with:
            - winner: 'attacker', 'defender', or 'tie'
            - net_hits: Difference in hits
            - attacker_success: True if attacker won
    """
    net_hits = attacker_hits - defender_hits

    if net_hits > 0:
        winner = 'attacker'
        attacker_success = True
    elif net_hits < 0:
        winner = 'defender'
        attacker_success = False
    else:
        winner = 'tie'
        attacker_success = False  # Tie goes to defender

    return {
        'winner': winner,
        'net_hits': abs(net_hits),
        'attacker_success': attacker_success,
    }


def get_hit_description(hits: int) -> str:
    """
    Get a descriptive text for the number of hits.

    Args:
        hits: Number of hits

    Returns:
        Descriptive string
    """
    if hits == 0:
        return "No hits"
    elif hits == 1:
        return "1 hit"
    elif hits <= 3:
        return f"{hits} hits (Marginal success)"
    elif hits <= 5:
        return f"{hits} hits (Good success)"
    elif hits <= 8:
        return f"{hits} hits (Great success)"
    else:
        return f"{hits} hits (Exceptional success!)"
