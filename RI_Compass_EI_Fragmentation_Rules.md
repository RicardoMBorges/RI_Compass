# RI Compass --- EI Fragmentation Rules

## Technical Guide to the `hierarchical relational engine v4`

> **Purpose of this document:** to clearly and transparently explain how
> RI Compass converts a deconvoluted EI spectrum into chemical-class
> evidence. This document describes **the rules currently implemented in
> the software**. These are heuristic screening rules and **must not be
> interpreted as universal rules for structural identification**.

------------------------------------------------------------------------

# 1. What the `EI fragmentation engine` does

RI Compass does not attempt to automatically reconstruct a complete
molecular structure from an EI spectrum.

Its purpose is more focused:

> **to search for combinations of fragments, relationships among ions,
> and spectral context that are compatible with specific chemical
> classes.**

The engine therefore addresses questions such as:

``` text
Does the spectrum show an Alkane-like pattern?
Does the spectrum show a Styrenic-like pattern?
Is there evidence compatible with FAME chemistry?
Is there evidence compatible with a TMS derivative?
Is the fragmentation pattern consistent with terpenoid chemistry?
Is there evidence of siloxane background?
```

The output is a **structural/class signature**, not an unequivocal
compound identification.

------------------------------------------------------------------------

# 2. Fundamental principle

A single fragment is rarely sufficiently specific.

For example:

``` text
m/z 43
m/z 55
m/z 57
m/z 69
m/z 73
m/z 91
```

can occur in many different compounds.

RI Compass therefore does not rely on the simple logic:

``` text
m/z X present → class Y
```

Instead, the engine combines four levels of evidence:

``` text
1. Ion evidence
2. Relational evidence
3. Parent chemical gate
4. Hierarchical assignment
```

The complete workflow is:

``` text
Deconvoluted EI spectrum
        │
        ▼
Base-peak normalization
        │
        ▼
Diagnostic + supporting + conflicting ions
        │
        ▼
Ion score
        │
        ├───────────────┐
        ▼               ▼
Relational rules     Δ14 series
        │
        ▼
raw_score
        │
        ▼
Parent chemical gate
        │
   PASS ─┴─ FAIL
    │        │
    ▼        ▼
final score  0
    │
    ▼
Superclass → Class group → Leaf signature
```

------------------------------------------------------------------------

# 3. Spectral input

The engine uses the deconvoluted EI spectra supplied to RI Compass,
normally in MGF format.

Each spectrum is converted into a nominal-mass profile.

## 3.1 `Nominal-ion tolerance`

The current default is:

``` text
Nominal-ion tolerance = ±0.5 Da
```

For each integer mass, the program searches for a peak within this
window.

Example:

``` text
target = m/z 91

90.5 ≤ observed m/z ≤ 91.5
```

The most intense peak within the window represents that nominal ion.

------------------------------------------------------------------------

# 4. Intensity normalization

All intensities are normalized to the base peak:

``` text
relative intensity (%) =
100 × ion intensity / base-peak intensity
```

Therefore:

``` text
base peak = 100%
```

The fragmentation rules operate on **relative intensity**, not absolute
intensity.

------------------------------------------------------------------------

# 5. `Minimum relative ion intensity`

The parameter:

``` text
Minimum relative ion intensity (%)
```

defines the minimum intensity required for an ion to be considered
present.

The current default is:

``` text
5%
```

Thus, with the default setting:

``` text
I91 = 18% → present
I91 = 3%  → absent for rule evaluation
```

This parameter affects:

-   diagnostic ions;
-   supporting ions;
-   co-occurrence rules;
-   ratio rules;
-   parent-mass evidence;
-   neutral-loss evidence;
-   parent gates.

------------------------------------------------------------------------

# 6. Types of evidence used by the `leaf rules`

Each `class_signature` may use several components.

## 6.1 `Diagnostic ions`

These are the highest-weight ions within a rule.

Simplified example:

``` text
Alkane-like

m/z 57 → diagnostic
m/z 71 → diagnostic
```

Their presence contributes strongly to the `ion_score`.

## 6.2 `Supporting ions`

These fragments are compatible with the class but are less specific.

Example:

``` text
Alkane-like

m/z 43
m/z 85
m/z 99
m/z 113
```

They strengthen the evidence when they accompany the diagnostic ions.

## 6.3 `Conflicting ions`

Some rules contain ions whose strong presence reduces confidence in that
interpretation.

Example:

``` text
Alkane-like

conflicting:
m/z 91
m/z 104
```

These ions do not make the class impossible. They penalize the
`ion_score` when sufficiently intense.

Currently, a conflicting ion is penalized only when:

``` text
relative intensity ≥ max(20%, Minimum relative ion intensity)
```

## 6.4 `Ion series`

Some classes contain useful homologous series.

Example:

``` text
Alkane-like:
43 → 57 → 71 → 85 → 99 → 113

Δm = 14
```

and:

``` text
Alkene-like:
41 → 55 → 69 → 83 → 97 → 111

Δm = 14
```

When at least three members of a defined series are present, the engine
adds a `pattern_bonus`.

The bonus is capped at:

``` text
maximum = 0.20
```

------------------------------------------------------------------------

# 7. How the `ion_score` is calculated

For each diagnostic ion:

``` text
contribution =
weight × min(1, relative_intensity / 30)
```

For each supporting ion:

``` text
contribution =
weight × min(1, relative_intensity / 20)
```

Diagnostic ions therefore reach their maximum individual contribution at
approximately 30% relative intensity, whereas supporting ions saturate
at approximately 20%.

The basic component is:

``` text
positive evidence / maximum possible positive evidence
```

The engine then applies:

``` text
+ pattern_bonus
− 0.15 × conflict_penalty
```

The result is constrained to:

``` text
0 ≤ ion_score ≤ 1
```

------------------------------------------------------------------------

# 8. `Relational evidence`

The presence of individual ions alone is insufficient for many classes.

RI Compass therefore uses relational rules.

Four main types are currently implemented.

## 8.1 `Co-occurrence`

Requires several ions to occur simultaneously.

Example:

``` text
Alkane-like:
43 + 57 + 71
```

All ions must exceed the `Minimum relative ion intensity`.

## 8.2 `Ion ratios`

Compares relative intensities.

Examples:

``` text
Alkane-like:
I57 > 1.5 × I91
```

and:

``` text
Alkylbenzene-like:
I91 > I57
I91 > I77
```

## 8.3 `Parent-mass context`

Some rules search for an ion compatible with a plausible molecular mass.

Examples:

``` text
Monoterpene-hydrocarbon-like:
m/z 136
```

and:

``` text
Sesquiterpene-hydrocarbon-like:
m/z 204
```

This is only **supportive molecular-ion context**.

The program does not automatically assume that a high-mass peak is the
molecular ion.

## 8.4 `Neutral-loss context`

Some rules search for pairs of ions separated by a neutral loss.

Example:

``` text
M − 18
```

for dehydration-like fragmentation.

The engine searches for such a relationship only within the plausible
parent-mass range defined for the rule.

This remains contextual evidence rather than mechanistic proof.

------------------------------------------------------------------------

# 9. How the `relational_score` is calculated

Each relational rule has an assigned weight.

The engine sums:

``` text
points obtained
```

and divides by:

``` text
maximum possible relational points
```

to obtain:

``` text
0 ≤ relational_score ≤ 1
```

------------------------------------------------------------------------

# 10. How the `raw_score` is calculated

For a class with relational rules:

``` text
raw_score =
0.72 × ion_score
+
0.28 × relational_score
```

Thus:

``` text
72% → ion evidence
28% → relational evidence
```

Ion evidence remains the primary component. Relationships among ions
refine the interpretation.

For a class without relational rules:

``` text
raw_score = ion_score
```

Important:

> `raw_score` represents leaf-rule evidence **before** evaluation of the
> `parent gate`.

------------------------------------------------------------------------

# 11. Why `Parent chemical gates` are required

A major source of false-positive EI interpretation is the reuse of the
same ions by chemically different classes.

For example:

``` text
41 / 55 / 69
```

may occur in:

-   alkenes;
-   unsaturated FAMEs;
-   terpenes;
-   many other hydrocarbons.

Likewise:

``` text
73 / 147
```

may indicate:

-   TMS derivatives;
-   siloxane background.

The v4 engine therefore uses a two-stage classification:

``` text
Leaf evidence
      +
Parent chemistry evidence
      ↓
Final class evidence
```

A leaf receives a `final score` only if its `parent gate` passes.

The current default is:

``` text
Parent gate threshold = 0.45
```

------------------------------------------------------------------------

# 12. `Hydrocarbon gate`

The gate evaluates:

``` text
41
43
55
57
69
71
83
85
```

The engine calculates the fraction of these eight ions that are present.

If at least:

``` text
3 of 8
```

are present, the gate increases substantially.

Implemented as:

``` text
alkyl_fraction = number_present / 8
```

If:

``` text
alkyl_fraction ≥ 0.375
```

then:

``` text
Hydrocarbon gate =
min(1, 0.35 + 0.9 × alkyl_fraction)
```

otherwise:

``` text
Hydrocarbon gate =
0.25 × alkyl_fraction
```

This gate currently controls:

``` text
Alkane-like
Alkene-like
```

------------------------------------------------------------------------

# 13. `Aromatic gate`

The gate searches for:

``` text
65
77
91
103
104
105
```

The presence of `m/z 77` and `m/z 91` receives additional weight.

An additional bonus is applied when at least one of the following is
present:

``` text
128
152
178
202
228
```

providing context for aromatic molecular-ion regions / PAH-like
chemistry.

This gate controls:

``` text
Alkylbenzene-like
Styrenic-like
PAH-like
Phenolic-like
Phenylpropanoid-like
```

------------------------------------------------------------------------

# 14. `FAME gate`

The FAME gate is deliberately more restrictive.

Current scoring:

``` text
m/z 74 present      → +0.45
m/z 87 present      → +0.25
74 AND 87 present   → +0.20
101/115/129/143     → +0.10 if any is present
```

If strong TMS evidence is present:

``` text
m/z 73 ≥ 20%
AND
m/z 147 ≥ 15%
```

the FAME gate is penalized:

``` text
FAME gate × 0.55
```

This gate controls:

``` text
Saturated-FAME-like
Unsaturated-FAME-like
PUFA-FAME-like
```

This prevents generic unsaturation fragments from automatically
converting a hydrocarbon spectrum into a FAME assignment.

------------------------------------------------------------------------

# 15. `TMS derivative gate`

Current scoring:

``` text
m/z 73 present      → +0.45
m/z 147 present     → +0.35
73 AND 147 present  → +0.20
```

A pattern compatible with siloxane background penalizes the gate.

If any of the following is present at ≥10%:

``` text
m/z 207
m/z 281
m/z 355
```

then:

``` text
TMS gate × 0.55
```

This gate controls:

``` text
TMS-derivative-like
TMS-organic-acid-like
TMS-fatty-acid-like
TMS-amino-acid-like
TMS-sugar-polyol-like
```

------------------------------------------------------------------------

# 16. `Terpenoid gate`

The gate searches for a set of terpene-associated ions:

``` text
67
69
79
81
93
105
121
133
161
```

Each present ion adds evidence.

The basic component is:

``` text
min(0.65, number_present × 0.075)
```

Additional support is provided by:

``` text
m/z 136 → +0.25
m/z 204 → +0.30
```

and:

``` text
m/z 93
+
(m/z 121 OR m/z 161)
→ +0.15
```

This gate controls:

``` text
Monoterpene-hydrocarbon-like
Monoterpene-alcohol-like
Monoterpene-carbonyl-like
Sesquiterpene-hydrocarbon-like
Oxygenated-sesquiterpene-like
```

Its purpose is to avoid classifying generic unsaturated hydrocarbon
spectra as terpenes based only on a few common fragments.

------------------------------------------------------------------------

# 17. `Oxygenated gate`

The gate searches for:

``` text
29
31
43
44
58
60
71
95
```

Each present ion contributes:

``` text
0.25
```

up to a maximum of:

``` text
1.0
```

This gate currently controls:

``` text
Carbonyl-like
```

It is intentionally broad and should be interpreted as a screen for
oxygenated chemistry rather than a specific aldehyde or ketone
identification.

------------------------------------------------------------------------

# 18. `Background / QC gate`

The background gate detects two main situations.

## Siloxane context

``` text
73 + 147 + (207 OR 281)
```

provides strong `Background / QC` evidence.

## Phthalate context

``` text
m/z 149 ≥ 20%
```

produces:

``` text
Background gate = 0.75
```

Associated classes are:

``` text
Siloxane-background-like
Phthalate-like
```

In the current implementation, `Background / QC` is allowed
independently of the `Parent gate threshold` so that it can function as
a QC/background flag.

------------------------------------------------------------------------

# 19. How the `final score` is calculated

When:

``` text
gate_score ≥ Parent gate threshold
```

the leaf passes its parent gate.

The final score is:

``` text
final_score =
raw_score × (0.55 + 0.45 × gate_score)
```

Therefore, even a passing gate modulates the evidence.

Example:

``` text
raw_score = 0.90
gate_score = 0.60

final_score =
0.90 × (0.55 + 0.45 × 0.60)

final_score =
0.90 × 0.82

final_score = 0.738
```

A very strong raw signature therefore becomes:

``` text
probable
```

when support for the parent chemistry is only moderate.

If the gate fails:

``` text
final_score = 0
```

The `raw_score` is retained for inspection.

------------------------------------------------------------------------

# 20. Evidence categories

RI Compass currently uses:

    `final score` `evidence`
  --------------- ---------------
         `< 0.30` `weak / none`
      `0.30–0.59` `possible`
      `0.60–0.79` `probable`
         `≥ 0.80` `strong`

These are **heuristic screening categories**.

They are not statistical probabilities.

Thus:

``` text
score = 0.84
```

means:

``` text
strong rule-based class evidence
```

not:

``` text
84% probability of correct identification
```

------------------------------------------------------------------------

# 21. Implemented rules --- Hydrocarbons and aromatics

## `Alkane-like`

**Hierarchy**

``` text
Hydrocarbon
└── Aliphatic hydrocarbon
    └── Alkane-like
```

**Diagnostic ions**

``` text
57 (weight 4.0)
71 (weight 2.0)
```

**Supporting ions**

``` text
43  (1.0)
85  (1.0)
99  (0.7)
113 (0.5)
```

**Homologous series**

``` text
43 → 57 → 71 → 85 → 99 → 113
Δ14
```

**Conflicting ions**

``` text
91  (0.5)
104 (0.5)
```

**Relational evidence**

``` text
43 + 57 + 71
I57 > 1.5 × I91
```

**Interpretation**

Saturated aliphatic fragmentation with a coherent alkyl-ion series.

------------------------------------------------------------------------

## `Alkene-like`

**Hierarchy**

``` text
Hydrocarbon
└── Aliphatic hydrocarbon
    └── Alkene-like
```

**Diagnostic ions**

``` text
41 (3.0)
55 (3.0)
69 (2.0)
```

**Supporting ions**

``` text
83  (1.0)
97  (0.7)
111 (0.5)
```

**Series**

``` text
41 → 55 → 69 → 83 → 97 → 111
Δ14
```

**Conflicting ion**

``` text
91 (0.4)
```

**Relational evidence**

``` text
41 + 55 + 69
I55 > 0.8 × I57
```

**Interpretation**

Allylic/unsaturated fragmentation pattern.

------------------------------------------------------------------------

## `Alkylbenzene-like`

**Hierarchy**

``` text
Aromatic
└── Alkylbenzene
    └── Alkylbenzene-like
```

**Diagnostic ion**

``` text
91 (5.0)
```

**Supporting ions**

``` text
77  (2.0)
65  (1.0)
105 (1.0)
119 (0.8)
```

**Conflicting ions**

``` text
73  (0.8)
147 (0.8)
```

**Relational evidence**

``` text
77 + 91
I91 > I57
I91 > I77
```

**Interpretation**

Benzyl/tropylium-centered aromatic signature.

------------------------------------------------------------------------

## `Styrenic-like`

**Hierarchy**

``` text
Aromatic
└── Styrenic
    └── Styrenic-like
```

**Diagnostic ions**

``` text
104 (5.0)
77  (2.0)
```

**Supporting ions**

``` text
51  (1.2)
78  (1.5)
103 (0.7)
```

**Conflicting ions**

``` text
73  (0.8)
147 (0.8)
```

**Relational evidence**

``` text
77 + 104
51 + 77 + 104
I104 > 1.2 × I91
```

**Interpretation**

Styrenic/aromatic C8H8-like pattern.

> `Styrenic-like` is a class signature. It does not by itself identify
> styrene.

------------------------------------------------------------------------

## `Phenolic-like`

**Diagnostic ion**

``` text
94 (4.0)
```

**Supporting ions**

``` text
65  (1.5)
66  (0.8)
77  (1.0)
107 (1.0)
108 (1.0)
```

**Relational evidence**

``` text
65 + 94
```

**Interpretation**

Phenol/alkylphenol-like aromatic oxygenated signature.

------------------------------------------------------------------------

## `PAH-like`

**Diagnostic candidate masses**

``` text
128
152
178
202
228
```

each with weight `2.5`.

**Supporting ions**

``` text
77  (0.8)
89  (0.5)
101 (0.5)
```

**Interpretation**

Screen for stable aromatic molecular-ion patterns associated with
condensed aromatic chemistry.

> These masses are not unique to PAHs and do not identify a specific
> PAH.

------------------------------------------------------------------------

## `Carbonyl-like`

**Hierarchy**

``` text
Oxygenated
└── Carbonyl
    └── Carbonyl-like
```

**Diagnostic ions**

``` text
43 (2.0)
44 (2.0)
58 (2.0)
60 (2.5)
```

**Supporting ions**

``` text
29 (0.8)
31 (0.8)
71 (0.5)
```

**Interpretation**

Broad carbonyl/oxygenated screening rule. Additional evidence is
required for subclass assignment.

------------------------------------------------------------------------

# 22. Essential-oil / terpenoid rules

## `Monoterpene-hydrocarbon-like`

**Diagnostic ions**

``` text
93  (3.0)
136 (2.0)
```

**Supporting ions**

``` text
41, 53, 67, 69, 79, 81, 91, 105, 121
```

**Relational evidence**

``` text
69 + 93 + 121
m/z 136 as plausible C10H16 molecular-ion context
```

**Interpretation**

C10 terpene-hydrocarbon-like EI signature.

RI and library evidence remain essential for isomer discrimination.

------------------------------------------------------------------------

## `Monoterpene-alcohol-like`

**Diagnostic ions**

``` text
71 (1.5)
93 (2.0)
95 (2.0)
```

**Supporting ions**

``` text
41, 55, 67, 69, 81, 121
```

**Relational evidence**

``` text
69 + 93 + 95
M − 18 dehydration-like
plausible parent range = 136–172
```

**Interpretation**

Oxygenated monoterpene/alcohol-like screen.

The 18 Da neutral loss is contextual evidence only and does not
automatically establish loss of water from a confirmed molecular ion.

------------------------------------------------------------------------

## `Monoterpene-carbonyl-like`

**Diagnostic ions**

``` text
81  (2.0)
95  (2.0)
110 (1.2)
112 (1.2)
```

**Supporting ions**

``` text
41, 55, 69, 84, 94
```

**Relational evidence**

``` text
81 + 95
plausible parent range = 148–170
```

**Interpretation**

Broad monoterpene aldehyde/ketone-like screen.

------------------------------------------------------------------------

## `Phenylpropanoid-like`

**Diagnostic ions**

``` text
77  (1.8)
91  (1.5)
103 (1.2)
107 (1.2)
```

**Supporting ions**

``` text
105, 121, 131, 135, 149, 164
```

**Relational evidence**

``` text
77 + 103
77 + 107
```

**Interpretation**

Intentionally broad phenylpropanoid/benzenoid-like aromatic signature.

------------------------------------------------------------------------

## `Sesquiterpene-hydrocarbon-like`

**Diagnostic ions**

``` text
93  (2.0)
161 (2.0)
204 (1.8)
```

**Supporting ions**

``` text
41, 55, 67, 69, 79, 81, 91,
105, 119, 133, 147, 189
```

**Relational evidence**

``` text
93 + 161
m/z 204 as plausible C15H24 molecular-ion context
```

**Interpretation**

C15 terpene-hydrocarbon-like signature.

------------------------------------------------------------------------

## `Oxygenated-sesquiterpene-like`

**Diagnostic ions**

``` text
93  (1.5)
161 (1.5)
189 (1.2)
```

**Supporting ions**

``` text
41, 55, 69, 81, 105, 119, 133, 147
```

**Relational evidence**

``` text
M − 18 dehydration-like
plausible parent range = 204–240
```

**Interpretation**

Broad oxygenated C15-terpenoid-like screen intended for prioritization
rather than identification.

------------------------------------------------------------------------

# 23. FAME rules

## `Saturated-FAME-like`

**Diagnostic ions**

``` text
74 (4.0)
87 (2.5)
```

**Supporting ions**

``` text
43, 55, 57, 69, 75, 101, 143
```

**Relational evidence**

``` text
74 + 87
I74 > I73
```

The rule also records the expectation of a homologous parent step:

``` text
Δ14
```

**Interpretation**

Saturated fatty-acid methyl-ester-like signature.

`m/z 74` is used as classic McLafferty-type evidence.

------------------------------------------------------------------------

## `Unsaturated-FAME-like`

**Diagnostic ions**

``` text
55 (2.5)
69 (2.0)
74 (1.5)
```

**Supporting ions**

``` text
41, 67, 79, 81, 83, 87, 97
```

**Relational evidence**

``` text
55 + 69 + 74
I55 > I57
```

**Interpretation**

Unsaturated FAME-like fragmentation.

The rule does not resolve double-bond position or geometric isomerism.

------------------------------------------------------------------------

## `PUFA-FAME-like`

**Diagnostic ions**

``` text
67 (2.5)
79 (2.5)
81 (2.0)
```

**Supporting ions**

``` text
41, 55, 69, 91, 93, 95, 105
```

**Relational evidence**

``` text
67 + 79 + 81
I79 > 0.5 × I74
```

**Interpretation**

Polyunsaturated-FAME-like fragmentation.

Additional RI/library/molecular-ion evidence is required.

------------------------------------------------------------------------

# 24. TMS rules

## `TMS-derivative-like`

**Diagnostic ions**

``` text
73  (4.0)
147 (3.0)
```

**Supporting ions**

``` text
45, 75, 133, 149
```

**Relational evidence**

``` text
73 + 147
M − 15 methyl-loss-like
```

**Interpretation**

Generic trimethylsilyl-derivative signature.

> `73 + 147` may also occur in silicone/siloxane background. QC context
> is essential.

------------------------------------------------------------------------

## `TMS-organic-acid-like`

**Diagnostic ions**

``` text
73  (3.0)
147 (2.0)
```

**Supporting ions**

``` text
117, 133, 189, 191
```

**Relational evidence**

``` text
73 + 117 + 147
```

**Conflicting ions**

``` text
207
281
```

**Interpretation**

Broad TMS-derivatized organic-acid-like screen.

------------------------------------------------------------------------

## `TMS-fatty-acid-like`

**Diagnostic ions**

``` text
73  (2.5)
117 (3.0)
```

**Supporting ions**

``` text
75, 129, 145
```

**Relational evidence**

``` text
73 + 117
```

**Conflicting ions**

``` text
207
281
```

**Interpretation**

Fatty-acid TMS-ester-like screen.

It should be distinguished from FAME chemistry and silicone background.

------------------------------------------------------------------------

## `TMS-amino-acid-like`

**Diagnostic ions**

``` text
73  (2.5)
147 (1.8)
```

**Supporting ions**

``` text
100, 116, 174, 218, 246
```

**Relational evidence**

``` text
73 + 147 + 174
```

**Conflicting ions**

``` text
207
281
```

**Interpretation**

Broad TMS-amino-acid-like screen.

------------------------------------------------------------------------

## `TMS-sugar-polyol-like`

**Diagnostic ions**

``` text
73  (2.5)
147 (2.0)
204 (2.0)
217 (2.0)
```

**Supporting ions**

``` text
103, 129, 191, 319
```

**Relational evidence**

``` text
73 + 147 + 204 + 217
I204 > 0.5 × I207
```

**Conflicting ions**

``` text
207
281
```

**Interpretation**

Highly silylated carbohydrate/polyol-like signature.

Derivatization state may strongly alter the EI spectrum.

------------------------------------------------------------------------

# 25. Background / QC rules

## `Siloxane-background-like`

**Diagnostic ions**

``` text
73  (3.0)
147 (4.0)
```

**Supporting ions**

``` text
207 (2.5)
221 (1.0)
281 (2.5)
355 (1.0)
```

**Relational evidence**

``` text
73 + 147 + 207
OR
73 + 147 + 281

I147 > I117
```

**Interpretation**

Siloxane/background pattern.

It may indicate:

-   column bleed;
-   septum/silicone contamination;
-   analytical background;
-   derivatization-related silicone contamination.

It should be evaluated against blanks.

------------------------------------------------------------------------

## `Phthalate-like`

**Diagnostic ion**

``` text
149 (5.0)
```

**Supporting ions**

``` text
167
279
293
```

**Relational evidence**

``` text
149 + 167
```

**Interpretation**

Phthalate/plasticizer-like screening flag.

Confirmation should consider library match, RI, and blanks.

------------------------------------------------------------------------

# 26. Currently implemented hierarchy

``` text
Hydrocarbon
└── Aliphatic hydrocarbon
    ├── Alkane-like
    └── Alkene-like

Aromatic
├── Alkylbenzene
│   └── Alkylbenzene-like
├── Styrenic
│   └── Styrenic-like
├── PAH
│   └── PAH-like
└── Phenolic / phenylpropanoid
    ├── Phenolic-like
    └── Phenylpropanoid-like

Oxygenated
└── Carbonyl
    └── Carbonyl-like

FAME
└── Fatty-acid methyl ester
    ├── Saturated-FAME-like
    ├── Unsaturated-FAME-like
    └── PUFA-FAME-like

TMS derivative
├── Generic TMS derivative
│   └── TMS-derivative-like
└── TMS metabolite
    ├── TMS-organic-acid-like
    ├── TMS-fatty-acid-like
    ├── TMS-amino-acid-like
    └── TMS-sugar-polyol-like

Terpenoid
├── Monoterpene
│   ├── Monoterpene-hydrocarbon-like
│   ├── Monoterpene-alcohol-like
│   └── Monoterpene-carbonyl-like
└── Sesquiterpene
    ├── Sesquiterpene-hydrocarbon-like
    └── Oxygenated-sesquiterpene-like

Background / QC
├── Siloxane
│   └── Siloxane-background-like
└── Plasticizer
    └── Phthalate-like
```

------------------------------------------------------------------------

# 27. `Best leaf only`

A single feature may support more than one fragmentation signature.

Example:

``` text
Alkene-like                    0.88
Monoterpene-hydrocarbon-like   0.66
Unsaturated-FAME-like          0.31
```

RI Compass preserves all scores.

However, `Best leaf only` selects:

``` text
highest final score
```

to provide one conservative classification per feature.

In this example:

``` text
best_leaf_class = Alkene-like
best_leaf_score = 0.88
```

This is especially important in the Sunburst to avoid double counting.

------------------------------------------------------------------------

# 28. `All supported classes`

In:

``` text
All supported classes
```

all signatures that:

``` text
pass the parent gate
AND
score ≥ selected threshold
```

may be visualized.

This mode is useful for investigating:

-   ambiguous spectra;
-   overlapping fragmentation patterns;
-   class competition;
-   overly permissive rules;
-   features requiring manual review.

It should not be interpreted as quantitative chemical composition.

------------------------------------------------------------------------

# 29. How to interpret a complete result

Hypothetical example:

``` text
feature_id              48
superclass              Aromatic
class_group             Styrenic
class_signature         Styrenic-like

ion_score               0.94
relational_score        1.00
raw_score               0.957

gate_score              0.82
gate_pass               True

final score             0.879
evidence                strong
```

The correct interpretation is:

> The EI spectrum shows strong rule-based evidence compatible with a
> `Styrenic-like` fragmentation signature and also satisfies the
> `Aromatic parent gate`.

An **incorrect** interpretation would be:

> The compound was identified as styrene with 87.9% confidence.

For stronger compound annotation, additional evidence should still be
considered:

``` text
EI library match
+
Experimental RI
+
Reference RI
+
Blank behavior
+
Authentic standard, when required
```

------------------------------------------------------------------------

# 30. What fragmentation rules add to library search

The `EI library search` asks:

``` text
Which reference spectrum most closely resembles the experimental spectrum?
```

The `fragmentation engine` asks:

``` text
Which structural/class fragmentation patterns are supported by the experimental spectrum?
```

These are related but distinct questions.

Example:

``` text
Library candidate:
Compound X

EI cosine:
0.91

Experimental RI:
concordant

Fragmentation engine:
Aromatic → Styrenic-like
score = 0.87
```

This represents **convergent evidence**.

In contrast:

``` text
Library candidate:
FAME candidate

EI cosine:
0.84

RI:
plausible

FAME gate:
fail

FAME final score:
0
```

represents a:

``` text
structural/class conflict
```

and deserves review.

This is one of the most important uses of the fragmentation engine.

------------------------------------------------------------------------

# 31. What the fragmentation rules do NOT do

The current rules do not:

-   unequivocally identify a compound;
-   replace EI reference libraries;
-   replace experimental RI;
-   replace authentic standards;
-   determine a molecular formula;
-   necessarily distinguish positional isomers;
-   necessarily distinguish stereoisomers;
-   resolve coelution;
-   correct poor deconvolution;
-   convert feature counts into concentration;
-   provide identification probabilities;
-   prove fragmentation mechanisms;
-   guarantee that a high-mass peak is the molecular ion.

------------------------------------------------------------------------

# 32. Most important scientific limitation

These rules are **heuristics implemented in RI Compass**.

They were designed to capture chemically plausible patterns and reduce
interpretations based on isolated ions, but they still require
systematic benchmarking.

At this stage, the recommended terminology is:

``` text
rule-based EI structural-signature screening
```

or:

``` text
rule-based EI chemical-class screening
```

rather than:

``` text
automated EI compound identification
```

------------------------------------------------------------------------

# 33. How the rules should be validated

Each leaf class should be tested against:

``` text
Positive controls
+
Hard negative controls
+
Independent datasets
```

Example:

``` text
Alkane-like
    ↓
known alkanes
+
known alkenes
+
branched hydrocarbons
+
alkylbenzenes
+
terpenes
```

For `TMS derivative`:

``` text
true TMS metabolites
+
siloxane background
+
underivatized metabolites
```

For FAME:

``` text
saturated FAME
+
MUFA FAME
+
PUFA FAME
+
free fatty acids
+
hydrocarbons
+
TMS fatty-acid derivatives
```

------------------------------------------------------------------------

# 34. Recommended benchmarking metrics

For each class signature:

``` text
Sensitivity
Specificity
Precision
Recall
F1 score
False-positive rate
False-negative rate
```

Metrics of particular importance to RI Compass include:

``` text
Parent-gate rejection rate
Class overlap
Best-leaf accuracy
Confusion between related classes
Incremental value beyond EI library search
```

The central question is not only:

> Does the rule recognize its own class?

but also:

> **Does it reject chemically similar classes that share many of the
> same fragments?**

------------------------------------------------------------------------

# 35. Current default parameters

``` text
Minimum relative ion intensity = 5%
Nominal-ion tolerance          = ±0.5 Da
Parent gate threshold          = 0.45
```

For a conservative Sunburst summary:

``` text
Minimum final score = 0.60
Assignment          = Best leaf only
```

These values are operational defaults and should continue to be
evaluated during benchmarking.

------------------------------------------------------------------------

# 36. Important output fields

  -----------------------------------------------------------------------
  Field                               Meaning
  ----------------------------------- -----------------------------------
  `feature_id`                        Feature identifier

  `query_rt_min`                      Retention time

  `superclass`                        Parent chemical superclass

  `class_group`                       Intermediate hierarchy level

  `class_signature`                   Leaf rule evaluated

  `ion_score`                         Evidence from ion
                                      presence/intensity

  `relational_score`                  Evidence from relationships among
                                      ions

  `raw_score`                         Leaf evidence before the parent
                                      gate

  `gate_score`                        Evidence supporting parent
                                      chemistry

  `gate_pass`                         Whether the leaf can be promoted

  `score`                             Gate-adjusted final score

  `evidence`                          `weak / none`, `possible`,
                                      `probable`, `strong`

  `diagnostic_ions`                   Diagnostic ions detected

  `supporting_ions`                   Supporting ions detected

  `relational_evidence`               Satisfied
                                      co-occurrence/ratio/parent/loss
                                      rules

  `conflicting_ions`                  Conflicting ions detected

  `best_leaf_class`                   Highest final-score class for the
                                      feature

  `best_leaf_score`                   Score of that classification
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# 37. Interpretation principle

The RI Compass logic can be summarized as:

``` text
One ion is a clue.
A pattern is evidence.
A parent gate adds chemical context.
RI adds chromatographic evidence.
A library match adds reference-spectrum evidence.
Agreement strengthens an annotation.
Disagreement is information.
```

------------------------------------------------------------------------

# 38. Golden rule

> **`fragmentation score` is not `identification confidence`.**

The `EI fragmentation engine` should be used as an independent evidence
layer to:

-   prioritize;
-   inspect;
-   challenge;
-   organize;
-   contextualize annotations.

It was deliberately designed to **add evidence without hiding
uncertainty**.
