# Tutorial - Alterando o MINIX 
(Certifique-se de estar no endereço da pasta pelo terminal)
(Sempre substitua "nome" nos comandos pelo nome do arquivo que você está usando (FCFS, LOTTERY, PRIORITY...))

## Passo 1 — Criar uma ponte e fazer uma cópia do disco

```powershell
fsutil file createnew ponte.img 10485760
```

```powershell
Copy-Item MINIX.MNX MINIX_NOME.MNX
```

---

## Passo 2 — Injetar um arquivo no disco-ponte

> **Anote o número de bytes** que aparecer na saída do script. Você vai precisar dele no comando `dd`.

```powershell
python injetar_arquivo.py ponte.img proc_NOME.h
```

---

## Passo 3 — Iniciar o MINIX

```powershell
qemu-system-i386 -machine pc -cpu pentium3 -m 128 -drive file=MINIX_NOME.MNX,format=raw,if=ide -drive file=ponte.img,format=raw,if=ide -vga std -net none
```

---

## Passo 4 — Copiar o arquivo para o MINIX

Dentro do MINIX:

```sh
cd /usr/src/kernel
```

```sh
cp proc.h proc.h.backup
```

```sh
dd if=/dev/c0d1 of=proc.h bs=NUMERO_QUE_APARECEU count=1
```

Substitua `NUMERO_QUE_APARECEU` pelo valor informado pelo script no Passo 2.

---

## Passo 5 — Repetir para os outros arquivos

Feche o QEMU.

### Para `proc.c`

No PowerShell:

```powershell
python injetar_arquivo.py ponte.img proc.c
```

Abra novamente o QEMU usando o mesmo comando do **Passo 3**.

Dentro do MINIX:

```sh
cd /usr/src/kernel
```

```sh
cp proc.c proc.c.backup
```

```sh
dd if=/dev/c0d1 of=proc.c bs=NUMERO_QUE_APARECEU count=1
```

---

Feche novamente o QEMU.

### Para `clock.c`

No PowerShell:

```powershell
python injetar_arquivo.py ponte.img clock.c
```

Abra novamente o QEMU usando o comando do **Passo 3**.

Dentro do MINIX:

```sh
cd /usr/src/kernel
```

```sh
cp clock.c clock.c.backup
```

```sh
dd if=/dev/c0d1 of=clock.c bs=NUMERO_QUE_APARECEU count=1
```

---

## Passo 6 — Compilar o sistema

Dentro do MINIX:

```sh
cd /usr/src/tools
```

```sh
make hdboot
```

---

## Passo 7 — Reiniciar

```sh
reboot
```

Se o MINIX travar durante o reinício, feche a janela do QEMU, abra novamente usando o comando do **Passo 3** e inicialize normalmente.

---

## Passo 8 — Executar os testes

```sh
cd /root/bench
```

```sh
make
```

```sh
./ex1.sh
```
