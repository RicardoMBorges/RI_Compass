# RI Compass --- Tutorial and Interpretation Guide

**Retention-index calibration, GC--EI spectral matching, hierarchical EI
chemical-class screening, Cytoscape export, and report-ready output**

RI Compass is a Streamlit application designed to combine several
complementary sources of evidence from GC--MS data without treating any
single source as definitive compound identification.

The workflow brings together:

1.  **Retention-index (RI) calibration and annotation**
2.  **GC--EI spectral-library matching**
3.  **Hierarchical rule-based EI chemical-class screening**
4.  **Experimental-feature spectral relationships**
5.  **Cytoscape-compatible network export**
6.  **Report- and manuscript-ready tables and text**

The central principle is simple:

> **Retention behavior, EI spectral similarity, and EI structural
> signatures are complementary evidence streams. They should reinforce
> one another, not be confused with one another.**

Accordingly, RI Compass uses conservative terminology. A high class
score is evidence for a **chemical-class or structural signature**, not
proof of a compound identity. Likewise, an RI match alone does not
identify a compound, and a library match should be interpreted in the
context of retention behavior, diagnostic fragments, library provenance,
and authentic standards whenever available.

------------------------------------------------------------------------

## 1. What problem does RI Compass solve?

Routine GC--MS interpretation often produces several disconnected
outputs:

-   a chromatographic feature table;
-   an n-alkane calibration run;
-   library-search candidates;
-   EI spectra;
-   retention-index references;
-   molecular-network information;
-   and finally a manually assembled report.

RI Compass organizes these data into a single evidence-centered
workflow.

Instead of asking only:

> "What compound does the library call this peak?"

the application encourages a more defensible sequence of questions:

> **Where does the feature elute?**\
> **What is its experimental retention index?**\
> **Which reference spectra resemble its EI spectrum?**\
> **Does the observed RI support or conflict with those candidates?**\
> **Which chemical-class signatures are independently supported by the
> EI fragmentation pattern?**\
> **How does the feature relate spectrally to other experimental
> features?**

This distinction is particularly important for complex samples such as
pyrolysis oils, essential oils, volatile extracts, derivatized
metabolomics samples, fatty-acid methyl esters, and other mixtures
containing homologous or highly isomeric compounds.

------------------------------------------------------------------------

# 2. Recommended workflow

A robust analysis normally follows this order:

**n-alkane calibration → feature RI calculation → RI candidate screening
→ EI library search → EI/RI integration → hierarchical EI class
screening → mirror-spectrum inspection → network export → report
generation**

The individual modules can be used independently, but the strongest
interpretation comes from combining orthogonal evidence.

------------------------------------------------------------------------

# 3. Input files

## 3.1 n-Alkane calibration CSV

Upload a CSV containing the known n-alkane series used under the same
chromatographic conditions as the samples.

At minimum, the file must provide:

-   **carbon number**
-   **retention time**

For example:

``` text
Carbon_Number,RT
8,312.4
9,421.8
10,531.6
11,640.9
...
```

Retention times may be supplied in the units expected by the interface.
Always verify the selected unit before running the analysis.

### Good practice

The calibration mixture and analytical samples should be acquired using
the **same chromatographic method**, including:

-   stationary phase;
-   column dimensions;
-   carrier-gas conditions;
-   oven program;
-   inlet conditions;
-   and preferably the same instrument configuration.

RI values calculated from chromatographically incompatible runs should
not be treated as directly comparable.

------------------------------------------------------------------------

## 3.2 Feature table CSV

Upload the GC--MS feature table containing at least a feature identifier
and retention time.

Tables exported from deconvolution workflows may additionally contain
sample peak areas. When present, these values can be propagated to
downstream tables and network attributes.

RI Compass distinguishes between:

-   **Study samples**
-   **n-Alkane standard mixture**

The latter option is useful when inspecting the feature table generated
from the alkane calibration injection itself.

------------------------------------------------------------------------

## 3.3 Deconvoluted EI spectra in MGF format

The **EI spectral search** and **EI substructure search** modules use
deconvoluted spectra supplied as MGF.

A typical spectrum contains a feature/scan identifier, retention-time
metadata, and an ion list.

Example:

``` text
BEGIN IONS
SCANS=125
RTINSECONDS=942.6
43 38.2
55 51.4
57 100.0
71 74.1
85 42.7
END IONS
```

The app reuses the same uploaded sample MGF for the hierarchical EI
classification.

### Important note about `PEPMASS`

RI Compass does **not** automatically interpret MGF `PEPMASS` as the EI
molecular ion.

In GC--EI data, particularly after deconvolution or conversion through
LC/MS-oriented formats, this field may not represent a chemically
meaningful molecular-ion assignment. Molecular-ion context must
therefore be interpreted conservatively.

------------------------------------------------------------------------

## 3.4 EI reference libraries

The spectral-search module accepts reference spectra in:

-   **MSP**
-   **MGF**

format.

Reference libraries may include general EI databases, specialized
libraries, in-house spectra, or application-specific collections.

Whenever possible, retain:

-   compound name;
-   library record identifier;
-   InChIKey;
-   reference RI;
-   stationary-phase information;
-   and provenance.

The quality of the reference library directly affects the usefulness of
the search.

------------------------------------------------------------------------

# 4. Retention-index calculation

## 4.1 Temperature-programmed GC

For temperature-programmed GC, RI Compass uses the linear
retention-index formulation commonly associated with the van den
Dool--Kratz approach:

\[ RI = 100`\left[n +
\frac{t_R(x)-t_R(n)}
{t_R(n+1)-t_R(n)}
\right]`{=tex}\]

where:

-   (t_R(x)) is the retention time of the analyte;
-   (t_R(n)) is the retention time of the preceding n-alkane;
-   (t_R(n+1)) is the retention time of the following n-alkane;
-   \(n\) is the carbon number of the preceding n-alkane.

For example, an analyte eluting halfway between n-decane and n-undecane
will have an RI close to 1050.

------------------------------------------------------------------------

## 4.2 Isothermal GC

For an isothermal experiment, RI Compass also provides the logarithmic
Kovats formulation using adjusted retention times:

\[ t'\_R=t_R-t_M \]

where (t_M) is the dead time.

Select this option **only** when the chromatographic experiment is
genuinely isothermal and the dead time is known.

------------------------------------------------------------------------

## 4.3 No uncontrolled extrapolation

Features outside the calibrated n-alkane range should not be assigned RI
values by uncontrolled extrapolation.

If the calibration covers C8--C30, for example, the most defensible RI
region is bounded by the retention times of those standards.

This is especially important for very volatile compounds and
high-boiling material.

------------------------------------------------------------------------

# 5. RI-based candidate screening

After RI calculation, the application can compare experimental indices
with reference RI values.

Candidate selection considers:

-   observed RI;
-   reference RI;
-   absolute (`\Delta `{=tex}RI);
-   stationary-phase compatibility;
-   selected RI database/source;
-   user-defined tolerance;
-   and feature detection filters.

The fundamental quantity is:

\[ `\Delta `{=tex}RI = RI\_{observed} - RI\_{reference} \]

A small (\|`\Delta `{=tex}RI\|) strengthens retention-based support, but
it does **not** establish identity.

Many structural isomers have similar retention indices, particularly
within homologous series or related terpene families.

### Recommended interpretation

Use RI as **orthogonal evidence**:

-   a good RI agreement supports a spectral candidate;
-   a large RI disagreement can flag a candidate for review;
-   RI alone normally provides a **candidate**, not a confirmed
    identification.

------------------------------------------------------------------------

# 6. GC--EI spectral-library search

Open the **EI spectral search** tab and upload:

1.  the sample deconvoluted MGF;
2.  one or more MSP/MGF reference libraries.

Then configure the search.

Typical defaults include:

  Parameter                  Typical default
  ------------------------ -----------------
  Minimum cosine                        0.65
  Candidates per feature                   5
  Minimum matched ions                     6
  RI agreement window            30 RI units
  Fragment range                 m/z 40--700

These are screening settings, not universal analytical thresholds.

------------------------------------------------------------------------

## 6.1 Spectral similarity

The current search uses:

-   nominal/unit-mass bins;
-   square-root intensity transformation;
-   cosine similarity.

Square-root transformation reduces the dominance of the base peak and
allows lower-intensity fragments to contribute more meaningfully to the
comparison.

The result table can include:

-   feature ID;
-   query RT;
-   candidate compound;
-   source library;
-   library record ID;
-   InChIKey;
-   cosine;
-   number of matched ions;
-   reference RI.

------------------------------------------------------------------------

## 6.2 Why cosine alone is insufficient

Two compounds may have similar EI spectra while differing structurally,
especially:

-   positional isomers;
-   terpene isomers;
-   homologous hydrocarbons;
-   alkylbenzenes;
-   closely related oxygenated compounds.

A high cosine should therefore be interpreted as **spectral
similarity**, not automatically as identification.

------------------------------------------------------------------------

# 7. Integrated EI + RI evidence

When both experimental RI and library RI are available, RI Compass
combines the two evidence streams.

The application distinguishes categories such as:

-   **EI + RI concordant**
-   **EI + RI tentative**
-   **EI similarity only**
-   **RI conflict / review**
-   **weak / review**
-   **RI-only candidate**
-   **unannotated**

The exact label should be read as a screening interpretation.

A strong spectral match with an RI conflict is intentionally flagged
rather than silently accepted.

The integrated screening rank gives more weight to EI similarity while
using RI proximity as independent supporting evidence. It is a **ranking
aid**, not an identification probability.

------------------------------------------------------------------------

# 8. Hierarchical EI structural-signature search

The **EI substructure search** tab provides a different type of
information from the library search.

It asks:

> **What type of chemical fragmentation pattern is supported by this
> spectrum?**

rather than:

> **Which named library compound is most similar?**

This distinction is crucial.

The engine uses interpretable rules based on combinations of:

-   diagnostic ions;
-   supporting ions;
-   relative ion intensities;
-   homologous fragmentation patterns;
-   relational evidence;
-   conflicting ions;
-   parent chemical-class gates;
-   and selected molecular-ion context where defensible.

------------------------------------------------------------------------

# 9. Why the engine is hierarchical

Many EI fragments are chemically informative but **not unique**.

For example:

-   m/z 43 occurs in numerous aliphatic and oxygenated compounds;
-   m/z 57 is common in saturated hydrocarbon fragmentation;
-   m/z 69 and 83 occur in many unsaturated structures;
-   m/z 91 is characteristic of benzyl/tropylium chemistry but does not
    uniquely identify an alkylbenzene;
-   m/z 73 may indicate trimethylsilyl chemistry but is also common in
    siloxane contamination.

A flat rule system can therefore overclassify spectra.

RI Compass uses a two-stage hierarchy:

``` text
Broad parent chemistry
        ↓
Parent gate
        ↓
Subclass / leaf signature
        ↓
Gate-adjusted final score
```

A subclass is promoted only when its parent chemistry is sufficiently
supported.

Examples include:

``` text
Terpenoid-like
├── Monoterpene-like
│   ├── Monoterpene hydrocarbon-like
│   └── Oxygenated monoterpene-like
└── Sesquiterpene-like
    ├── Sesquiterpene hydrocarbon-like
    └── Oxygenated sesquiterpene-like
```

and conceptually:

``` text
FAME-like
├── Saturated FAME-like
├── Unsaturated FAME-like
└── PUFA-like
```

This architecture reduces false subclass assignments driven by generic
fragments.

------------------------------------------------------------------------

# 10. Parent chemical gates

The hierarchical engine evaluates broad evidence for parent chemical
domains such as:

-   **Hydrocarbon**
-   **Aromatic**
-   **FAME**
-   **TMS derivative**
-   **Terpenoid**
-   **Oxygenated**
-   **Background / QC**

Only after a parent gate passes can its dependent leaf rules receive a
meaningful final score.

This is especially useful for chemically ambiguous signatures.

### Example: TMS chemistry

m/z 73 alone should not automatically produce a TMS-metabolite
assignment.

A convincing TMS classification requires a broader TMS fragmentation
context, while a siloxane-like ion series can act as evidence for
background contamination instead.

### Example: FAME chemistry

Generic hydrocarbon fragments are not enough to classify a feature as a
fatty-acid methyl ester.

The FAME parent gate must first support ester/FAME chemistry before
saturated, unsaturated, or polyunsaturated subclasses are promoted.

### Example: terpenoids

Terpene-like fragments are highly overlapping among isomers.

The engine therefore evaluates terpene-core evidence before assigning
more specific monoterpene- or sesquiterpene-like signatures.

------------------------------------------------------------------------

# 11. Understanding the EI class score

The engine reports both raw and hierarchical evidence.

Important columns include:

-   `raw_score`
-   `gate_score`
-   `gate_pass`
-   `score`
-   `ion_score`
-   `relational_score`
-   `diagnostic_ions`
-   `supporting_ions`
-   `relational_evidence`
-   `conflicting_ions`
-   `best_superclass`
-   `best_class_group`
-   `best_leaf_class`
-   `best_leaf_score`

The final score is a **rule-based screening score between 0 and 1**.

It is **not a posterior probability**, identification probability, or
percentage confidence.

### Suggested interpretation

    Final score Interpretation
  ------------- -------------------------------
       `< 0.30` weak / no meaningful evidence
    `0.30–0.59` possible signature
    `0.60–0.79` probable class signature
       `≥ 0.80` strong class signature

For routine composition summaries, **0.60 is the recommended default
threshold**.

This means that the summary focuses on **probable + strong** class
signatures.

------------------------------------------------------------------------

# 12. `raw_score` versus final `score`

This distinction is important.

A spectrum may contain fragments that resemble a subclass and therefore
produce a meaningful `raw_score`.

However, if the required parent chemistry is not sufficiently supported,
`gate_pass` will be false and the final `score` will be suppressed.

This prevents a few generic fragments from being interpreted as a
chemically specific assignment.

Therefore:

> **Use `score` for the main interpretation. Use `raw_score` to
> investigate why a spectrum partially resembled a rule.**

------------------------------------------------------------------------

# 13. Best leaf assignment

A single EI spectrum can legitimately support overlapping signatures.

For exploratory analysis, RI Compass can retain these overlaps.

For composition-style summaries, however, counting every supported class
would count the same feature multiple times.

The application therefore provides:

-   **Best leaf only**
-   **All supported classes**

## Recommended default: `Best leaf only`

`Best leaf only` assigns each feature once, using its highest-ranking
gated leaf class.

This is the recommended mode for:

-   Sunburst summaries;
-   sample-level composition views;
-   figures;
-   comparative reporting.

`All supported classes` is better suited to mechanistic inspection of
overlapping fragmentation signatures.

------------------------------------------------------------------------

# 14. Interactive chemical-class Sunburst

The Sunburst summarizes the hierarchy:

``` text
Superclass → class group → leaf class
```

The recommended default settings are:

``` text
Minimum final score = 0.60
Assignment = Best leaf only
```

This produces a conservative visualization in which each accepted
feature contributes once.

The hover information includes:

-   number of features;
-   median score;
-   mean score.

The interactive plot can be exported as HTML, and its underlying data
can be downloaded as CSV.

### Critical interpretation note

The number of classified features is **not automatically a quantitative
chemical composition**.

Unless an abundance-aware model with appropriate response correction is
used, the Sunburst primarily describes the **distribution of classified
features**, not weight percent, molar percent, or absolute
concentration.

------------------------------------------------------------------------

# 15. Essential oils and terpene-rich samples

The hierarchical architecture is particularly useful for essential oils
because EI spectra of terpenes are often highly similar.

Typical fragmentation regions include ions around:

-   m/z 41
-   53
-   67
-   69
-   79
-   81
-   91
-   93
-   105
-   119
-   121
-   133
-   136
-   147
-   161
-   189
-   204

These ions should **not** be treated as unique compound markers.

Instead, RI Compass uses combinations of fragments and hierarchical
chemical context to support broader terpene classes.

For essential oils, the strongest workflow is therefore:

``` text
EI spectrum
   +
experimental RI
   +
reference RI
   +
library similarity
   +
hierarchical terpene signature
```

This is much more defensible than assigning compounds from one
diagnostic ion or library rank alone.

Authentic standards remain the preferred route when definitive isomer
discrimination is required.

------------------------------------------------------------------------

# 16. Pyrolysis oils and hydrocarbon-rich samples

Pyrolysis oils frequently contain homologous hydrocarbon series and
aromatic products.

Useful EI patterns may include:

### Saturated aliphatic pattern

``` text
43 → 57 → 71 → 85 → 99 → 113
```

The approximately 14 Da progression is consistent with repeated CH₂
units.

### Unsaturated / allylic pattern

``` text
41 → 55 → 69 → 83 → 97
```

### Aromatic / alkylbenzene context

Common supporting ions can include:

``` text
77, 91, 105, 119
```

m/z 91 is often associated with benzyl/tropylium fragmentation but
should never be treated as a unique alkylbenzene identifier.

### Styrenic context

A combination involving ions such as:

``` text
51, 77, 78, 104
```

may support styrenic chemistry, but a nominal m/z 104 molecular region
alone cannot distinguish all C8H8 isomers.

RI and reference-spectrum agreement are particularly important here.

------------------------------------------------------------------------

# 17. Mirror-spectrum inspection

Automated ranking should be followed by visual inspection for important
features.

The **Mirror spectra** module allows comparison between:

-   the experimental EI spectrum;
-   the candidate reference spectrum.

Inspect:

-   base-peak agreement;
-   diagnostic fragments;
-   missing high-intensity ions;
-   unexpected ions;
-   relative-intensity patterns;
-   molecular-ion region;
-   and possible coelution/deconvolution artifacts.

A high numerical cosine can conceal chemically meaningful disagreements.

Mirror plots are therefore an important expert-review step.

------------------------------------------------------------------------

# 18. Cytoscape network export

RI Compass can export a GraphML network for Cytoscape.

The network is designed to preserve evidence rather than only displaying
a single annotation.

Typical node types include:

### `feature`

An experimental GC--MS feature.

Feature nodes may carry:

-   feature ID;
-   retention time;
-   experimental RI;
-   peak-area information;
-   top EI candidate;
-   cosine;
-   matched-ion count;
-   RI agreement;
-   evidence level;
-   and optionally spectral peak lists.

### `reference`

A reference-library compound connected to one or more experimental
features through EI library matches.

------------------------------------------------------------------------

## 18.1 Library-match edges

`EI_library_match` edges represent candidate relationships between an
experimental feature and a library record.

Alternative ranked candidates can remain in the network even when only
the best proposal is displayed as the feature label.

This prevents the graph from hiding annotation ambiguity.

------------------------------------------------------------------------

## 18.2 Feature--feature similarity edges

Optional `EI_feature_similarity` edges connect experimental features
based on EI spectral cosine.

These edges mean:

> **the EI spectra are similar**

They do **not** mean:

> **the two nodes are the same compound**

This distinction is especially important for homologues and structural
isomers.

The user can configure:

-   minimum feature--feature cosine;
-   minimum shared ions;
-   maximum EI neighbors per feature.

------------------------------------------------------------------------

# 19. Suggested Cytoscape interpretation

A useful Cytoscape style can map:

-   **node shape** → node type;
-   **node label** → feature ID / putative candidate;
-   **node size** → abundance or another selected experimental quantity;
-   **border width** → annotation/evidence strength;
-   **edge type** → library match versus feature similarity;
-   **edge width** → cosine or integrated screening score.

Avoid using visual styling that implies confirmed identification when
the evidence is only putative.

------------------------------------------------------------------------

# 20. Report & manuscript output

The **Report & manuscript** tab assembles selected analytical results
into a publication-oriented table and explanatory text.

The report can integrate:

-   feature ID;
-   RT;
-   experimental RI;
-   proposed compound;
-   reference RI;
-   ΔRI;
-   EI cosine;
-   matched ions;
-   evidence level;
-   screening score;
-   and sample peak areas where available.

The app also prepares editable sections for:

-   **Methods**
-   **Results and interpretation**
-   **Table legend**

These outputs should be reviewed and adapted to the actual experiment
before publication.

------------------------------------------------------------------------

# 21. Identification language

RI Compass deliberately uses conservative terminology.

Recommended language includes:

-   **putative annotation**
-   **candidate**
-   **spectral match**
-   **RI-supported candidate**
-   **class signature**
-   **consistent with**
-   **supports**
-   **requires review**

Avoid automatically converting computational output into terms such as:

-   "confirmed compound"
-   "identified with 95% confidence"
-   "80% probability"
-   "definitively detected"

unless the experimental design independently supports that level of
identification.

------------------------------------------------------------------------

# 22. A practical interpretation example

Suppose an experimental feature gives:

``` text
RT                 25.24 min
Experimental RI    1124
Top library hit    Candidate X
EI cosine           0.91
Matched ions        14
Reference RI        1120
ΔRI                 +4
Best EI class       Aromatic / styrenic-like
Class score         0.84
```

A defensible interpretation is:

> The feature shows strong EI spectral similarity to Candidate X, with
> concordant retention-index behavior and a strong aromatic/styrenic EI
> structural signature. The evidence supports Candidate X as a
> high-priority putative annotation, subject to review of the reference
> spectrum and, where required, confirmation with an authentic standard.

A less defensible statement would be:

> Candidate X was definitively identified with 84% confidence.

The class score does not represent identification probability.

------------------------------------------------------------------------

# 23. Troubleshooting

## No RI is calculated for some features

Check whether the feature retention time lies outside the n-alkane
calibration range.

Also verify:

-   RT units;
-   alkane ordering;
-   missing standards;
-   duplicated carbon numbers;
-   and chromatographic compatibility.

------------------------------------------------------------------------

## Too many RI candidates

Reduce the RI tolerance or restrict the reference
sources/stationary-phase policy.

Remember that RI is a candidate filter, not necessarily a unique
identifier.

------------------------------------------------------------------------

## No EI library hits

Consider whether:

-   the cosine threshold is too high;
-   the minimum matched-ion count is too restrictive;
-   the reference library covers the relevant chemistry;
-   the MGF spectra contain enough ions;
-   the acquisition mass range matches the library;
-   deconvolution quality is adequate.

------------------------------------------------------------------------

## Too many EI library hits

Increase:

-   minimum cosine;
-   minimum matched ions;

and rely more strongly on:

-   RI agreement;
-   diagnostic-ion review;
-   mirror spectra;
-   library provenance.

------------------------------------------------------------------------

## A class has a high `raw_score` but final `score = 0`

The leaf rule found partial spectral evidence, but the required parent
gate did not pass.

This is intentional and is one of the safeguards of the hierarchical
engine.

------------------------------------------------------------------------

## Terpenes appear in several classes

This is expected because EI fragmentation of terpene isomers is highly
overlapping.

Use:

-   `Best leaf only` for a conservative summary;
-   `All supported classes` to investigate overlapping evidence;
-   RI + spectral-library evidence for compound-level interpretation.

------------------------------------------------------------------------

## TMS-like signals dominate

Inspect whether the spectrum represents a derivatized metabolite or
siloxane background.

Common GC--MS background ions can strongly resemble
derivatization-related fragments if interpreted without a chemical gate.

------------------------------------------------------------------------

# 24. Recommended defaults

For a general first-pass analysis:

``` text
RI:
  Use temperature-programmed linear RI when appropriate
  Avoid extrapolation outside the alkane range
  RI agreement window: ~30 units as an initial screen

EI library search:
  Minimum cosine: 0.65
  Minimum matched ions: 6
  Candidates per feature: 5
  Fragment range: adapt to the acquisition method

Hierarchical EI classification:
  Minimum relative ion intensity: 5%
  Parent gate threshold: 0.45
  Main interpretation threshold: 0.60

Sunburst:
  Minimum final score: 0.60
  Assignment: Best leaf only
```

These values are starting points and should be validated for the
analytical platform and sample type.

------------------------------------------------------------------------

# 25. What RI Compass does not do

RI Compass does not replace:

-   expert EI interpretation;
-   authentic-standard confirmation;
-   chromatographic method validation;
-   quantitative calibration;
-   manual review of deconvolution;
-   or critical evaluation of reference-library quality.

It also does not assume that:

-   the largest library score is automatically correct;
-   PEPMASS is the EI molecular ion;
-   one diagnostic fragment uniquely defines a structure;
-   one RI value uniquely identifies a compound;
-   feature counts equal chemical concentration.

The application is best understood as an **evidence-integration and
prioritization environment**.

------------------------------------------------------------------------

# 26. Reproducibility recommendations

For reproducible analyses, record:

-   RI Compass version/commit;
-   GC column and stationary phase;
-   column dimensions;
-   oven program;
-   carrier-gas conditions;
-   alkane calibration range;
-   RI equation used;
-   RI tolerance;
-   EI ionization energy;
-   scan range;
-   deconvolution software and settings;
-   spectral libraries and versions;
-   cosine threshold;
-   minimum matched ions;
-   class-engine thresholds;
-   selected rule domains;
-   and any manual exclusions.

Export the result tables rather than relying only on screenshots.

------------------------------------------------------------------------

# 27. Suggested Methods wording

The following text can be adapted for manuscripts:

> Retention indices were calculated from an n-alkane calibration series
> acquired under chromatographic conditions compatible with the study
> samples. For temperature-programmed analyses, linear retention indices
> were calculated by interpolation between the bracketing n-alkanes.
> Deconvoluted electron-ionization spectra were compared with reference
> EI libraries using nominal-mass binning, square-root intensity
> transformation, and cosine similarity. Spectral candidates were
> evaluated together with experimental-to-reference retention-index
> agreement. In parallel, EI spectra were screened using a hierarchical
> rule-based chemical-class engine based on diagnostic and supporting
> ions, relational fragmentation evidence, conflicting ions, and
> parent-class chemical gates. Rule-based class scores were treated as
> structural-signature evidence rather than compound-identification
> probabilities. Compound-level assignments were considered putative
> unless supported by the appropriate level of orthogonal evidence
> and/or authentic standards.

------------------------------------------------------------------------

# 28. Suggested Results wording

> GC--MS features were evaluated using complementary retention and EI
> spectral evidence. Experimental retention indices were used to assess
> chromatographic consistency with reference candidates, while EI
> library matching provided spectrum-level similarity. The hierarchical
> EI engine independently summarized fragmentation evidence at the
> chemical-class level. For class-composition visualization, only the
> best gated leaf assignment per feature with a final score ≥0.60 was
> retained, thereby preventing multiple counting of features with
> overlapping EI signatures. These class assignments should be
> interpreted as fragmentation-based chemical signatures and not as
> quantitative concentrations or definitive compound identifications.

------------------------------------------------------------------------

# 29. Citation and software reporting

When using RI Compass in scientific work, report:

-   the software version or Git commit;
-   the date of analysis;
-   the reference libraries used;
-   the retention-index source/database;
-   the chromatographic stationary phase;
-   and all relevant screening thresholds.

If the repository has a DOI, software paper, or archived release, cite
that persistent record in addition to the GitHub repository.

------------------------------------------------------------------------

# 30. Final interpretation philosophy

The most important principle in RI Compass is that **different
analytical clues answer different questions**.

  -----------------------------------------------------------------------
  Evidence                            Main question
  ----------------------------------- -----------------------------------
  Retention index                     Does the chromatographic behavior
                                      fit?

  EI library cosine                   Does the spectrum resemble a
                                      reference spectrum?

  Diagnostic fragments                Which fragmentation motifs are
                                      present?

  Hierarchical class score            Which chemical-class signature is
                                      supported?

  Feature--feature cosine             Which experimental spectra resemble
                                      one another?

  Authentic standard                  Does an experimentally controlled
                                      reference support identity?
  -----------------------------------------------------------------------

No single row of this table should silently replace the others.

The strongest annotation is obtained when independent evidence
converges.

> **Use RI Compass to prioritize, inspect, integrate, and document
> evidence --- not to hide uncertainty.**
