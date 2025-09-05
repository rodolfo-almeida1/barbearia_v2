#!/usr/bin/env python
import os
import subprocess
import sys
import time

# Adiciona o diretório atual ao path para importar os módulos
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Importa os scripts de população de dados
from app.scripts.criar_admin import criar_admin
from app.scripts.adicionar_servicos import adicionar_servicos
from app.scripts.adicionar_barbeiros import adicionar_barbeiros
from app.scripts.adicionar_clientes import adicionar_clientes
from app.scripts.adicionar_horarios import adicionar_horarios


def executar_comando(comando, mensagem):
    """Executa um comando de terminal e exibe uma mensagem."""
    print(f"\n{mensagem}")
    print("-" * 50)
    try:
        resultado = subprocess.run(comando, shell=True, check=True, text=True, capture_output=True)
        print(resultado.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar o comando: {e}")
        print(f"Saída de erro: {e.stderr}")
        return False


def fase_construcao():
    """Executa os comandos para construir o banco de dados."""
    print("\n===== FASE DE CONSTRUÇÃO DO BANCO DE DADOS =====")
    
    # Configurar a variável de ambiente FLASK_APP
    os.environ['FLASK_APP'] = 'app.app'
    
    # Inicializa o ambiente de migração
    if not executar_comando("flask db init", "A inicializar o ambiente de migração..."):
        return False
    
    # Cria a migração inicial
    if not executar_comando('flask db migrate -m "Criação inicial de todas as tabelas"', "A criar a migração inicial..."):
        return False
    
    # Aplica a migração
    if not executar_comando("flask db upgrade", "A aplicar a migração ao banco de dados..."):
        return False
    
    print("\nFase de construção concluída com sucesso!")
    return True


def fase_populacao():
    """Executa os scripts para popular o banco de dados."""
    print("\n===== FASE DE POPULAÇÃO DO BANCO DE DADOS =====")
    
    # Adiciona usuário administrador
    print("\n1. População de Usuários Administradores")
    print("-" * 50)
    criar_admin()
    
    # Adiciona serviços
    print("\n2. População de Serviços")
    print("-" * 50)
    adicionar_servicos()
    
    # Adiciona barbeiros
    print("\n3. População de Barbeiros")
    print("-" * 50)
    adicionar_barbeiros()
    
    # Adiciona clientes
    print("\n4. População de Clientes")
    print("-" * 50)
    adicionar_clientes()
    
    # Adiciona horários de funcionamento
    print("\n5. População de Horários de Funcionamento")
    print("-" * 50)
    adicionar_horarios()
    
    print("\nFase de população concluída com sucesso!")
    return True


def main():
    """Função principal que executa todo o processo de inicialização."""
    print("===== INICIALIZAÇÃO DO BANCO DE DADOS DA BARBEARIA V2 =====")
    print("Iniciando o processo de configuração do banco de dados...\n")
    
    # Executa a fase de construção
    if not fase_construcao():
        print("\nERRO: A fase de construção falhou. Abortando o processo.")
        return False
    
    # Pequena pausa para garantir que o banco de dados está pronto
    time.sleep(1)
    
    # Executa a fase de população
    if not fase_populacao():
        print("\nERRO: A fase de população falhou. Abortando o processo.")
        return False
    
    print("\n===== INICIALIZAÇÃO CONCLUÍDA COM SUCESSO! =====")
    print("O banco de dados foi configurado e populado com sucesso.")
    print("A aplicação está pronta para ser utilizada.")
    return True


if __name__ == "__main__":
    # Define a variável de ambiente FLASK_APP para o app.py
    os.environ["FLASK_APP"] = "app.app"
    
    # Executa o processo de inicialização
    main()