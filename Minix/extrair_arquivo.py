#!/usr/bin/env python3
"""
extrair_arquivo.py

Le arquivos diretamente de dentro da imagem MINIX.MNX, sem precisar
abrir o QEMU. Funciona porque a imagem contem um sistema de arquivos
Minix V2 que este script sabe interpretar.

USO (no PowerShell, na mesma pasta onde estao MINIX.MNX e minixfs.py):

    python extrair_arquivo.py MINIX.MNX src/kernel/proc.c proc.c
    python extrair_arquivo.py MINIX.MNX src/kernel/proc.h proc.h
    python extrair_arquivo.py MINIX.MNX src/kernel/clock.c clock.c
    python extrair_arquivo.py MINIX.MNX src/kernel/table.c table.c

Isso cria uma copia local (proc.c, proc.h, etc) que voce pode abrir
e editar normalmente no VS Code.

Requisitos: Python 3 instalado no Windows (nao precisa instalar nada
mais, so usa bibliotecas padrao). O arquivo minixfs.py precisa estar
na mesma pasta.
"""
import sys
from minixfs import MinixFS

# Partição onde o /usr fica montado (3a partição, "p2").
# Se sua imagem for diferente, rode com --listpartitions para descobrir.
USR_PARTITION_START_SECTOR = 11074

def main():
    if len(sys.argv) < 2:
        print("uso: python extrair_arquivo.py <imagem.MNX> [caminho/dentro/do/usr] [arquivo_saida]")
        print("exemplo: python extrair_arquivo.py MINIX.MNX src/kernel/proc.c proc.c")
        sys.exit(1)

    image_path = sys.argv[1]
    data = open(image_path, 'rb').read()
    fs = MinixFS(data, USR_PARTITION_START_SECTOR * 512)

    if len(sys.argv) == 2:
        # sem caminho: lista a raiz do /usr para explorar
        root = fs.read_inode(1)
        print("Conteudo de /usr:")
        for name in sorted(fs.list_dir(root)):
            print(" ", name)
        return

    inner_path = sys.argv[2]
    out_path = sys.argv[3] if len(sys.argv) > 3 else inner_path.split('/')[-1]

    content = fs.read_path(inner_path)
    with open(out_path, 'wb') as f:
        f.write(content)
    print(f"OK: /usr/{inner_path} -> {out_path} ({len(content)} bytes)")

if __name__ == "__main__":
    main()
