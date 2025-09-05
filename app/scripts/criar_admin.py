from werkzeug.security import generate_password_hash
from app.app import app, db, UsuarioAdmin

def criar_admin():
    """Cria um usuário administrador padrão no banco de dados."""
    print("A adicionar usuário administrador...")
    
    with app.app_context():
        # Verifica se já existe algum administrador
        admin_existente = UsuarioAdmin.query.filter_by(email='admin@barbearia.com').first()
        
        if admin_existente:
            print("Usuário administrador já existe.")
            return
        
        # Cria um novo administrador
        novo_admin = UsuarioAdmin(
            nome='Administrador',
            email='admin@barbearia.com',
            senha_hash=generate_password_hash('admin123')
        )
        
        # Adiciona ao banco de dados
        db.session.add(novo_admin)
        db.session.commit()
        
        print("Usuário administrador criado com sucesso!")
        print("Email: admin@barbearia.com")
        print("Senha: admin123")


if __name__ == "__main__":
    criar_admin()