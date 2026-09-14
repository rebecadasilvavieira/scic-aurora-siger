# SCIC — Sistema de Comunicação Interplanetária da Colônia

## Objetivo

O SCIC é um protótipo didático para apoiar o gerenciamento inteligente da comunicação da colônia Aurora Siger. O sistema carrega uma base CSV simulada, calcula indicadores operacionais, avalia uma previsão simples de latência, prioriza alertas com heap e realiza busca de registros por prefixo com trie.

## Arquivos

| Arquivo | Finalidade |
|---|---|
| `codigo_fonte.py` | Sistema principal em Python, com menu e modo demonstração. |
| `dados_aurora_siger.csv` | Dados operacionais e de comunicação simulados. |
| `relatorio_tecnico.md` | Relatório técnico completo do projeto. |
| `link_video.txt` | Local reservado para o link do vídeo não listado. |
| `graficos_ou_imagens/` | Pasta opcional para evidências visuais. |

## Como executar

Requer Python 3.9 ou superior. Não há dependências externas.

```bash
python codigo_fonte.py --demo
```

Para navegar pelo menu interativo:

```bash
python codigo_fonte.py
```

## Funcionalidades implementadas

O protótipo oferece carregamento de dados CSV, consulta de registros, latência média, perda de pacotes, disponibilidade aproximada, potência elétrica média, erro absoluto, erro relativo, MAE, MSE, RMSE, R², média móvel para previsão, heap de alertas críticos e trie de busca por prefixo.

## Observação sobre o vídeo

O arquivo `link_video.txt` deve ser atualizado pela equipe com o endereço do vídeo publicado no YouTube como “Não listado” antes do envio final.
