import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env")))

import pandas as pd
from datetime import datetime
from sqlmodel import Session, select
from app.models.base import engine
from app.models.produtor import Produtor


ASSENTAMENTOS = {
    "PaBrasilia.xlsx":                "PA Brasília",
    "PaMariaDeLourdesRodrigues.xlsx": "PA Maria De Lourdes Rodrigues",
    "PaMontepio.xlsx":                "PA Montepío",
    "PaUniaoAmeircoSantana.xlsx":     "PA União Ameirco Santana",
}

PASTA = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dados"))


def limpar(valor, max_len=None):
    if pd.isna(valor):
        return None
    resultado = str(valor).strip() or None
    if resultado and max_len:
        resultado = resultado[:max_len]
    return resultado


def limpar_cpf(valor):
    if pd.isna(valor):
        return None
    cpf = str(valor).strip()
    if cpf.endswith('.0'):
        cpf = cpf[:-2]
    # Remove formatação e mantém só números
    cpf_numeros = ''.join(filter(str.isdigit, cpf))
    if not cpf_numeros:
        return None
    # Formata como XXX.XXX.XXX-XX se tiver 11 dígitos
    if len(cpf_numeros) == 11:
        return f"{cpf_numeros[:3]}.{cpf_numeros[3:6]}.{cpf_numeros[6:9]}-{cpf_numeros[9:]}"
    return cpf_numeros[:14] or None


def parse_situacao_data(valor):
    if pd.isna(valor):
        return None, None
    partes = str(valor).strip().split(" ")
    for i, parte in enumerate(partes):
        for fmt in ("%d/%m/%Y", "%d/%m/%y"):
            try:
                data = datetime.strptime(parte, fmt).date()
                situacao = " ".join(partes[:i]).strip() or None
                return situacao, data
            except ValueError:
                continue
    return str(valor).strip()[:100], None  # limita situacao a 100 chars


total_criados = 0
total_atualizados = 0
total_sem_cpf = 0

with Session(engine) as session:
    for arquivo, nome_assentamento in ASSENTAMENTOS.items():
        caminho = os.path.join(PASTA, arquivo)

        if not os.path.exists(caminho):
            print(f"⚠️  Arquivo não encontrado: {caminho}")
            continue

        df = pd.read_excel(caminho)
        criados = atualizados = sem_cpf = 0

        for idx, row in df.iterrows():
            cpf = limpar_cpf(row.get("CPF BENEFICIARIO"))
            codigo = limpar(row.get("CÓDIGO DO BENEFICIÁRIO"), max_len=30)

            if not cpf and not codigo:
                print(f"  ⚠️  Linha {idx+2}: sem CPF e sem código, ignorada")
                continue

            situacao, data_homo = parse_situacao_data(
                row.get("SITUAÇÃO E DATA DA HOMOLOGAÇÃO")
            )

            dados = {
                "codigo_beneficiario": codigo,
                "nome_completo":       limpar(row.get("BENEFICIÁRIO"), max_len=150),
                "conjuge_nome":        limpar(row.get("CONJUGE"), max_len=150),
                "cpf_conjuge":         limpar_cpf(row.get("CPF CONJUGE")),
                "situacao":            situacao,
                "data_homologacao":    data_homo,
                "lote":                limpar(row.get("LOTE"), max_len=20),
                "assentamento":        nome_assentamento,
            }

            existente = None

            if cpf:
                existente = session.exec(
                    select(Produtor).where(Produtor.cpf_beneficiario == cpf)
                ).first()
                if not existente:
                    cpf_sem_formato = ''.join(filter(str.isdigit, cpf))
                    existente = session.exec(
                        select(Produtor).where(
                            Produtor.cpf_beneficiario.in_([
                                cpf,
                                cpf_sem_formato,
                                cpf_sem_formato + ".0"
                            ])
                        )
                    ).first()

            if not existente and codigo:
                existente = session.exec(
                    select(Produtor).where(Produtor.codigo_beneficiario == codigo)
                ).first()

            if existente:
                for campo, valor in dados.items():
                    setattr(existente, campo, valor)
                if cpf:
                    existente.cpf_beneficiario = cpf
                existente.atualizado_em = datetime.now()
                atualizados += 1
            else:
                # Placeholder curto: SC_ + últimos 10 chars do código (max ~13 chars)
                if not cpf:
                    sufixo = (codigo or str(idx))[-10:]
                    cpf_final = f"SC_{sufixo}"  # max 13 chars — cabe em VARCHAR(14)
                else:
                    cpf_final = cpf

                try:
                    session.add(Produtor(cpf_beneficiario=cpf_final, **dados))
                    session.flush()  # detecta erros imediatamente por linha
                    criados += 1
                    if not cpf:
                        sem_cpf += 1
                except Exception as e:
                    session.rollback()
                    print(f"  ❌  Linha {idx+2} ignorada por erro: {e}")

        print(f"📁 {nome_assentamento}")
        print(f"   Criados: {criados} | Atualizados: {atualizados} | Sem CPF: {sem_cpf}")

        total_criados += criados
        total_atualizados += atualizados
        total_sem_cpf += sem_cpf

    session.commit()

print(f"\n✅ Importação total concluída!")
print(f"   Criados:     {total_criados}")
print(f"   Atualizados: {total_atualizados}")
print(f"   Sem CPF:     {total_sem_cpf} (salvos com código como identificador)")
