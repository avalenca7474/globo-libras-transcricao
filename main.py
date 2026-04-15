import gradio as gr
import whisper
import os
import subprocess
import json

def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def processar_transcricao(video_path, tamanho_modelo, formatos):
    # 1. Extração de áudio
    audio_temp = "temp_audio.wav"
    comando = f'ffmpeg -i "{video_path}" -ar 16000 -ac 1 -c:a pcm_s16le "{audio_temp}" -y'
    subprocess.run(comando, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 2. IA Whisper
    modelo = whisper.load_model(tamanho_modelo.lower())
    resultado = modelo.transcribe(video_path, language="pt")
    
    arquivos_gerados = []
    nome_base = "transcricao_globo"
    resumo_texto = ""

    # 3. Gerar SRT
    if "SRT" in formatos:
        srt_path = f"{nome_base}.srt"
        with open(srt_path, "w", encoding="utf-8") as srt:
            for i, seg in enumerate(resultado["segments"], start=1):
                inicio, fim = format_timestamp(seg['start']), format_timestamp(seg['end'])
                srt.write(f"{i}\n{inicio} --> {fim}\n{seg['text'].strip()}\n\n")
        arquivos_gerados.append(srt_path)
        resumo_texto += "✅ Legenda SRT gerada.\n"

    # 4. Gerar JSON (Pedido do Grupo 3)
    if "JSON" in formatos:
        json_path = f"{nome_base}.json"
        dados_json = [{"id": i+1, "start": format_timestamp(s['start']), "end": format_timestamp(s['end']), "text": s['text'].strip()} 
                      for i, s in enumerate(resultado["segments"])]
        with open(json_path, "w", encoding="utf-8") as jf:
            json.dump(dados_json, jf, ensure_ascii=False, indent=4)
        arquivos_gerados.append(json_path)
        resumo_texto += "✅ Arquivo JSON (Avatar 3D) gerado.\n"

    # Limpeza
    if os.path.exists(audio_temp): os.remove(audio_temp)
    
    return resumo_texto, arquivos_gerados

# --- INTERFACE GRADIO ---
with gr.Blocks(theme=gr.themes.Soft(), title="Transcrição Globo - Sprint 03") as demo:
    gr.Markdown("# Transcrição de Vídeo para Acessibilidade")
    gr.Markdown("Protótipo funcional para geração de legendas e dados para o Avatar 3D.")
    
    with gr.Row():
        with gr.Column():
            video_input = gr.File(label=" Selecione o arquivo de vídeo da Globo")
            modelo_input = gr.Dropdown(["Base", "Small", "Medium"], label=" Tamanho do Modelo (IA)", value="Small")
            formatos_input = gr.CheckboxGroup(["SRT", "JSON"], label=" Formatos de Saída", value=["SRT", "JSON"])
            btn = gr.Button(" Iniciar Processamento", variant="primary")
        
        with gr.Column():
            status_output = gr.Textbox(label="Status")
            files_output = gr.File(label="⬇️ Baixe seus arquivos aqui", file_count="multiple")

    btn.click(
        fn=processar_transcricao, 
        inputs=[video_input, modelo_input, formatos_input], 
        outputs=[status_output, files_output]
    )

if __name__ == "__main__":
    demo.launch(share=False) 