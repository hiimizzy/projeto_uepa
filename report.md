# Report



Verificar se as variáveis básicas de território, demanda e concorrência conseguem reproduzir as categorias de prioridade definidas pelo IP.



Identificar quais variáveis mais contribuem para a classificação das prioridades (via SHAP).



Detectar casos de discordância entre o IP e o modelo, sinalizando possíveis revisões metodológicas.



Servir como ferramenta de auditoria das decisões geradas pelo índice multicritério.



1. #### Validação do ML

Objetivo: Treinar o modelo metodológico e sem vazamento.



Modelo	                        Accuracy (CV)	 F1-macro (CV)

Random Forest – Modelo A	0,8464 ± 0,0445	 0,4964 ± 0,1044

Random Forest – Modelo B	0,7188 ± 0,1317	 0,4257 ± 0,1163

Logistic Regression – Modelo A	0,5797 ± 0,1885	 0,3840 ± 0,1338

Logistic Regression – Modelo B	0,6000 ± 0,2059	 0,4170 ± 0,1279

Dummy (baseline)	        0,8245 ± 0,0627	 0,3324 ± 0,0712

Obs: O Random Forest com Modelo A (4 features) apresentou o melhor desempenho.



#### 2\. SHAP

Importância global das variáveis:



Variável	        Mean |SHAP|

n\_ies\_presenciais	0,0486

n\_cursos\_concorrentes	0,0441

vagas\_regulares	0,0309

D4\_demanda\_municipal	0,0267

Obs:

SHAP mede contribuição, não causalidade.



Correlação positiva ≠ relação monotônica.



O modelo reproduz o IP, não descobre fatores causais de expansão.



#### 3.LIMITAÇÕES IDENTIFICADAS

Target circular — o ML tenta reproduzir um índice construído pelo próprio projeto.



Desbalanceamento extremo — 82,4% dos registros na classe "Alta".



Classes minoritárias ignoradas — "Baixa" e "Muito Alta" não foram previstas.



Features incompletas — 4 variáveis de um total de 5 dimensões do IP oficial.



Redundância entre features — n\_ies\_presenciais e n\_cursos\_concorrentes têm correlação ≈ 0,97.



Acurácia enganosa — 84,7% é puxada pela classe majoritária.



Ausência de causalidade — SHAP mede contribuição, não determinação.



#### 4\. Validação Final (Out-of-Fold)

Métrica	       Valor (OOF)

Accuracy	0,8470

F1-macro	0,3704

Cohen's Kappa	0,3619

F1-weighted	0,8035

#### 

Matriz de confusão (OOF):



Real \\ Predito	Alta	Baixa	Muito Alta	Média

Alta	        487	0       0               14

Baixa		1	0	0               10

Muito Alta	48	0	0	        0

Média		20	0	0                28

Obs: O modelo nunca previu "Baixa" nem "Muito Alta" — o desempenho está concentrado na classe majoritária.



#### 5\. CONCLUSÃO



O treinamento de Ml complementa: 

Verificar se as variáveis básicas de território, demanda e concorrência conseguem reproduzir as categorias de prioridade do IP. 

O Random Forest apresentou acurácia global de 84,7% nas previsões out-of-fold, porém o desempenho foi fortemente concentrado na classe majoritária ("Alta"), com recall igual a zero para as classes "Baixa" e "Muito Alta". 

A análise SHAP indicou que n\_ies\_presenciais, n\_cursos\_concorrentes, vagas\_regulares e D4\_demanda\_municipal são as variáveis com maior contribuição para as decisões do modelo, sem que isso implique causalidade. 

Conclui-se que o ML possui utilidade complementar para auditoria e convergência territorial, mas capacidade limitada para reproduzir todas as categorias do IP — especialmente as classes minoritárias, cuja baixa representatividade reduz a confiabilidade estatística.

