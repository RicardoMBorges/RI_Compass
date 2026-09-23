# RI Compass no Cenário de Software para GC-MS

## Escopo, sobreposição com ferramentas existentes, limitações e contribuição pretendida

> **Versão curta:** o RI Compass **não** pretende substituir softwares
> de GC-MS para preprocessing, peak detection, spectral deconvolution
> ou alignment. Ele é um ambiente de interpretação pós-processamento
> para dados GC--EI já processados. Seu objetivo é reunir evidências de
> experimental retention index, EI spectral-library evidence, evidências
> interpretáveis baseadas em regras de EI fragmentation e visualização
> do chemical space em um workflow transparente.

------------------------------------------------------------------------

## 1. Por que esse posicionamento é importante

O campo de software para GC-MS é maduro. Diversos programas
estabelecidos já executam uma ou mais das seguintes tarefas:

-   importação de raw data;
-   peak detection;
-   chromatographic feature resolving;
-   EI spectral deconvolution;
-   feature alignment;
-   retention-index calculation;
-   spectral-library searching;
-   retention-index filtering;
-   molecular networking;
-   statistical analysis;
-   compound annotation.

Por isso, o RI Compass **não deve ser descrito como uma nova plataforma
geral de processamento de GC-MS**.

Seu papel pretendido começa **depois que os dados cromatográficos já
foram processados**.

Uma entrada típica para o RI Compass é:

``` text
Processed GC–MS feature table
        +
Deconvoluted EI spectra
        +
n-Alkane calibration
        +
Optional EI reference libraries
```

Esses dados podem vir de MZmine, MS-DIAL, AMDIS, software do fabricante
ou outro workflow adequado de preprocessing.

A questão central abordada pelo RI Compass não é:

> Como detectar e deconvoluir peaks cromatográficos?

Mas sim:

> **Dado um conjunto de dados GC--EI já processado, como retention
> behavior e EI fragmentation evidence podem ser interrogados
> conjuntamente para fortalecer, questionar, organizar e comunicar
> chemical annotations?**

------------------------------------------------------------------------

# 2. Posição analítica pretendida para o RI Compass

O workflow conceitual é:

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

Essa distinção é importante porque o RI Compass foi concebido como uma
**camada downstream de interpretação**, e não como um concorrente de
engines de raw-data processing.

------------------------------------------------------------------------

# 3. O que o RI Compass faz atualmente

O RI Compass concentra-se em cinco tarefas relacionadas.

## 3.1 Experimental retention-index calculation

A aplicação utiliza uma série experimental de n-alkanes para calcular
retention indices das features de GC-MS já processadas.

Dependendo do modo cromatográfico, isso inclui:

-   temperature-programmed linear retention indices;
-   cálculos do tipo Kovats em condições isothermal, quando apropriado;
-   interpolação dentro da faixa experimentalmente calibrada pelos
    alkanes;
-   comparação com reference RI values.

O retention index é tratado como uma linha independente de evidência
cromatográfica.

RI agreement apoia um candidate.

RI disagreement pode questionar um candidate.

RI isoladamente não é tratado como prova de identidade.

------------------------------------------------------------------------

## 3.2 EI spectral-library comparison

Deconvoluted EI spectra podem ser comparados com EI reference libraries.

As evidências resultantes incluem, por exemplo:

-   spectral cosine;
-   number of matched ions;
-   library provenance;
-   reference RI, quando disponível;
-   candidate ranking.

Novamente, spectral similarity não é automaticamente interpretada como
identificação.

Um library score elevado significa que o experimental spectrum se parece
com um reference spectrum. Structural isomers, homologues, coelution,
deconvolution artifacts e bibliotecas incompletas continuam sendo
limitações relevantes.

------------------------------------------------------------------------

## 3.3 Rule-based EI fragmentation interpretation

Esta é a parte do RI Compass conceitualmente mais distinta do library
searching convencional.

Em vez de perguntar apenas:

> Qual reference spectrum é mais semelhante?

o EI structural-signature engine também pergunta:

> **Quais chemically interpretable fragmentation patterns são
> independentemente sustentados pelo experimental EI spectrum?**

O engine avalia combinações de:

-   diagnostic ions;
-   supporting ions;
-   ion-intensity relationships;
-   homologous fragmentation patterns;
-   conflicting ions;
-   relational fragmentation evidence;
-   selected neutral-loss ou molecular-ion context, quando defensável;
-   broad parent-chemistry gates.

Exemplos de broad chemical domains incluem:

``` text
Hydrocarbon
Aromatic
FAME
TMS derivative
Terpenoid
Oxygenated
Background / QC
```

Possible downstream signatures incluem padrões como:

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

O objetivo **não** é predizer uma estrutura molecular única a partir dos
EI fragments.

O objetivo é gerar uma camada de evidência estrutural/de classe que seja
interpretável, auditável e parcialmente independente do library hit.

------------------------------------------------------------------------

## 3.4 Evidence integration

A ideia analítica central é que diferentes evidence streams respondem a
perguntas diferentes.

  -----------------------------------------------------------------------
  Evidence                            Pergunta principal
  ----------------------------------- -----------------------------------
  Experimental RI                     O chromatographic behavior é
                                      compatível?

  EI library similarity               O experimental spectrum se parece
                                      com um reference spectrum?

  Diagnostic EI fragments             Quais fragmentation motifs estão
                                      presentes?

  Hierarchical EI class score         Qual chemical-class signature é
                                      sustentada?

  Feature--feature EI similarity      Quais experimental spectra se
                                      parecem entre si?

  Authentic standard                  Um experimentally controlled
                                      reference sustenta a identidade?
  -----------------------------------------------------------------------

Essas evidências não devem ser cegamente condensadas em uma única
probabilidade.

Um exemplo útil é:

``` text
Library candidate: Styrene
EI similarity: strong
Experimental RI: concordant
EI parent class: Aromatic
EI leaf signature: Styrenic-like
Parent gate: pass
```

Aqui, múltiplas linhas de evidência convergem.

Mas o RI Compass tem igual interesse em divergências:

``` text
Library candidate: Fatty-acid methyl ester
EI library similarity: moderate
Experimental RI: plausible
FAME parent gate: fail
```

Isso não representa uma análise que falhou.

É uma informação útil:

``` text
Structural evidence conflict → review candidate
```

A capacidade de expor concordância **e conflito** é central ao workflow
pretendido.

------------------------------------------------------------------------

# 4. Network e Sunburst são resultados da interpretação, não identification engines

O RI Compass também produz duas representações complementares do dataset
interpretado.

## 4.1 Evidence-enriched spectral network

A network representa relações entre experimental EI features e, quando
aplicável, reference-library candidates.

Experimental feature nodes podem carregar atributos como:

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

Feature--feature edges representam EI spectral similarity.

Eles **não** implicam que dois nodes correspondam ao mesmo composto.

A network responde, portanto, a uma pergunta relacional:

> **Quais experimental EI spectra estão relacionados e quais annotation
> evidences estão associadas a cada feature?**

## 4.2 Hierarchical chemical-class Sunburst

O Sunburst responde a outra pergunta:

> **Qual espaço de chemical classes sustentado por fragmentation está
> representado no processed dataset?**

A hierarquia pode ser representada como:

``` text
Superclass
    ↓
Class group
    ↓
Leaf class
```

Para summaries conservadores, o modo recomendado é:

``` text
Minimum final score = 0.60
Assignment = Best leaf only
```

Isso impede que uma feature com overlapping EI signatures seja contada
repetidamente na visualização principal do tipo composition summary.

É importante destacar que feature counts no Sunburst **não equivalem a
chemical concentration, weight percentage ou molar composition**.

------------------------------------------------------------------------

# 5. Comparação com softwares existentes para GC-MS

A comparação abaixo é deliberadamente conservadora.

O RI Compass apresenta sobreposição com softwares existentes em diversas
áreas. Essas sobreposições devem ser reconhecidas, e não apresentadas
como novidade.

------------------------------------------------------------------------

## 5.1 MZmine

O MZmine é atualmente uma das comparações mais importantes, pois oferece
um workflow moderno de GC--EI que inclui:

-   raw-data import;
-   mass detection;
-   feature resolving;
-   GC--EI spectral deconvolution;
-   alignment usando retention time e spectral similarity;
-   spectral-library searching;
-   retention-index filtering;
-   annotation-quality summaries;
-   statistics;
-   spectral/molecular networking;
-   network visualization;
-   GraphML export.

O MZmine pode tratar GC--EI pseudo-spectra como MS1 spectra para library
searching e oferece abordagens de spectral similarity voltadas a GC,
como composite cosine identity.

Ele também permite retention-index tolerance durante spectral-library
search.

### Onde o RI Compass se sobrepõe ao MZmine

``` text
Retention-index use
EI library search
Spectral similarity
Feature–feature relationships
Molecular/spectral networking
GraphML export
Annotation evidence
```

Essas capacidades, portanto, **não constituem isoladamente contribuições
exclusivas do RI Compass**.

### Onde a ênfase pretendida é diferente

MZmine é uma ampla plataforma de mass-spectrometry data processing e
analysis.

O RI Compass deliberadamente começa downstream:

``` text
MZmine
    ↓
processed feature table + deconvoluted EI spectra
    ↓
RI Compass
```

A distinção pretendida é o uso explícito de uma camada **human-readable,
hierarchical, rule-based EI structural-signature** ao lado de RI e
library evidence, seguida de visualização downstream orientada às
evidências.

Isso deve ser entendido como diferença de ênfase analítica e
arquitetura, e não como evidência de que o MZmine não possui recursos
sofisticados de annotation.

De fato, o MZmine possui um `Annotation Quality Summary` que integra
diferentes dimensões de annotation, incluindo spectral matching e
informações relacionadas a RI. Portanto, seria inadequado afirmar que o
RI Compass é o primeiro software a combinar múltiplos critérios de
annotation.

------------------------------------------------------------------------

# 6. AMDIS e o ecossistema NIST

AMDIS é uma ferramenta fundamental para GC-MS e uma comparação
importante.

AMDIS realiza:

-   component detection;
-   mass-spectral deconvolution;
-   comparação com target/reference libraries;
-   retention-index calibration;
-   uso combinado de mass-spectral e retention-index information.

O ecossistema NIST também inclui:

-   NIST EI libraries;
-   GC retention-index collections;
-   NIST MS Search;
-   MSPepSearch;
-   Mass Spectrum Interpreter.

Portanto, os seguintes conceitos **não são novos**:

``` text
EI library matching
+
retention-index evidence
+
GC–MS compound identification support
```

### Onde o RI Compass difere em ênfase

O RI Compass não pretende reproduzir a deconvolution do AMDIS.

Em vez disso, aceita dados já processados/deconvoluídos e expõe as
evidências em um framework mais explicitamente exploratório que inclui:

-   hierarchical EI chemical-class signatures;
-   parent chemical gates;
-   retained alternative evidence;
-   feature--feature spectral relationships;
-   Cytoscape-oriented network export;
-   hierarchical Sunburst visualization;
-   report-oriented tables.

O NIST Mass Spectrum Interpreter também é um precedente conceitual
importante, pois conecta chemical structures e mass spectra e dá suporte
à interpretação de fragmentation.

Consequentemente, o RI Compass **não deve alegar ter inventado a
interpretação de EI fragmentation**.

A distinção pretendida é mais estreita: o RI Compass aplica transparent
fragmentation rules diretamente a processed experimental EI spectra como
uma camada adicional de **class-level evidence**, capaz de concordar ou
discordar dos RI e library candidates.

------------------------------------------------------------------------

# 7. MS-DIAL

MS-DIAL é outra plataforma madura, amplamente utilizada em GC-MS
metabolomics.

Workflows publicados de GC-MS usando MS-DIAL incluem:

-   peak detection;
-   deconvolution;
-   alignment;
-   EI spectral-library matching;
-   retention-index information;
-   metabolite annotation.

MS-DIAL é, portanto, outro exemplo de upstream platform capaz de
produzir o tipo de informação processada que o RI Compass pretende
interrogar.

### Overlap

``` text
EI spectra
Retention indices
Library-based annotation
Processed feature tables
```

### Intended difference

O RI Compass não pretende substituir o processamento do MS-DIAL.

Um workflow realista é:

``` text
MS-DIAL
   ↓
deconvoluted / aligned GC–EI dataset
   ↓
RI Compass
   ↓
independent RI + fragmentation evidence exploration
```

Novamente, a distinção está principalmente na interpretação
pós-processamento, e não no raw-data handling.

------------------------------------------------------------------------

# 8. GNPS-GC: o precedente histórico mais próximo de parte do workflow

GNPS-GC merece discussão explícita porque constitui um precedente
particularmente relevante.

O workflow original de GC-MS do GNPS aceita:

-   deconvoluted EI spectra em MGF;
-   feature quantification table;
-   metadata;
-   spectral libraries;
-   optional carbon-marker table.

Ele realiza:

-   GC--EI spectral-library search;
-   cosine-based spectral matching;
-   molecular networking;
-   Kovats RI calculation;
-   annotation tables;
-   Cytoscape-compatible network output.

Isso representa sobreposição substancial com parte do workflow do RI
Compass.

Portanto, seria incorreto afirmar que o RI Compass introduziu a ideia
de:

``` text
Processed GC–EI spectra
        +
Kovats RI
        +
Library search
        +
Molecular networking
```

O GNPS-GC claramente antecede o RI Compass na combinação desses
elementos.

### Distinção prática importante

No momento desta comparação, o workflow documentado de GC-MS pertence à
documentação/ecossistema do GNPS original. Não foi identificado um
workflow GC--EI equivalente claramente exposto na interface atual do
GNPS2.

Essa observação deve ser interpretada com cautela.

Ela **não** significa que o GNPS-GC nunca existiu ou que sua
contribuição científica esteja obsoleta.

Significa que o workflow histórico GNPS-GC deve ser citado como um
importante precedente metodológico, enquanto o RI Compass está sendo
desenvolvido como um ambiente local atual de pós-processamento, com
ênfase interpretativa diferente.

### Onde o RI Compass pretende estender esse conceito

A principal extensão proposta não é molecular networking em si.

É a camada explícita:

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

A class evidence resultante pode então ser propagada para:

``` text
Network
+
Sunburst
+
Report
```

Essa é a parte que deve ser avaliada como potencial contribuição
metodológica.

------------------------------------------------------------------------

# 9. Comparação honesta de funcionalidades

A tabela abaixo descreve **escopo e ênfase**, e não afirma que cada
programa seja absolutamente desprovido de qualquer função relacionada.

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

\* GNPS-GC refere-se aqui ao workflow GC-MS documentado no GNPS
original.

### Como interpretar esta tabela

Um **Yes** não significa que duas implementações sejam idênticas.

Da mesma forma, "not identified as equivalent" significa exatamente
isso: uma função equivalente não foi identificada na documentação
revisada nesta comparação. Isso **não deve ser interpretado como prova
de que nenhuma funcionalidade relacionada exista em qualquer parte do
software**.

------------------------------------------------------------------------

# 10. O que não é novidade no RI Compass

Os itens abaixo **não devem ser apresentados individualmente como
inovações metodológicas**.

## Retention-index calculation

Kovats e linear retention indices são métodos estabelecidos de GC e
implementados em múltiplos pacotes.

## EI spectral-library searching

É uma estratégia central de identificação por GC-MS, amplamente
implementada por NIST software, AMDIS, MZmine, MS-DIAL, GNPS-GC e
outros.

## Combinação de EI similarity com RI

Isso também já está estabelecido.

AMDIS/NIST, MZmine, workflows do MS-DIAL e GNPS-GC fornecem mecanismos
para utilizar retention information juntamente com spectral evidence.

## Molecular networking de GC--EI spectra

Isso não é novo.

GNPS-GC demonstrou molecular networking de deconvoluted EI spectra, e a
documentação atual do MZmine também descreve molecular networking para
GC/EI-MS pseudo-spectra.

## Cytoscape export

É útil, mas não é novidade.

## Mirror-spectrum visualization

Também é útil, mas comum.

------------------------------------------------------------------------

# 11. O que pode ser distintivo

A contribuição potencialmente distintiva do RI Compass está na
**combinação e organização explícita** de várias ideias em torno de
processed GC--EI data.

O candidato mais forte é:

> **Um framework interpretável de pós-processamento no qual
> retention-index evidence, EI spectral-library evidence e hierarchical
> rule-based EI fragmentation evidence são avaliadas como linhas
> distintas de evidência, comparadas quanto à concordância ou conflito e
> propagadas para visualizações relacionais e hierárquicas do chemical
> space.**

Essa distinção possui vários componentes.

## 11.1 Independent fragmentation evidence

O fragmentation engine não é simplesmente outro library score.

Uma feature pode possuir:

``` text
Library evidence
Retention evidence
Fragmentation-class evidence
```

e essas evidências podem discordar.

Essa discordância é preservada, e não escondida.

## 11.2 Parent chemical gates

Generic EI ions são comuns.

Por exemplo:

``` text
m/z 43
m/z 57
m/z 69
m/z 73
m/z 91
```

são quimicamente informativos, mas não exclusivamente diagnósticos.

O hierarchical engine pergunta, portanto, se a broad parent chemistry
possui suporte antes de promover uma leaf signature mais específica.

Conceitualmente:

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

Isso pretende reduzir a sobreinterpretação de diagnostic ions isolados.

## 11.3 Human-readable rules

O rule system foi desenhado para permanecer inspecionável.

O usuário pode examinar:

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

O objetivo não é apenas obter um label, mas compreender **por que esse
label foi proposto**.

## 11.4 Concordance em vez de uma black-box probability

Uma direção futura para o RI Compass é uma camada explícita de
**Evidence Concordance**.

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

Essa abordagem evita deliberadamente converter todas as evidências em
uma aparentemente precisa "identification probability".

Um `class score = 0.84`, por exemplo, **não** significa que um composto
tenha 84% de probabilidade de estar corretamente identificado.

------------------------------------------------------------------------

# 12. Por que a network vem depois da evidence integration

A network não deve ser interpretada como o principal annotation
algorithm.

Seu papel é organizar relacionalmente o dataset interpretado.

Um feature node pode conter:

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

Um EI similarity edge diz:

> Estes experimental spectra são semelhantes.

Ele não diz:

> Estas features são o mesmo composto.

Essa distinção é essencial para:

-   homologous series;
-   positional isomers;
-   terpene families;
-   related hydrocarbons;
-   coeluting/deconvoluted GC-MS features.

A network é, portanto, melhor descrita como:

> **evidence-enriched EI spectral network**

e não como identification network.

------------------------------------------------------------------------

# 13. Por que o Sunburst vem depois da fragmentation analysis

O Sunburst não é um library taxonomy plot.

Ele resume a chemical-class evidence produzida pelo hierarchical EI rule
engine.

Por exemplo:

``` text
All classified features
        ↓
Hydrocarbon
        ↓
Aliphatic hydrocarbon
        ↓
Alkane-like
```

ou:

``` text
All classified features
        ↓
Terpenoid
        ↓
Sesquiterpene
        ↓
Oxygenated-sesquiterpene-like
```

Usar `Best leaf only` permite que cada accepted feature contribua uma
única vez para o summary principal.

Usar `All supported classes` permite investigar overlapping EI
signatures.

Esses modos respondem a perguntas diferentes e não devem ser
confundidos.

------------------------------------------------------------------------

# 14. O que o RI Compass atualmente não reivindica

O RI Compass **não** reivindica:

-   substituir MZmine;
-   substituir MS-DIAL;
-   substituir AMDIS;
-   substituir NIST MS Search;
-   substituir authentic standards;
-   realizar chromatographic deconvolution superior;
-   fornecer definitive structural elucidation a partir de EI spectra;
-   calcular identification probability;
-   quantificar chemical classes a partir de feature counts;
-   provar que um library candidate está correto;
-   introduzir GC--EI molecular networking como um novo conceito.

Também não reivindica que o EI rule engine atual esteja universalmente
validado em todos os chemical spaces de GC-MS.

As fragmentation rules requerem avaliação continuada com:

-   positive-control datasets;
-   negative-control datasets;
-   authentic standards;
-   diferentes stationary phases;
-   diferentes instrument platforms;
-   derivatized e underivatized samples;
-   chemically diverse sample types.

------------------------------------------------------------------------

# 15. Limitação científica atual: validation

Esta provavelmente é a limitação mais importante do conceito atual do RI
Compass.

Uma regra quimicamente razoável não é automaticamente um validated
classifier.

Por exemplo, uma rule criada para:

``` text
FAME-like
TMS-like
Terpenoid-like
Styrenic-like
Alkane-like
```

deve ser desafiada com spectra de compostos que:

1.  realmente pertençam à target class;
2.  se pareçam com a target class, mas não pertençam a ela;
3.  contenham common interfering fragments;
4.  representem realistic GC-MS backgrounds;
5.  venham de independent datasets.

Portanto, o rule engine deve atualmente ser descrito como:

> **rule-based chemical-class screening**

e não como:

> **validated automated compound-class identification**

Essa distinção é cientificamente importante.

------------------------------------------------------------------------

# 16. Recommended validation strategy

Uma validation rigorosa pode utilizar múltiplos reference datasets.

## Positive controls

Known spectra de:

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

Exemplos devem incluir classes quimicamente confundíveis:

``` text
Alkanes vs alkenes
Alkylbenzenes vs styrenic compounds
Terpenes vs generic unsaturated hydrocarbons
TMS metabolites vs siloxane background
FAMEs vs long-chain hydrocarbons
Phenylpropanoids vs other substituted aromatics
```

## Metrics

Potential metrics incluem:

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

O objetivo não seria transformar o sistema em um black-box classifier,
mas quantificar onde as interpretable rules funcionam e onde falham.

------------------------------------------------------------------------

# 17. Nicho prático do RI Compass

O nicho prático mais claro é:

> **Pesquisadores que já possuem processed GC--EI data e desejam
> interrogar compound annotations usando retention behavior e
> interpretable fragmentation evidence sem retornar a um workflow
> completo de raw-data processing.**

Isso inclui datasets gerados por:

``` text
MZmine
MS-DIAL
AMDIS
vendor software
custom pipelines
```

Potential applications incluem:

-   pyrolysis oils;
-   essential oils;
-   volatile natural products;
-   environmental GC-MS;
-   FAME profiling;
-   derivatized metabolomics;
-   chemical fingerprinting;
-   exploratory characterization of complex mixtures.

------------------------------------------------------------------------

# 18. Relação com upstream software

O RI Compass deve ser visto como complementar a upstream processing
software.

## Exemplo: MZmine → RI Compass

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

O mesmo conceito pode ser aplicado ao MS-DIAL ou a outra preprocessing
platform.

Essa modularidade é intencional.

------------------------------------------------------------------------

# 19. Por que não fazer tudo dentro do processing software?

Essa é uma pergunta legítima.

Para muitas análises rotineiras, um pacote maduro como MZmine, MS-DIAL,
AMDIS/NIST ou o workflow histórico GNPS-GC pode já oferecer
funcionalidade suficiente.

O RI Compass torna-se útil quando a pergunta analítica é
especificamente:

> **Como os annotation candidates se comportam quando retention evidence
> e um modelo independente e interpretável de EI fragmentation class são
> examinados conjuntamente?**

Seu valor, portanto, depende de essa camada interpretativa adicional
melhorar:

-   expert review;
-   detecção de conflicting annotations;
-   class-level characterization;
-   transparency;
-   reproducibility;
-   communication of uncertainty.

Isso deve, em última análise, ser demonstrado empiricamente.

------------------------------------------------------------------------

# 20. Contribuição científica proposta

Uma descrição cautelosa do projeto seria:

> **RI Compass é um ambiente de pós-processamento para processed GC--EI
> data que integra experimental retention-index evaluation, EI
> spectral-library comparison e interpretable hierarchical rule-based
> fragmentation screening. Em vez de tratar esses resultados como
> identification scores intercambiáveis, o workflow os preserva como
> linhas complementares de evidência que podem convergir ou entrar em
> conflito. As evidências resultantes podem ser exploradas como uma EI
> spectral network, resumidas por meio de um hierarchical chemical-class
> Sunburst e exportadas em formato orientado a relatórios.**

Uma alegação mais forte deve ser feita apenas após systematic
benchmarking.

------------------------------------------------------------------------

# 21. O que deve ser testado antes de reivindicar methodological novelty

Antes de descrever o RI Compass em uma publicação como um novo
identification ou annotation framework, pelo menos quatro perguntas
devem ser respondidas.

### 1. O hierarchical fragmentation engine acrescenta informação além de library similarity?

Se o rule-based output apenas reproduzir o top library hit, seu valor
incremental será limitado.

### 2. O engine consegue detectar library candidates incorretos, porém espectralmente plausíveis?

Essa seria uma demonstração forte de complementary evidence.

### 3. O parent gating reduz false class assignments?

Isso testa diretamente uma das principais decisões de design.

### 4. Combinar RI, library e fragmentation evidence melhora annotation prioritization?

Isso deve ser avaliado sem transformar o resultado em uma probabilidade
injustificada.

Se essas perguntas forem respondidas positivamente, a contribuição
metodológica torna-se substancialmente mais forte.

------------------------------------------------------------------------

# 22. Conclusão

RI Compass atua em um campo com softwares estabelecidos e robustos.

MZmine, AMDIS/NIST, MS-DIAL e o workflow original GNPS-GC já cobrem
partes substanciais do processamento de GC-MS, retention-index
analysis, spectral-library matching e, em alguns casos, molecular
networking.

Essa sobreposição é real e deve ser reconhecida.

A contribuição pretendida do RI Compass, portanto, **não** é:

> mais um pacote de GC-MS preprocessing,

e também **não** é:

> a primeira combinação de Kovats RI, EI library search e molecular
> networking.

O projeto está concentrado em:

> **interpretação transparente pós-processamento de processed GC--EI
> data por meio da avaliação conjunta, porém explicitamente separada, de
> retention-index evidence, spectral-library evidence e hierarchical
> rule-based EI fragmentation evidence, seguida de evidence-enriched
> network e chemical-class visualization.**

Se essa abordagem oferece uma vantagem metodológica significativa, isso
deve ser estabelecido por validation e benchmarking.

Essa é uma posição científica mais forte do que reivindicar novidade
para componentes individuais que já existem.

------------------------------------------------------------------------

# References and software documentation

Os seguintes recursos são particularmente relevantes para o
posicionamento do RI Compass:

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

> **RI Compass deve acrescentar evidência, não esconder incerteza.**

O objetivo não é fazer GC-MS annotations parecerem mais certas do que
realmente são.

O objetivo é tornar as evidências que as sustentam mais fáceis de
inspecionar, questionar, organizar e comunicar.
