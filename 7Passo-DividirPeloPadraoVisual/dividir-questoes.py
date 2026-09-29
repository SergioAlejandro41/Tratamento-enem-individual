from PIL import Image
import os

def converter_cor_gimp_para_rgb(gimp_r, gimp_g, gimp_b):
    """
    Converte valores do GIMP (0-100) para RGB (0-255)
    """
    r = int((gimp_r / 100) * 255)
    g = int((gimp_g / 100) * 255)
    b = int((gimp_b / 100) * 255)
    return (r, g, b)

def encontrar_faixa_alvo(imagem, cor_alvo=(167, 169, 172), tolerancia=15, altura_base=12, margem_erro=3):
    """
    Encontra posições na coluna x=1030 onde há um padrão visual com altura de 12px (±3px).
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    posicoes_corte = []
    coluna_x = 1030
    
    # Garantir que a coluna x=1030 existe na imagem
    if coluna_x >= largura:
        coluna_x = largura - 1
        print(f"Aviso: coluna 1030 fora do limite. Ajustado para x={coluna_x}")
    
    y = 0
    while y < altura:
        # Pega a cor do pixel atual na coluna 1030
        pixel = pixels[coluna_x, y]
        if len(pixel) == 4:
            r, g, b, a = pixel
        else:
            r, g, b = pixel[:3]
        
        # Verifica se o pixel inicial corresponde à cor alvo
        if (abs(r - cor_alvo[0]) <= tolerancia and 
            abs(g - cor_alvo[1]) <= tolerancia and 
            abs(b - cor_alvo[2]) <= tolerancia):
            
            inicio_padrao = y
            # Mede a altura real do bloco dessa cor
            while y < altura:
                p = pixels[coluna_x, y]
                pr, pg, pb = p[:3]
                if (abs(pr - cor_alvo[0]) <= tolerancia and 
                    abs(pg - cor_alvo[1]) <= tolerancia and 
                    abs(pb - cor_alvo[2]) <= tolerancia):
                    y += 1
                else:
                    break
            
            altura_encontrada = y - inicio_padrao
            
            # Aceita se a altura estiver entre 12 - 3 (9) e 12 + 3 (15) pixels
            if (altura_base - margem_erro) <= altura_encontrada <= (altura_base + margem_erro):
                posicao_corte = inicio_padrao - 26
                if posicao_corte < 0:
                    posicao_corte = 0
                
                posicoes_corte.append(posicao_corte)
                print(f"Padrão de {altura_encontrada}px encontrado em y={inicio_padrao}, cortando em y={posicao_corte}")
        else:
            y += 1
            
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_alvo=(167, 169, 172)):
    """
    Divide a imagem verticalmente mantendo os 26 pixels anteriores ao padrão na parte cortada.
    """
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    posicoes_corte = encontrar_faixa_alvo(imagem, cor_alvo)
    
    if not posicoes_corte:
        print("Nenhum padrão encontrado na imagem!")
        return
    
    print(f"Encontrados {len(posicoes_corte)} padrões para corte")
    
    os.makedirs(pasta_saida, exist_ok=True)
    
    posicao_anterior = 0
    
    for i, posicao_corte in enumerate(posicoes_corte):
        if posicao_corte <= posicao_anterior:
            continue
            
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        posicao_anterior = posicao_corte
    
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{len(posicoes_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    caminho_imagem = "colunas_concatenadas_verticalmente.png"  # Substitua pelo caminho da sua imagem
    pasta_saida = "colunas"           # Substitua pelo nome da pasta de saída
    
    # Cor especificada diretamente em RGB 0-255
    cor_do_padrao = (167, 169, 172)
    
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_do_padrao)
    
    print("Divisão concluída!")