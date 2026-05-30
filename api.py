import os
import re
import tempfile
import uvicorn
from datetime import timedelta
from fastapi import FastAPI, File, UploadFile, Response, HTTPException
from faster_whisper import WhisperModel

app = FastAPI(title="Motor de Transcrição V-Libras")

prompt_tecnico = "Transcrição para a Globo. Termos: GloboPlay, V-Libras, Projac, UNICAP. Personagens: Seu Galdin, Boutazar. Mantenha gírias como 'mó'."

DICIONARIO_LIMPEZA = {
    "gerro": "genro",
    "gerros": "genros",
    "morre regaço": "mó arregaço",
    "galo de jim": "Seu Galdin",
    "seu galvão": "Seu Galdin",
    "pão no jar": "plano já"
}

print("[*] Carregando o modelo Large-v3 otimizado (CPU/INT8)...")
# Ajustado para CPU e INT8 devido à arquitetura AMD local
model = WhisperModel("large-v3", device="cpu", compute_type="int8")

def format_timestamp(seconds):
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    millis = int((seconds - int(seconds)) * 1000)
    # Mantendo o formato exato HH:MM:SS,mmm exigido pelo padrão SRT
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def aplicar_limpeza_manual(texto):
    for erro, correcao in DICIONARIO_LIMPEZA.items():
        padrao = re.compile(re.escape(erro), re.IGNORECASE)
        texto = padrao.sub(correcao, texto)
    return texto

@app.post("/gerar-srt")
async def gerar_srt(file: UploadFile = File(...)):
    print(f"[*] Processando requisição: {file.filename}")

    # 1. Defesa: Validação de formato na porta (barra vídeos e arquivos incorretos)
    extensao = file.filename.split('.')[-1].lower()
    formatos_permitidos = ['wav', 'mp3', 'ogg', 'flac', 'm4a']
    
    if extensao not in formatos_permitidos:
        raise HTTPException(
            status_code=400, 
            detail=f"Formato .{extensao} não suportado. A API aceita apenas áudio ({', '.join(formatos_permitidos)})."
        )

    # 2. Defesa: Salvando o arquivo em blocos de 1MB (evita estouro de memória RAM)
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{extensao}") as temp_file:
        while chunk := await file.read(1024 * 1024):
            temp_file.write(chunk)
        temp_path = temp_file.name

    try:
        # 3. Defesa: vad_filter=True ignora silêncios e acelera o processamento
        segments, info = model.transcribe(
            temp_path, 
            language="pt", 
            beam_size=5, 
            initial_prompt=prompt_tecnico,
            vad_filter=True
        )

        srt_content = ""
        for i, seg in enumerate(segments, start=1):
            inicio = format_timestamp(seg.start)
            fim = format_timestamp(seg.end)
            texto_limpo = aplicar_limpeza_manual(seg.text.strip())
            srt_content += f"{i}\n{inicio} --> {fim}\n{texto_limpo}\n\n"

        # Extrai o nome do arquivo original sem a extensão e cria o nome do SRT
        nome_arquivo_base = os.path.splitext(file.filename)[0]
        nome_srt = f"{nome_arquivo_base}_vlibras.srt"

        # Retorna forçando o download como arquivo .srt com o media_type oficial
        return Response(
            content=srt_content,
            media_type="application/x-subrip",
            headers={
                "Content-Disposition": f'attachment; filename="{nome_srt}"'
            }
        )

    finally:
        # Limpeza do arquivo temporário do servidor
        if os.path.exists(temp_path):
            os.remove(temp_path)

# Bloco para rodar a API direto do terminal do VS Code
if __name__ == "__main__":
    print("[*] Iniciando servidor local na porta 8000...")
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)