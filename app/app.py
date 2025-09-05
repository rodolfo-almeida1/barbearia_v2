from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import check_password_hash
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
import os

# Configuração da aplicação Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave-secreta-da-aplicacao'

# Configuração da sessão
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutos

# Configuração do SQLAlchemy para SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, '..', 'barbearia.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialização do SQLAlchemy
db = SQLAlchemy(app)

# Configuração do Flask-Migrate
migrate = Migrate(app, db)

# Configuração do Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return UsuarioAdmin.query.get(int(user_id))

# Definição dos modelos

class Servico(db.Model):
    __tablename__ = 'servicos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    preco = db.Column(db.Float, nullable=False)
    duracao_minutos = db.Column(db.Integer, nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamento com agendamentos
    agendamentos = db.relationship('Agendamento', backref='servico', lazy=True)
    
    def __repr__(self):
        return f'<Servico {self.nome}>'


class Barbeiro(db.Model):
    __tablename__ = 'barbeiros'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    sobrenome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefone = db.Column(db.String(20))
    especialidade = db.Column(db.String(100))
    data_contratacao = db.Column(db.Date, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    agendamentos = db.relationship('Agendamento', backref='barbeiro', lazy=True)
    horarios = db.relationship('HorarioFuncionamento', backref='barbeiro', lazy=True)
    
    def __repr__(self):
        return f'<Barbeiro {self.nome} {self.sobrenome}>'


class Cliente(db.Model):
    __tablename__ = 'clientes'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    sobrenome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefone = db.Column(db.String(20))
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento com agendamentos
    agendamentos = db.relationship('Agendamento', backref='cliente', lazy=True)
    
    def __repr__(self):
        return f'<Cliente {self.nome} {self.sobrenome}>'


class HorarioFuncionamento(db.Model):
    __tablename__ = 'horarios_funcionamento'
    
    id = db.Column(db.Integer, primary_key=True)
    barbeiro_id = db.Column(db.Integer, db.ForeignKey('barbeiros.id'), nullable=False)
    dia_semana = db.Column(db.Integer, nullable=False)  # 0=Segunda, 1=Terça, ..., 6=Domingo
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fim = db.Column(db.Time, nullable=False)
    
    def __repr__(self):
        dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        return f'<Horário {dias[self.dia_semana]} {self.hora_inicio}-{self.hora_fim}>'


class DiaSemana(db.Model):
    __tablename__ = 'dias_semana'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(20), nullable=False)  # Segunda-feira, Terça-feira, etc.
    hora_abertura = db.Column(db.Time, nullable=False)
    hora_fechamento = db.Column(db.Time, nullable=False)
    ativo = db.Column(db.Boolean, default=True)  # Se o dia está aberto ou fechado
    
    def __repr__(self):
        status = "Aberto" if self.ativo else "Fechado"
        return f'<{self.nome}: {self.hora_abertura}-{self.hora_fechamento}, {status}>'


class UsuarioAdmin(UserMixin, db.Model):
    __tablename__ = 'usuarios_admin'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128), nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def is_admin(self):
        return True
    
    def __repr__(self):
        return f'<UsuarioAdmin {self.nome}>'


class Agendamento(db.Model):
    __tablename__ = 'agendamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    barbeiro_id = db.Column(db.Integer, db.ForeignKey('barbeiros.id'), nullable=False)
    servico_id = db.Column(db.Integer, db.ForeignKey('servicos.id'), nullable=False)
    data = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fim = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='agendado')  # agendado, concluído, cancelado
    observacoes = db.Column(db.Text)
    data_agendamento = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Agendamento {self.id} - {self.data} {self.hora_inicio}>'


# Rota principal (apenas para teste inicial)
@app.route('/')
def index():
    return 'Barbearia V2 - Aplicação Flask'


# Rota de logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('admin_id', None)
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('login'))


# Rota de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Buscar usuário no banco de dados
        usuario = UsuarioAdmin.query.filter_by(email=username).first()
        
        # Verificar se o usuário existe e a senha está correta
        if usuario and check_password_hash(usuario.senha_hash, password):
            # Fazer login com Flask-Login
            login_user(usuario)
            # Manter compatibilidade com código existente
            session['admin_id'] = usuario.id
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Credenciais inválidas. Por favor, tente novamente.', 'danger')
    
    return render_template('login.html')


# Rota de dashboard
@app.route('/admin/dashboard')
def admin_dashboard():
    # Verificar se o usuário está logado
    if 'admin_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    # Cálculo da faturação semanal (últimos 7 dias)
    from datetime import datetime, timedelta
    import locale
    
    # Configurar locale para formato de data em português
    try:
        locale.setlocale(locale.LC_TIME, 'pt_PT.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
        except:
            pass  # Se não conseguir definir o locale, usa o padrão
    
    # Data atual e data de 7 dias atrás
    hoje = datetime.now().date()
    data_inicio = hoje - timedelta(days=6)  # 7 dias incluindo hoje
    
    # Lista para armazenar as datas e valores de faturação
    datas_faturacao = []
    valores_faturacao = []
    
    # Calcular faturação para cada dia
    for i in range(7):
        data = data_inicio + timedelta(days=i)
        
        # Buscar agendamentos concluídos para esta data
        agendamentos_dia = Agendamento.query.filter(
            Agendamento.data == data,
            Agendamento.status == 'concluído'
        ).all()
        
        # Calcular faturação do dia
        faturacao_dia = sum(agendamento.servico.preco for agendamento in agendamentos_dia)
        
        # Formatar a data para exibição (ex: "Seg, 01/09")
        data_formatada = data.strftime('%a, %d/%m')
        
        # Adicionar às listas
        datas_faturacao.append(data_formatada)
        valores_faturacao.append(round(faturacao_dia, 2))
    
    # Cálculo da popularidade dos serviços
    from sqlalchemy import func
    
    # Buscar todos os serviços ativos
    servicos = Servico.query.filter_by(ativo=True).all()
    
    # Listas para armazenar nomes e contagens
    nomes_servicos = []
    contagens_servicos = []
    
    # Para cada serviço, contar quantos agendamentos existem
    for servico in servicos:
        # Contar agendamentos para este serviço
        contagem = Agendamento.query.filter_by(servico_id=servico.id).count()
        
        # Adicionar às listas apenas se houver pelo menos um agendamento
        if contagem > 0:
            nomes_servicos.append(servico.nome)
            contagens_servicos.append(contagem)
    
    # Estatísticas adicionais para o dashboard
    agendamentos_hoje = Agendamento.query.filter_by(data=hoje).count()
    total_clientes = Cliente.query.count()
    
    # Calcular faturação total (todos os agendamentos concluídos)
    faturacao_total = db.session.query(func.sum(Servico.preco)).join(
        Agendamento, Agendamento.servico_id == Servico.id
    ).filter(Agendamento.status == 'concluído').scalar() or 0
    
    # Renderizar o template com os dados calculados
    return render_template(
        'admin_dashboard.html',
        datas_faturacao=datas_faturacao,
        valores_faturacao=valores_faturacao,
        nomes_servicos=nomes_servicos,
        contagens_servicos=contagens_servicos,
        agendamentos_hoje=agendamentos_hoje,
        total_clientes=total_clientes,
        faturacao_total=round(faturacao_total, 2)
    )


# Rota da agenda
@app.route('/agenda')
def agenda():
    # Verificar se o usuário está logado
    if 'admin_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    # Buscar todos os agendamentos do banco de dados
    agendamentos = Agendamento.query.all()
    
    # Agrupar agendamentos por data
    agendamentos_por_data = {}
    
    for agendamento in agendamentos:
        # Converter a data para string formatada para exibição
        data_formatada = agendamento.data.strftime('%d/%m/%Y')
        
        # Se a data ainda não existe no dicionário, criar uma lista vazia
        if data_formatada not in agendamentos_por_data:
            agendamentos_por_data[data_formatada] = []
        
        # Adicionar o agendamento à lista da data correspondente
        agendamentos_por_data[data_formatada].append(agendamento)
    
    # Renderizar o template com os agendamentos agrupados
    return render_template('agenda.html', agendamentos_por_data=agendamentos_por_data)


# Rotas para gerenciamento de serviços
@app.route('/admin/servicos')
def admin_servicos():
    # Verificar se o usuário está logado
    if 'admin_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    # Buscar todos os serviços
    servicos = Servico.query.all()
    
    return render_template('admin_servicos.html', servicos=servicos)


@app.route('/admin/servicos/adicionar', methods=['POST'])
def admin_servicos_adicionar():
    # Verificar se o usuário está logado
    if 'admin_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    # Obter dados do formulário
    nome = request.form.get('nome')
    descricao = request.form.get('descricao')
    preco = request.form.get('preco')
    duracao_minutos = request.form.get('duracao_minutos')
    
    # Validar dados
    if not nome or not preco or not duracao_minutos:
        flash('Por favor, preencha todos os campos obrigatórios.', 'danger')
        return redirect(url_for('admin_servicos'))
    
    try:
        # Converter para os tipos corretos
        preco = float(preco)
        duracao_minutos = int(duracao_minutos)
        
        # Criar novo serviço
        novo_servico = Servico(
            nome=nome,
            descricao=descricao,
            preco=preco,
            duracao_minutos=duracao_minutos,
            ativo=True
        )
        
        # Adicionar ao banco de dados
        db.session.add(novo_servico)
        db.session.commit()
        
        flash(f'Serviço "{nome}" adicionado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao adicionar serviço: {str(e)}', 'danger')
    
    return redirect(url_for('admin_servicos'))


@app.route('/admin/servicos/editar/<int:id>', methods=['GET', 'POST'])
def admin_servicos_editar(id):
    # Verificar se o usuário está logado
    if 'admin_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    # Buscar o serviço pelo ID
    servico = Servico.query.get_or_404(id)
    
    if request.method == 'POST':
        # Obter dados do formulário
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        preco = request.form.get('preco')
        duracao_minutos = request.form.get('duracao_minutos')
        ativo = 'ativo' in request.form
        
        # Validar dados
        if not nome or not preco or not duracao_minutos:
            flash('Por favor, preencha todos os campos obrigatórios.', 'danger')
            return render_template('admin_servicos_editar.html', servico=servico)
        
        try:
            # Atualizar serviço
            servico.nome = nome
            servico.descricao = descricao
            servico.preco = float(preco)
            servico.duracao_minutos = int(duracao_minutos)
            servico.ativo = ativo
            
            # Salvar alterações
            db.session.commit()
            
            flash(f'Serviço "{nome}" atualizado com sucesso!', 'success')
            return redirect(url_for('admin_servicos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar serviço: {str(e)}', 'danger')
    
    # Renderizar formulário de edição
    return render_template('admin_servicos_editar.html', servico=servico)


@app.route('/admin/servicos/apagar/<int:id>', methods=['POST'])
def admin_servicos_apagar(id):
    # Verificar se o usuário está logado
    if 'admin_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    # Buscar o serviço pelo ID
    servico = Servico.query.get_or_404(id)
    
    try:
        # Verificar se o serviço está sendo usado em algum agendamento
        agendamentos = Agendamento.query.filter_by(servico_id=id).count()
        
        if agendamentos > 0:
            # Se estiver sendo usado, apenas marcar como inativo
            servico.ativo = False
            db.session.commit()
            flash(f'O serviço "{servico.nome}" foi desativado pois possui agendamentos associados.', 'warning')
        else:
            # Se não estiver sendo usado, remover do banco de dados
            nome_servico = servico.nome
            db.session.delete(servico)
            db.session.commit()
            flash(f'Serviço "{nome_servico}" removido com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao remover serviço: {str(e)}', 'danger')
    
    return redirect(url_for('admin_servicos'))


# Rotas para gerenciar barbeiros
@app.route('/admin/barbeiros')
def admin_barbeiros():
    # Verificar se o usuário está logado
    if 'admin_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    # Buscar todos os barbeiros
    barbeiros = Barbeiro.query.all()
    
    return render_template('admin_barbeiros.html', barbeiros=barbeiros)


@app.route('/admin/barbeiros/adicionar', methods=['POST'])
def admin_barbeiros_adicionar():
    # Verificar se o usuário está logado
    if 'admin_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    # Obter dados do formulário
    nome = request.form.get('nome')
    especialidade = request.form.get('especialidade')
    
    # Validar dados
    if not nome:
        flash('Por favor, preencha o nome do barbeiro.', 'danger')
        return redirect(url_for('admin_barbeiros'))
    
    try:
        # Criar novo barbeiro
        novo_barbeiro = Barbeiro(
            nome=nome,
            sobrenome='',  # Campo obrigatório no modelo, mas não no formulário
            email=f'{nome.lower().replace(" ", "")}@barbearia.com',  # Email temporário
            telefone='',
            especialidade=especialidade,
            ativo=True
        )
        
        # Adicionar ao banco de dados
        db.session.add(novo_barbeiro)
        db.session.commit()
        
        flash(f'Barbeiro "{nome}" adicionado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao adicionar barbeiro: {str(e)}', 'danger')
    
    return redirect(url_for('admin_barbeiros'))


@app.route('/admin/barbeiros/editar/<int:id>', methods=['GET', 'POST'])
def admin_barbeiros_editar(id):
    # Verificar se o usuário está logado
    if 'admin_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    # Buscar o barbeiro pelo ID
    barbeiro = Barbeiro.query.get_or_404(id)
    
    if request.method == 'POST':
        # Obter dados do formulário
        nome = request.form.get('nome')
        especialidade = request.form.get('especialidade')
        ativo = 'ativo' in request.form
        
        # Validar dados
        if not nome:
            flash('Por favor, preencha o nome do barbeiro.', 'danger')
            return render_template('admin_barbeiros_editar.html', barbeiro=barbeiro)
        
        try:
            # Atualizar barbeiro
            barbeiro.nome = nome
            barbeiro.especialidade = especialidade
            barbeiro.ativo = ativo
            
            # Salvar alterações
            db.session.commit()
            
            flash(f'Barbeiro "{nome}" atualizado com sucesso!', 'success')
            return redirect(url_for('admin_barbeiros'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar barbeiro: {str(e)}', 'danger')
    
    # Renderizar formulário de edição
    return render_template('admin_barbeiros_editar.html', barbeiro=barbeiro)


@app.route('/admin/barbeiros/apagar/<int:id>', methods=['POST'])
def admin_barbeiros_apagar(id):
    # Verificar se o usuário está logado
    if 'admin_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    # Buscar o barbeiro pelo ID
    barbeiro = Barbeiro.query.get_or_404(id)
    
    try:
        # Verificar se o barbeiro está sendo usado em algum agendamento
        agendamentos = Agendamento.query.filter_by(barbeiro_id=id).count()
        
        if agendamentos > 0:
            # Se estiver sendo usado, apenas marcar como inativo
            barbeiro.ativo = False
            db.session.commit()
            flash(f'O barbeiro "{barbeiro.nome}" foi desativado pois possui agendamentos associados.', 'warning')
        else:
            # Se não estiver sendo usado, remover do banco de dados
            nome_barbeiro = barbeiro.nome
            db.session.delete(barbeiro)
            db.session.commit()
            flash(f'Barbeiro "{nome_barbeiro}" removido com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao remover barbeiro: {str(e)}', 'danger')
    
    return redirect(url_for('admin_barbeiros'))


# Rotas para gerenciar clientes
@app.route('/admin/clientes')
def admin_clientes():
    # Verificar se o usuário está logado
    if 'admin_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    # Obter parâmetro de busca, se existir
    busca = request.args.get('busca', '')
    
    # Buscar clientes com filtro, se houver busca
    if busca:
        clientes = Cliente.query.filter(
            db.or_(
                Cliente.nome.ilike(f'%{busca}%'),
                Cliente.sobrenome.ilike(f'%{busca}%')
            )
        ).order_by(Cliente.nome).all()
    else:
        clientes = Cliente.query.order_by(Cliente.nome).all()
    
    # Adicionar funções de URL para verificação de segurança no template
    url_for_security = {
        'admin_clientes_editar': True,
        'admin_clientes_apagar': True
    }
    
    return render_template('admin_clientes.html', clientes=clientes, url_for_security=url_for_security)


# Rotas para gerenciar horários de funcionamento
@app.route('/admin/horarios')
def admin_horarios():
    # Verificar se o usuário está logado
    if 'admin_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    # Buscar todos os dias da semana
    dias = DiaSemana.query.all()
    
    # Se não existirem dias cadastrados, criar os 7 dias da semana
    if not dias:
        dias_nomes = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']
        for i, nome in enumerate(dias_nomes):
            # Horário padrão: 9h às 18h para dias de semana, 9h às 13h para sábado, fechado para domingo
            if i < 5:  # Segunda a Sexta
                hora_abertura = datetime.strptime('09:00', '%H:%M').time()
                hora_fechamento = datetime.strptime('18:00', '%H:%M').time()
                ativo = True
            elif i == 5:  # Sábado
                hora_abertura = datetime.strptime('09:00', '%H:%M').time()
                hora_fechamento = datetime.strptime('13:00', '%H:%M').time()
                ativo = True
            else:  # Domingo
                hora_abertura = datetime.strptime('00:00', '%H:%M').time()
                hora_fechamento = datetime.strptime('00:00', '%H:%M').time()
                ativo = False
            
            dia = DiaSemana(nome=nome, hora_abertura=hora_abertura, hora_fechamento=hora_fechamento, ativo=ativo)
            db.session.add(dia)
        
        db.session.commit()
        dias = DiaSemana.query.all()
    
    return render_template('admin_horarios.html', dias=dias)


@app.route('/admin/horarios/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_horarios_editar(id):
    # Verificar se o usuário é admin
    if not current_user.is_admin:
        flash('Acesso restrito a administradores.', 'danger')
        return redirect(url_for('index'))
    
    # Buscar o dia pelo ID
    dia = DiaSemana.query.get_or_404(id)
    
    # Se for GET, renderizar o template de edição
    if request.method == 'GET':
        return render_template('admin_horarios_editar.html', dia=dia)
    
    # Obter os novos horários do formulário
    hora_abertura = request.form.get('hora_abertura')
    hora_fechamento = request.form.get('hora_fechamento')
    
    try:
        # Atualizar apenas o campo que foi enviado
        if hora_abertura:
            dia.hora_abertura = datetime.strptime(hora_abertura, '%H:%M').time()
            flash(f'Hora de abertura de {dia.nome} atualizada com sucesso!', 'success')
        
        if hora_fechamento:
            dia.hora_fechamento = datetime.strptime(hora_fechamento, '%H:%M').time()
            flash(f'Hora de fechamento de {dia.nome} atualizada com sucesso!', 'success')
        
        db.session.commit()
    except ValueError:
        flash('Formato de horário inválido. Use o formato HH:MM.', 'danger')
    
    return redirect(url_for('admin_horarios'))


@app.route('/admin/horarios/alternar-status/<int:id>', methods=['POST'])
@login_required
def admin_horarios_alternar_status(id):
    # Verificar se o usuário é admin
    if not current_user.is_admin:
        flash('Acesso restrito a administradores.', 'danger')
        return redirect(url_for('index'))
    
    # Buscar o dia pelo ID
    dia = DiaSemana.query.get_or_404(id)
    
    # Alternar o status
    dia.ativo = not dia.ativo
    
    db.session.commit()
    
    status = "aberto" if dia.ativo else "fechado"
    flash(f'{dia.nome} agora está {status}.', 'success')
    
    return redirect(url_for('admin_horarios'))


@app.route('/admin/cliente/<int:id>')
def admin_cliente_detalhe(id):
    # Verificar se o usuário está logado
    if 'admin_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    # Buscar o cliente pelo ID
    cliente = Cliente.query.get_or_404(id)
    
    # Buscar agendamentos do cliente
    agendamentos = Agendamento.query.filter_by(cliente_id=id).order_by(Agendamento.data.desc(), Agendamento.hora_inicio).all()
    
    # Adicionar funções de URL para verificação de segurança no template
    url_for_security = {
        'admin_clientes_editar': True
    }
    
    return render_template('admin_cliente_detalhe.html', cliente=cliente, agendamentos=agendamentos, url_for_security=url_for_security)


@app.route('/admin/clientes/editar/<int:id>', methods=['GET', 'POST'])
def admin_clientes_editar(id):
    # Verificar se o usuário está logado
    if 'admin_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    # Buscar o cliente pelo ID
    cliente = Cliente.query.get_or_404(id)
    
    if request.method == 'POST':
        # Obter dados do formulário
        nome = request.form.get('nome')
        sobrenome = request.form.get('sobrenome')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        
        # Validar dados
        if not nome or not sobrenome or not email:
            flash('Por favor, preencha todos os campos obrigatórios.', 'danger')
            return render_template('admin_clientes_editar.html', cliente=cliente)
        
        try:
            # Verificar se o email já está em uso por outro cliente
            cliente_existente = Cliente.query.filter(Cliente.email == email, Cliente.id != id).first()
            if cliente_existente:
                flash('Este email já está em uso por outro cliente.', 'danger')
                return render_template('admin_clientes_editar.html', cliente=cliente)
            
            # Atualizar cliente
            cliente.nome = nome
            cliente.sobrenome = sobrenome
            cliente.email = email
            cliente.telefone = telefone
            
            # Salvar alterações
            db.session.commit()
            
            flash(f'Cliente "{nome} {sobrenome}" atualizado com sucesso!', 'success')
            return redirect(url_for('admin_cliente_detalhe', id=cliente.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar cliente: {str(e)}', 'danger')
    
    # Renderizar formulário de edição
    return render_template('admin_clientes_editar.html', cliente=cliente)


@app.route('/admin/clientes/apagar/<int:id>', methods=['POST'])
def admin_clientes_apagar(id):
    # Verificar se o usuário está logado
    if 'admin_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    # Buscar o cliente pelo ID
    cliente = Cliente.query.get_or_404(id)
    
    try:
        # Verificar se o cliente está sendo usado em algum agendamento
        agendamentos = Agendamento.query.filter_by(cliente_id=id).count()
        
        if agendamentos > 0:
            flash(f'O cliente "{cliente.nome} {cliente.sobrenome}" não pode ser removido pois possui agendamentos associados.', 'warning')
        else:
            # Se não estiver sendo usado, remover do banco de dados
            nome_cliente = f"{cliente.nome} {cliente.sobrenome}"
            db.session.delete(cliente)
            db.session.commit()
            flash(f'Cliente "{nome_cliente}" removido com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao remover cliente: {str(e)}', 'danger')
    
    return redirect(url_for('admin_clientes'))


# Rota para trocar horários entre agendamentos
@app.route('/admin/agendamento/trocar', methods=['POST'])
@login_required
def admin_agendamento_trocar():
    # Verificar se o usuário é admin
    if not current_user.is_admin:
        return jsonify({'status': 'error', 'message': 'Acesso restrito a administradores.'}), 403
    
    # Obter os IDs dos agendamentos do corpo da requisição JSON
    data = request.get_json()
    
    if not data or 'agendamento1_id' not in data or 'agendamento2_id' not in data:
        return jsonify({'status': 'error', 'message': 'Dados incompletos. IDs dos agendamentos são necessários.'}), 400
    
    agendamento1_id = data['agendamento1_id']
    agendamento2_id = data['agendamento2_id']
    
    # Buscar os agendamentos no banco de dados
    agendamento1 = Agendamento.query.get(agendamento1_id)
    agendamento2 = Agendamento.query.get(agendamento2_id)
    
    # Verificar se ambos os agendamentos foram encontrados
    if not agendamento1 or not agendamento2:
        return jsonify({'status': 'error', 'message': 'Um ou ambos os agendamentos não foram encontrados.'}), 404
    
    # Verificar se ambos os agendamentos estão com status 'agendado'
    if agendamento1.status != 'agendado' or agendamento2.status != 'agendado':
        return jsonify({'status': 'error', 'message': 'Apenas agendamentos com status "agendado" podem ser trocados.'}), 400
    
    try:
        # Trocar os horários entre os agendamentos
        # Salvar os valores temporariamente
        temp_data = agendamento1.data
        temp_hora_inicio = agendamento1.hora_inicio
        temp_hora_fim = agendamento1.hora_fim
        
        # Atualizar agendamento1 com os valores do agendamento2
        agendamento1.data = agendamento2.data
        agendamento1.hora_inicio = agendamento2.hora_inicio
        agendamento1.hora_fim = agendamento2.hora_fim
        
        # Atualizar agendamento2 com os valores temporários (originalmente do agendamento1)
        agendamento2.data = temp_data
        agendamento2.hora_inicio = temp_hora_inicio
        agendamento2.hora_fim = temp_hora_fim
        
        # Salvar as alterações no banco de dados
        db.session.commit()
        
        return jsonify({
            'status': 'success', 
            'message': 'Horários trocados com sucesso!',
            'agendamento1': {
                'id': agendamento1.id,
                'cliente': f"{agendamento1.cliente.nome} {agendamento1.cliente.sobrenome}",
                'data': agendamento1.data.strftime('%d/%m/%Y'),
                'hora_inicio': agendamento1.hora_inicio.strftime('%H:%M'),
                'hora_fim': agendamento1.hora_fim.strftime('%H:%M')
            },
            'agendamento2': {
                'id': agendamento2.id,
                'cliente': f"{agendamento2.cliente.nome} {agendamento2.cliente.sobrenome}",
                'data': agendamento2.data.strftime('%d/%m/%Y'),
                'hora_inicio': agendamento2.hora_inicio.strftime('%H:%M'),
                'hora_fim': agendamento2.hora_fim.strftime('%H:%M')
            }
        })
    except Exception as e:
        # Em caso de erro, desfazer as alterações
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Erro ao trocar horários: {str(e)}'}), 500


# Rotas para confirmar e cancelar agendamentos via AJAX
@app.route('/agendamento/confirmar/<int:id>', methods=['POST'])
@login_required
def agendamento_confirmar(id):
    # Verificar se o usuário é admin
    if not current_user.is_admin:
        return jsonify({'status': 'error', 'message': 'Acesso restrito a administradores.'}), 403
    
    # Buscar o agendamento pelo ID
    agendamento = Agendamento.query.get_or_404(id)
    
    try:
        # Atualizar o status do agendamento para 'concluído'
        agendamento.status = 'concluído'
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Agendamento confirmado com sucesso!',
            'agendamento_id': agendamento.id,
            'novo_status': 'concluído'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Erro ao confirmar agendamento: {str(e)}'}), 500


@app.route('/agendamento/cancelar/<int:id>', methods=['POST'])
@login_required
def agendamento_cancelar(id):
    # Verificar se o usuário é admin
    if not current_user.is_admin:
        return jsonify({'status': 'error', 'message': 'Acesso restrito a administradores.'}), 403
    
    # Buscar o agendamento pelo ID
    agendamento = Agendamento.query.get_or_404(id)
    
    try:
        # Atualizar o status do agendamento para 'cancelado'
        agendamento.status = 'cancelado'
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Agendamento cancelado com sucesso!',
            'agendamento_id': agendamento.id,
            'novo_status': 'cancelado'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Erro ao cancelar agendamento: {str(e)}'}), 500


# Execução da aplicação
if __name__ == '__main__':
    app.run(debug=True, port=5001)