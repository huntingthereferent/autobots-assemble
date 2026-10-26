"""Finite certificate for the **observed original SDK SP80 Stage4** row y63
action budget display. Source experiment #40250466381 produced four genuine
independently reset native SDK games and observed GAME_OVER at action100.
Earlier source run #40243990606 directly retained exact bottom rows
through action43.

This is a finite theorem of the explicitly declared observed clock,
not a general model of the underlying ARC game's hidden state or
equivalence to the separate mathematical F3-48 two-letter system.
"""
from __future__ import annotations
from dataclasses import asdict,dataclass
import json

# These are transcribed first-palette14-x SOURCE observations, not generated
# from the candidate equation:
#   action0..43: original full native y63 rows in artifact #12618156519
#   action90..100: original full native 64x64 frames in artifact #12620253953
OBSERVED_EARLY=(
    0,1,1,2,3,3,4,4,5,6,6,7,8,8,9,10,10,11,12,12,13,13,
    14,15,15,16,17,17,18,19,19,20,20,21,22,22,23,24,24,25,
    26,26,27,28
)
OBSERVED_LATE={
    90:58,91:58,92:59,93:60,94:60,95:61,
    96:61,97:62,98:63,99:63,100:64
}

def clock(n:int)->int:
    """Integer formula: number of zero cells at left of original bottom row.

    64 pixels spread over 100 actions, nearest-integer rounding.
    For 0<=n<=100, result=0..64. The source row is zero[:value] and
    palette14[value:64]; n100 has no palette14 pixels and is GAME_OVER.
    """
    if type(n) is not int or not 0<=n<=100:
        raise ValueError("Only genuine Stage4 0..100 finite clock domain")
    return (64*n+50)//100

def rendered_native_row_candidate(n:int)->tuple[int,...]:
    left=clock(n)
    return (0,)*left+(14,)*(64-left)

@dataclass(frozen=True)
class ClockCertificate:
    status:str
    first_clock_value:int
    last_clock_value:int
    finite_index_domain:tuple[int,int]
    exact_source_observed_early_indices:int
    exact_source_observed_late_indices:int
    same_clock_at_two_different_index_pairs:int
    max_index_distance_for_matching_clock:int
    same_parity_different_index_pairs:int
    every_two_step_clock_advance:bool
    original_native_terminal_status:str
    source_original_native_game_count:int

def certify()->ClockCertificate:
    assert len(OBSERVED_EARLY)==44
    assert len(OBSERVED_LATE)==11
    assert all(clock(i)==x for i,x in enumerate(OBSERVED_EARLY))
    assert all(clock(i)==x for i,x in OBSERVED_LATE.items())
    assert rendered_native_row_candidate(0)==(14,)*64
    assert rendered_native_row_candidate(100)==(0,)*64
    same=[
       (a,b)
       for a in range(101)
       for b in range(a+1,101)
       if clock(a)==clock(b)
    ]
    even=[(a,b) for a,b in same if (b-a)%2==0]
    advance=all(clock(n+2)>clock(n) for n in range(99))
    result=ClockCertificate(
        status="CLOSED_FINITE_CLOCK_PROJECTION_CERTIFICATE" if not even and advance
               else "OPEN_CLOCK_INDEX_INJECTION",
        first_clock_value=clock(0),
        last_clock_value=clock(100),
        finite_index_domain=(0,100),
        exact_source_observed_early_indices=len(OBSERVED_EARLY),
        exact_source_observed_late_indices=len(OBSERVED_LATE),
        same_clock_at_two_different_index_pairs=len(same),
        max_index_distance_for_matching_clock=max((b-a for a,b in same),default=0),
        same_parity_different_index_pairs=len(even),
        every_two_step_clock_advance=advance,
        original_native_terminal_status="GAME_OVER",
        source_original_native_game_count=4,
    )
    assert result.status=="CLOSED_FINITE_CLOCK_PROJECTION_CERTIFICATE"
    assert result.max_index_distance_for_matching_clock==1
    assert result.same_clock_at_two_different_index_pairs==36
    assert result.same_parity_different_index_pairs==0
    return result

if __name__=="__main__":
    print("SP80_ORIGINAL_NATIVE_FINITE_CLOCK_CERTIFICATE "+
          json.dumps(asdict(certify()),sort_keys=True))
