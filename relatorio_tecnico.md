# Relatório Técnico — SCIC Aurora Siger

## 1. Resumo executivo

O Sistema de Comunicação Interplanetária da Colônia (SCIC) é um protótipo em Python para apoiar o gerenciamento da comunicação da Aurora Siger. A solução transforma registros de telemetria simulados em indicadores compreensíveis, identifica desvios de latência, estima o próximo comportamento por média móvel, organiza alertas por criticidade e permite localizar módulos por prefixo.

A implementação atende aos requisitos funcionais com uma solução simples, executável e sem bibliotecas externas. O uso da biblioteca padrão reduz a complexidade de instalação e facilita a reprodução pelo avaliador.

## 2. Contexto da solução

Uma colônia interplanetária depende de enlaces de comunicação para coordenar sensores, antenas e repetidores. A latência elevada pode atrasar comandos, enquanto a perda de pacotes pode comprometer a confiabilidade da telemetria. O SCIC oferece uma camada inicial de análise para identificar quais módulos merecem atenção primeiro.

O sistema não substitui um centro real de supervisão. Ele simula o fluxo de coleta, análise e priorização usando dados estruturados em CSV. Essa escolha mantém o projeto compatível com o nível da atividade e permite demonstrar as decisões técnicas em um terminal.

## 3. Dados utilizados

A base `dados_aurora_siger.csv` possui dez registros simulados. Cada registro representa uma medição de um módulo de comunicação ou de sensoriamento.

| Campo | Descrição |
|---|---|
| `timestamp` | Data e hora da medição. |
| `modulo` | Código do módulo monitorado. |
| `dispositivo` | Nome funcional do dispositivo. |
| `latencia_real_ms` | Latência observada em milissegundos. |
| `latencia_prevista_ms` | Latência estimada pelo modelo de referência. |
| `pacotes_enviados` e `pacotes_perdidos` | Quantidades usadas para calcular a perda. |
| `tensao_v` e `corrente_a` | Grandezas elétricas usadas para estimar potência. |
| `status` | Classificação operacional do registro. |

A fórmula da perda de pacotes é `pacotes_perdidos / pacotes_enviados × 100`. A disponibilidade aproximada é calculada como `100 − perda média`.

## 4. Indicadores de comunicação e operação

O código calcula latência média, perda média de pacotes, disponibilidade aproximada, tensão média e potência média. A potência é obtida pela relação elétrica básica `P = V × I`, em que `P` é a potência em watts, `V` é a tensão em volts e `I` é a corrente em ampères.

Na execução da base fornecida, a latência média é de aproximadamente **161,5 ms**, a perda média é de **0,84%**, a disponibilidade aproximada é de **99,16%** e a potência média é de **35,88 W**. Esses resultados sugerem uma operação geral estável, mas com alguns módulos que exigem investigação.

## 5. Erros numéricos

Para cada registro, o erro absoluto é calculado por:

`erro absoluto = |latência real − latência prevista|`.

O erro relativo é calculado por:

`erro relativo = erro absoluto / latência real × 100`.

O erro absoluto informa o desvio na mesma unidade da latência. O erro relativo facilita a comparação entre observações com escalas diferentes. Na execução da base, o erro absoluto médio é de aproximadamente **26,0 ms** e o erro relativo médio é de aproximadamente **13,16%**.

## 6. Modelo simples de previsão

O modelo utilizado é uma média móvel das três últimas latências observadas. Essa técnica é transparente e adequada para uma demonstração introdutória: ela suaviza oscilações recentes sem exigir treinamento de uma rede neural ou integração externa.

A previsão é recalculada com os últimos registros disponíveis. O método tem limitações. Ele não representa sazonalidade, mudanças de rota ou falhas repentinas. Em uma evolução futura, seria possível incluir janela adaptativa, regressão linear e variáveis como horário, carga e estado do enlace.

## 7. Métricas de avaliação

O sistema calcula quatro métricas de performance.

| Métrica | Interpretação |
|---|---|
| MAE | Média dos erros absolutos; indica o desvio médio em milissegundos. |
| MSE | Média dos erros elevados ao quadrado; penaliza desvios grandes. |
| RMSE | Raiz do MSE; retorna à unidade de milissegundos e mantém penalização de outliers. |
| R² | Mede quanto da variação observada é explicada pelas previsões; quanto mais próximo de 1, melhor. |

Para a base simulada, os valores aproximados são **MAE = 26,0 ms**, **MSE = 1.385,0 ms²**, **RMSE = 37,22 ms** e **R² = 0,41**. O RMSE superior ao MAE mostra que alguns desvios maiores influenciam a avaliação. O R² moderado indica que a média móvel é útil como referência inicial, mas ainda não explica toda a variação das latências.

## 8. Priorização de alertas com heap

Alertas são criados quando a latência ultrapassa 180 ms ou quando a perda de pacotes é igual ou superior a 2%. A severidade usada no protótipo combina o erro de latência com a perda:

`severidade = erro absoluto + 5 × perda percentual`.

A fila de prioridade é implementada com `heapq`. Como a biblioteca padrão implementa um min-heap, o código armazena a severidade negativa para que o alerta mais grave seja apresentado primeiro. Essa estrutura permite inserir e remover prioridades de forma eficiente e torna explícita a regra de decisão.

## 9. Busca de registros com trie

A classe `Trie` armazena os códigos dos módulos e os nomes dos dispositivos caractere a caractere. Ao consultar um prefixo, o sistema percorre apenas o caminho correspondente e coleta as palavras descendentes. Exemplos demonstrados no modo `--demo` incluem os prefixos `com`, `sens` e `prop`.

A trie é apropriada quando o operador precisa localizar rapidamente famílias de módulos, como todas as antenas de comunicação ou todos os sensores. A busca não depende de uma comparação completa com cada palavra em cada consulta.

## 10. Dispositivos, bases numéricas e eletricidade

Os dispositivos representam entradas e saídas do sistema. Sensores produzem medições; antenas e repetidores participam do envio e da retransmissão; o terminal exibe a saída analítica para o operador. Os estados poderiam ser transmitidos em bits ou flags binárias, enquanto os relatórios são apresentados em base decimal para facilitar a leitura humana.

A relação elétrica é demonstrada com tensão, corrente e potência. O protótipo não controla hardware real, mas calcula a potência estimada de cada módulo e a média da operação. Esse indicador ajuda a relacionar a qualidade da comunicação com o consumo dos dispositivos.

## 11. Gerenciamento inteligente da comunicação

O SCIC apoia decisões em três níveis. Primeiro, resume a operação com indicadores. Segundo, mede o erro do modelo e evita interpretar uma previsão sem avaliar sua qualidade. Terceiro, ordena os alertas para que o operador investigue primeiro os eventos com maior impacto potencial.

A inteligência do protótipo é baseada em regras explicáveis. Isso é adequado para uma primeira versão, pois o operador consegue entender por que um alerta foi priorizado. Uma versão avançada poderia incorporar histórico maior, limiares dinâmicos, detecção de anomalias e previsão por regressão.

## 12. Reflexão social, cultural e sustentável

Uma comunicação confiável favorece a segurança coletiva, a coordenação de atividades e o acesso equilibrado às informações da colônia. O sistema deve evitar que decisões automatizadas ocultem a necessidade de supervisão humana. Os critérios de alerta precisam ser documentados para que equipes diferentes possam auditá-los.

Do ponto de vista cultural, a interface deve usar mensagens claras e permitir que operadores com diferentes níveis de experiência compreendam os resultados. Do ponto de vista sustentável, monitorar potência e perda de pacotes ajuda a evitar retransmissões desnecessárias e consumo excessivo de energia.

## 13. Limitações e melhorias

A base é simulada e pequena. Portanto, os indicadores não representam uma rede real. O modelo de média móvel não identifica causas de falha. A disponibilidade é uma aproximação baseada apenas na perda de pacotes. A trie foi usada para demonstrar busca por prefixo, mas não substitui um banco de dados em uma aplicação de grande escala.

Como melhorias, podem ser adicionados persistência de alertas, gráficos históricos, testes automatizados, validação de dados, limiares configuráveis, autenticação de operadores e uma interface visual. Também é possível comparar modelos de média móvel e regressão linear usando validação temporal.

## 14. Roteiro sugerido para o vídeo de até cinco minutos

| Tempo | Demonstração |
|---|---|
| 0:00–0:35 | Contexto da Aurora Siger e objetivo do SCIC. |
| 0:35–1:10 | Mostrar o CSV e explicar os campos operacionais. |
| 1:10–2:00 | Executar `python codigo_fonte.py --demo` e comentar indicadores, erros e métricas. |
| 2:00–2:40 | Explicar a média móvel e a interpretação de MAE, MSE, RMSE e R². |
| 2:40–3:25 | Mostrar a lista de alertas priorizados pelo heap. |
| 3:25–4:00 | Mostrar as buscas `com`, `sens` e `prop` na trie. |
| 4:00–4:35 | Relacionar dispositivos, bases numéricas, tensão, corrente e potência. |
| 4:35–5:00 | Apresentar limitações, melhorias e gerenciamento inteligente. |

## 15. Conclusão

O SCIC atende aos requisitos centrais da atividade ao conectar organização de dados, indicadores, erros numéricos, previsão simples, métricas de avaliação, heap, trie, dispositivos e eletricidade em um único fluxo executável. O resultado é um protótipo compreensível, demonstrável e preparado para evolução.

## Referências

[1]: https://docs.python.org/3/library/csv.html "Python Documentation — csv"

[2]: https://docs.python.org/3/library/heapq.html "Python Documentation — heapq"

[3]: https://docs.python.org/3/library/collections.html "Python Documentation — collections"

[4]: https://on.fiap.com.br/mod/assign/view.php?id=658154 "FIAP — Atividade Integradora: Sistema de Comunicação Interplanetária da Colônia"
