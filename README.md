# 📺 Motor de Transcrição V-Libras (Sprint 06)

Protótipo definitivo de alta performance para geração automatizada de legendas (.srt) em nuvem, integrado com a arquitetura de microsserviços do ecossistema V-Libras.

Este projeto foi desenvolvido para a **Residência Tecnológica da Globo**, com o objetivo de otimizar e automatizar a transcrição de mídias. Utilizando Inteligência Artificial de ponta, o microsserviço converte diálogos em texto com sincronia milimétrica, servindo como base fiel para a tradução e animação do Avatar 3D.

🚀 **Links do Ambiente em Produção:**

* **Interface Swagger (Docs):** [https://adrianovalenca-api-vlibras-transcricao.hf.space/docs](https://adrianovalenca-api-vlibras-transcricao.hf.space/docs)
* **Hugging Face Space:** [https://huggingface.co/spaces/AdrianoValenca/api-vlibras-transcricao](https://huggingface.co/spaces/AdrianoValenca/api-vlibras-transcricao)

---

## 🚀 Funcionalidades

* **Arquitetura Assíncrona (Anti-Timeout):** Processamento pesado em segundo plano via `BackgroundTasks`. A API recebe o áudio, libera a conexão imediatamente com um ID único (`task_id`) e evita quedas de conexão por tempo limite de requisição HTTP (*timeout*).
* **Inteligência Artificial de Alta Precisão:** Motor alimentado pelo modelo `faster-whisper` (**Large-v3**), otimizado para execução estável em CPU (`compute_type="int8"`).
* **Filtro VAD Dinâmico:** Ativação nativa de detecção de atividade de voz (`vad_filter=True`), ignorando trechos de silêncio absoluto para acelerar o processamento.
* **Camada de Limpeza Heurística:** Filtro baseado em dicionário regex que corrige automaticamente alucinações fonéticas comuns da IA e ajusta jargões específicos (ex: *"gerro"* para *"genro"*, *"galo de jim"* para *"Seu Galdin"*, *"morre regaço"* para *"mó arregaço"*).
* **Validação de Formatos:** Bloqueio nativo de arquivos incompatíveis direto na porta de entrada. Formatos de áudio permitidos: `.wav`, `.mp3`, `.ogg`, `.flac` e `.m4a`.

---

## 🛠️ Tecnologias e Dependências

* **FastAPI:** Framework web moderno e veloz para a construção dos endpoints.
* **faster-whisper:** Reimplementação otimizada do Whisper da OpenAI, consumindo menos memória e entregando maior velocidade de inferência.
* **Uvicorn:** Servidor ASGI para sustentação da aplicação em tempo real.
* **Docker:** Conteinerização completa para o deploy contínuo em infraestrutura cloud.

---

## 🎮 Como Executar o Projeto Localmente

### 1. Clonando o Repositório

```bash
git clone https://github.com/avalenca7474/globo-libras-transcricao.git
cd globo-libras-transcricao

```

### 2. Instalando as Dependências

Certifique-se de ter o `FFmpeg` instalado no sistema operacional e configurado no seu PATH. Em seguida, instale as bibliotecas do ecossistema Python:

```bash
pip install -r requirements.txt

```

### 3. Inicializando a API local

Execute o comando Uvicorn para ligar o servidor de desenvolvimento:

```bash
python api.py

```

O painel interativo do Swagger ficará disponível localmente em: `http://127.0.0.1:8000/docs`

---

## 📂 Estrutura de Arquivos

```text
PROJETO/
├── api.py               # Arquivo principal (Configuração FastAPI, Regras de Negócio e Endpoints)
├── requirements.txt     # Gerenciador de bibliotecas e dependências do projeto
├── README.md            # Documentação técnica do sistema
└── Dockerfile           # Arquivo de receita de container para deploy na nuvem

```

---

## 🤝 Contrato de Integração (Fluxo de Consumo para o Grupo 4)

A comunicação com o motor deve seguir obrigatoriamente a estrutura em dois passos:

### 📍 1. Enviar o arquivo de áudio (`POST /gerar-srt`)

O orquestrador do ecossistema realiza o upload do arquivo usando a chave `file`.

* **Exemplo de Resposta (JSON imediato):**

```json
{
  "mensagem": "Áudio recebido com sucesso. Processamento iniciado em segundo plano.",
  "task_id": "a0be785b-b7cb-4b4e-a0c6-e80aae1be1b2",
  "status_url": "/status/a0be785b-b7cb-4b4e-a0c6-e80aae1be1b2"
}

```

### 📍 2. Consultar o progresso (`GET /status/{task_id}`)

O sistema consome o endpoint em ciclos periódicos (ex: a cada 30 segundos) injetando o ID recebido.

* **Enquanto a IA processa:** Retorna `{"status": "processando", "mensagem": "..."}`.
* **Quando a IA finaliza:** A rota altera os cabeçalhos HTTP para `media_type="application/x-subrip"` e **força o download direto** do arquivo `.srt` estruturado e limpo.

---

## 👥 Membros do Grupo (Equipe 2)

* Adriano Valença
* Carlos Henrique
* Gabriel Soares
* Cauã Oliveira

**Status do Projeto:** 🟢 Concluído e em Produção (Sprint 06)
