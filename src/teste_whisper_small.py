import whisper

# 1. Função Matemática: Converte segundos puros para o formato de relógio do SRT (HH:MM:SS,mmm)
def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

print("Carregando o modelo Whisper (Tamanho: Small)...")
print("Aviso: A primeira execução fará o download do modelo, aguarde.")

# 2. Carrega o modelo com maior capacidade de compreensão
modelo = whisper.load_model("small")

# Nome do arquivo de vídeo/áudio que você quer testar
arquivo_midia = "26-03-30_LibrasTrechosBaseLimpa_Justica.mp4" # ATENÇÃO: Mude para o nome real do seu vídeo

# 3. Contexto: "Dicionário" para ajudar a IA com palavras-chave do projeto
contexto_projeto = "Projeto de acessibilidade em Libras da TV Globo. Ferramentas e termos: Audacity, inteligência artificial, SRT, Avatar 3D, Rybená, Hand Talk, V-Libras, Coday."

print(f"Ouvindo o arquivo '{arquivo_midia}' e calculando os tempos de fala...")

# 4. Executa a transcrição com os "poderes" ativados
resultado = modelo.transcribe(
    arquivo_midia,
    language="pt",                  # Força a IA a ouvir apenas em português
    initial_prompt=contexto_projeto # Passa o contexto inicial
)

nome_arquivo_srt = "teste_02_video_small.srt"
print(f"\nGerando o arquivo de legendas: {nome_arquivo_srt}...")

# 5. Escreve o resultado no arquivo físico
with open(nome_arquivo_srt, "w", encoding="utf-8") as srt_file:
    # O Whisper guarda cada frase detectada dentro da lista "segments"
    for i, segment in enumerate(resultado["segments"], start=1):
        
        # Formata os tempos de início e fim
        start_time = format_timestamp(segment["start"])
        end_time = format_timestamp(segment["end"])
        
        # Extrai o texto limpo
        texto = segment["text"].strip()
        
        # Escreve os 4 elementos obrigatórios do formato SRT no arquivo
        srt_file.write(f"{i}\n")
        srt_file.write(f"{start_time} --> {end_time}\n")
        srt_file.write(f"{texto}\n\n")

print("✅ Sucesso! A transcrição foi concluída e o arquivo SRT está pronto na sua pasta.")