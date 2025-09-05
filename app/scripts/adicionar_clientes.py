from app.app import app, db, Cliente
from datetime import datetime

def adicionar_clientes():
    """Adiciona clientes iniciais ao banco de dados."""
    print("A adicionar clientes iniciais...")
    
    with app.app_context():
        # Verifica se já existem clientes cadastrados
        if Cliente.query.count() > 0:
            print("Já existem clientes cadastrados.")
            return
        
        # Lista de clientes a serem adicionados
        clientes = [
            {
                'nome': 'Pedro',
                'sobrenome': 'Oliveira',
                'email': 'pedro.oliveira@email.com',
                'telefone': '912345678'
            },
            {
                'nome': 'Ana',
                'sobrenome': 'Costa',
                'email': 'ana.costa@email.com',
                'telefone': '923456789'
            },
            {
                'nome': 'Manuel',
                'sobrenome': 'Rodrigues',
                'email': 'manuel.rodrigues@email.com',
                'telefone': '934567890'
            },
            {
                'nome': 'Sofia',
                'sobrenome': 'Martins',
                'email': 'sofia.martins@email.com',
                'telefone': '945678901'
            },
            {
                'nome': 'Rui',
                'sobrenome': 'Fernandes',
                'email': 'rui.fernandes@email.com',
                'telefone': '956789012'
            }
        ]
        
        # Adiciona cada cliente ao banco de dados
        for cliente_info in clientes:
            cliente = Cliente(
                nome=cliente_info['nome'],
                sobrenome=cliente_info['sobrenome'],
                email=cliente_info['email'],
                telefone=cliente_info['telefone']
            )
            db.session.add(cliente)
        
        # Commit das alterações
        db.session.commit()
        print(f"Foram adicionados {len(clientes)} clientes ao banco de dados.")


if __name__ == "__main__":
    adicionar_clientes()