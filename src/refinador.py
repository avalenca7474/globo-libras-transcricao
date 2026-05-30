import json
import re
from openai import OpenAI # Funciona com GPT-4o ou Llama 3 local via Ollama

class RefinadorContextual:
    def __init__(self, api_key=None, base_url=None):
        # Se usar Ollama local (aproveitando sua RX 7600), o base_url é http://localhost:11434/v1
        self.client = OpenAI(api_key=api_key or "ollama", base_url=base_url)
        
        # O "Cérebro" da operação: Instruções rigorosas para manter a alma da fala
        self.system_prompt = (
            "Você é um especialista em linguística e acessibilidade da Globo. "
            "Sua tarefa é corrigir erros fonéticos e de sentido, além de melhorar a frase entendendo o contexto, de uma transcrição SRT gerada por IA. "
            "DIRETRIZES RIGOROSAS:\n"
            "1. Corrija apenas o que for claramente um erro de audição (ex: 'pão no jar' -> 'plano já').\n"
            "2. PRESERVE gírias, regionalismos e contrações (tô, pra, cê, saca, mó, umas). E se atente para termos como (cremeira), que não existe, e troque por (cremosa)\n"
            "3. NÃO formalize a fala. Se o falante usa 'nós fumo', mantenha para o V-Libras.\n"
            "4. Mantenha o contexto da frase.\n"
            "5. Retorne APENAS o texto corrigido, sem explicações."
            "6. Palavras que não que não fazem sentido juntas como (morre regaço) e (nós dois semanas) são na verdade (Mó arregaço) e (Umas duas semanas), se atente para gírias regionalizadas"
            "7. Validação Semântica: O sentido lógico da frase precede a gíria. Não substitua substantivos ou objetos centrais por gírias se o resultado for incompreensível (ex: 'aplicativos quebram restaurantes' tem lógica, 'quebram mó' não tem)."
            "8. Se o Whisper transcreveu NOMES ou APELIDOS como 'Galdinho' ou 'Galdin', MANTENHA"
        )

    def processar_texto(self, texto_bruto):
        """Envia o bloco de texto para o LLM refinar o contexto."""
        response = self.client.chat.completions.create(
            model="llama3", # Ou gpt-4o se preferir nuvem
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Refine este texto mantendo a regionalidade: {texto_bruto}"}
            ],
            temperature=0.3 # Baixa temperatura para evitar que a IA 'invente' muito
        )
        return response.choices[0].message.content

    def refinar_srt(self, caminho_srt, output_path):
        """Lê o SRT, limpa os blocos e reconstrói com o texto refinado."""
        with open(caminho_srt, 'r', encoding='utf-8') as f:
            conteudo = f.read()

        # Regex para separar blocos de SRT (ID, Tempo, Texto)
        blocos = re.findall(r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3})\n(.*?)(?=\n\n|\Z)', conteudo, re.DOTALL)
        
        srt_refinado = []
        print(f"[*] Refinando {len(blocos)} segmentos...")

        for id_bloco, tempo, texto in blocos:
            texto_limpo = self.processar_texto(texto.replace('\n', ' '))
            srt_refinado.append(f"{id_bloco}\n{tempo}\n{texto_limpo}\n\n")
            print(f"[#] Bloco {id_bloco} corrigido.")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(srt_refinado)
        
        print(f"[+] Arquivo refinado salvo em: {output_path}")

if __name__ == "__main__":
    # Para rodar local na sua RX 7600 usando Ollama:
    refinador = RefinadorContextual(base_url="http://localhost:11434/v1")
    refinador.refinar_srt("transcricao_final.srt", "transcricao_100_limpa.srt")    