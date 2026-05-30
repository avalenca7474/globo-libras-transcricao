import whisper
import os
import subprocess
import json
import time
from datetime import timedelta

class TranscritorGloboPro:
    def __init__(self):
        self.modelos_disponiveis = {
            "tiny": "Velocidade máxima, precisão reduzida (~1GB VRAM)",
            "base": "Equilíbrio entre velocidade e peso (~1GB VRAM)",
            "small": "Otimizado para desktops padrão (~2GB VRAM)",
            "medium": "Alta precisão, recomendado para sua RX 7600 (~5GB VRAM)",
            "large": "Máxima precisão, processamento lento (~10GB VRAM)"
        }
        
        self.prompt_tecnico = (
            "Transcrição para a Globo. Termos: GloboPlay, V-Libras, Projac, "
            "Gshow, Jornal Nacional, UNICAP. Mantenha sotaques regionais."
        )

    def format_timestamp(self, seconds):
        """Converte segundos para o formato SRT: HH:MM:SS,mmm"""
        td = timedelta(seconds=seconds)
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        secs = total_seconds % 60
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def processar(self, video_path, model_size="medium", output_name="transcricao_final"):
        if model_size not in self.modelos_disponiveis:
            print(f"[!] Modelo {model_size} inválido. Usando 'small'.")
            model_size = "small"

        start_time = time.time()
        audio_temp = f"temp_{int(start_time)}.wav"
        
        try:
            print(f"[*] Carregando modelo: {model_size.upper()}...")
            modelo_ia = whisper.load_model(model_size)

            print(f"[*] Extraindo áudio de: {video_path}")
            comando = ['ffmpeg', '-i', video_path, '-ar', '16000', '-ac', '1', '-c:a', 'pcm_s16le', audio_temp, '-y']
            subprocess.run(comando, capture_output=True, check=True)

            print(f"[*] Iniciando Transcrição...")
            resultado = modelo_ia.transcribe(audio_temp, language="pt", initial_prompt=self.prompt_tecnico)

            # --- GERAÇÃO DO SRT ---
            srt_content = ""
            for i, seg in enumerate(resultado["segments"], start=1):
                inicio = self.format_timestamp(seg['start'])
                fim = self.format_timestamp(seg['end'])
                srt_content += f"{i}\n{inicio} --> {fim}\n{seg['text'].strip()}\n\n"

            with open(f"{output_name}.srt", "w", encoding="utf-8") as srt_file:
                srt_file.write(srt_content)

            # --- GERAÇÃO DO JSON (Grupo 3) ---
            json_output = [
                {
                    "id": i + 1,
                    "start": self.format_timestamp(s['start']),
                    "end": self.format_timestamp(s['end']),
                    "text": s['text'].strip()
                } 
                for i, s in enumerate(resultado["segments"])
            ]

            with open(f"{output_name}.json", "w", encoding="utf-8") as jf:
                json.dump(json_output, jf, ensure_ascii=False, indent=4)

            print(f"[+] Sucesso! Arquivos .srt e .json gerados em {time.time() - start_time:.2f}s")
            return json_output

        except Exception as e:
            print(f"[!] Erro no pipeline: {str(e)}")
        finally:
            if os.path.exists(audio_temp):
                os.remove(audio_temp)

if __name__ == "__main__":
    app = TranscritorGloboPro()
    app.processar("26-03-30_LibrasTrechosBaseLimpa_Encantados.mp4", model_size="medium")