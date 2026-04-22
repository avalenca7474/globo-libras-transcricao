import gradio as gr
import whisper
import os
import subprocess
import json
import language_tool_python
import time

tool = language_tool_python.LanguageTool('pt-BR')

def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def update_stepper(step):
    steps = ["Upload", "Extração", "Transcrição", "Download"]
    html = '<div class="stepper-container">'
    for i, label in enumerate(steps, 1):
        status = "active" if i == step else ("done" if i < step else "")
        content = i if i >= step else "✓"
        html += f"""
        <div class="step {status}">
            <div class="step-circle">{content}</div>
            <div class="step-label">{label}</div>
        </div>
        """
    html += '</div>'
    return html

def limpar_historico():
    return (
        None,                   
        update_stepper(1),     
        "Aguardando...",       
        None,                 
        "",                   
        None                    
    )

# --- FUNÇÃO PRINCIPAL (GERADOR) ---
def processar_transcricao(video_path, tamanho_modelo, formatos, usar_correcao):
    audio_temp = "temp_audio.wav"
    arquivos_gerados = []
    srt_preview = ""
    json_preview = []
    
    yield update_stepper(1), "Iniciando processamento...", None, "", []

    try:
        # ETAPA 2: EXTRAÇÃO
        yield update_stepper(2), "⏳ Extraindo áudio do vídeo via FFmpeg...", None, "", []
        comando = f'ffmpeg -i "{video_path}" -ar 16000 -ac 1 -c:a pcm_s16le "{audio_temp}" -y'
        subprocess.run(comando, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # ETAPA 3: TRANSCRIÇÃO (WHISPER)
        yield update_stepper(3), f"🤖 Transcrevendo com modelo {tamanho_modelo}...", None, "", []
        modelo = whisper.load_model(tamanho_modelo.lower())
        
        resultado = modelo.transcribe(
            audio_temp, 
            language="pt", 
            initial_prompt="Transcrição para a Globo, foco em acessibilidade e V-Libras."
        )

        if usar_correcao:
            yield update_stepper(3), "✍️ Aplicando refinamento gramatical...", None, "", []
            for seg in resultado["segments"]:
                seg['text'] = tool.correct(seg['text'].strip())
        else:
            for seg in resultado["segments"]:
                seg['text'] = seg['text'].strip()

        # ETAPA 4: GERAÇÃO DE ARQUIVOS E PREVIEWS
        yield update_stepper(4), "📂 Gerando arquivos e previews...", None, "", []
        nome_base = "transcricao_globo_prod"

        if "SRT" in formatos:
            srt_path = f"{nome_base}.srt"
            with open(srt_path, "w", encoding="utf-8") as srt:
                for i, seg in enumerate(resultado["segments"], start=1):
                    inicio, fim = format_timestamp(seg['start']), format_timestamp(seg['end'])
                    bloco = f"{i}\n{inicio} --> {fim}\n{seg['text']}\n\n"
                    srt.write(bloco)
                    srt_preview += bloco
            arquivos_gerados.append(srt_path)

        if "JSON" in formatos:
            json_path = f"{nome_base}.json"
            json_preview = [{"id": i+1, "start": format_timestamp(s['start']), "end": format_timestamp(s['end']), "text": s['text']} 
                          for i, s in enumerate(resultado["segments"])]
            with open(json_path, "w", encoding="utf-8") as jf:
                json.dump(json_preview, jf, ensure_ascii=False, indent=4)
            arquivos_gerados.append(json_path)

        yield update_stepper(4), "✅ Processamento concluído!", arquivos_gerados, srt_preview, json_preview

    except Exception as e:
        yield update_stepper(1), f"❌ Erro: {str(e)}", None, "", []
    
    finally:
        if os.path.exists(audio_temp): 
            os.remove(audio_temp)

# --- CSS CUSTOMIZADO ---
custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
body, .gradio-container { background-color: #0B0F17 !important; font-family: 'Inter', sans-serif !important; }

.nav-header { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid #1F2937; margin-bottom: 25px; }
.nav-logo { display: flex; align-items: center; gap: 12px; color: #363636; }
.logo-box { background: #3B82F6; padding: 8px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 18px; line-height: 1; }
.logo-text { font-weight: 700; font-size: 14px; letter-spacing: 0.5px; margin: 0; padding: 0; }

.hero-title { color: #363636; font-size: 24px !important; font-weight: 700; margin-bottom: 4px; }
.hero-subtitle { color: #9CA3AF; font-size: 13px !important; margin-bottom: 25px; }

.file-upload-subtle .upload-container label span { font-size: 0px !important; } 
.file-upload-subtle .upload-container label::after { 
    content: "Fazer Upload"; 
    font-size: 14px !important; font-weight: 700; color: #3B82F6; letter-spacing: 0.5px;
}
.file-upload-subtle { border: 2px dashed #1F2937 !important; border-radius: 12px !important; background: #0D1117 !important; transition: all 0.3s; }
.file-upload-subtle:hover { border-color: #3B82F6 !important; box-shadow: 0 0 15px rgba(59, 130, 246, 0.1); }

@keyframes pulse-icon { 0% { transform: scale(1); opacity: 0.8; } 50% { transform: scale(1.1); opacity: 1; } 100% { transform: scale(1); opacity: 0.8; } }
.upload-icon-anim { font-size: 30px; animation: pulse-icon 2s infinite ease-in-out; display: block; margin-bottom: 10px; }

.custom-card { background: #111827 !important; border: 1px solid #1F2937 !important; border-radius: 12px !important; padding: 22px !important; margin-bottom: 15px; }
.btn-primary { background: #3B82F6 !important; border: none !important; border-radius: 10px !important; height: 50px !important; font-weight: 700 !important; transition: all 0.3s !important; }
.btn-primary:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(59, 130, 246, 0.3); }
.btn-clear { background: #696969 !important; border: none !important; border-radius: 10px !important; height: 50px !important; font-weight: 700 !important; transition: all 0.3s !important; }
.btn-clear:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(59, 130, 246, 0.3); }

.stepper-container { display: flex; justify-content: space-between; position: relative; margin-bottom: 30px; padding: 0 40px; }
.stepper-container::before { content: ""; position: absolute; top: 15px; left: 60px; right: 60px; height: 2px; background: #1F2937; z-index: 1; }
.step-circle { width: 32px; height: 32px; border: 2px solid #1F2937; border-radius: 50%; background: #0B0F17; display: flex; align-items: center; justify-content: center; margin: 0 auto 8px; color: #4B5563; font-weight: bold; z-index: 2; position: relative; transition: all 0.4s; }
.step.active .step-circle { border-color: #3B82F6; color: #3B82F6; box-shadow: 0 0 15px rgba(59, 130, 246, 0.4); transform: scale(1.1); }
.step.done .step-circle { background: #3B82F6; border-color: #3B82F6; color: #363636; }
"""

with gr.Blocks(css=custom_css, title="Globo Transcrição v4.0") as demo:
    
    # NAVBAR
    gr.HTML("""
    <div class="nav-header">
        <div class="nav-logo">
            <div class="logo-box">📺</div>
            <div class="logo-text">RESIDÊNCIA GLOBO — SPRINT 04</div>
        </div>
        <div style="color: #9CA3AF; font-size: 11px; font-weight: 600;">UNICAP | SISTEMAS PARA A INTERNET</div>
    </div>
    """)

    gr.HTML("""
    <h1 class="hero-title">Transcrição Profissional</h1>
    <p class="hero-subtitle">Pipeline minimalista otimizado para acessibilidade e V-Libras.</p>
    """)

    stepper_html = gr.HTML(update_stepper(1))

    with gr.Row():
        # COLUNA ESQUERDA: INPUTS
        with gr.Column(scale=1):
            with gr.Column(elem_classes="custom-card"):
                gr.HTML('<div style="text-align:center;"><span class="upload-icon-anim">📤</span></div>')
                video_input = gr.File(label=None, container=False, elem_classes="file-upload-subtle")
                
                with gr.Row():
                    #BASE
                    modelo_input = gr.Dropdown(label="IA", choices=["Base", "Small", "Medium"], value="Small")
                    formatos_input = gr.CheckboxGroup(label="FORMATOS", choices=["SRT", "JSON"], value=["SRT", "JSON"])
                
                correcao_toggle = gr.Checkbox(label="Refinamento gramatical", value=False)

            btn = gr.Button("🚀 INICIAR PROCESSAMENTO", variant="primary", elem_classes="btn-primary")
            btn_clear = gr.Button("🗑️ LIMPAR HISTÓRICO", elem_classes="btn-clear")

        # COLUNA DIREITA: PROGRESSO E PREVIEWS
        with gr.Column(scale=1):
            with gr.Column(elem_classes="custom-card"):
                gr.HTML("<b style='color: #363636; font-size: 13px;'>STATUS & DOWNLOAD</b>")
                status_box = gr.Textbox(show_label=False, placeholder="Aguardando...", container=False, interactive=False, lines=2)
                files_output = gr.File(label=None, container=False, file_count="multiple")
            
            with gr.Tabs(elem_classes="custom-card"):
                with gr.TabItem("📄 Preview SRT"):
                    srt_view = gr.Textbox(label=None, lines=8, interactive=False, container=False)
                with gr.TabItem("📦 Preview JSON"):
                    json_view = gr.JSON(label=None)

    with gr.Accordion("❓ Informação sobre Fidelidade", open=False):
        gr.Markdown("O refinamento gramatical começa desativado para preservar a intenção original do falante. Para o V-Libras e Avatares 3D, capturar gírias e marcas de oralidade é essencial para uma tradução com sentido e emoção.")

    # EVENTOS
    btn.click(
        fn=processar_transcricao,
        inputs=[video_input, modelo_input, formatos_input, correcao_toggle],
        outputs=[stepper_html, status_box, files_output, srt_view, json_view]
    )

    btn_clear.click(
        fn=limpar_historico,
        outputs=[video_input, stepper_html, status_box, files_output, srt_view, json_view]
    )

if __name__ == "__main__":
    demo.launch(share=False)