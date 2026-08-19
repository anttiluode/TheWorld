# TheWorld

A thinking ledger for the mathematics between the SplatWorld / TinyAvatar / WorldModel line and the SplatNeuron / dendrite / observer line.

> **Do not begin by claiming a brain architecture. Begin by asking what a partial observer can actually know about a larger world.**

The repo starts from one sentence:

> **Each unit has a small nonlinear observation map into a vastly richer surrounding state.**

The word *subspace* is deliberately not used globally. A nonlinear observation map has fibers / indistinguishable sets; only its local differential has a literal linear row-space and nullspace.

The first note develops that distinction and connects it to:

- directional observability and multi-view geometry;
- WorldModel's separation of belief from external support;
- SplatNeuron's receiver-specific observation maps;
- dendritic compartmentalization and nonlinear branch integration;
- visual stability across interrupted input and self-motion;
- entorhinal / hippocampal internal sweeps;
- a possible distributed **observer atlas** rather than one monolithic internal canvas.

## Current files

- `notes/001_observer_atlas.md` — first derivation, literature boundary, and falsifiable gates.
- `experiments/observer_atlas_gate0.py` — tiny numerical instrument: one camera view leaves a hidden direction; internal prediction does not create evidence; a second baseline view increases observation rank.

## House rule

Keep three things separate:

1. **belief/content** — what the system currently predicts;
2. **observability/support** — which directions have actually been constrained by external measurements;
3. **internal queries / imagination** — useful operations on belief that are not new evidence.

A compelling internal world is allowed to be wrong. The bookkeeping must remain able to say *where* it is weakly anchored.
