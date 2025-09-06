#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para limpar dados de teste da aplicação barbearia_v2.
Remove todos os registros das tabelas Agendamento e Cliente, preservando outras tabelas.
"""

from app.app import app, db, Agendamento, Cliente
import sys


def limpar_dados_teste():
    """Remove todos os registros das tabelas Agendamento e Cliente."""
    
    # Exibir mensagem de aviso
    print("\n" + "=" * 80)
    print("ATENÇÃO: Este script irá apagar TODOS os registros das tabelas:")
    print("- Agendamento")
    print("- Cliente")
    print("\nNenhum registro será apagado das tabelas:")
    print("- Servico, Barbeiro, HorarioFuncionamento, UsuarioAdmin, Configuracao")
    print("=" * 80)
    
    # Solicitar confirmação do usuário
    confirmacao = input("\nTem certeza de que deseja continuar? (s/n): ").lower()
    
    if confirmacao != 's':
        print("\nOperação cancelada pelo usuário.")
        return False
    
    try:
        with app.app_context():
            # Contar registros antes da limpeza
            total_agendamentos = Agendamento.query.count()
            total_clientes = Cliente.query.count()
            
            # Remover todos os agendamentos
            print(f"\nRemovendo {total_agendamentos} agendamentos...")
            Agendamento.query.delete()
            
            # Remover todos os clientes
            print(f"Removendo {total_clientes} clientes...")
            Cliente.query.delete()
            
            # Confirmar as alterações no banco de dados
            db.session.commit()
            
            print("\nLimpeza concluída com sucesso!")
            print(f"- {total_agendamentos} agendamentos removidos")
            print(f"- {total_clientes} clientes removidos")
            
            return True
    except Exception as e:
        # Em caso de erro, fazer rollback para evitar inconsistências
        db.session.rollback()
        print(f"\nERRO: Ocorreu um problema durante a limpeza: {str(e)}")
        return False


if __name__ == "__main__":
    # Executar a função de limpeza
    sucesso = limpar_dados_teste()
    
    # Definir código de saída com base no resultado
    sys.exit(0 if sucesso else 1)