#!/usr/bin/env python3
"""
injetar_arquivo.py

Grava um arquivo editado no seu Windows dentro do disco-ponte (ponte.img),
para depois ser lido de dentro do MINIX (via /dev/c0d1) e copiado para o
lugar certo no kernel.

USO:
    python injetar_arquivo.py ponte.img proc.c

Isso escreve o conteudo de proc.c no comeco do ponte.img, e imprime o
tamanho exato em bytes -- anote esse numero, voce vai precisar dele no
comando "dd" dentro do MINIX.
"""
import sys

def main():
    if len(sys.argv) != 3:
        print("uso: python injetar_arquivo.py <ponte.img> <arquivo_editado>")
        sys.exit(1)

    ponte_path = sys.argv[1]
    file_path = sys.argv[2]

    with open(file_path, 'rb') as f:
        content = f.read()

    size = len(content)

    # le o ponte.img inteiro, sobrescreve o inicio com o novo conteudo,
    # mantem o resto (nao importa, so precisamos dos primeiros `size` bytes)
    with open(ponte_path, 'r+b') as f:
        f.seek(0)
        f.write(content)

    print(f"OK: {file_path} ({size} bytes) gravado no inicio de {ponte_path}")
    print(f"")
    print(f">>> ANOTE ESSE NUMERO: {size} bytes <<<")
    print(f"")
    print(f"Dentro do MINIX, use:")
    print(f"    dd if=/dev/c0d1 of=proc_novo.c bs={size} count=1")

if __name__ == "__main__":
    main()
