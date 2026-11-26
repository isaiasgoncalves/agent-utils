# -*- coding: utf-8 -*-
"""
baixar_imagem.py — Busca e baixa imagens da web para usar nas cenas, guardando
o crédito e a licença de cada uma em assets/imagens/creditos.json.

USO (de dentro da pasta do projeto):
  # 1) buscar candidatas com licença livre (Wikimedia Commons e Openverse)
  python <SKILL>/scripts/baixar_imagem.py buscar "Andrey Markov retrato" --n 8 --previas
  #    --previas baixa miniaturas em assets/imagens/_previas/ para você olhar (Read) antes
  # 2) baixar a escolhida pelo número da busca
  python <SKILL>/scripts/baixar_imagem.py baixar --da-busca 3 --nome markov
  # 3) ou baixar uma URL direta (figura de paper, site do autor...)
  python <SKILL>/scripts/baixar_imagem.py baixar https://site/fig2.png --nome fig2 \
         --credito "Fig. 2 de Silva et al. (2024)" --licenca "verificar" --pagina https://site/paper
  # listar o que já foi baixado e os créditos
  python <SKILL>/scripts/baixar_imagem.py creditos

Opções de busca: --fonte wikimedia|openverse|todas  --qualquer-licenca  --n 10
Respeita video.config.json -> imagens (permitir_download, pasta, licencas_aceitas, max_mb).
Converte WebP/GIF/TIFF para PNG (Manim lê PNG/JPG; SVG vira SVGMobject).
"""
import argparse, datetime, html, json, os, re, subprocess, sys, time, urllib.error, urllib.parse, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _comum import carregar_config, find_ffmpeg  # noqa: E402

UA = "manim-explainer-video/1.1 (educational explainer video tool; python-urllib)"
MAGIC = [(b"\x89PNG", ".png"), (b"\xff\xd8\xff", ".jpg"), (b"GIF8", ".gif"),
         (b"RIFF", ".webp"), (b"II*\x00", ".tif"), (b"MM\x00*", ".tif")]


def _get(url, max_bytes=None, tentativas=4):
    """GET com User-Agent e nova tentativa em 429/503 (Wikimedia limita a taxa)."""
    for k in range(tentativas):
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                dados = r.read(max_bytes + 1) if max_bytes else r.read()
                if max_bytes and len(dados) > max_bytes:
                    sys.exit(f"ERRO: arquivo maior que {max_bytes // 2**20} MB (imagens.max_mb)")
                return dados, r.headers.get("Content-Type", "")
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and k + 1 < tentativas:
                espera = min(float(e.headers.get("Retry-After") or 2 * 2 ** k), 20)
                time.sleep(espera)
                continue
            raise


def _sem_html(s):
    t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()
    w = t.split(" ")
    h = len(w) // 2
    return " ".join(w[:h]) if len(w) % 2 == 0 and w[:h] == w[h:] else t   # "X Y X Y" duplicado


def norm_licenca(s):
    s = (s or "").lower().replace("_", "-")
    if "cc0" in s or "cc-zero" in s:
        return "cc0"
    if "public domain" in s or s in ("pd", "pdm") or s.startswith("pd-"):
        return "pdm"
    m = re.search(r"by(-nc)?(-nd)?(-sa)?", s)
    if "cc" in s and m:
        return m.group(0)
    return s or "desconhecida"


def credito_curto(autor, licenca, fonte):
    if licenca and re.match(r"(cc|by)", licenca.lower()):
        licenca = licenca.upper()
    partes = [p for p in [autor and autor[:60], licenca, fonte] if p]
    return " · ".join(partes)


# ----------------------------------------------------------------- busca ---
def buscar_wikimedia(q, n):
    url = ("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
        "action": "query", "generator": "search", "gsrsearch": q, "gsrnamespace": 6,
        "gsrlimit": n, "prop": "imageinfo", "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": 1280, "format": "json"}))
    d = json.loads(_get(url)[0])
    out = []
    for p in sorted(d.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 0)):
        ii = (p.get("imageinfo") or [{}])[0]
        if not ii.get("mime", "").startswith("image/"):
            continue
        em = ii.get("extmetadata", {})
        lic = em.get("LicenseShortName", {}).get("value", "")
        out.append({"fonte": "Wikimedia Commons", "titulo": p.get("title", "").replace("File:", ""),
                    "autor": _sem_html(em.get("Artist", {}).get("value", "")),
                    "licenca": lic, "licenca_norm": norm_licenca(lic),
                    "licenca_url": em.get("LicenseUrl", {}).get("value", ""),
                    "pagina": ii.get("descriptionurl", ""),
                    "url": ii.get("thumburl") or ii.get("url"),
                    "previa": (ii.get("thumburl") or ii.get("url") or "").replace("/1280px-", "/330px-"),
                    "tamanho": f"{ii.get('width')}x{ii.get('height')}"})
    return out


def buscar_openverse(q, n, licencas):
    params = {"q": q, "page_size": n}
    lic_ok = [l for l in licencas if l in ("cc0", "pdm", "by", "by-sa", "by-nc", "by-nd", "by-nc-sa", "by-nc-nd")]
    if lic_ok:
        params["license"] = ",".join(lic_ok)
    d = json.loads(_get("https://api.openverse.org/v1/images/?" + urllib.parse.urlencode(params))[0])
    out = []
    for r in d.get("results", []):
        lic = f"{r.get('license', '')} {r.get('license_version', '') or ''}".strip()
        out.append({"fonte": f"Openverse/{r.get('source', '')}", "titulo": r.get("title", ""),
                    "autor": r.get("creator", "") or "", "licenca": lic,
                    "licenca_norm": norm_licenca("cc " + r.get("license", "") if r.get("license") not in ("cc0", "pdm") else r.get("license")),
                    "licenca_url": r.get("license_url", ""), "pagina": r.get("foreign_landing_url", ""),
                    "url": r.get("url"), "previa": r.get("thumbnail") or r.get("url"), "previa2": r.get("url"),
                    "tamanho": f"{r.get('width')}x{r.get('height')}"})
    return out


def cmd_buscar(a, ci):
    fontes = ci.get("fontes_busca", ["wikimedia", "openverse"]) if a.fonte == "todas" else [a.fonte]
    aceitas = [] if a.qualquer_licenca else ci.get("licencas_aceitas", [])
    res = []
    for f in fontes:
        try:
            res += buscar_wikimedia(a.termo, a.n) if f == "wikimedia" else buscar_openverse(a.termo, a.n, aceitas)
        except Exception as e:
            print(f"  aviso: busca em {f} falhou: {e}")
    if aceitas:
        res = [r for r in res if r["licenca_norm"] in aceitas]
    pasta = ci.get("pasta", "assets/imagens")
    os.makedirs(pasta, exist_ok=True)
    json.dump(res, open(os.path.join(pasta, "_busca.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if a.previas:
        os.makedirs(os.path.join(pasta, "_previas"), exist_ok=True)
    for i, r in enumerate(res, 1):
        print(f"[{i}] {r['titulo'][:70]}\n     {r['tamanho']} · {r['licenca'] or '?'} · {r['autor'][:50]} · {r['fonte']}\n     {r['pagina']}")
        if a.previas and r.get("previa"):
            erro = "sem URL"
            for u in [r["previa"], r.get("previa2")]:
                if not u:
                    continue
                try:
                    dados, _ = _get(u, 8 * 2**20)
                    ext = next((e for m, e in MAGIC if dados.startswith(m)), ".jpg")
                    p = os.path.join(pasta, "_previas", f"{i:02d}{ext}")
                    open(p, "wb").write(dados)
                    print(f"     prévia: {p}")
                    break
                except Exception as e:
                    erro = e
            else:
                print(f"     (prévia falhou: {erro})")
            time.sleep(0.5)                               # gentileza com os servidores
    if not res:
        print("Nada encontrado com as licenças aceitas. Tente outro termo ou --qualquer-licenca.")


# ---------------------------------------------------------------- baixar ---
def _salvar(dados, ctype, destino_sem_ext):
    ext = next((e for m, e in MAGIC if dados.startswith(m)), None)
    if ext == ".webp" and dados[8:12] != b"WEBP":
        ext = None
    if ext is None and (b"<svg" in dados[:2048] or "svg" in ctype):
        ext = ".svg"
    if ext is None:
        sys.exit(f"ERRO: o conteúdo baixado não é uma imagem reconhecida (Content-Type: {ctype})")
    if ext in (".png", ".jpg", ".svg"):
        p = destino_sem_ext + ext
        open(p, "wb").write(dados)
        return p
    bruto = destino_sem_ext + ext                        # webp/gif/tif -> png
    open(bruto, "wb").write(dados)
    p = destino_sem_ext + ".png"
    try:
        from PIL import Image
        Image.open(bruto).convert("RGBA").save(p)
    except ImportError:
        r = subprocess.run([find_ffmpeg(), "-y", "-loglevel", "error", "-i", bruto, "-frames:v", "1", p])
        if r.returncode != 0:
            sys.exit("ERRO: não consegui converter para PNG (instale Pillow)")
    os.remove(bruto)
    return p


def cmd_baixar(a, ci):
    pasta = ci.get("pasta", "assets/imagens")
    os.makedirs(pasta, exist_ok=True)
    if a.da_busca:
        busca = json.load(open(os.path.join(pasta, "_busca.json"), encoding="utf-8"))
        meta = dict(busca[a.da_busca - 1])
    elif a.url:
        meta = {"fonte": urllib.parse.urlparse(a.url).netloc, "titulo": a.nome or "", "autor": "",
                "licenca": a.licenca or "verificar", "licenca_url": "", "pagina": a.pagina or a.url, "url": a.url}
    else:
        sys.exit("Passe uma URL ou --da-busca N")
    if a.credito:
        meta["autor"] = a.credito
    nome = re.sub(r"[^\w-]+", "_", a.nome or meta.get("titulo") or "imagem").strip("_")[:50] or "imagem"
    dados, ctype = _get(meta["url"], int(ci.get("max_mb", 15) * 2**20))
    p = _salvar(dados, ctype, os.path.join(pasta, nome))
    meta.update({"arquivo": os.path.basename(p), "baixado_em": datetime.date.today().isoformat(),
                 "credito_curto": a.credito or credito_curto(meta.get("autor"), meta.get("licenca"), meta.get("fonte"))})
    meta.pop("previa", None); meta.pop("previa2", None)
    cp = os.path.join(pasta, "creditos.json")
    cred = json.load(open(cp, encoding="utf-8")) if os.path.exists(cp) else {}
    cred[meta["arquivo"]] = meta
    json.dump(cred, open(cp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"salvo: {p}\ncrédito: {meta['credito_curto']}")
    if norm_licenca(meta.get("licenca")) in ("verificar", "desconhecida"):
        print("ATENÇÃO: licença não verificada. Confirme o direito de uso antes de publicar o vídeo.")


def cmd_creditos(ci):
    cp = os.path.join(ci.get("pasta", "assets/imagens"), "creditos.json")
    if not os.path.exists(cp):
        print("Nenhuma imagem baixada ainda.")
        return
    for arq, m in json.load(open(cp, encoding="utf-8")).items():
        print(f"- {arq}: {m.get('titulo', '')} — {m.get('autor', '')} · {m.get('licenca', '')} · {m.get('pagina', '')}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("buscar")
    b.add_argument("termo")
    b.add_argument("--fonte", default="todas", choices=["todas", "wikimedia", "openverse"])
    b.add_argument("--n", type=int, default=10)
    b.add_argument("--previas", action="store_true")
    b.add_argument("--qualquer-licenca", action="store_true")
    d = sub.add_parser("baixar")
    d.add_argument("url", nargs="?")
    d.add_argument("--da-busca", type=int)
    d.add_argument("--nome")
    d.add_argument("--credito")
    d.add_argument("--licenca")
    d.add_argument("--pagina")
    sub.add_parser("creditos")
    a = ap.parse_args()
    ci = carregar_config(".")["imagens"]
    if a.cmd != "creditos" and not ci.get("permitir_download", True):
        sys.exit("Download de imagens desligado (video.config.json -> imagens.permitir_download).")
    try:
        {"buscar": lambda: cmd_buscar(a, ci), "baixar": lambda: cmd_baixar(a, ci),
         "creditos": lambda: cmd_creditos(ci)}[a.cmd]()
    except (urllib.error.URLError, OSError) as e:
        sys.exit(f"ERRO de rede: {e}. Tente de novo em alguns segundos ou use outra URL.")


if __name__ == "__main__":
    main()
