// Variáveis para armazenar as seleções
let servicoSelecionado = null;
let barbeiroSelecionado = null;
let dataSelecionada = null;
let horarioSelecionado = null;

// Configurar a data mínima como hoje
const hoje = new Date().toISOString().split('T')[0];
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('data').setAttribute('min', hoje);
    document.getElementById('data').value = hoje;
    
    // Inicializar os event listeners
    inicializarEventListeners();
});

/**
 * Inicializa todos os event listeners da página
 */
function inicializarEventListeners() {
    // Seleção de serviço (Passo 1)
    const servicosCards = document.querySelectorAll('#passo1 .card-selecao');
    servicosCards.forEach(card => {
        card.addEventListener('click', selecionarServico);
        card.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                selecionarServico.call(this);
            }
        });
    });
    
    // Seleção de barbeiro (Passo 2)
    const barbeirosCards = document.querySelectorAll('#passo2 .card-selecao');
    barbeirosCards.forEach(card => {
        card.addEventListener('click', selecionarBarbeiro);
        card.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                selecionarBarbeiro.call(this);
            }
        });
    });
    
    // Seleção de data (Passo 3)
    document.getElementById('data').addEventListener('change', function() {
        dataSelecionada = this.value;
        carregarHorarios();
    });
    
    // Seleção de horário (Passo 3)
    document.getElementById('horario').addEventListener('change', function() {
        horarioSelecionado = this.value;
        // Habilitar o botão de próximo quando um horário for selecionado
        document.getElementById('btn-proximo-3').disabled = !horarioSelecionado;
    });
    
    // Botão próximo do passo 3
    document.getElementById('btn-proximo-3').addEventListener('click', function() {
        avancarPasso(3, 4);
    });
    
    // Finalizar agendamento
    document.getElementById('btn-finalizar').addEventListener('click', finalizarAgendamento);
    
    // Carregar horários iniciais se a data já estiver preenchida
    if (document.getElementById('data').value) {
        dataSelecionada = document.getElementById('data').value;
    }
}

/**
 * Função para selecionar um serviço
 */
function selecionarServico() {
    // Remover seleção anterior
    document.querySelectorAll('#passo1 .card-selecao').forEach(c => {
        c.classList.remove('selecionado');
        c.setAttribute('aria-pressed', 'false');
    });
    
    // Adicionar seleção ao card clicado
    this.classList.add('selecionado');
    this.setAttribute('aria-pressed', 'true');
    
    // Armazenar o ID do serviço selecionado
    servicoSelecionado = {
        id: this.dataset.id,
        duracao: this.dataset.duracao
    };
    
    // Avançar para o próximo passo após um breve delay
    setTimeout(() => {
        avancarPasso(1, 2);
    }, 300);
}

/**
 * Função para selecionar um barbeiro
 */
function selecionarBarbeiro() {
    // Remover seleção anterior
    document.querySelectorAll('#passo2 .card-selecao').forEach(c => {
        c.classList.remove('selecionado');
        c.setAttribute('aria-pressed', 'false');
    });
    
    // Adicionar seleção ao card clicado
    this.classList.add('selecionado');
    this.setAttribute('aria-pressed', 'true');
    
    // Armazenar o ID do barbeiro selecionado
    barbeiroSelecionado = this.dataset.id;
    
    // Avançar para o próximo passo após um breve delay
    setTimeout(() => {
        avancarPasso(2, 3);
        // Carregar horários disponíveis para a data atual
        carregarHorarios();
    }, 300);
}

/**
 * Função para avançar para o próximo passo com animação
 * @param {number} atual - Número do passo atual
 * @param {number} proximo - Número do próximo passo
 */
function avancarPasso(atual, proximo) {
    const passoAtual = document.getElementById(`passo${atual}`);
    const passoProximo = document.getElementById(`passo${proximo}`);
    
    // Adicionar classe para iniciar animação de saída
    passoAtual.classList.remove('ativo');
    passoAtual.classList.add('slide-out-left');
    
    // Após a animação de saída, mostrar o próximo passo
    setTimeout(() => {
        passoAtual.classList.remove('slide-out-left');
        passoAtual.style.display = 'none';
        
        // Mostrar o próximo passo com animação de entrada
        passoProximo.style.display = 'block';
        passoProximo.classList.add('slide-in-right');
        passoProximo.classList.add('ativo');
        
        // Se estiver avançando para o passo 3, focar no campo de data
        if (proximo === 3) {
            setTimeout(() => {
                document.getElementById('data').focus();
            }, 100);
        }
        
        // Remover a classe de animação após a conclusão
        setTimeout(() => {
            passoProximo.classList.remove('slide-in-right');
        }, 500);
    }, 500);
}

/**
 * Função para voltar ao passo anterior com animação
 * @param {number} passo - Número do passo anterior
 */
function voltarPasso(passo) {
    const passoAtual = document.querySelector('.passo.ativo');
    const passoAnterior = document.getElementById(`passo${passo}`);
    
    passoAtual.classList.remove('ativo');
    passoAtual.classList.add('fade-out');
    
    setTimeout(() => {
        passoAtual.classList.remove('fade-out');
        passoAtual.style.display = 'none';
        
        passoAnterior.style.display = 'block';
        passoAnterior.classList.add('fade-in');
        passoAnterior.classList.add('ativo');
        
        setTimeout(() => {
            passoAnterior.classList.remove('fade-in');
        }, 500);
    }, 500);
}

/**
 * Função para carregar horários disponíveis via AJAX
 */
function carregarHorarios() {
    if (!dataSelecionada) {
        dataSelecionada = document.getElementById('data').value;
    }
    
    if (!servicoSelecionado || !barbeiroSelecionado || !dataSelecionada) {
        return;
    }
    
    const horarioSelect = document.getElementById('horario');
    const loadingSpinner = document.getElementById('loading-horarios');
    
    // Mostrar indicador de carregamento
    horarioSelect.disabled = true;
    horarioSelect.innerHTML = '<option value="">Carregando horários...</option>';
    loadingSpinner.classList.remove('d-none');
    
    // Fazer requisição AJAX para a API
    fetch(`/api/horarios-disponiveis?data=${dataSelecionada}&barbeiro_id=${barbeiroSelecionado}&servico_id=${servicoSelecionado.id}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro na resposta da rede');
            }
            return response.json();
        })
        .then(data => {
            horarioSelect.innerHTML = '';
            
            if (data.status === 'success' && data.horarios_disponiveis.length > 0) {
                // Adicionar opção padrão
                const defaultOption = document.createElement('option');
                defaultOption.value = '';
                defaultOption.textContent = 'Selecione um horário';
                horarioSelect.appendChild(defaultOption);
                
                // Adicionar horários disponíveis
                data.horarios_disponiveis.forEach(horario => {
                    const option = document.createElement('option');
                    option.value = horario.hora_inicio;
                    option.textContent = `${horario.hora_inicio} - ${horario.hora_fim}`;
                    horarioSelect.appendChild(option);
                });
                
                horarioSelect.disabled = false;
            } else {
                // Sem horários disponíveis
                const option = document.createElement('option');
                option.value = '';
                option.textContent = 'Sem horários disponíveis para esta data';
                horarioSelect.appendChild(option);
            }
            
            // Esconder indicador de carregamento
            loadingSpinner.classList.add('d-none');
        })
        .catch(error => {
            console.error('Erro ao carregar horários:', error);
            horarioSelect.innerHTML = '<option value="">Erro ao carregar horários</option>';
            loadingSpinner.classList.add('d-none');
        });
}

/**
 * Função para finalizar o agendamento
 */
function finalizarAgendamento() {
    const nome = document.getElementById('nome').value;
    const telefone = document.getElementById('telefone').value;
    const observacoes = document.getElementById('observacoes').value;
    
    // Validar campos obrigatórios
    if (!nome || !telefone) {
        mostrarMensagem('Por favor, preencha todos os campos obrigatórios.', 'erro');
        return;
    }
    
    // Validar formato do telefone (opcional)
    const telefoneRegex = /^\(\d{2}\)\s\d{4,5}-\d{4}$/;
    if (!telefoneRegex.test(telefone)) {
        mostrarMensagem('Por favor, insira um telefone válido no formato (00) 00000-0000.', 'erro');
        return;
    }
    
    // Preparar dados para envio
    const dados = {
        nome: nome,
        telefone: telefone,
        observacoes: observacoes,
        servico_id: servicoSelecionado.id,
        barbeiro_id: barbeiroSelecionado,
        data: dataSelecionada,
        hora_inicio: horarioSelecionado
    };
    
    // Desabilitar botão para evitar múltiplos envios
    const btnFinalizar = document.getElementById('btn-finalizar');
    btnFinalizar.disabled = true;
    btnFinalizar.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processando...';
    
    // Enviar dados via AJAX
    fetch('/agendar', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(dados)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Erro na resposta da rede');
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            // Limpar formulário e mostrar mensagem de sucesso
            document.getElementById('nome').value = '';
            document.getElementById('telefone').value = '';
            document.getElementById('observacoes').value = '';
            
            // Mostrar mensagem de sucesso
            mostrarMensagem('Agendamento realizado com sucesso! Em breve entraremos em contato para confirmar.', 'sucesso');
            
            // Voltar para o passo 1 após alguns segundos
            setTimeout(() => {
                resetarFormulario();
            }, 3000);
        } else {
            // Mostrar mensagem de erro
            mostrarMensagem(`Erro ao realizar agendamento: ${data.message}`, 'erro');
        }
        
        // Reabilitar botão
        btnFinalizar.disabled = false;
        btnFinalizar.innerHTML = 'Finalizar Agendamento';
    })
    .catch(error => {
        console.error('Erro:', error);
        mostrarMensagem('Erro ao processar sua solicitação. Por favor, tente novamente.', 'erro');
        
        // Reabilitar botão
        btnFinalizar.disabled = false;
        btnFinalizar.innerHTML = 'Finalizar Agendamento';
    });
}

/**
 * Função para mostrar mensagens de sucesso ou erro
 * @param {string} texto - Texto da mensagem
 * @param {string} tipo - Tipo da mensagem (sucesso ou erro)
 */
function mostrarMensagem(texto, tipo) {
    const mensagemDiv = document.getElementById('mensagem');
    mensagemDiv.textContent = texto;
    mensagemDiv.className = `mensagem ${tipo}`;
    mensagemDiv.style.display = 'block';
    
    // Rolar para o topo para mostrar a mensagem
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    // Esconder a mensagem após alguns segundos
    setTimeout(() => {
        mensagemDiv.style.display = 'none';
    }, 5000);
}

/**
 * Função para resetar o formulário e voltar ao passo 1
 */
function resetarFormulario() {
    // Voltar para o passo 1
    voltarPasso(1);
    
    // Limpar seleções
    servicoSelecionado = null;
    barbeiroSelecionado = null;
    dataSelecionada = document.getElementById('data').value; // Manter a data atual
    horarioSelecionado = null;
    
    // Limpar seleções visuais
    document.querySelectorAll('.card-selecao').forEach(card => {
        card.classList.remove('selecionado');
        card.setAttribute('aria-pressed', 'false');
    });
    
    document.getElementById('horario').innerHTML = '<option value="">Selecione uma data primeiro</option>';
    document.getElementById('btn-proximo-3').disabled = true;
}