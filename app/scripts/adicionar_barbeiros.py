from app.app import app, db, Barbeiro
from datetime import date

def adicionar_barbeiros():
    """Adiciona barbeiros iniciais ao banco de dados."""
    print("A adicionar barbeiros iniciais...")
    
    with app.app_context():
        # Lista de barbeiros a serem adicionados
        barbeiros = [
            {
                'nome': 'João',
                'sobrenome': 'Silva',
                'email': 'joao.silva@barbearia.com',
                'telefone': '912345678',
                'data_contratacao': date(2020, 1, 15)
            },
            {
                'nome': 'Miguel',
                'sobrenome': 'Santos',
                'email': 'miguel.santos@barbearia.com',
                'telefone': '923456789',
                'data_contratacao': date(2021, 3, 10)
            },
            {
                'nome': 'António',
                'sobrenome': 'Ferreira',
                'email': 'antonio.ferreira@barbearia.com',
                'telefone': '934567890',
                'data_contratacao': date(2022, 5, 20)
            }
        ]
        
        # Verifica se já existem barbeiros cadastrados
        if Barbeiro.query.count() > 0:
            print("Já existem barbeiros cadastrados no banco de dados.")
            return
        
        # Adiciona cada barbeiro ao banco de dados
        for barbeiro_info in barbeiros:
            barbeiro = Barbeiro(
                nome=barbeiro_info['nome'],
                sobrenome=barbeiro_info['sobrenome'],
                email=barbeiro_info['email'],
                telefone=barbeiro_info['telefone'],
                data_contratacao=barbeiro_info['data_contratacao'],
                ativo=True
            )
            db.session.add(barbeiro)
        
        # Commit das alterações
        db.session.commit()
        print(f"Foram adicionados {len(barbeiros)} barbeiros ao banco de dados.")


if __name__ == "__main__":
    adicionar_barbeiros()