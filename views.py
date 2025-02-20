from models import Conta, engine, Bancos, Status, Historico, Tipos
from sqlmodel import Session, select
from datetime import date, timedelta

def criar_conta(conta: Conta):
    # Criar uma sessão e quando terminar fechar
    with Session(engine) as session:
        statement = select(Conta).where(Conta.banco == conta.banco)
        results = session.exec(statement).all()

        # Validando se conta já existe        
        if results:
            print("Conta já existe")
            return
        
        session.add(conta)
        session.commit()
        return conta
    
def listar_contas():
    with Session(engine) as session:
        statement = select(Conta)
        results = session.exec(statement).all()
    return results
    

def desativar_conta(id):
    with Session(engine) as session:
        statement = select(Conta).where(Conta.id == id)
        conta = session.exec(statement).first()
        if conta.valor > 0:
            raise ValueError("Conta não pode ser desativada, ainda possui saldo")
        conta.status = Status.INATIVO
        session.commit()

def transferir_saldo(id_conta_saida,id_conta_entrada,Valor):
    with Session(engine) as session:
        statement = select(Conta).where(Conta.id == id_conta_saida)
        conta_saida = session.exec(statement).first()
        statement2 = select(Conta).where(Conta.id == id_conta_entrada)
        conta_entrada= session.exec(statement2).first()
        if conta_entrada.status == Status.INATIVO or conta_saida.status == Status.INATIVO:
            raise ValueError("Conta inativa")
        if conta_saida.valor < Valor:
            raise ValueError("Saldo insuficiente")
        
        
        conta_saida.valor -= Valor
        conta_entrada.valor += Valor
        session.commit()
        
def movimentar_dinheiro(historico: Historico):
    with Session(engine) as session:
        statement = select(Conta).where(Conta.id == historico.conta_id)
        conta = session.exec(statement).first()
        if conta.status == Status.INATIVO:
            raise ValueError("Conta inativa")
        if historico.tipo == Tipos.ENTRADA:
            conta.valor += historico.valor
        else:
            if conta.valor < historico.valor:
                raise ValueError("Saldo insuficiente")
            conta.valor -= historico.valor
        session.add(historico)
        session.commit()
        return historico

def total_contas():
    with Session(engine) as session:
        statement = select(Conta)
        results = session.exec(statement).all()
    total = 0
    for conta in results:
        total += conta.valor
    return float(total)

def buscar_historico_entre_datas (data_inicio: date, data_fim: date):
    with Session(engine) as session:
        statement = select(Historico).where(
            Historico.data >= data_inicio,
            Historico.data <= data_fim
        )
        results = session.exec(statement).all()
        return results

def criar_grafico_por_conta():
    with Session(engine) as session:
        statement = select(Conta).where(Conta.status==Status.ATIVO)
        contas = session.exec(statement).all()
        bancos = [i.banco.value[0] for i in contas]
        total = [i.valor for i in contas]
        import matplotlib.pyplot as plt
        plt.bar(bancos, total)
        plt.show()
        
