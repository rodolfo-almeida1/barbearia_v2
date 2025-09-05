from app.app import app, db, Cliente, Barbeiro, Servico, Agendamento
from datetime import datetime, time, timedelta

def adicionar_agendamentos():
    """Adiciona agendamentos de teste, incluindo alguns concluídos para testar o dashboard."""
    print("A adicionar agendamentos de teste...")
    
    with app.app_context():
        # Verificar se já existem agendamentos cadastrados
        if Agendamento.query.count() > 0:
            print("Já existem agendamentos cadastrados.")
            return
        
        # Buscar clientes, barbeiros e serviços
        clientes = Cliente.query.all()
        barbeiros = Barbeiro.query.filter_by(ativo=True).all()
        servicos = Servico.query.filter_by(ativo=True).all()
        
        if not clientes or not barbeiros or not servicos:
            print("Não há clientes, barbeiros ou serviços suficientes para criar agendamentos.")
            return
        
        # Data atual
        hoje = datetime.now().date()
        
        # Criar alguns agendamentos para os últimos 7 dias (para testar o gráfico de faturação)
        agendamentos = []
        
        # Distribuir agendamentos pelos últimos 7 dias
        for i in range(7):
            data = hoje - timedelta(days=i)
            
            # Criar 2-4 agendamentos por dia
            num_agendamentos = min(len(clientes), (i % 3) + 2)  # 2 a 4 agendamentos
            
            for j in range(num_agendamentos):
                # Alternar entre clientes, barbeiros e serviços
                cliente = clientes[j % len(clientes)]
                barbeiro = barbeiros[j % len(barbeiros)]
                servico = servicos[(i + j) % len(servicos)]
                
                # Horário de início (entre 9h e 16h)
                hora_inicio = time(9 + (j * 2), 0)
                
                # Calcular hora de fim baseado na duração do serviço
                hora_fim_minutos = hora_inicio.hour * 60 + hora_inicio.minute + servico.duracao_minutos
                hora_fim = time(hora_fim_minutos // 60, hora_fim_minutos % 60)
                
                # Status: concluído para dias passados, agendado para hoje e futuro
                status = 'concluído' if data < hoje else 'agendado'
                
                # Criar o agendamento
                agendamento = Agendamento(
                    cliente_id=cliente.id,
                    barbeiro_id=barbeiro.id,
                    servico_id=servico.id,
                    data=data,
                    hora_inicio=hora_inicio,
                    hora_fim=hora_fim,
                    status=status,
                    observacoes=f"Agendamento de teste para {servico.nome}"
                )
                
                db.session.add(agendamento)
                agendamentos.append(agendamento)
        
        # Adicionar alguns agendamentos para hoje e dias futuros
        for i in range(5):
            data = hoje + timedelta(days=i)
            
            # 2 agendamentos por dia futuro
            for j in range(2):
                cliente = clientes[(i + j) % len(clientes)]
                barbeiro = barbeiros[(i + j) % len(barbeiros)]
                servico = servicos[(i + j) % len(servicos)]
                
                hora_inicio = time(10 + j * 2, 0)
                hora_fim_minutos = hora_inicio.hour * 60 + hora_inicio.minute + servico.duracao_minutos
                hora_fim = time(hora_fim_minutos // 60, hora_fim_minutos % 60)
                
                agendamento = Agendamento(
                    cliente_id=cliente.id,
                    barbeiro_id=barbeiro.id,
                    servico_id=servico.id,
                    data=data,
                    hora_inicio=hora_inicio,
                    hora_fim=hora_fim,
                    status='agendado',
                    observacoes=f"Agendamento futuro para {servico.nome}"
                )
                
                db.session.add(agendamento)
                agendamentos.append(agendamento)
        
        db.session.commit()
        print(f"Foram adicionados {len(agendamentos)} agendamentos ao banco de dados.")


if __name__ == "__main__":
    adicionar_agendamentos()