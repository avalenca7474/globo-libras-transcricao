📺 Transcrição de Vídeo para Acessibilidade (Sprint 03)
Protótipo funcional de alta performance para geração automatizada de legendas e integração com tecnologias assistivas (Libras).

Este projeto foi desenvolvido para a Residência Tecnológica da Globo, com o objetivo de otimizar a transcrição de vídeos. Utilizamos inteligência artificial para converter diálogos em texto com marcação temporal, entregando arquivos prontos para uso em players de vídeo e motores de Avatar 3D.

🚀 Funcionalidades
Extração de Áudio: Processamento via FFmpeg para isolar o som de arquivos .mp4.
Inteligência Artificial: Motor de transcrição OpenAI Whisper com suporte a múltiplos modelos.
Interface Interativa: Front-end amigável via Gradio (sem necessidade de terminal para o usuário final).
Exportação Dupla: Geração de arquivos .srt (legenda) e .json (estruturado para o Grupo 3 - Avatar).

🛠️ Tecnologias e Dependências
O projeto utiliza as seguintes bibliotecas principais:
openai-whisper: O motor de IA.
gradio: A interface web.
ffmpeg-python: Integração com o processador de mídia.

📦 Mobilização do Ambiente (Instalação)
Para garantir que todas as ferramentas funcionem corretamente, utilizamos um arquivo de dependências (requirements.txt).
1. Clonando o Repositório
Bash
git clone https://github.com/avalenca7474/globo-libras-transcricao.git
cd seu-repositorio
2. Instalando as Dependências via requirements.txt
O arquivo requirements.txt contém a lista exata de bibliotecas necessárias. Para instalar tudo de uma vez, execute o comando abaixo no seu terminal:
Bash
pip install -r requirements.txt
Nota: Certifique-se de que o FFmpeg esteja instalado no seu sistema operacional e configurado no PATH do Windows/Linux.

🎮 Como Executar o Projeto
Após a instalação das dependências, basta rodar o arquivo principal na raiz do projeto:
Bash
python main.py
O sistema irá gerar um link local (ex: http://127.0.0.1:7860). Basta abri-lo no seu navegador para começar a transcrever.

📂 Estrutura de Arquivos
Plaintext
PROJETO/
├── main.py              # Protótipo Final (Interface + Motor)
├── requirements.txt     # Manual de dependências para instalação rápida
├── README.md            # Documentação do projeto
├── .gitignore           # Filtro de arquivos para o Git
└── research/            # Pasta com testes e comparativos de modelos

🤝 Integração de Dados (Output JSON)
Atendendo aos requisitos de integração entre grupos, o sistema exporta os dados mastigados para o Grupo 3 (Avatar 3D) no seguinte formato:
JSON
{
    "id": 1,
    "start": "00:00:01,200",
    "end": "00:00:04,500",
    "text": "Conteúdo da fala para tradução em Libras"
}
Status: 🟢 Concluído para Apresentação (Sprint 03)