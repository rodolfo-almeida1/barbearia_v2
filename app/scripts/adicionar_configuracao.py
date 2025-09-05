from app.app import app, db, Configuracao

def adicionar_configuracao():
    """Cria uma configuração inicial para a aplicação."""
    print("A adicionar configuração inicial...")
    
    with app.app_context():
        # Verifica se já existe alguma configuração
        config_existente = Configuracao.query.first()
        
        if config_existente:
            print("Configuração já existe.")
            return
        
        # Cria uma nova configuração
        nova_config = Configuracao(
            nome_barbearia="Barbearia App",
            logo_url=None,
            cor_primaria="#3498db"
        )
        
        # Adiciona ao banco de dados
        db.session.add(nova_config)
        db.session.commit()
        
        print("Configuração inicial criada com sucesso!")


if __name__ == "__main__":
    adicionar_configuracao()