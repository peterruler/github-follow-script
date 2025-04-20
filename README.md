# Documentação do Script de Follow no GitHub

## Visão Geral
Este script automatiza o processo de seguir usuários no GitHub com base em critérios específicos para aumentar a rede de contatos de forma estratégica. O objetivo é identificar usuários ativos que têm maior probabilidade de seguir de volta, ajudando a crescer sua própria base de seguidores.

## Algoritmo Principal

O algoritmo segue estas etapas principais:

1. **Coleta de Informações do Usuário**:
   - Obtém dados do usuário autenticado (seguidores e seguindo)
   - Coleta informações de outros usuários via API do GitHub

2. **Identificação de Candidatos Potenciais**:
   - Analisa seguidores dos seus seguidores (rede secundária)
   - Verifica quem seus seguidores também seguem
   - Remove duplicatas e usuários já seguidos

3. **Filtragem por Critérios**:
   - Atividade recente (últimos 60 dias)
   - Proporção de following/followers (favorável a seguir de volta)
   - Limites de seguidores/seguindo para evitar contas inativas ou muito populares

4. **Execução dos Follows**:
   - Segue os usuários selecionados
   - Implementa pausas aleatórias entre requisições
   - Limita o número de follows por dia (20)

## Configurações

### Parâmetros Ajustáveis
```python
MAX_FOLLOWING = 1000  # Limite de contas que o usuário segue
MIN_FOLLOWERS = 5     # Mínimo de seguidores para considerar a conta
MAX_FOLLOWERS = 1000  # Máximo de seguidores para considerar a conta
INACTIVITY_DAYS = 60  # Máximo de dias sem atividade
FOLLOW_RATIO_THRESHOLD = 1.2  # Razão following/followers ideal
MAX_FOLLOWS_PER_DAY = 20  # Limite diário de follows
```

### Requisitos de Autenticação
- Token de acesso pessoal do GitHub com permissão `user:follow`
- Token deve ser inserido na variável `TOKEN`

## Funções Principais

1. **`is_good_follow_candidate(username)`**:
   - Avalia se um usuário atende todos os critérios para ser seguido
   - Retorna True/False com base na análise

2. **`find_potential_follows()`**:
   - Implementa as estratégias de busca por candidatos
   - Usa amostragem aleatória de seguidores para diversificar a busca
   - Retorna lista de usuários válidos para seguir

3. **`main()`**:
   - Orquestra todo o processo
   - Verifica limites da API
   - Executa os follows com pausas estratégicas

## Estratégias de Busca

1. **Rede Secundária**:
   - Analisa quem seus seguidores estão seguindo
   - Baseado na premissa que conexões compartilhadas têm maior chance de reciprocidade

2. **Seguidores de Seguidores**:
   - Verifica quem também segue seus seguidores
   - Expande o alcance para além da rede imediata

## Considerações de Segurança e Limites

- Respeita os rate limits da API do GitHub
- Implementa delays aleatórios entre 2-5 segundos entre ações
- Limita o número de follows por execução (20)
- Verifica sempre a disponibilidade de requisições na API

## Como Usar

1. Gerar um token de acesso pessoal no GitHub com permissão `user:follow`
2. Substituir o valor da variável `TOKEN`
3. Executar o script: `python github-follow-script.py`
4. O script imprimirá um log detalhado das ações realizadas
5. ##
