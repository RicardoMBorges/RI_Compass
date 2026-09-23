# RI Compass --- Tutorial e Guia de Interpretação

**Calibração de retention index, GC--EI spectral matching, hierarchical
EI chemical-class screening, Cytoscape export e resultados prontos para
relatórios**

RI Compass é uma aplicação Streamlit desenvolvida para combinar
diferentes fontes complementares de evidência obtidas por GC--MS, sem
tratar nenhuma delas isoladamente como identificação definitiva de um
composto.

O workflow integra:

1.  **Retention-index (RI) calibration and annotation**
2.  **GC--EI spectral-library matching**
3.  **Hierarchical rule-based EI chemical-class screening**
4.  **Experimental-feature spectral relationships**
5.  **Cytoscape-compatible network export**
6.  **Report- and manuscript-ready tables and text**

> **Retention behavior, EI spectral similarity e EI structural
> signatures são fontes complementares de evidência. Elas devem se
> reforçar mutuamente, e não ser confundidas entre si.**

Por isso, o RI Compass utiliza terminologia conservadora. Um
`class score` elevado representa evidência para uma **chemical-class ou
structural signature**, e não prova da identidade de um composto. Da
mesma forma, um `RI match` isolado não identifica um composto, e um
`library match` deve ser interpretado considerando retention behavior,
diagnostic fragments, library provenance e, quando disponíveis,
authentic standards.

------------------------------------------------------------------------

# 1. Que problema o RI Compass resolve?

A interpretação rotineira de GC--MS frequentemente gera vários
resultados desconectados:

-   uma chromatographic feature table;
-   uma corrida de calibração com n-alkanes;
-   candidatos de library search;
-   EI spectra;
-   referências de retention index;
-   informações de molecular network;
-   e, por fim, um relatório montado manualmente.

O RI Compass organiza essas informações em um único workflow centrado em
evidências.

Em vez de perguntar apenas:

> **"Qual composto a library atribuiu a este peak?"**

o programa estimula uma sequência mais defensável de perguntas:

> **Onde a feature elui?**\
> **Qual é seu experimental retention index?**\
> **Quais reference spectra se parecem com seu EI spectrum?**\
> **O RI observado apoia ou contradiz esses candidates?**\
> **Quais chemical-class signatures são independentemente sustentadas
> pelo EI fragmentation pattern?**\
> **Como essa feature se relaciona espectralmente com outras
> experimental features?**

Essa distinção é especialmente importante para amostras complexas, como
pyrolysis oils, essential oils, volatile extracts, derivatized
metabolomics samples, fatty-acid methyl esters e outras misturas
contendo compostos homólogos ou altamente isoméricos.

------------------------------------------------------------------------

# 2. Recommended workflow

Uma análise robusta normalmente segue esta ordem:

**n-alkane calibration → feature RI calculation → RI candidate screening
→ EI library search → EI/RI integration → hierarchical EI class
screening → mirror-spectrum inspection → network export → report
generation**

Os módulos podem ser usados individualmente, mas a interpretação mais
forte resulta da combinação de evidências ortogonais.

------------------------------------------------------------------------

# 3. Input files

## 3.1 n-Alkane calibration CSV

Faça upload de um CSV contendo a série conhecida de n-alkanes adquirida
sob as mesmas condições cromatográficas das amostras.

No mínimo, o arquivo deve conter:

-   **carbon number**
-   **retention time**

Exemplo:

``` text
Carbon_Number,RT
8,312.4
9,421.8
10,531.6
11,640.9
```

Os retention times devem estar nas unidades esperadas pela interface.
Sempre confira a unidade selecionada antes de executar a análise.

### Boa prática

A calibration mixture e as analytical samples devem ser adquiridas
usando o **mesmo chromatographic method**, incluindo:

-   stationary phase;
-   column dimensions;
-   carrier-gas conditions;
-   oven program;
-   inlet conditions;
-   e, preferencialmente, a mesma instrument configuration.

RI values calculados a partir de corridas cromatograficamente
incompatíveis não devem ser tratados como diretamente comparáveis.

------------------------------------------------------------------------

## 3.2 Feature table CSV

Faça upload da GC--MS feature table contendo, no mínimo, um feature
identifier e retention time.

Tabelas exportadas de workflows de deconvolution também podem conter
sample peak areas. Quando presentes, esses valores podem ser propagados
para downstream tables e network attributes.

O RI Compass distingue:

-   **Study samples**
-   **n-Alkane standard mixture**

A segunda opção é útil para inspecionar a feature table gerada a partir
da própria injeção do alkane calibration standard.

------------------------------------------------------------------------

## 3.3 Deconvoluted EI spectra em formato MGF

Os módulos **EI spectral search** e **EI substructure search** utilizam
deconvoluted spectra fornecidos em MGF.

Um spectrum típico contém feature/scan identifier, retention-time
metadata e uma lista de ions.

Exemplo:

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

O app reutiliza o mesmo sample MGF no hierarchical EI classification.

### Nota importante sobre `PEPMASS`

O RI Compass **não** interpreta automaticamente o campo MGF `PEPMASS`
como o EI molecular ion.

Em dados GC--EI, especialmente após deconvolution ou conversão por
formatos originalmente orientados a LC/MS, esse campo pode não
representar uma atribuição quimicamente válida de molecular ion. O
contexto de molecular ion deve, portanto, ser interpretado de forma
conservadora.

------------------------------------------------------------------------

## 3.4 EI reference libraries

O módulo **EI spectral search** aceita reference spectra nos formatos:

-   **MSP**
-   **MGF**

As reference libraries podem incluir bibliotecas gerais de EI,
specialized libraries, in-house spectra ou coleções específicas para
determinada aplicação.

Sempre que possível, preserve:

-   compound name;
-   library record identifier;
-   InChIKey;
-   reference RI;
-   stationary-phase information;
-   provenance.

A qualidade da reference library afeta diretamente a utilidade do
search.

------------------------------------------------------------------------

# 4. Retention-index calculation

## 4.1 Temperature-programmed GC

Para temperature-programmed GC, o RI Compass utiliza a formulação de
linear retention index normalmente associada à abordagem de van den
Dool--Kratz:

\[ RI = 100`\left[n +
\frac{t_R(x)-t_R(n)}
{t_R(n+1)-t_R(n)}
\right]`{=tex}\]

onde:

-   (t_R(x)) é o retention time do analyte;
-   (t_R(n)) é o retention time do n-alkane imediatamente anterior;
-   (t_R(n+1)) é o retention time do n-alkane imediatamente posterior;
-   \(n\) é o carbon number do n-alkane anterior.

Por exemplo, um analyte que elui exatamente no meio entre n-decane e
n-undecane terá RI próximo de 1050.

------------------------------------------------------------------------

## 4.2 Isothermal GC

Para um experimento isothermal, o RI Compass também disponibiliza a
formulação logarítmica de Kovats usando adjusted retention times:

\[ t'\_R=t_R-t_M \]

onde (t_M) é o dead time.

Selecione essa opção **somente** quando o experimento cromatográfico for
realmente isothermal e o dead time for conhecido.

------------------------------------------------------------------------

## 4.3 Evite extrapolação não controlada

Features fora do intervalo calibrado pelos n-alkanes não devem receber
RI por extrapolação não controlada.

Se a calibração cobre C8--C30, por exemplo, a região de RI mais
defensável é aquela delimitada pelos retention times desses standards.

Isso é particularmente importante para compostos muito voláteis e
material de alto ponto de ebulição.

------------------------------------------------------------------------

# 5. RI-based candidate screening

Após o RI calculation, o programa pode comparar experimental RI com
reference RI.

O candidate screening considera:

-   observed RI;
-   reference RI;
-   absolute `ΔRI`;
-   stationary-phase compatibility;
-   RI database/source selecionado;
-   user-defined tolerance;
-   feature detection filters.

A quantidade fundamental é:

\[ `\Delta `{=tex}RI = RI\_{observed} - RI\_{reference} \]

Um pequeno `|ΔRI|` fortalece o suporte baseado em retention behavior,
mas **não estabelece identidade**.

Muitos structural isomers apresentam retention indices semelhantes,
especialmente dentro de homologous series ou famílias relacionadas de
terpenes.

### Recommended interpretation

Use RI como **orthogonal evidence**:

-   bom RI agreement apoia um spectral candidate;
-   grande RI disagreement pode sinalizar um candidate para review;
-   RI isoladamente normalmente fornece um **candidate**, e não uma
    confirmed identification.

------------------------------------------------------------------------

# 6. GC--EI spectral-library search

Abra a tab **EI spectral search** e faça upload de:

1.  sample deconvoluted MGF;
2.  uma ou mais MSP/MGF reference libraries.

Em seguida, configure o search.

Defaults típicos:

  Parameter                    Typical default
  -------------------------- -----------------
  `Minimum cosine`                        0.65
  `Candidates per feature`                   5
  `Minimum matched ions`                     6
  `RI agreement window`            30 RI units
  `Fragment range`                 m/z 40--700

Esses valores são parâmetros de screening, não thresholds analíticos
universais.

------------------------------------------------------------------------

## 6.1 Spectral similarity

O search atual utiliza:

-   nominal/unit-mass bins;
-   square-root intensity transformation;
-   cosine similarity.

A square-root transformation reduz a dominância do base peak e permite
que fragments de menor intensidade contribuam de forma mais
significativa para a comparação.

A result table pode incluir:

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

## 6.2 Por que `cosine` sozinho não é suficiente?

Dois compostos podem apresentar EI spectra semelhantes e ainda assim
possuir estruturas diferentes, especialmente:

-   positional isomers;
-   terpene isomers;
-   homologous hydrocarbons;
-   alkylbenzenes;
-   closely related oxygenated compounds.

Portanto, um cosine elevado deve ser interpretado como **spectral
similarity**, e não automaticamente como identificação.

------------------------------------------------------------------------

# 7. Integrated EI + RI evidence

Quando experimental RI e library RI estão disponíveis, o RI Compass
combina essas duas fontes de evidência.

O programa distingue categorias como:

-   **EI + RI concordant**
-   **EI + RI tentative**
-   **EI similarity only**
-   **RI conflict / review**
-   **weak / review**
-   **RI-only candidate**
-   **unannotated**

Esses labels devem ser interpretados como categorias de screening.

Um strong spectral match acompanhado de RI conflict é deliberadamente
marcado para review, em vez de ser aceito silenciosamente.

O integrated screening rank atribui maior peso à EI similarity,
utilizando RI proximity como evidência independente de suporte. Ele é um
**ranking aid**, e não uma identification probability.

------------------------------------------------------------------------

# 8. Hierarchical EI structural-signature search

A tab **EI substructure search** fornece um tipo de informação diferente
daquela obtida em **EI spectral search**.

Ela pergunta:

> **Que tipo de chemical fragmentation pattern é sustentado por este
> spectrum?**

em vez de:

> **Qual composto nominal da library é mais semelhante?**

Essa distinção é fundamental.

O engine utiliza regras interpretáveis baseadas em combinações de:

-   diagnostic ions;
-   supporting ions;
-   relative ion intensities;
-   homologous fragmentation patterns;
-   relational evidence;
-   conflicting ions;
-   parent chemical-class gates;
-   selected molecular-ion context, quando defensável.

------------------------------------------------------------------------

# 9. Por que o engine é hierarchical?

Muitos EI fragments são quimicamente informativos, mas **não são
exclusivos**.

Por exemplo:

-   m/z 43 ocorre em numerosos compostos alifáticos e oxigenados;
-   m/z 57 é comum na fragmentação de saturated hydrocarbons;
-   m/z 69 e 83 aparecem em muitas estruturas insaturadas;
-   m/z 91 é característico de benzyl/tropylium chemistry, mas não
    identifica sozinho um alkylbenzene;
-   m/z 73 pode indicar trimethylsilyl chemistry, mas também é comum em
    siloxane contamination.

Um flat rule system pode, portanto, superclassificar spectra.

O RI Compass utiliza uma hierarquia em duas etapas:

``` text
Broad parent chemistry
        ↓
Parent gate
        ↓
Subclass / leaf signature
        ↓
Gate-adjusted final score
```

Uma subclass só é promovida quando a parent chemistry apresenta suporte
suficiente.

Exemplo:

``` text
Terpenoid-like
├── Monoterpene-like
│   ├── Monoterpene hydrocarbon-like
│   └── Oxygenated monoterpene-like
└── Sesquiterpene-like
    ├── Sesquiterpene hydrocarbon-like
    └── Oxygenated sesquiterpene-like
```

e, conceitualmente:

``` text
FAME-like
├── Saturated FAME-like
├── Unsaturated FAME-like
└── PUFA-like
```

Essa arquitetura reduz false subclass assignments provocadas por generic
fragments.

------------------------------------------------------------------------

# 10. Parent chemical gates

O hierarchical engine avalia broad evidence para parent chemical domains
como:

-   **Hydrocarbon**
-   **Aromatic**
-   **FAME**
-   **TMS derivative**
-   **Terpenoid**
-   **Oxygenated**
-   **Background / QC**

Somente depois que um `parent gate` passa é que as leaf rules
dependentes podem receber um final score significativo.

Isso é especialmente útil para signatures quimicamente ambíguas.

### Exemplo: TMS chemistry

m/z 73 sozinho não deve produzir automaticamente uma TMS-metabolite
assignment.

Uma classificação TMS convincente exige um contexto mais amplo de TMS
fragmentation, enquanto uma série de ions típica de siloxane pode
funcionar como evidência de background contamination.

### Exemplo: FAME chemistry

Generic hydrocarbon fragments não são suficientes para classificar uma
feature como fatty-acid methyl ester.

O `FAME parent gate` precisa primeiro sustentar ester/FAME chemistry
antes que subclasses saturated, unsaturated ou polyunsaturated sejam
promovidas.

### Exemplo: terpenoids

Terpene-like fragments apresentam grande sobreposição entre isomers.

O engine avalia primeiro terpene-core evidence antes de atribuir
signatures mais específicas de monoterpene ou sesquiterpene.

------------------------------------------------------------------------

# 11. Entendendo o EI class score

O engine apresenta tanto raw evidence quanto hierarchical evidence.

Colunas importantes incluem:

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

O `score` final é um **rule-based screening score entre 0 e 1**.

Ele **não** é posterior probability, identification probability ou
percentage confidence.

### Suggested interpretation

    Final score Interpretation
  ------------- -------------------------------
       `< 0.30` weak / no meaningful evidence
    `0.30–0.59` possible signature
    `0.60–0.79` probable class signature
       `≥ 0.80` strong class signature

Para routine composition summaries, **0.60 é o recommended default
threshold**.

Isso significa que o summary considera principalmente **probable +
strong** class signatures.

------------------------------------------------------------------------

# 12. `raw_score` versus final `score`

Essa distinção é importante.

Um spectrum pode conter fragments que se parecem com determinada
subclass e, portanto, produzir um `raw_score` significativo.

Entretanto, se a parent chemistry necessária não tiver suporte
suficiente, `gate_pass` será `False` e o `score` final será suprimido.

Isso evita que alguns generic fragments sejam interpretados como uma
classificação química específica.

> **Use `score` para a interpretação principal. Use `raw_score` para
> investigar por que um spectrum apresentou semelhança parcial com
> determinada rule.**

------------------------------------------------------------------------

# 13. `Best leaf only`

Um único EI spectrum pode legitimamente sustentar signatures
sobrepostas.

Para exploratory analysis, o RI Compass pode preservar essas
sobreposições.

Entretanto, em composition-style summaries, contar todas as classes
suportadas faria a mesma feature ser contabilizada mais de uma vez.

O programa oferece:

-   **Best leaf only**
-   **All supported classes**

## Recommended default: `Best leaf only`

`Best leaf only` atribui cada feature apenas uma vez, utilizando sua
highest-ranking gated leaf class.

É o modo recomendado para:

-   Sunburst summaries;
-   sample-level composition views;
-   figures;
-   comparative reporting.

`All supported classes` é mais adequado para investigar mecanisticamente
overlapping fragmentation signatures.

------------------------------------------------------------------------

# 14. Interactive chemical-class Sunburst

O Sunburst resume a hierarquia:

``` text
Superclass → class group → leaf class
```

Recommended default settings:

``` text
Minimum final score = 0.60
Assignment = Best leaf only
```

Isso produz uma visualização conservadora em que cada accepted feature
contribui uma única vez.

As informações exibidas em hover incluem:

-   number of features;
-   median score;
-   mean score.

O interactive plot pode ser exportado como HTML e os dados subjacentes
podem ser baixados como CSV.

### Nota crítica de interpretação

O número de classified features **não representa automaticamente
composição química quantitativa**.

Na ausência de um abundance-aware model com correções apropriadas de
resposta, o Sunburst descreve principalmente a **distribuição das
classified features**, e não weight percent, molar percent ou absolute
concentration.

------------------------------------------------------------------------

# 15. Essential oils e terpene-rich samples

A hierarchical architecture é particularmente útil para essential oils
porque EI spectra de terpenes frequentemente são muito semelhantes.

Regiões típicas de fragmentação incluem ions próximos de:

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

Esses ions **não** devem ser tratados como unique compound markers.

O RI Compass utiliza combinações de fragments e hierarchical chemical
context para sustentar broader terpene classes.

Para essential oils, o workflow mais forte é:

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

Isso é muito mais defensável do que atribuir compounds com base em um
único diagnostic ion ou no primeiro library rank.

Authentic standards continuam sendo a abordagem preferencial quando é
necessária discriminação definitiva entre isomers.

------------------------------------------------------------------------

# 16. Pyrolysis oils e hydrocarbon-rich samples

Pyrolysis oils frequentemente contêm homologous hydrocarbon series e
aromatic products.

Padrões úteis de EI podem incluir:

### Saturated aliphatic pattern

``` text
43 → 57 → 71 → 85 → 99 → 113
```

A progressão de aproximadamente 14 Da é consistente com unidades
repetidas de CH₂.

### Unsaturated / allylic pattern

``` text
41 → 55 → 69 → 83 → 97
```

### Aromatic / alkylbenzene context

Supporting ions comuns podem incluir:

``` text
77, 91, 105, 119
```

m/z 91 é frequentemente associado a benzyl/tropylium fragmentation, mas
nunca deve ser tratado como identificador exclusivo de alkylbenzene.

### Styrenic context

Uma combinação envolvendo ions como:

``` text
51, 77, 78, 104
```

pode sustentar styrenic chemistry, mas a região nominal de m/z 104
isoladamente não distingue todos os C8H8 isomers.

RI e reference-spectrum agreement são particularmente importantes nesse
caso.

------------------------------------------------------------------------

# 17. Mirror-spectrum inspection

Automated ranking deve ser seguido de visual inspection para features
importantes.

O módulo **Mirror spectra** permite comparar:

-   experimental EI spectrum;
-   candidate reference spectrum.

Inspecione:

-   base-peak agreement;
-   diagnostic fragments;
-   missing high-intensity ions;
-   unexpected ions;
-   relative-intensity patterns;
-   molecular-ion region;
-   possíveis coelution/deconvolution artifacts.

Um cosine numericamente elevado pode ocultar divergências quimicamente
relevantes.

Por isso, mirror plots constituem uma etapa importante de expert review.

------------------------------------------------------------------------

# 18. Cytoscape network export

O RI Compass pode exportar uma GraphML network para Cytoscape.

A network foi desenhada para preservar evidências, e não apenas exibir
uma única annotation.

Node types típicos incluem:

### `feature`

Uma experimental GC--MS feature.

Feature nodes podem conter:

-   feature ID;
-   retention time;
-   experimental RI;
-   peak-area information;
-   top EI candidate;
-   cosine;
-   matched-ion count;
-   RI agreement;
-   evidence level;
-   opcionalmente spectral peak lists.

### `reference`

Um reference-library compound conectado a uma ou mais experimental
features por EI library matches.

------------------------------------------------------------------------

## 18.1 Library-match edges

Edges `EI_library_match` representam candidate relationships entre uma
experimental feature e um library record.

Alternative ranked candidates podem permanecer na network mesmo quando
apenas a best proposal é exibida como feature label.

Isso evita que a graph esconda annotation ambiguity.

------------------------------------------------------------------------

## 18.2 Feature--feature similarity edges

Edges opcionais `EI_feature_similarity` conectam experimental features
com base no EI spectral cosine.

Esses edges significam:

> **the EI spectra are similar**

Eles **não** significam:

> **the two nodes are the same compound**

Essa distinção é especialmente importante para homologues e structural
isomers.

O usuário pode configurar:

-   minimum feature--feature cosine;
-   minimum shared ions;
-   maximum EI neighbors per feature.

------------------------------------------------------------------------

# 19. Suggested Cytoscape interpretation

Um Cytoscape style útil pode mapear:

-   **node shape** → node type;
-   **node label** → feature ID / putative candidate;
-   **node size** → abundance ou outra experimental quantity;
-   **border width** → annotation/evidence strength;
-   **edge type** → library match versus feature similarity;
-   **edge width** → cosine ou integrated screening score.

Evite visual styling que sugira confirmed identification quando a
evidência é apenas putative.

------------------------------------------------------------------------

# 20. `Report & manuscript`

A tab **Report & manuscript** reúne resultados analíticos selecionados
em uma publication-oriented table e em texto explicativo.

O report pode integrar:

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
-   sample peak areas, quando disponíveis.

O app também prepara seções editáveis para:

-   **Methods**
-   **Results and interpretation**
-   **Table legend**

Esses outputs devem ser revisados e adaptados ao experimento real antes
da publicação.

------------------------------------------------------------------------

# 21. Linguagem de identificação

O RI Compass utiliza deliberadamente terminologia conservadora.

Termos recomendados incluem:

-   **putative annotation**
-   **candidate**
-   **spectral match**
-   **RI-supported candidate**
-   **class signature**
-   **consistent with**
-   **supports**
-   **requires review**

Evite converter automaticamente computational output em expressões como:

-   "confirmed compound"
-   "identified with 95% confidence"
-   "80% probability"
-   "definitively detected"

a menos que o experimental design sustente independentemente esse nível
de identificação.

------------------------------------------------------------------------

# 22. Exemplo prático de interpretação

Considere uma experimental feature com:

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

Uma interpretação defensável seria:

> A feature apresenta forte EI spectral similarity com Candidate X,
> acompanhada de concordant retention-index behavior e strong
> aromatic/styrenic EI structural signature. O conjunto de evidências
> sustenta Candidate X como uma high-priority putative annotation,
> sujeita à revisão do reference spectrum e, quando necessário, à
> confirmação com authentic standard.

Uma afirmação menos defensável seria:

> Candidate X foi definitivamente identificado com 84% de confiança.

O `class score` não representa identification probability.

------------------------------------------------------------------------

# 23. Troubleshooting

## Nenhum RI é calculado para algumas features

Verifique se o feature retention time está fora do n-alkane calibration
range.

Confira também:

-   RT units;
-   alkane ordering;
-   missing standards;
-   duplicated carbon numbers;
-   chromatographic compatibility.

------------------------------------------------------------------------

## Muitos RI candidates

Reduza o RI tolerance ou restrinja reference sources/stationary-phase
policy.

Lembre-se: RI funciona como candidate filter, não necessariamente como
unique identifier.

------------------------------------------------------------------------

## Nenhum EI library hit

Considere se:

-   `Minimum cosine` está alto demais;
-   `Minimum matched ions` está restritivo demais;
-   a reference library cobre a química relevante;
-   os MGF spectra contêm ions suficientes;
-   o acquisition mass range é compatível com a library;
-   a deconvolution quality é adequada.

------------------------------------------------------------------------

## EI library hits demais

Aumente:

-   `Minimum cosine`;
-   `Minimum matched ions`;

e dê maior peso interpretativo a:

-   RI agreement;
-   diagnostic-ion review;
-   mirror spectra;
-   library provenance.

------------------------------------------------------------------------

## Uma class apresenta `raw_score` alto, mas `score = 0`

A leaf rule encontrou partial spectral evidence, mas o parent gate
necessário não passou.

Isso é intencional e constitui uma das salvaguardas do hierarchical
engine.

------------------------------------------------------------------------

## Terpenes aparecem em várias classes

Isso é esperado porque a EI fragmentation de terpene isomers apresenta
grande sobreposição.

Use:

-   `Best leaf only` para um conservative summary;
-   `All supported classes` para investigar overlapping evidence;
-   RI + spectral-library evidence para compound-level interpretation.

------------------------------------------------------------------------

## TMS-like signals dominam

Verifique se o spectrum representa um derivatized metabolite ou siloxane
background.

GC--MS background ions comuns podem se parecer fortemente com
derivatization-related fragments quando interpretados sem um chemical
gate.

------------------------------------------------------------------------

# 24. Recommended defaults

Para uma primeira análise geral:

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

Esses valores são starting points e devem ser validados para a
analytical platform e o sample type.

------------------------------------------------------------------------

# 25. O que o RI Compass não faz

O RI Compass não substitui:

-   expert EI interpretation;
-   authentic-standard confirmation;
-   chromatographic method validation;
-   quantitative calibration;
-   manual review of deconvolution;
-   critical evaluation of reference-library quality.

O programa também não assume que:

-   o maior library score é automaticamente correto;
-   `PEPMASS` representa o EI molecular ion;
-   um diagnostic fragment define sozinho uma estrutura;
-   um RI value identifica sozinho um composto;
-   feature counts equivalem a chemical concentration.

O app deve ser entendido como um **evidence-integration and
prioritization environment**.

------------------------------------------------------------------------

# 26. Recomendações para reprodutibilidade

Para análises reprodutíveis, registre:

-   RI Compass version/commit;
-   GC column e stationary phase;
-   column dimensions;
-   oven program;
-   carrier-gas conditions;
-   alkane calibration range;
-   RI equation usada;
-   RI tolerance;
-   EI ionization energy;
-   scan range;
-   deconvolution software e settings;
-   spectral libraries e versions;
-   cosine threshold;
-   minimum matched ions;
-   class-engine thresholds;
-   selected rule domains;
-   manual exclusions.

Exporte as result tables em vez de depender apenas de screenshots.

------------------------------------------------------------------------

# 27. Suggested Methods wording

O texto abaixo pode ser adaptado para manuscripts:

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

> **Nota:** esta seção foi mantida em inglês porque foi preparada para
> inserção direta em um manuscript.

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

> **Nota:** esta seção também foi mantida em inglês para facilitar seu
> uso direto em manuscript/report.

------------------------------------------------------------------------

# 29. Citation and software reporting

Ao utilizar RI Compass em trabalho científico, reporte:

-   software version ou Git commit;
-   date of analysis;
-   reference libraries utilizadas;
-   retention-index source/database;
-   chromatographic stationary phase;
-   todos os relevant screening thresholds.

Se o repository possuir DOI, software paper ou archived release, cite
esse registro persistente além do GitHub repository.

------------------------------------------------------------------------

# 30. Filosofia final de interpretação

O princípio mais importante do RI Compass é que **diferentes analytical
clues respondem a perguntas diferentes**.

  -----------------------------------------------------------------------
  Evidence                            Pergunta principal
  ----------------------------------- -----------------------------------
  Retention index                     O chromatographic behavior é
                                      compatível?

  EI library cosine                   O spectrum se parece com um
                                      reference spectrum?

  Diagnostic fragments                Quais fragmentation motifs estão
                                      presentes?

  Hierarchical class score            Qual chemical-class signature é
                                      sustentada?

  Feature--feature cosine             Quais experimental spectra se
                                      parecem entre si?

  Authentic standard                  Um experimentally controlled
                                      reference sustenta a identidade?
  -----------------------------------------------------------------------

Nenhuma linha dessa tabela deve substituir silenciosamente as demais.

A annotation mais forte é obtida quando fontes independentes de
evidência convergem.

> **Use RI Compass para priorizar, inspecionar, integrar e documentar
> evidências --- não para esconder incerteza.**
