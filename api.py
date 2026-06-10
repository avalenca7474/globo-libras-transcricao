import os
import re
import tempfile
import uvicorn
import uuid
from datetime import timedelta
from fastapi import FastAPI, File, UploadFile, Response, HTTPException, BackgroundTasks
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
model = WhisperModel("large-v3", device="cpu", compute_type="int8")

# Dicionário em memória para guardar o status das transcrições
tarefas_em_andamento = {}

def format_timestamp(seconds):
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def aplicar_limpeza_manual(texto):
    for erro, correcao in DICIONARIO_LIMPEZA.items():
        padrao = re.compile(re.escape(erro), re.IGNORECASE)
        texto = padrao.sub(correcao, texto)
    return texto

# Função pesada que vai rodar em segundo plano
def processar_transcricao(task_id: str, temp_path: str, nome_arquivo_original: str):
    try:
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

        nome_arquivo_base = os.path.splitext(nome_arquivo_original)[0]
        nome_srt = f"{nome_arquivo_base}_vlibras.srt"

        # Salva o resultado no dicionário
        tarefas_em_andamento[task_id] = {
            "status": "concluido",
            "srt_content": srt_content,
            "nome_srt": nome_srt
        }

    except Exception as e:
        tarefas_em_andamento[task_id] = {
            "status": "erro",
            "detalhe": str(e)
        }
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# --- ENDPOINT 1: RECEBE O ÁUDIO E DEVOLVE UMA SENHA ---
@app.post("/gerar-srt")
async def gerar_srt(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    print(f"[*] Recebendo requisição: {file.filename}")

    extensao = file.filename.split('.')[-1].lower()
    formatos_permitidos = ['wav', 'mp3', 'ogg', 'flac', 'm4a']
    
    if extensao not in formatos_permitidos:
        raise HTTPException(status_code=400, detail="Formato não suportado.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{extensao}") as temp_file:
        while chunk := await file.read(1024 * 1024):
            temp_file.write(chunk)
        temp_path = temp_file.name

    # Gera um ID único para essa tarefa
    task_id = str(uuid.uuid4())
    tarefas_em_andamento[task_id] = {"status": "processando"}

    # Joga a função pesada para rodar em segundo plano
    background_tasks.add_task(processar_transcricao, task_id, temp_path, file.filename)

    # Retorna imediatamente para o Grupo 4 não tomar timeout
    return {
        "mensagem": "Áudio recebido com sucesso. Processamento iniciado em segundo plano.",
        "task_id": task_id,
        "status_url": f"/status/{task_id}"
    }

# --- ENDPOINT 2: GRUPO 4 CONSULTA ESSE ENDPOINT USANDO A SENHA ---
@app.get("/status/{task_id}")
async def checar_status(task_id: str):
    if task_id not in tarefas_em_andamento:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada.")

    tarefa = tarefas_em_andamento[task_id]

    if tarefa["status"] == "processando":
        return {"status": "processando", "mensagem": "A IA ainda está trabalhando. Tente novamente em alguns segundos."}
    
    elif tarefa["status"] == "erro":
        return {"status": "erro", "detalhe": tarefa["detalhe"]}
    
    elif tarefa["status"] == "concluido":
        # Se terminou, força o download do SRT
        return Response(
            content=tarefa["srt_content"],
            media_type="application/x-subrip",
            headers={
                "Content-Disposition": f'attachment; filename="{tarefa["nome_srt"]}"'
            }
        )

if __name__ == "__main__":
    print("[*] Iniciando servidor local na porta 8000...")
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)