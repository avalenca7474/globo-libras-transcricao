import whisper

# 1. Função Matemática: Converte segundos para o formato de relógio do SRT (HH:MM:SS,mmm)
def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

print("Carregando o modelo Whisper (Tamanho: Medium)...")
print("Aviso: O primeiro download é pesado (~1.5GB). Aguarde a conclusão.")

# 2. Carrega o modelo com alta capacidade de compreensão e pontuação
modelo = whisper.load_model("medium")

# Nome do arquivo de vídeo/áudio que você quer testar
arquivo_midia = "video_da_globo.mp4" # Substitua pelo nome exato do seu vídeo

# 3. Contexto: "Dicionário" para ajudar a IA com palavras-chave
contexto_projeto = "Projeto de acessibilidade em Libras da TV Globo. Ferramentas e termos: Audacity, inteligência artificial, SRT, Avatar 3D, Rybená, Hand Talk, V-Libras, Coday."

print(f"Ouvindo o arquivo '{arquivo_midia}' e calculando tempos...")

# 4. Executa a transcrição com precisão aprimorada
resultado = modelo.transcribe(
    arquivo_midia,
    language="pt",
    initial_prompt=contexto_projeto
)

nome_arquivo_srt = "legenda_globo_medium.srt"
print(f"\nGerando o arquivo de legendas: {nome_arquivo_srt}...")

# 5. Escreve o resultado no arquivo SRT
with open(nome_arquivo_srt, "w", encoding="utf-8") as srt_file:
    for i, segment in enumerate(resultado["segments"], start=1):
        
        start_time = format_timestamp(segment["start"])
        end_time = format_timestamp(segment["end"])
        texto = segment["text"].strip()
        
        srt_file.write(f"{i}\n")
        srt_file.write(f"{start_time} --> {end_time}\n")
        srt_file.write(f"{texto}\n\n")

print(f"✅ Sucesso! A transcrição 'medium' foi concluída e salva como {nome_arquivo_srt}.")