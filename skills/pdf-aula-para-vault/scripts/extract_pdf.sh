#!/usr/bin/env bash
# extract_pdf.sh — ponto de partida rápido para converter um PDF de aula.
#
# Roda pdftotext (espinha textual + ordem) e pdfimages (figuras embutidas) num
# diretório temporário. NÃO substitui a leitura das páginas como imagem com a
# tool Read: o pdftotext DESCARTA as equações e não traz as figuras. Use a saída
# daqui como esqueleto e complete a matemática (LaTeX) e a conferência das
# figuras lendo o PDF como imagem.
#
# Uso: scripts/extract_pdf.sh <arquivo.pdf> [dir_saida]
#   dir_saida default: /tmp/pdfaula/<nome-do-pdf>/

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "uso: $0 <arquivo.pdf> [dir_saida]" >&2
  exit 1
fi

PDF="$1"
if [[ ! -f "$PDF" ]]; then
  echo "arquivo não encontrado: $PDF" >&2
  exit 1
fi

BASENAME="$(basename "${PDF%.*}")"
OUT="${2:-/tmp/pdfaula/$BASENAME}"
mkdir -p "$OUT/imgs"

# dependências
for bin in pdftotext pdfimages pdfinfo; do
  command -v "$bin" >/dev/null 2>&1 || {
    echo "instalando poppler-utils…" >&2
    (apt-get install -y poppler-utils >/dev/null 2>&1) || \
      pip install --break-system-packages pdf2image >/dev/null 2>&1 || true
    break
  }
done

echo "== $PDF =="
pdfinfo "$PDF" | grep -E "Pages|Page size" || true

# texto (layout preservado; equações vão faltar — normal)
pdftotext -layout "$PDF" "$OUT/texto.txt"
echo "texto  -> $OUT/texto.txt"

# figuras embutidas, numeradas na ordem de aparição
pdfimages -png "$PDF" "$OUT/imgs/img" || true
NIMG=$(find "$OUT/imgs" -name '*.png' | wc -l | tr -d ' ')
echo "figuras-> $OUT/imgs/ ($NIMG png)"

echo
echo "Próximo: leia as páginas do PDF como imagem (Read, param pages) para"
echo "transcrever as equações em LaTeX e conferir/renomear as figuras antes de"
echo "embuti-las como ![[nome.png]] no markdown."
