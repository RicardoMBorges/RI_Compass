# RI Compass --- EI Fragmentation Rules

## Guia técnico do `hierarchical relational engine v4`

> **Objetivo deste documento:** explicar de forma transparente como o RI
> Compass transforma um espectro EI já deconvoluído em evidência de
> classe química. Este documento descreve **as regras atualmente
> implementadas no software**. Elas são regras heurísticas de
> *screening* e **não devem ser interpretadas como regras universais de
> identificação estrutural**.

------------------------------------------------------------------------

# 1. O que o `EI fragmentation engine` faz

O RI Compass não tenta reconstruir automaticamente uma estrutura
molecular completa a partir de um espectro EI.

O objetivo é mais restrito:

> **procurar combinações de fragmentos, relações entre íons e contexto
> espectral compatíveis com determinadas classes químicas.**

Assim, o engine responde a perguntas como:

``` text
O espectro apresenta um padrão Alkane-like?
O espectro apresenta um padrão Styrenic-like?
Há evidência compatível com FAME?
Há evidência compatível com TMS derivative?
O padrão é mais consistente com terpene chemistry?
Há sinais de siloxane background?
```

O resultado é uma **structural/class signature**, e não uma
identificação inequívoca do composto.

------------------------------------------------------------------------

# 2. Princípio fundamental

Um único fragmento raramente é suficientemente específico.

Por exemplo:

``` text
m/z 43
m/z 55
m/z 57
m/z 69
m/z 73
m/z 91
```

podem ocorrer em numerosos compostos.

Por isso, o RI Compass não utiliza apenas a lógica:

``` text
m/z X presente → classe Y
```

O engine combina quatro níveis de evidência:

``` text
1. Ion evidence
2. Relational evidence
3. Parent chemical gate
4. Hierarchical assignment
```

O fluxo completo é:

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

# 3. Entrada espectral

O engine utiliza os espectros EI deconvoluídos fornecidos ao RI Compass,
normalmente em MGF.

Cada espectro é convertido em um perfil nominal.

## 3.1 `Nominal-ion tolerance`

Por padrão:

``` text
Nominal-ion tolerance = ±0.5 Da
```

Para cada massa inteira, o programa procura um peak dentro dessa janela.

Exemplo:

``` text
target = m/z 91

90.5 ≤ observed m/z ≤ 91.5
```

O peak mais intenso dentro da janela representa aquele nominal ion.

------------------------------------------------------------------------

# 4. Normalização da intensidade

Todas as intensidades são normalizadas pelo base peak:

``` text
relative intensity (%) =
100 × ion intensity / base-peak intensity
```

Portanto:

``` text
base peak = 100%
```

As fragmentation rules trabalham com **relative intensity**, não com
intensidade absoluta.

------------------------------------------------------------------------

# 5. `Minimum relative ion intensity`

O parâmetro:

``` text
Minimum relative ion intensity (%)
```

define a intensidade mínima para considerar um ion presente.

O default atual é:

``` text
5%
```

Assim, com o default:

``` text
I91 = 18% → presente
I91 = 3%  → ausente para a regra
```

Esse parâmetro influencia:

-   diagnostic ions;
-   supporting ions;
-   co-occurrence rules;
-   ratio rules;
-   parent-mass evidence;
-   neutral-loss evidence;
-   parent gates.

------------------------------------------------------------------------

# 6. Tipos de evidência usados nas `leaf rules`

Cada `class_signature` pode utilizar diferentes componentes.

## 6.1 `Diagnostic ions`

São os íons de maior peso dentro da regra.

Exemplo simplificado:

``` text
Alkane-like

m/z 57 → diagnostic
m/z 71 → diagnostic
```

A presença desses íons contribui mais fortemente para o `ion_score`.

------------------------------------------------------------------------

## 6.2 `Supporting ions`

São fragmentos compatíveis com a classe, mas menos específicos.

Exemplo:

``` text
Alkane-like

m/z 43
m/z 85
m/z 99
m/z 113
```

Eles aumentam a evidência quando acompanham os diagnostic ions.

------------------------------------------------------------------------

## 6.3 `Conflicting ions`

Algumas regras contêm íons cuja presença intensa reduz a confiança
naquela interpretação.

Exemplo:

``` text
Alkane-like

conflicting:
m/z 91
m/z 104
```

Esses íons não tornam a classe impossível.

Eles apenas penalizam o `ion_score` quando aparecem com intensidade
suficientemente alta.

Atualmente, um conflicting ion só é penalizado quando:

``` text
relative intensity ≥ max(20%, Minimum relative ion intensity)
```

------------------------------------------------------------------------

## 6.4 `Ion series`

Algumas classes apresentam séries homólogas úteis.

Exemplo:

``` text
Alkane-like:
43 → 57 → 71 → 85 → 99 → 113

Δm = 14
```

e:

``` text
Alkene-like:
41 → 55 → 69 → 83 → 97 → 111

Δm = 14
```

Se pelo menos três membros da série estiverem presentes, o engine
adiciona um `pattern_bonus`.

Esse bônus é limitado a:

``` text
maximum = 0.20
```

------------------------------------------------------------------------

# 7. Como o `ion_score` é calculado

Para cada diagnostic ion:

``` text
contribution =
weight × min(1, relative_intensity / 30)
```

Para cada supporting ion:

``` text
contribution =
weight × min(1, relative_intensity / 20)
```

Isso significa que diagnostic ions atingem sua contribuição máxima
quando chegam a aproximadamente 30% de relative intensity, enquanto
supporting ions saturam em aproximadamente 20%.

O componente básico é:

``` text
positive evidence / maximum possible positive evidence
```

Depois são adicionados ou subtraídos:

``` text
+ pattern_bonus
− 0.15 × conflict_penalty
```

O resultado é limitado ao intervalo:

``` text
0 ≤ ion_score ≤ 1
```

------------------------------------------------------------------------

# 8. `Relational evidence`

A simples presença dos ions não é suficiente para várias classes.

Por isso, o RI Compass utiliza regras relacionais.

Elas podem ser de quatro tipos principais.

## 8.1 `Co-occurrence`

Exige que vários ions ocorram simultaneamente.

Exemplo:

``` text
Alkane-like:
43 + 57 + 71
```

Todos precisam superar o `Minimum relative ion intensity`.

------------------------------------------------------------------------

## 8.2 `Ion ratios`

Compara intensidades relativas.

Exemplo:

``` text
Alkane-like:
I57 > 1.5 × I91
```

ou:

``` text
Alkylbenzene-like:
I91 > I57
I91 > I77
```

------------------------------------------------------------------------

## 8.3 `Parent-mass context`

Algumas regras procuram um ion compatível com uma massa molecular
plausível.

Exemplo:

``` text
Monoterpene-hydrocarbon-like:
m/z 136
```

ou:

``` text
Sesquiterpene-hydrocarbon-like:
m/z 204
```

Isso é apenas **supportive molecular-ion context**.

O programa não assume automaticamente que um peak de alta massa seja o
molecular ion.

------------------------------------------------------------------------

## 8.4 `Neutral-loss context`

Algumas regras procuram pares de ions separados por uma neutral loss.

Exemplo:

``` text
M − 18
```

para um padrão de dehydration-like fragmentation.

O engine procura esse padrão somente dentro de uma faixa de parent
masses considerada plausível para a regra.

Isso continua sendo evidência contextual, não prova mecanística.

------------------------------------------------------------------------

# 9. Como o `relational_score` é calculado

Cada relational rule recebe um peso.

O programa soma:

``` text
points obtained
```

e divide por:

``` text
maximum possible relational points
```

produzindo:

``` text
0 ≤ relational_score ≤ 1
```

------------------------------------------------------------------------

# 10. Como o `raw_score` é calculado

Quando uma classe possui `relational rules`:

``` text
raw_score =
0.72 × ion_score
+
0.28 × relational_score
```

Portanto:

``` text
72% → ion evidence
28% → relational evidence
```

A presença dos fragmentos continua sendo o componente principal.

As relações entre eles refinam a interpretação.

Se uma classe não possuir relational rule:

``` text
raw_score = ion_score
```

Importante:

> `raw_score` representa a evidência da leaf rule **antes** da avaliação
> do `parent gate`.

------------------------------------------------------------------------

# 11. Por que existem `Parent chemical gates`

Uma das maiores fontes de falsos positivos em interpretação EI é a
reutilização dos mesmos ions por diferentes classes.

Exemplo:

``` text
41 / 55 / 69
```

podem ocorrer em:

-   alkenes;
-   unsaturated FAMEs;
-   terpenes;
-   diversos outros hydrocarbons.

Da mesma forma:

``` text
73 / 147
```

podem representar:

-   TMS derivatives;
-   siloxane background.

Por isso, o engine v4 utiliza uma classificação em duas etapas:

``` text
Leaf evidence
      +
Parent chemistry evidence
      ↓
Final class evidence
```

Uma leaf só recebe `final score` quando o seu `parent gate` passa.

O default atual é:

``` text
Parent gate threshold = 0.45
```

------------------------------------------------------------------------

# 12. `Hydrocarbon gate`

O gate avalia os ions:

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

O programa calcula a fração desses oito ions que está presente.

Se pelo menos:

``` text
3 de 8
```

estiverem presentes, o gate aumenta fortemente.

Em termos implementados:

``` text
alkyl_fraction = number_present / 8
```

Se:

``` text
alkyl_fraction ≥ 0.375
```

então:

``` text
Hydrocarbon gate =
min(1, 0.35 + 0.9 × alkyl_fraction)
```

Caso contrário:

``` text
Hydrocarbon gate =
0.25 × alkyl_fraction
```

Esse gate controla atualmente:

``` text
Alkane-like
Alkene-like
```

------------------------------------------------------------------------

# 13. `Aromatic gate`

O gate procura:

``` text
65
77
91
103
104
105
```

A presença de `m/z 77` e `m/z 91` recebe peso adicional.

Também existe um bônus se aparecer pelo menos uma das massas:

``` text
128
152
178
202
228
```

que podem fornecer contexto para aromatic molecular-ion regions /
PAH-like chemistry.

Esse gate controla:

``` text
Alkylbenzene-like
Styrenic-like
PAH-like
Phenolic-like
Phenylpropanoid-like
```

------------------------------------------------------------------------

# 14. `FAME gate`

O gate FAME é deliberadamente mais restritivo.

Pontuação atual:

``` text
m/z 74 present      → +0.45
m/z 87 present      → +0.25
74 AND 87 present   → +0.20
101/115/129/143     → +0.10 if any is present
```

Se houver forte evidência TMS:

``` text
m/z 73 ≥ 20%
AND
m/z 147 ≥ 15%
```

o gate FAME é penalizado:

``` text
FAME gate × 0.55
```

O gate controla:

``` text
Saturated-FAME-like
Unsaturated-FAME-like
PUFA-FAME-like
```

Isso é importante porque ions de unsaturation isolados não devem
transformar automaticamente um hydrocarbon spectrum em FAME.

------------------------------------------------------------------------

# 15. `TMS derivative gate`

Pontuação atual:

``` text
m/z 73 present      → +0.45
m/z 147 present     → +0.35
73 AND 147 present  → +0.20
```

Porém, uma série compatível com siloxane background penaliza o gate.

Se houver:

``` text
m/z 207
OR
m/z 281
OR
m/z 355
```

com relative intensity ≥ 10%:

``` text
TMS gate × 0.55
```

O gate controla:

``` text
TMS-derivative-like
TMS-organic-acid-like
TMS-fatty-acid-like
TMS-amino-acid-like
TMS-sugar-polyol-like
```

------------------------------------------------------------------------

# 16. `Terpenoid gate`

O gate procura um conjunto de terpene-associated ions:

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

Cada ion presente adiciona evidência.

O componente básico é:

``` text
min(0.65, number_present × 0.075)
```

Há suporte adicional para:

``` text
m/z 136 → +0.25
m/z 204 → +0.30
```

e:

``` text
m/z 93
+
(m/z 121 OR m/z 161)
→ +0.15
```

O gate controla:

``` text
Monoterpene-hydrocarbon-like
Monoterpene-alcohol-like
Monoterpene-carbonyl-like
Sesquiterpene-hydrocarbon-like
Oxygenated-sesquiterpene-like
```

O objetivo é evitar classificar generic unsaturated hydrocarbon spectra
como terpenes apenas pela presença de alguns fragmentos comuns.

------------------------------------------------------------------------

# 17. `Oxygenated gate`

O gate procura:

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

Cada ion presente contribui:

``` text
0.25
```

até o máximo de:

``` text
1.0
```

Atualmente esse gate controla:

``` text
Carbonyl-like
```

Ele é intencionalmente amplo e deve ser interpretado como um screen de
oxygenated chemistry, não como identificação específica de aldehyde ou
ketone.

------------------------------------------------------------------------

# 18. `Background / QC gate`

O background gate procura duas situações.

## Siloxane context

``` text
73 + 147 + (207 OR 281)
```

produz forte evidência de `Background / QC`.

## Phthalate context

``` text
m/z 149 ≥ 20%
```

produz:

``` text
Background gate = 0.75
```

As classes associadas são:

``` text
Siloxane-background-like
Phthalate-like
```

No código atual, `Background / QC` é permitido independentemente do
`Parent gate threshold`, para funcionar como flag de QC/background.

------------------------------------------------------------------------

# 19. Como o `final score` é calculado

Quando:

``` text
gate_score ≥ Parent gate threshold
```

a leaf passa pelo gate.

O `final score` é:

``` text
final_score =
raw_score × (0.55 + 0.45 × gate_score)
```

Portanto, mesmo quando o gate passa, ele modula a evidência.

Exemplo:

``` text
raw_score = 0.90
gate_score = 0.60

final_score =
0.90 × (0.55 + 0.45 × 0.60)

final_score =
0.90 × 0.82

final_score = 0.738
```

A interpretação passa então de uma raw signature muito forte para:

``` text
probable
```

porque o suporte à parent chemistry é apenas moderado.

Se o gate falhar:

``` text
final_score = 0
```

O `raw_score` continua armazenado para inspeção.

------------------------------------------------------------------------

# 20. Faixas de interpretação

O RI Compass utiliza atualmente:

    `final score` `evidence`
  --------------- ---------------
         `< 0.30` `weak / none`
      `0.30–0.59` `possible`
      `0.60–0.79` `probable`
         `≥ 0.80` `strong`

Esses intervalos são **categorias heurísticas de screening**.

Eles não representam probabilidades estatísticas.

Assim:

``` text
score = 0.84
```

significa:

``` text
strong rule-based class evidence
```

e **não**:

``` text
84% probability of correct identification
```

------------------------------------------------------------------------

# 21. Regras implementadas --- Hydrocarbons and aromatics

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

**Diagnostic**

``` text
41 (3.0)
55 (3.0)
69 (2.0)
```

**Support**

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

**Conflict**

``` text
91 (0.4)
```

**Relations**

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

**Diagnostic**

``` text
91 (5.0)
```

**Support**

``` text
77  (2.0)
65  (1.0)
105 (1.0)
119 (0.8)
```

**Conflict**

``` text
73  (0.8)
147 (0.8)
```

**Relations**

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

**Diagnostic**

``` text
104 (5.0)
77  (2.0)
```

**Support**

``` text
51  (1.2)
78  (1.5)
103 (0.7)
```

**Conflict**

``` text
73  (0.8)
147 (0.8)
```

**Relations**

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

**Diagnostic**

``` text
94 (4.0)
```

**Support**

``` text
65  (1.5)
66  (0.8)
77  (1.0)
107 (1.0)
108 (1.0)
```

**Relations**

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

cada uma com weight `2.5`.

**Support**

``` text
77  (0.8)
89  (0.5)
101 (0.5)
```

**Interpretation**

Screen para stable aromatic molecular-ion patterns associados a
condensed aromatic chemistry.

> As massas não são exclusivas de PAHs e não identificam um PAH
> específico.

------------------------------------------------------------------------

## `Carbonyl-like`

**Hierarchy**

``` text
Oxygenated
└── Carbonyl
    └── Carbonyl-like
```

**Diagnostic**

``` text
43 (2.0)
44 (2.0)
58 (2.0)
60 (2.5)
```

**Support**

``` text
29 (0.8)
31 (0.8)
71 (0.5)
```

**Interpretation**

Broad carbonyl/oxygenated screening rule. Requer confirmação adicional
para subclass assignment.

------------------------------------------------------------------------

# 22. Essential-oil / terpenoid rules

## `Monoterpene-hydrocarbon-like`

**Diagnostic**

``` text
93  (3.0)
136 (2.0)
```

**Support**

``` text
41, 53, 67, 69, 79, 81, 91, 105, 121
```

**Relations**

``` text
69 + 93 + 121
m/z 136 as plausible C10H16 molecular-ion context
```

**Interpretation**

C10 terpene-hydrocarbon-like EI signature.

RI e library evidence continuam essenciais para isomer discrimination.

------------------------------------------------------------------------

## `Monoterpene-alcohol-like`

**Diagnostic**

``` text
71 (1.5)
93 (2.0)
95 (2.0)
```

**Support**

``` text
41, 55, 67, 69, 81, 121
```

**Relations**

``` text
69 + 93 + 95
M − 18 dehydration-like
plausible parent range = 136–172
```

**Interpretation**

Oxygenated monoterpene/alcohol-like screen.

A neutral loss de 18 Da só é contextual e não demonstra automaticamente
perda de água de um molecular ion confirmado.

------------------------------------------------------------------------

## `Monoterpene-carbonyl-like`

**Diagnostic**

``` text
81  (2.0)
95  (2.0)
110 (1.2)
112 (1.2)
```

**Support**

``` text
41, 55, 69, 84, 94
```

**Relation**

``` text
81 + 95
plausible parent range = 148–170
```

**Interpretation**

Broad monoterpene aldehyde/ketone-like screen.

------------------------------------------------------------------------

## `Phenylpropanoid-like`

**Diagnostic**

``` text
77  (1.8)
91  (1.5)
103 (1.2)
107 (1.2)
```

**Support**

``` text
105, 121, 131, 135, 149, 164
```

**Relations**

``` text
77 + 103
77 + 107
```

**Interpretation**

Intentionally broad phenylpropanoid/benzenoid-like aromatic signature.

------------------------------------------------------------------------

## `Sesquiterpene-hydrocarbon-like`

**Diagnostic**

``` text
93  (2.0)
161 (2.0)
204 (1.8)
```

**Support**

``` text
41, 55, 67, 69, 79, 81, 91,
105, 119, 133, 147, 189
```

**Relations**

``` text
93 + 161
m/z 204 as plausible C15H24 molecular-ion context
```

**Interpretation**

C15 terpene-hydrocarbon-like signature.

------------------------------------------------------------------------

## `Oxygenated-sesquiterpene-like`

**Diagnostic**

``` text
93  (1.5)
161 (1.5)
189 (1.2)
```

**Support**

``` text
41, 55, 69, 81, 105, 119, 133, 147
```

**Relation**

``` text
M − 18 dehydration-like
plausible parent range = 204–240
```

**Interpretation**

Broad oxygenated C15-terpenoid-like screen intended for prioritization.

------------------------------------------------------------------------

# 23. FAME rules

## `Saturated-FAME-like`

**Diagnostic**

``` text
74 (4.0)
87 (2.5)
```

**Support**

``` text
43, 55, 57, 69, 75, 101, 143
```

**Relations**

``` text
74 + 87
I74 > I73
```

A regra também registra a expectativa de homologous parent step:

``` text
Δ14
```

**Interpretation**

Saturated fatty-acid methyl-ester-like signature.

`m/z 74` é usado como classic McLafferty-type evidence.

------------------------------------------------------------------------

## `Unsaturated-FAME-like`

**Diagnostic**

``` text
55 (2.5)
69 (2.0)
74 (1.5)
```

**Support**

``` text
41, 67, 79, 81, 83, 87, 97
```

**Relations**

``` text
55 + 69 + 74
I55 > I57
```

**Interpretation**

Unsaturated FAME-like fragmentation.

A regra não resolve double-bond position ou geometric isomerism.

------------------------------------------------------------------------

## `PUFA-FAME-like`

**Diagnostic**

``` text
67 (2.5)
79 (2.5)
81 (2.0)
```

**Support**

``` text
41, 55, 69, 91, 93, 95, 105
```

**Relations**

``` text
67 + 79 + 81
I79 > 0.5 × I74
```

**Interpretation**

Polyunsaturated-FAME-like fragmentation.

Requer suporte adicional de RI/library/molecular-ion context.

------------------------------------------------------------------------

# 24. TMS rules

## `TMS-derivative-like`

**Diagnostic**

``` text
73  (4.0)
147 (3.0)
```

**Support**

``` text
45, 75, 133, 149
```

**Relations**

``` text
73 + 147
M − 15 methyl-loss-like
```

**Interpretation**

Generic trimethylsilyl-derivative signature.

> `73 + 147` também pode ocorrer em silicone/siloxane background. O
> contexto de QC é obrigatório.

------------------------------------------------------------------------

## `TMS-organic-acid-like`

**Diagnostic**

``` text
73  (3.0)
147 (2.0)
```

**Support**

``` text
117, 133, 189, 191
```

**Relations**

``` text
73 + 117 + 147
```

**Conflict**

``` text
207
281
```

**Interpretation**

Broad TMS-derivatized organic-acid-like screen.

------------------------------------------------------------------------

## `TMS-fatty-acid-like`

**Diagnostic**

``` text
73  (2.5)
117 (3.0)
```

**Support**

``` text
75, 129, 145
```

**Relation**

``` text
73 + 117
```

**Conflict**

``` text
207
281
```

**Interpretation**

Fatty-acid TMS-ester-like screen.

Deve ser distinguido de FAME chemistry e silicone background.

------------------------------------------------------------------------

## `TMS-amino-acid-like`

**Diagnostic**

``` text
73  (2.5)
147 (1.8)
```

**Support**

``` text
100, 116, 174, 218, 246
```

**Relation**

``` text
73 + 147 + 174
```

**Conflict**

``` text
207
281
```

**Interpretation**

Broad TMS-amino-acid-like screen.

------------------------------------------------------------------------

## `TMS-sugar-polyol-like`

**Diagnostic**

``` text
73  (2.5)
147 (2.0)
204 (2.0)
217 (2.0)
```

**Support**

``` text
103, 129, 191, 319
```

**Relations**

``` text
73 + 147 + 204 + 217
I204 > 0.5 × I207
```

**Conflict**

``` text
207
281
```

**Interpretation**

Highly silylated carbohydrate/polyol-like signature.

Derivatization state pode alterar fortemente o EI spectrum.

------------------------------------------------------------------------

# 25. Background / QC rules

## `Siloxane-background-like`

**Diagnostic**

``` text
73  (3.0)
147 (4.0)
```

**Support**

``` text
207 (2.5)
221 (1.0)
281 (2.5)
355 (1.0)
```

**Relations**

``` text
73 + 147 + 207
OR
73 + 147 + 281

I147 > I117
```

**Interpretation**

Siloxane/background pattern.

Pode indicar:

-   column bleed;
-   septum/silicone contamination;
-   background;
-   derivatization-related silicone contamination.

Deve ser avaliado contra blanks.

------------------------------------------------------------------------

## `Phthalate-like`

**Diagnostic**

``` text
149 (5.0)
```

**Support**

``` text
167
279
293
```

**Relation**

``` text
149 + 167
```

**Interpretation**

Phthalate/plasticizer-like screening flag.

Confirmação deve considerar library match, RI e blanks.

------------------------------------------------------------------------

# 26. Hierarquia atualmente implementada

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

Uma mesma feature pode sustentar mais de uma fragmentation signature.

Exemplo:

``` text
Alkene-like                    0.88
Monoterpene-hydrocarbon-like   0.66
Unsaturated-FAME-like          0.31
```

O RI Compass preserva todas as scores.

Entretanto, `Best leaf only` seleciona:

``` text
highest final score
```

para fornecer uma classificação conservadora única.

Nesse exemplo:

``` text
best_leaf_class = Alkene-like
best_leaf_score = 0.88
```

Isso é especialmente importante no Sunburst para evitar double counting.

------------------------------------------------------------------------

# 28. `All supported classes`

No modo:

``` text
All supported classes
```

todas as signatures que:

``` text
passam o parent gate
AND
score ≥ selected threshold
```

podem ser visualizadas.

Esse modo é útil para estudar:

-   ambiguous spectra;
-   overlapping fragmentation patterns;
-   class competition;
-   regras excessivamente permissivas;
-   features que exigem revisão manual.

Ele não deve ser confundido com uma composição química quantitativa.

------------------------------------------------------------------------

# 29. Como interpretar um resultado completo

Exemplo hipotético:

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

A interpretação correta é:

> O EI spectrum apresenta forte evidência rule-based compatível com uma
> `Styrenic-like` fragmentation signature e também satisfaz o
> `Aromatic parent gate`.

A interpretação **incorreta** seria:

> O composto foi identificado como styrene com 87.9% de confiança.

Para chegar a uma compound annotation mais forte, ainda devem ser
avaliados:

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

# 30. O que os fragmentation rules acrescentam ao library search

O `EI library search` pergunta:

``` text
Qual reference spectrum mais se parece com o experimental spectrum?
```

O `fragmentation engine` pergunta:

``` text
Quais structural/class fragmentation patterns são sustentados pelo experimental spectrum?
```

São perguntas relacionadas, mas não idênticas.

Exemplo:

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

Aqui existe **convergent evidence**.

Mas:

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

é um caso de:

``` text
structural/class conflict
```

e merece revisão.

Esse é um dos usos mais importantes do fragmentation engine.

------------------------------------------------------------------------

# 31. O que os fragmentation rules NÃO fazem

As regras atuais não:

-   identificam inequivocamente um composto;
-   substituem EI reference libraries;
-   substituem experimental RI;
-   substituem authentic standards;
-   determinam molecular formula;
-   distinguem necessariamente positional isomers;
-   distinguem necessariamente stereoisomers;
-   resolvem coelution;
-   corrigem uma deconvolution ruim;
-   transformam feature counts em concentração;
-   fornecem identification probabilities;
-   demonstram mecanismos de fragmentação;
-   garantem que um peak de alta massa seja o molecular ion.

------------------------------------------------------------------------

# 32. Limitação científica mais importante

As regras são **heurísticas implementadas no RI Compass**.

Elas foram construídas para capturar padrões químicos plausíveis e
reduzir interpretações baseadas em ions isolados, mas ainda precisam de
benchmarking sistemático.

Portanto, neste estágio, a nomenclatura recomendada é:

``` text
rule-based EI structural-signature screening
```

ou:

``` text
rule-based EI chemical-class screening
```

e não:

``` text
automated EI compound identification
```

------------------------------------------------------------------------

# 33. Como as regras devem ser validadas

Cada leaf class deve ser testada contra:

``` text
Positive controls
+
Hard negative controls
+
Independent datasets
```

Exemplo:

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

Para `TMS derivative`:

``` text
true TMS metabolites
+
siloxane background
+
underivatized metabolites
```

Para FAME:

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

# 34. Métricas recomendadas para benchmarking

Para cada class signature:

``` text
Sensitivity
Specificity
Precision
Recall
F1 score
False-positive rate
False-negative rate
```

Também são particularmente importantes para o RI Compass:

``` text
Parent-gate rejection rate
Class overlap
Best-leaf accuracy
Confusion between related classes
Incremental value beyond EI library search
```

A pergunta principal não é apenas:

> A rule reconhece sua própria classe?

Mas também:

> **Ela rejeita classes quimicamente semelhantes que compartilham os
> mesmos fragmentos?**

------------------------------------------------------------------------

# 35. Parâmetros default atuais

``` text
Minimum relative ion intensity = 5%
Nominal-ion tolerance          = ±0.5 Da
Parent gate threshold          = 0.45
```

Para visualização conservadora no Sunburst:

``` text
Minimum final score = 0.60
Assignment          = Best leaf only
```

Esses valores são defaults operacionais e ainda devem ser avaliados
durante benchmarking.

------------------------------------------------------------------------

# 36. Campos importantes no output

  -----------------------------------------------------------------------
  Campo                               Significado
  ----------------------------------- -----------------------------------
  `feature_id`                        Identificador da feature

  `query_rt_min`                      Retention time

  `superclass`                        Parent chemical superclass

  `class_group`                       Nível intermediário

  `class_signature`                   Leaf rule avaliada

  `ion_score`                         Evidência baseada em ion
                                      presence/intensity

  `relational_score`                  Evidência baseada em relações entre
                                      ions

  `raw_score`                         Leaf evidence antes do parent gate

  `gate_score`                        Evidência da parent chemistry

  `gate_pass`                         Indica se a leaf pode ser promovida

  `score`                             Gate-adjusted final score

  `evidence`                          `weak / none`, `possible`,
                                      `probable`, `strong`

  `diagnostic_ions`                   Diagnostic ions encontrados

  `supporting_ions`                   Supporting ions encontrados

  `relational_evidence`               Co-occurrence/ratio/parent/loss
                                      rules satisfeitas

  `conflicting_ions`                  Conflict ions encontrados

  `best_leaf_class`                   Maior final score da feature

  `best_leaf_score`                   Score dessa classificação
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# 37. Princípio de interpretação

A lógica do RI Compass pode ser resumida assim:

``` text
One ion is a clue.
A pattern is evidence.
A parent gate adds chemical context.
RI adds chromatographic evidence.
A library match adds reference-spectrum evidence.
Agreement strengthens an annotation.
Disagreement is information.
```

Ou, em português:

> **Um fragmento é uma pista. Um padrão de fragmentação é evidência. O
> `parent gate` acrescenta contexto químico. O RI acrescenta evidência
> cromatográfica. O library match acrescenta evidência espectral de
> referência. A concordância fortalece uma anotação; o conflito indica
> que ela deve ser revisada.**

------------------------------------------------------------------------

# 38. Regra de ouro

> **`fragmentation score` não é `identification confidence`.**

O `EI fragmentation engine` deve ser utilizado como uma camada
independente de evidência para:

-   priorizar;
-   revisar;
-   questionar;
-   organizar;
-   e contextualizar annotations.

Ele foi deliberadamente construído para **acrescentar evidência sem
esconder incerteza**.
