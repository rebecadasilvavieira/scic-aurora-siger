#!/usr/bin/env python3
"""SCIC - Sistema de Comunicação Interplanetária da Colônia Aurora Siger.

Projeto didático sem dependências externas. Execute `python codigo_fonte.py --demo`
para uma demonstração completa ou sem argumentos para abrir o menu interativo.
"""
from __future__ import annotations

import argparse
import csv
import heapq
import math
from dataclasses import dataclass
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "dados_aurora_siger.csv"

@dataclass
class Registro:
    timestamp: str
    modulo: str
    dispositivo: str
    latencia_real_ms: float
    latencia_prevista_ms: float
    pacotes_enviados: int
    pacotes_perdidos: int
    tensao_v: float
    corrente_a: float
    status: str

    @property
    def perda_percentual(self) -> float:
        return self.pacotes_perdidos / self.pacotes_enviados * 100 if self.pacotes_enviados else 0.0

    @property
    def erro_absoluto_ms(self) -> float:
        return abs(self.latencia_real_ms - self.latencia_prevista_ms)

    @property
    def erro_relativo_percentual(self) -> float:
        return self.erro_absoluto_ms / self.latencia_real_ms * 100 if self.latencia_real_ms else 0.0

    @property
    def potencia_w(self) -> float:
        return self.tensao_v * self.corrente_a


def carregar_dados(caminho: Path = CSV_PATH) -> list[Registro]:
    """Carrega os registros estruturados do arquivo CSV."""
    with caminho.open(newline="", encoding="utf-8") as arquivo:
        return [Registro(
            row["timestamp"], row["modulo"], row["dispositivo"],
            float(row["latencia_real_ms"]), float(row["latencia_prevista_ms"]),
            int(row["pacotes_enviados"]), int(row["pacotes_perdidos"]),
            float(row["tensao_v"]), float(row["corrente_a"]), row["status"]
        ) for row in csv.DictReader(arquivo)]


def media(valores: list[float]) -> float:
    return sum(valores) / len(valores) if valores else 0.0


def calcular_indicadores(registros: list[Registro]) -> dict[str, float]:
    """Calcula latência, disponibilidade aproximada, perda e consumo médios."""
    return {
        "latencia_media_ms": media([r.latencia_real_ms for r in registros]),
        "perda_media_percentual": media([r.perda_percentual for r in registros]),
        "disponibilidade_percentual": 100 - media([r.perda_percentual for r in registros]),
        "potencia_media_w": media([r.potencia_w for r in registros]),
        "tensao_media_v": media([r.tensao_v for r in registros]),
    }


def calcular_metricas(registros: list[Registro]) -> dict[str, float]:
    """Calcula erros absolutos/relativos e MAE, MSE, RMSE e R²."""
    reais = [r.latencia_real_ms for r in registros]
    previstos = [r.latencia_prevista_ms for r in registros]
    erros = [abs(a - p) for a, p in zip(reais, previstos)]
    mae = media(erros)
    mse = media([(a - p) ** 2 for a, p in zip(reais, previstos)])
    rmse = math.sqrt(mse)
    media_real = media(reais)
    soma_quadrados = sum((a - media_real) ** 2 for a in reais)
    r2 = 1 - sum((a - p) ** 2 for a, p in zip(reais, previstos)) / soma_quadrados if soma_quadrados else 0.0
    return {
        "erro_absoluto_medio_ms": mae,
        "erro_relativo_medio_percentual": media([r.erro_relativo_percentual for r in registros]),
        "MAE_ms": mae, "MSE_ms2": mse, "RMSE_ms": rmse, "R2": r2,
    }


def prever_latencia(registros: list[Registro], janela: int = 3) -> float:
    """Modelo simples: média móvel das últimas latências observadas."""
    return media([r.latencia_real_ms for r in registros[-janela:]])


class TrieNode:
    def __init__(self):
        self.children: dict[str, TrieNode] = {}
        self.words: list[str] = []


class Trie:
    """Estrutura para busca eficiente de módulos e dispositivos por prefixo."""
    def __init__(self, palavras: list[str]):
        self.root = TrieNode()
        for palavra in sorted(set(palavras)):
            self.inserir(palavra)

    def inserir(self, palavra: str) -> None:
        node = self.root
        for char in palavra.lower():
            node = node.children.setdefault(char, TrieNode())
        if palavra not in node.words:
            node.words.append(palavra)

    def buscar(self, prefixo: str) -> list[str]:
        node = self.root
        for char in prefixo.lower():
            if char not in node.children:
                return []
            node = node.children[char]
        resultado: list[str] = []
        def coletar(atual: TrieNode) -> None:
            resultado.extend(atual.words)
            for filho in atual.children.values():
                coletar(filho)
        coletar(node)
        return sorted(resultado)


def priorizar_alertas(registros: list[Registro], limite_latencia: float = 180.0) -> list[tuple[float, str]]:
    """Usa min-heap com prioridade negativa: maior severidade sai primeiro."""
    heap: list[tuple[float, str]] = []
    for r in registros:
        severidade = r.erro_absoluto_ms + r.perda_percentual * 5
        if r.latencia_real_ms > limite_latencia or r.perda_percentual >= 2:
            heapq.heappush(heap, (-severidade, f"{r.modulo} | latência {r.latencia_real_ms:.1f} ms | perda {r.perda_percentual:.1f}%"))
    return [(-prioridade, descricao) for prioridade, descricao in [heapq.heappop(heap) for _ in range(len(heap))]]


def imprimir_relatorio(registros: list[Registro]) -> None:
    indicadores = calcular_indicadores(registros)
    metricas = calcular_metricas(registros)
    print("\n=== INDICADORES DE COMUNICAÇÃO ===")
    for chave, valor in indicadores.items(): print(f"{chave}: {valor:.2f}")
    print("\n=== ERROS E PERFORMANCE DO MODELO ===")
    for chave, valor in metricas.items(): print(f"{chave}: {valor:.4f}")
    print(f"Previsão da próxima latência (média móvel): {prever_latencia(registros):.2f} ms")
    print("\nInterpretação: MAE/RMSE menores indicam previsões mais próximas do real; R² próximo de 1 indica maior poder explicativo.")


def executar_demo(registros: list[Registro]) -> None:
    print("SCIC | Aurora Siger | demonstração integrada")
    print(f"Registros carregados: {len(registros)}")
    imprimir_relatorio(registros)
    print("\n=== ALERTAS PRIORIZADOS COM HEAP ===")
    for severidade, alerta in priorizar_alertas(registros): print(f"prioridade {severidade:.2f} -> {alerta}")
    trie = Trie([r.modulo for r in registros] + [r.dispositivo for r in registros])
    print("\n=== BUSCA DE PREFIXO COM TRIE ===")
    for prefixo in ("com", "sens", "prop"):
        print(f"'{prefixo}' -> {trie.buscar(prefixo)}")
    print("\n=== RELAÇÃO COM DISPOSITIVOS E ELETRICIDADE ===")
    print("Sensores e antenas atuam como entrada/saída; tensão × corrente estima a potência elétrica dos módulos.")
    print("As bases decimal e binária podem representar estados de dispositivos e flags de alerta.")


def menu(registros: list[Registro]) -> None:
    while True:
        print("\n--- SCIC Aurora Siger ---\n1. Listar registros\n2. Analisar indicadores e erros\n3. Priorizar alertas\n4. Buscar por prefixo (trie)\n5. Executar demonstração completa\n0. Sair")
        opcao = input("Escolha: ").strip()
        if opcao == "1":
            for r in registros: print(f"{r.timestamp} | {r.modulo} | {r.status} | {r.latencia_real_ms:.1f} ms")
        elif opcao == "2": imprimir_relatorio(registros)
        elif opcao == "3":
            for severidade, alerta in priorizar_alertas(registros): print(f"{severidade:.2f} -> {alerta}")
        elif opcao == "4":
            prefixo = input("Prefixo: ").strip()
            print(Trie([r.modulo for r in registros] + [r.dispositivo for r in registros]).buscar(prefixo))
        elif opcao == "5": executar_demo(registros)
        elif opcao == "0": print("Encerrado."); break
        else: print("Opção inválida.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Protótipo SCIC Aurora Siger")
    parser.add_argument("--demo", action="store_true", help="executa todas as funcionalidades sem interação")
    args = parser.parse_args()
    dados = carregar_dados()
    executar_demo(dados) if args.demo else menu(dados)

# Exemplo de execução: python codigo_fonte.py --demo
# O projeto utiliza apenas a biblioteca padrão do Python.
