from app.app import app, db, Servico

def adicionar_servicos():
    """Adiciona serviços iniciais ao banco de dados."""
    print("A adicionar serviços iniciais...")
    
    with app.app_context():
        # Lista de serviços a serem adicionados
        servicos = [
            {
                'nome': 'Corte de Cabelo',
                'descricao': 'Corte tradicional com tesoura e máquina',
                'preco': 25.00,
                'duracao_minutos': 30
            },
            {
                'nome': 'Barba',
                'descricao': 'Aparo e modelagem de barba com navalha',
                'preco': 15.00,
                'duracao_minutos': 20
            },
            {
                'nome': 'Corte e Barba',
                'descricao': 'Combo de corte de cabelo e barba',
                'preco': 35.00,
                'duracao_minutos': 45
            },
            {
                'nome': 'Lavagem',
                'descricao': 'Lavagem de cabelo com shampoo e condicionador',
                'preco': 10.00,
                'duracao_minutos': 15
            },
            {
                'nome': 'Hidratação',
                'descricao': 'Tratamento de hidratação profunda para cabelo',
                'preco': 30.00,
                'duracao_minutos': 40
            }
        ]
        
        # Verifica se já existem serviços cadastrados
        if Servico.query.count() > 0:
            print("Já existem serviços cadastrados no banco de dados.")
            return
        
        # Adiciona cada serviço ao banco de dados
        for servico_info in servicos:
            servico = Servico(
                nome=servico_info['nome'],
                descricao=servico_info['descricao'],
                preco=servico_info['preco'],
                duracao_minutos=servico_info['duracao_minutos'],
                ativo=True
            )
            db.session.add(servico)
        
        # Commit das alterações
        db.session.commit()
        print(f"Foram adicionados {len(servicos)} serviços ao banco de dados.")


if __name__ == "__main__":
    adicionar_servicos()