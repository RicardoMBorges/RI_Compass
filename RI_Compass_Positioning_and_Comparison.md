# RI Compass in the GC-MS Software Landscape

## Scope, overlap with existing tools, limitations, and intended contribution

> **Short version:** RI Compass is **not** intended to replace GC-MS
> preprocessing, peak detection, spectral deconvolution, or alignment
> software. It is a post-processing interpretation environment for
> already processed GC-EI data. Its purpose is to bring together
> experimental retention-index evidence, EI spectral-library evidence,
> interpretable rule-based EI fragmentation evidence, and chemical-space
> visualization in a transparent workflow.

------------------------------------------------------------------------

## 1. Why this positioning matters

GC-MS software is a mature field. Several established programs already
perform one or more of the following tasks:

-   raw-data import;
-   peak detection;
-   chromatographic feature resolving;
-   EI spectral deconvolution;
-   feature alignment;
-   retention-index calculation;
-   spectral-library searching;
-   retention-index filtering;
-   molecular networking;
-   statistical analysis;
-   and compound annotation.

For that reason, RI Compass should **not** be described as a new
general-purpose GC-MS processing platform.

Its intended role begins **after the chromatographic data have been
processed**.

A typical input to RI Compass is therefore:

``` text
Processed GC–MS feature table
        +
Deconvoluted EI spectra
        +
n-Alkane calibration
        +
Optional EI reference libraries
```

These inputs may come from MZmine, MS-DIAL, AMDIS, vendor software, or
another suitable preprocessing workflow.

The central question addressed by RI Compass is not:

> How do I detect and deconvolute chromatographic peaks?

Instead, it is:

> **Given a processed GC--EI dataset, how can retention behavior and EI
> fragmentation evidence be interrogated together to strengthen,
> challenge, organize, and communicate chemical annotations?**

------------------------------------------------------------------------

# 2. Intended analytical position of RI Compass

The conceptual workflow is:

``` text
RAW GC–MS
    │
    ▼
┌───────────────────────────────────────┐
│ Upstream processing                   │
│                                       │
│ MZmine / MS-DIAL / AMDIS / vendor SW │
│                                       │
│ Peak detection                        │
│ Deconvolution                         │
│ Alignment                             │
│ Quantification                        │
└───────────────────────────────────────┘
    │
    ├── Feature table
    └── Deconvoluted EI spectra
                │
                ▼
┌───────────────────────────────────────────────┐
│ RI COMPASS                                    │
│                                               │
│ Experimental RI / Kovats evidence             │
│                    +                          │
│ RI candidate evaluation                       │
│                    +                          │
│ EI spectral-library evidence                  │
│                    +                          │
│ Rule-based EI fragmentation evidence          │
│                    ↓                          │
│ Evidence integration / concordance            │
│                 ↙         ↘                   │
│      Spectral network     Hierarchical        │
│                           Sunburst            │
│                    ↓                          │
│             Report-ready output               │
└───────────────────────────────────────────────┘
```

This distinction is important because RI Compass is designed as a
**downstream interpretation layer**, not as a competing raw-data
processing engine.

------------------------------------------------------------------------

# 3. What RI Compass currently does

RI Compass focuses on five related tasks.

## 3.1 Experimental retention-index calculation

The application uses an experimental n-alkane series to calculate
retention indices for processed GC-MS features.

Depending on the chromatographic mode, this includes:

-   temperature-programmed linear retention indices;
-   isothermal Kovats-type calculations when appropriate;
-   interpolation within the experimentally calibrated alkane range;
-   and comparison with reference RI values.

The retention index is treated as an independent chromatographic line of
evidence.

RI agreement supports a candidate.

RI disagreement can challenge a candidate.

RI alone is not treated as proof of identity.

------------------------------------------------------------------------

## 3.2 EI spectral-library comparison

Deconvoluted EI spectra can be compared with reference EI libraries.

The resulting evidence includes, for example:

-   spectral cosine;
-   number of matched ions;
-   library provenance;
-   reference RI where available;
-   and candidate ranking.

Again, spectral similarity is not automatically interpreted as
identification.

A high library score means that the experimental spectrum resembles a
reference spectrum. Structural isomers, homologues, coelution,
deconvolution artifacts, and incomplete libraries remain relevant
limitations.

------------------------------------------------------------------------

## 3.3 Rule-based EI fragmentation interpretation

This is the part of RI Compass that is conceptually most distinct from
conventional library searching.

Instead of asking only:

> Which reference spectrum is most similar?

the EI structural-signature engine also asks:

> **Which chemically interpretable fragmentation patterns are
> independently supported by the experimental EI spectrum?**

The engine evaluates combinations of:

-   diagnostic ions;
-   supporting ions;
-   ion-intensity relationships;
-   homologous fragmentation patterns;
-   conflicting ions;
-   relational fragmentation evidence;
-   selected neutral-loss or molecular-ion context when defensible;
-   and broad parent-chemistry gates.

Examples of broad chemical domains include:

``` text
Hydrocarbon
Aromatic
FAME
TMS derivative
Terpenoid
Oxygenated
Background / QC
```

Possible downstream signatures include patterns such as:

``` text
Hydrocarbon
└── Aliphatic hydrocarbon
    ├── Alkane-like
    └── Alkene-like

Aromatic
├── Alkylbenzene-like
├── Styrenic-like
├── PAH-like
└── Phenolic / phenylpropanoid-like

FAME
├── Saturated-FAME-like
├── Unsaturated-FAME-like
└── PUFA-FAME-like

Terpenoid
├── Monoterpene-like
└── Sesquiterpene-like
```

The purpose is **not** to predict a unique molecular structure from EI
fragments.

The purpose is to generate an interpretable and auditable
structural/class-level evidence layer that is partly independent of the
library hit.

------------------------------------------------------------------------

## 3.4 Evidence integration

The central analytical idea is that different evidence streams answer
different questions.

  -----------------------------------------------------------------------
  Evidence                            Main question
  ----------------------------------- -----------------------------------
  Experimental RI                     Is the chromatographic behavior
                                      compatible?

  EI library similarity               Does the experimental spectrum
                                      resemble a reference spectrum?

  Diagnostic EI fragments             Which fragmentation motifs are
                                      present?

  Hierarchical EI class score         Which chemical-class signature is
                                      supported?

  Feature--feature EI similarity      Which experimental spectra resemble
                                      one another?

  Authentic standard                  Does an experimentally controlled
                                      reference support identity?
  -----------------------------------------------------------------------

These evidence streams should not be collapsed blindly into a single
probability.

A useful example is:

``` text
Library candidate: Styrene
EI similarity: strong
Experimental RI: concordant
EI parent class: Aromatic
EI leaf signature: Styrenic-like
Parent gate: pass
```

Here, multiple lines of evidence converge.

But RI Compass is equally interested in disagreement:

``` text
Library candidate: Fatty-acid methyl ester
EI library similarity: moderate
Experimental RI: plausible
FAME parent gate: fail
```

This is not a failed analysis.

It is useful information:

``` text
Structural evidence conflict → review candidate
```

The ability to expose agreement **and disagreement** is central to the
intended workflow.

------------------------------------------------------------------------

# 4. Network and Sunburst are outputs of interpretation, not identification engines

RI Compass also creates two complementary representations of the
interpreted dataset.

## 4.1 Evidence-enriched spectral network

The network represents relationships among experimental EI features and,
where applicable, reference-library candidates.

Experimental feature nodes can carry attributes such as:

``` text
Feature ID
Retention time
Experimental RI
Top library candidate
EI cosine
Matched ions
Reference RI
ΔRI
Evidence category
Superclass
Class group
Best leaf class
Class score
Sample abundance
```

Feature--feature edges represent EI spectral similarity.

They do **not** imply that two nodes are the same compound.

The network therefore answers a relational question:

> **Which experimental EI spectra are related, and what annotation
> evidence is associated with each feature?**

------------------------------------------------------------------------

## 4.2 Hierarchical chemical-class Sunburst

The Sunburst answers a different question:

> **What fragmentation-supported chemical-class space is represented in
> the processed dataset?**

The hierarchy can be represented as:

``` text
Superclass
    ↓
Class group
    ↓
Leaf class
```

For conservative summaries, the recommended mode is:

``` text
Minimum final score = 0.60
Assignment = Best leaf only
```

This prevents a feature with overlapping EI signatures from being
counted repeatedly in the main composition-style visualization.

Importantly, feature counts in the Sunburst are **not equivalent to
chemical concentration, weight percentage, or molar composition**.

------------------------------------------------------------------------

# 5. Comparison with existing GC-MS software

The comparison below is intentionally conservative.

RI Compass overlaps with existing software in several areas. Those
overlaps should be acknowledged rather than presented as novelty.

------------------------------------------------------------------------

## 5.1 MZmine

MZmine is currently one of the strongest comparisons because it provides
a modern GC--EI workflow that includes:

-   raw-data import;
-   mass detection;
-   feature resolving;
-   GC--EI spectral deconvolution;
-   alignment using retention time and spectral similarity;
-   spectral-library searching;
-   retention-index filtering;
-   annotation-quality summaries;
-   statistics;
-   spectral/molecular networking;
-   network visualization;
-   and GraphML export.

MZmine can treat GC--EI pseudo-spectra as MS1 spectra for library
searching and provides GC-oriented spectral-similarity approaches such
as composite cosine identity.

It also supports retention-index tolerance during spectral-library
search.

### Where RI Compass overlaps with MZmine

``` text
Retention-index use
EI library search
Spectral similarity
Feature–feature relationships
Molecular/spectral networking
GraphML export
Annotation evidence
```

These capabilities are therefore **not, by themselves, unique
contributions of RI Compass**.

### Where the intended emphasis differs

MZmine is a broad mass-spectrometry data-processing and analysis
platform.

RI Compass deliberately begins downstream:

``` text
MZmine
    ↓
processed feature table + deconvoluted EI spectra
    ↓
RI Compass
```

The intended distinction is the explicit use of a **human-readable,
hierarchical, rule-based EI structural-signature layer** alongside RI
and library evidence, followed by downstream evidence-oriented
visualization.

This should be regarded as a difference in analytical emphasis and
architecture, not as evidence that MZmine lacks sophisticated annotation
capabilities.

In fact, MZmine has an Annotation Quality Summary that integrates
multiple annotation dimensions, including spectral matching and
RI-related information. Any claim that RI Compass is the first software
to combine multiple annotation criteria would therefore be
inappropriate.

------------------------------------------------------------------------

# 6. AMDIS and the NIST ecosystem

AMDIS is a foundational GC-MS tool and an important comparison.

AMDIS performs:

-   component detection;
-   mass-spectral deconvolution;
-   comparison against target/reference libraries;
-   retention-index calibration;
-   and combined use of mass-spectral and retention-index information.

The broader NIST ecosystem also includes:

-   NIST EI libraries;
-   GC retention-index collections;
-   NIST MS Search;
-   MSPepSearch;
-   and the Mass Spectrum Interpreter.

Therefore, the following concepts are **not new**:

``` text
EI library matching
+
retention-index evidence
+
GC–MS compound identification support
```

### Where RI Compass differs in emphasis

RI Compass is not intended to reproduce AMDIS deconvolution.

Instead, it accepts already processed/deconvoluted data and exposes the
resulting evidence in a more explicitly exploratory framework that
includes:

-   hierarchical EI chemical-class signatures;
-   parent chemical gates;
-   retained alternative evidence;
-   feature--feature spectral relationships;
-   Cytoscape-oriented network export;
-   hierarchical Sunburst visualization;
-   and report-oriented tables.

The NIST Mass Spectrum Interpreter is also an important conceptual
precedent because it connects chemical structures and mass spectra and
supports fragmentation interpretation.

Consequently, RI Compass should **not** claim to have invented
interpretable EI fragmentation analysis.

The intended distinction is narrower: RI Compass applies transparent
fragmentation rules directly to processed experimental EI spectra as an
additional **class-level evidence stream** that can agree or disagree
with RI and library candidates.

------------------------------------------------------------------------

# 7. MS-DIAL

MS-DIAL is another mature platform used extensively for GC-MS
metabolomics.

Published GC-MS workflows using MS-DIAL include:

-   peak detection;
-   deconvolution;
-   alignment;
-   EI spectral-library matching;
-   retention-index information;
-   and metabolite annotation.

MS-DIAL is therefore another example of an upstream platform that can
produce the type of processed information RI Compass is intended to
interrogate.

### Overlap

``` text
EI spectra
Retention indices
Library-based annotation
Processed feature tables
```

### Intended difference

RI Compass is not trying to replace MS-DIAL processing.

A realistic workflow is:

``` text
MS-DIAL
   ↓
deconvoluted / aligned GC–EI dataset
   ↓
RI Compass
   ↓
independent RI + fragmentation evidence exploration
```

The distinction again lies primarily in post-processing interpretation
rather than raw-data handling.

------------------------------------------------------------------------

# 8. GNPS-GC: the closest historical precedent for part of the workflow

GNPS-GC deserves explicit discussion because it is a particularly
relevant precedent.

The original GNPS GC-MS workflow accepts:

-   deconvoluted EI spectra in MGF;
-   a feature quantification table;
-   metadata;
-   spectral libraries;
-   and an optional carbon-marker table.

It performs:

-   GC--EI spectral-library search;
-   cosine-based spectral matching;
-   molecular networking;
-   Kovats RI calculation;
-   annotation tables;
-   and Cytoscape-compatible network output.

This is substantial overlap with part of the RI Compass workflow.

Therefore, it would be incorrect to claim that RI Compass introduced the
idea of:

``` text
Processed GC–EI spectra
        +
Kovats RI
        +
Library search
        +
Molecular networking
```

GNPS-GC clearly predates RI Compass in combining these elements.

### Important practical distinction

At the time of writing, the documented GC-MS workflow belongs to the
original GNPS documentation/ecosystem. We have not found an equivalent
clearly exposed GC--EI workflow in the current GNPS2 interface.

This observation should be interpreted cautiously.

It does **not** mean that GNPS-GC never existed or that its scientific
contribution is obsolete.

It means that the historical GNPS-GC workflow should be cited as an
important methodological precedent, while RI Compass is being developed
as a current local post-processing environment with a different
interpretive emphasis.

### Where RI Compass aims to extend this concept

The main proposed extension is not molecular networking itself.

It is the explicit layer:

``` text
EI spectrum
    ↓
Rule-based fragmentation evidence
    ↓
Parent chemical gate
    ↓
Hierarchical structural/class signature
    ↓
Comparison with RI and library evidence
```

The resulting class evidence can then be propagated into:

``` text
Network
+
Sunburst
+
Report
```

This is the part that should be evaluated as the potential
methodological contribution.

------------------------------------------------------------------------

# 9. Honest feature comparison

The table below describes **scope and emphasis**, not a claim that every
program lacks every possible related function.

  ---------------------------------------------------------------------------------------------------------------------
  Capability                       RI Compass               MZmine           AMDIS/NIST          MS-DIAL      GNPS-GC\*
  ---------------------------- -------------- -------------------- -------------------- ---------------- --------------
  Raw GC-MS processing                    No                  Yes                  Yes              Yes Yes / upstream
                                                                                                               workflow

  Peak detection                           No                  Yes                  Yes              Yes Via processing
                                                                                                               workflow

  EI deconvolution                         No                  Yes                  Yes              Yes  Yes / accepts
                                                                                                               external

  Alignment                                No                  Yes            Limited /              Yes     Depends on
                                                                     workflow-dependent                   upstream data

  Experimental RI/Kovats                  Yes                  Yes                  Yes              Yes            Yes

  EI library search                       Yes                  Yes                  Yes              Yes            Yes

  RI-aware candidate                      Yes                  Yes                  Yes              Yes            Yes
  evaluation                                                                                             

  EI spectral similarity                  Yes                  Yes                  Yes              Yes            Yes

  Feature--feature EI network             Yes                  Yes  Not a primary focus      Not primary            Yes
                                                                                              focus here 

  Cytoscape/GraphML-oriented              Yes                  Yes    Not primary focus      Not primary            Yes
  network output                                                                              focus here 

  Rule-based EI class                 **Yes**      Not the central             Fragment  Not the central        Not the
  signatures                                         documented GC       interpretation  role considered        central
                                                          workflow       exists in NIST             here     documented
                                                                              ecosystem                        workflow

  Explicit parent-gated class         **Yes** Not identified as an    Not identified as   Not identified Not identified
  hierarchy                                             equivalent           equivalent    as equivalent  as equivalent
                                                     documented GC                                       
                                                           feature                                       

  Best-leaf hierarchical class        **Yes**    Not identified as    Not identified as   Not identified Not identified
  summary                                               equivalent           equivalent    as equivalent  as equivalent

  Chemical-class Sunburst from        **Yes**    Not identified as    Not identified as   Not identified Not identified
  EI rules                                              equivalent           equivalent    as equivalent  as equivalent

  Explicit evidence-conflict   **Developing /   Annotation-quality        Spectral + RI   Identification       Multiple
  exploration                       partial**     framework exists      evidence exists   scoring exists        metrics
                                                                                                              available

  Report-oriented downstream              Yes        Export/report Search/report output           Export   Downloadable
  output                                              capabilities                          capabilities  result tables
  ---------------------------------------------------------------------------------------------------------------------

\* GNPS-GC refers here to the documented original GNPS GC-MS workflow.

### How to read this table

A **Yes** does not imply that two implementations are identical.

Likewise, "not identified as equivalent" means exactly that: an
equivalent function was not identified in the documentation reviewed for
this comparison. It should **not** be interpreted as proof that no
related functionality exists anywhere in the software.

------------------------------------------------------------------------

# 10. What is not novel in RI Compass

The following should **not** be presented individually as methodological
innovations:

## Retention-index calculation

Kovats and linear retention indices are established GC methods
implemented in multiple software packages.

## EI spectral-library searching

This is a core GC-MS identification strategy and is extensively
implemented by NIST software, AMDIS, MZmine, MS-DIAL, GNPS-GC, and
others.

## Combining EI similarity with RI

This is also established.

AMDIS/NIST, MZmine, MS-DIAL workflows, and GNPS-GC all provide
mechanisms for using retention information together with spectral
evidence.

## Molecular networking of GC--EI spectra

This is not new.

GNPS-GC demonstrated molecular networking of deconvoluted EI spectra,
and current MZmine documentation also describes molecular networking for
GC/EI-MS pseudo-spectra.

## Cytoscape export

This is useful but not novel.

## Mirror-spectrum visualization

Also useful, but common.

------------------------------------------------------------------------

# 11. What may be distinctive

The potentially distinctive contribution of RI Compass is the
**combination and explicit organization** of several ideas around
processed GC--EI data.

The strongest candidate is:

> **An interpretable post-processing framework in which retention-index
> evidence, EI spectral-library evidence, and rule-based hierarchical EI
> fragmentation evidence are evaluated as distinct evidence streams,
> compared for concordance or conflict, and propagated into relational
> and hierarchical chemical-space visualizations.**

This distinction has several components.

------------------------------------------------------------------------

## 11.1 Independent fragmentation evidence

The fragmentation engine is not simply another library score.

A feature can have:

``` text
Library evidence
Retention evidence
Fragmentation-class evidence
```

and these can disagree.

That disagreement is preserved rather than hidden.

------------------------------------------------------------------------

## 11.2 Parent chemical gates

Generic EI ions are common.

For example:

``` text
m/z 43
m/z 57
m/z 69
m/z 73
m/z 91
```

are chemically informative but not uniquely diagnostic.

The hierarchical engine therefore asks whether broad parent chemistry is
supported before promoting a more specific leaf signature.

Conceptually:

``` text
Observed fragments
       ↓
Broad parent chemistry
       ↓
Parent gate
       ↓
Specific class rule
       ↓
Final class evidence
```

This is intended to reduce overinterpretation of isolated diagnostic
ions.

------------------------------------------------------------------------

## 11.3 Human-readable rules

The rule system is designed to remain inspectable.

The user can examine:

``` text
diagnostic_ions
supporting_ions
conflicting_ions
relational_evidence
raw_score
gate_score
gate_pass
final score
```

The objective is not merely to obtain a label, but to understand **why
the label was proposed**.

------------------------------------------------------------------------

## 11.4 Concordance rather than a black-box probability

A future direction for RI Compass is an explicit **Evidence
Concordance** layer.

For example:

  RI evidence   EI library   EI fragmentation   Interpretation
  ------------- ------------ ------------------ ------------------------
  Support       Support      Support            Concordant
  Support       Support      Conflict           Structural conflict
  Conflict      Support      Support            RI conflict
  Support       Missing      Support            Orthogonally supported
  Missing       Support      Support            EI-supported
  Support       Missing      Missing            RI-only
  Missing       Support      Missing            Library-only
  Missing       Missing      Support            Class evidence only
  Weak          Weak         Weak               Insufficient evidence

This approach deliberately avoids converting all evidence into an
apparently precise "identification probability".

A `class score = 0.84`, for example, does **not** mean that a compound
has an 84% probability of being correctly identified.

------------------------------------------------------------------------

# 12. Why the network comes after evidence integration

The network should not be interpreted as the primary annotation
algorithm.

Its role is to organize the interpreted dataset relationally.

A feature node can contain:

``` text
Experimental RI
Library candidate
Spectral similarity
RI deviation
Fragmentation superclass
Fragmentation class
Best leaf signature
Class score
Evidence status
Sample abundance
```

An EI similarity edge then says:

> These experimental spectra are similar.

It does not say:

> These features are the same compound.

This distinction is essential for:

-   homologous series;
-   positional isomers;
-   terpene families;
-   related hydrocarbons;
-   and coeluting/deconvoluted GC-MS features.

The network is therefore best described as an:

> **evidence-enriched EI spectral network**

rather than as an identification network.

------------------------------------------------------------------------

# 13. Why the Sunburst comes after fragmentation analysis

The Sunburst is not a library taxonomy plot.

It summarizes the chemical-class evidence generated by the hierarchical
EI rule engine.

For example:

``` text
All classified features
        ↓
Hydrocarbon
        ↓
Aliphatic hydrocarbon
        ↓
Alkane-like
```

or:

``` text
All classified features
        ↓
Terpenoid
        ↓
Sesquiterpene
        ↓
Oxygenated-sesquiterpene-like
```

Using `Best leaf only` allows each accepted feature to contribute once
to the main summary.

Using `All supported classes` instead allows exploration of overlapping
EI signatures.

These modes answer different questions and should not be confused.

------------------------------------------------------------------------

# 14. What RI Compass does not currently claim

RI Compass does **not** claim to:

-   replace MZmine;
-   replace MS-DIAL;
-   replace AMDIS;
-   replace NIST MS Search;
-   replace authentic standards;
-   perform superior chromatographic deconvolution;
-   provide definitive structural elucidation from EI spectra;
-   calculate an identification probability;
-   quantify chemical classes from feature counts;
-   prove that a library candidate is correct;
-   or introduce GC--EI molecular networking as a new concept.

It also does not claim that the current EI rule engine is universally
validated across all GC-MS chemical spaces.

The fragmentation rules require continued evaluation with:

-   positive-control datasets;
-   negative-control datasets;
-   authentic standards;
-   different stationary phases;
-   different instrument platforms;
-   derivatized and underivatized samples;
-   and chemically diverse sample types.

------------------------------------------------------------------------

# 15. Current scientific limitation: validation

This is probably the most important limitation of the current RI Compass
concept.

A chemically reasonable rule is not automatically a validated
classifier.

For example, a rule designed for:

``` text
FAME-like
TMS-like
Terpenoid-like
Styrenic-like
Alkane-like
```

must be challenged with spectra from compounds that:

1.  truly belong to the target class;
2.  resemble the target class but do not belong to it;
3.  contain common interfering fragments;
4.  represent realistic GC-MS backgrounds;
5.  and come from independent datasets.

Therefore, the rule engine should presently be described as:

> **rule-based chemical-class screening**

rather than:

> **validated automated compound-class identification**

This distinction is scientifically important.

------------------------------------------------------------------------

# 16. Recommended validation strategy

A rigorous validation could use multiple reference datasets.

## Positive controls

Known spectra from:

-   n-alkanes;
-   alkenes;
-   alkylbenzenes;
-   styrenic compounds;
-   PAHs;
-   FAME mixtures;
-   monoterpenes;
-   sesquiterpenes;
-   derivatized organic acids;
-   derivatized amino acids;
-   derivatized sugars/polyols.

## Hard negative controls

Examples should include chemically confusable classes:

``` text
Alkanes vs alkenes
Alkylbenzenes vs styrenic compounds
Terpenes vs generic unsaturated hydrocarbons
TMS metabolites vs siloxane background
FAMEs vs long-chain hydrocarbons
Phenylpropanoids vs other substituted aromatics
```

## Metrics

Potential metrics include:

``` text
Sensitivity
Specificity
Precision
Recall
F1 score
False-positive rate
Class confusion
Parent-gate failure rate
Best-leaf accuracy
```

The purpose would not be to force the system into a black-box
classifier, but to quantify where the interpretable rules work and where
they fail.

------------------------------------------------------------------------

# 17. Practical niche of RI Compass

The clearest practical niche is:

> **Scientists who already have processed GC--EI data and want to
> interrogate compound annotations using retention behavior and
> interpretable fragmentation evidence without returning to a full
> raw-data processing workflow.**

This includes datasets generated by:

``` text
MZmine
MS-DIAL
AMDIS
vendor software
custom pipelines
```

Potential applications include:

-   pyrolysis oils;
-   essential oils;
-   volatile natural products;
-   environmental GC-MS;
-   FAME profiling;
-   derivatized metabolomics;
-   chemical fingerprinting;
-   and exploratory characterization of complex mixtures.

------------------------------------------------------------------------

# 18. Relationship with upstream software

RI Compass should be viewed as complementary to upstream processing
software.

## Example: MZmine → RI Compass

``` text
MZmine
│
├── Peak detection
├── Feature resolving
├── EI deconvolution
├── Alignment
└── Export
       │
       ▼
RI Compass
│
├── Experimental RI
├── RI candidate evaluation
├── EI library evidence
├── Rule-based EI class evidence
├── Evidence concordance
├── Spectral network
├── Sunburst
└── Report
```

The same concept can apply to MS-DIAL or another preprocessing platform.

This modularity is intentional.

------------------------------------------------------------------------

# 19. Why not simply perform everything inside the processing software?

That is a legitimate question.

For many routine analyses, a mature package such as MZmine, MS-DIAL,
AMDIS/NIST, or the historical GNPS-GC workflow may already provide
sufficient functionality.

RI Compass becomes useful when the analytical question is specifically:

> **How do the annotation candidates behave when retention evidence and
> an independent, interpretable EI fragmentation-class model are
> examined together?**

Its value therefore depends on whether this additional interpretive
layer improves:

-   expert review;
-   detection of conflicting annotations;
-   class-level characterization;
-   transparency;
-   reproducibility;
-   and communication of uncertainty.

This must ultimately be demonstrated empirically.

------------------------------------------------------------------------

# 20. Proposed scientific contribution

A cautious description of the project is:

> **RI Compass is a post-processing environment for processed GC--EI
> data that integrates experimental retention-index evaluation, EI
> spectral-library comparison, and interpretable hierarchical rule-based
> fragmentation screening. Rather than treating these outputs as
> interchangeable identification scores, the workflow preserves them as
> complementary evidence streams that may converge or conflict. The
> resulting evidence can be explored as an EI spectral network,
> summarized through a hierarchical chemical-class Sunburst, and
> exported in report-oriented form.**

A stronger claim should only be made after systematic benchmarking.

------------------------------------------------------------------------

# 21. What should be tested before claiming methodological novelty

Before describing RI Compass as a novel identification or annotation
framework in a publication, at least four questions should be addressed.

### 1. Does the hierarchical fragmentation engine add information beyond library similarity?

If the rule-based output merely reproduces the top library hit, its
incremental value is limited.

### 2. Can the engine detect incorrect but spectrally plausible library candidates?

This would be a strong demonstration of complementary evidence.

### 3. Does parent gating reduce false class assignments?

This directly tests one of the central design choices.

### 4. Does combining RI, library, and fragmentation evidence improve annotation prioritization?

This should be evaluated without converting the result into an
unjustified probability.

If these questions are answered positively, the methodological
contribution becomes substantially stronger.

------------------------------------------------------------------------

# 22. Bottom line

RI Compass operates in a field with strong existing software.

MZmine, AMDIS/NIST, MS-DIAL, and the original GNPS-GC workflow already
cover substantial parts of GC-MS processing, retention-index analysis,
spectral-library matching, and, in some cases, molecular networking.

That overlap is real and should be acknowledged.

The intended contribution of RI Compass is therefore **not**:

> another GC-MS preprocessing package,

and it is **not**:

> the first combination of Kovats RI, EI library search, and molecular
> networking.

Instead, the project is focused on:

> **transparent post-processing interpretation of processed GC--EI data
> through the joint but explicitly separated evaluation of
> retention-index evidence, spectral-library evidence, and hierarchical
> rule-based EI fragmentation evidence, followed by evidence-enriched
> network and chemical-class visualization.**

Whether this approach provides a meaningful methodological advantage
must be established through validation and benchmarking.

That is a stronger scientific position than claiming novelty for
individual components that already exist.

------------------------------------------------------------------------

# References and software documentation

The following resources are particularly relevant when positioning RI
Compass:

-   **MZmine documentation --- Untargeted GC-MS workflow**\
    https://mzmine.github.io/mzmine_documentation/latest/workflows/gcmsworkflow/gcms-workflow.html

-   **MZmine documentation --- Spectral library search**\
    https://mzmine.github.io/mzmine_documentation/latest/module_docs/id_spectral_library_search/spectral_library_search.html

-   **MZmine documentation --- Spectral / Molecular Networking**\
    https://mzmine.github.io/mzmine_documentation/latest/module_docs/group_spectral_net/molecular_networking.html

-   **NIST AMDIS**\
    https://chemdata.nist.gov/dokuwiki/doku.php?id=chemdata:amdis

-   **NIST Mass Spectrometry Data Center / tools**\
    https://chemdata.nist.gov/

-   **GNPS documentation --- GC-MS EI Data Analysis**\
    https://ccms-ucsd.github.io/GNPSDocumentation/gcanalysis/

-   **GNPS documentation --- GC-MS Library Search and Molecular
    Networking**\
    https://ccms-ucsd.github.io/GNPSDocumentation/gc-ms-library-molecular-network/

-   **Aksenov et al. --- Auto-deconvolution and molecular networking of
    gas chromatography--mass spectrometry data**\
    *Nature Biotechnology* 39, 169--173 (2021).\
    https://doi.org/10.1038/s41587-020-0700-3

------------------------------------------------------------------------

## Development principle

> **RI Compass should add evidence, not hide uncertainty.**

The objective is not to make GC-MS annotations look more certain than
they are.

The objective is to make the evidence behind them easier to inspect,
challenge, organize, and communicate.
