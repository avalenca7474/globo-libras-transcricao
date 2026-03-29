import whisper

print("Carregando o modelo da IA...")
# O modelo "base" é leve e rápido para testes iniciais. 
# Existem modelos maiores ("small", "medium", "large") que são mais precisos, mas exigem mais do PC.
modelo = whisper.load_model("base")

print("Ouvindo o áudio...")
# Substitua pelo nome exato do arquivo que você exportou do Audacity
resultado = modelo.transcribe("teste 00.wav")

print("\n--- TRANSCRIÇÃO ---")
print(resultado["text"])