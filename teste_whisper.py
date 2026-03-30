import whisper

# Função para converter segundos puros no formato de relógio do SRT
def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

print("Carregando o modelo da IA...")
modelo = whisper.load_model("base")

print("Ouvindo o áudio e calculando os tempos de fala...")
resultado = modelo.transcribe("teste002.wav")

# Nome do arquivo que vamos criar
nome_arquivo_srt = "teste_00.srt"

print("\nGerando o arquivo de legendas...")

# Abre (ou cria) um arquivo de texto para escrevermos as legendas
with open(nome_arquivo_srt, "w", encoding="utf-8") as srt_file:
    
    # O Whisper guarda cada frase dentro de uma lista chamada "segments"
    for i, segment in enumerate(resultado["segments"], start=1):
        
        # Pega o tempo de início e fim e joga na nossa função formatadora
        start_time = format_timestamp(segment["start"])
        end_time = format_timestamp(segment["end"])
        
        # Pega o texto limpo
        texto = segment["text"].strip()
        
        # Escreve os 4 elementos obrigatórios do formato SRT no arquivo
        srt_file.write(f"{i}\n")
        srt_file.write(f"{start_time} --> {end_time}\n")
        srt_file.write(f"{texto}\n\n")

print(f"Sucesso! Verifique a pasta do seu projeto, o arquivo '{nome_arquivo_srt}' foi criado.")