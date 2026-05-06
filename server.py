"""
MCP Inspector Example - Eğitim Amaçlı Demo MCP Sunucusu
========================================================

Bu dosya; Model Context Protocol (MCP) konseptlerini sıfırdan öğrenmek
isteyenler için hazırlanmış, üzerinde MCP Inspector ile rahatça
oynanabilen bir referans sunucudur.

İçinde şu üç MCP kavramının da örneği vardır:

  1) Tools    -> LLM'in ÇAĞIRABİLECEĞİ fonksiyonlar
  2) Resources -> LLM'in OKUYABİLECEĞİ veri/context kaynakları
  3) Prompts  -> Kullanıcının kullanabileceği parametrik prompt şablonları

Çalıştırmak için:
    pip install -r requirements.txt
    python server.py

MCP Inspector ile test etmek için:
    npx @modelcontextprotocol/inspector python server.py
"""

from __future__ import annotations

import datetime
import os
import random
from typing import Any

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# .env dosyasını yükle (varsa). Repo'ya .env COMMIT ETME!
# Örnek değerler için .env.example dosyasına bak.
load_dotenv()


mcp = FastMCP("InspectorDemoSunucusu")


# ============================================================
# 1) TOOLS - LLM'in çalıştırabileceği fonksiyonlar
# ============================================================
#
# Her @mcp.tool() dekoratörü, LLM'e yeni bir "yetenek" verir.
# DİKKAT: Fonksiyonun docstring'i (üç tırnak içindeki açıklama)
# LLM'in tool'u ne zaman çağıracağını anlamasında kritik rol oynar.
# Açıklamayı kısa ama "ne işe yarar / hangi parametreyi alır"
# bilgisini net verecek şekilde yaz.
# ============================================================


@mcp.tool()
def selamla(isim: str) -> str:
    """Kullanıcıyı ismi ile karşılayan bir metin döndürür.

    Parametreler:
        isim: Karşılanacak kişinin ismi (örn. "Alperen").
    """
    return f"Merhaba {isim}, MCP dünyasına hoş geldin!"


@mcp.tool()
def topla(a: float, b: float) -> float:
    """İki sayıyı toplar ve sonucu döndürür.

    Parametreler:
        a: Birinci sayı.
        b: İkinci sayı.
    """
    return a + b


@mcp.tool()
def simdiki_zaman(timezone_offset_hours: int = 0) -> str:
    """Sunucunun bulunduğu makinenin saatini ISO 8601 formatında döner.

    Parametreler:
        timezone_offset_hours: UTC'ye göre saat farkı (örn. Türkiye için 3).
            Default = 0 (yerel saat).
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    if timezone_offset_hours:
        now = now + datetime.timedelta(hours=timezone_offset_hours)
    return now.strftime("%Y-%m-%d %H:%M:%S")


@mcp.tool()
def zar_at(yuz_sayisi: int = 6, adet: int = 1) -> dict[str, Any]:
    """Belirtilen yüzlü zarı, istenilen sayıda atar.

    Parametreler:
        yuz_sayisi: Zarın yüz sayısı (default 6, min 2, max 1000).
        adet: Kaç adet zar atılacak (default 1, max 100).
    """
    if yuz_sayisi < 2 or yuz_sayisi > 1000:
        raise ValueError("yuz_sayisi 2 ile 1000 arasında olmalı.")
    if adet < 1 or adet > 100:
        raise ValueError("adet 1 ile 100 arasında olmalı.")

    sonuclar = [random.randint(1, yuz_sayisi) for _ in range(adet)]
    return {
        "atilan_zar": f"d{yuz_sayisi}",
        "adet": adet,
        "sonuclar": sonuclar,
        "toplam": sum(sonuclar),
    }


# --- Stateful (durum tutan) tool örneği ---------------------
# Bu liste, sunucu çalıştığı sürece bellekte kalır.
# Sunucu durunca veriler silinir; gerçek hayatta DB kullanın!

_gorevler: list[dict[str, Any]] = []


@mcp.tool()
def gorev_ekle(baslik: str) -> str:
    """Görev listesine yeni bir görev (TODO) ekler.

    Parametreler:
        baslik: Görevin başlığı (örn. "Sunum hazırla").
    """
    if not baslik.strip():
        raise ValueError("Görev başlığı boş olamaz.")
    yeni = {
        "id": len(_gorevler) + 1,
        "baslik": baslik.strip(),
        "tamamlandi": False,
        "olusturulma": datetime.datetime.now().isoformat(timespec="seconds"),
    }
    _gorevler.append(yeni)
    return f"#{yeni['id']} '{yeni['baslik']}' eklendi. Toplam görev: {len(_gorevler)}"


@mcp.tool()
def gorev_tamamla(gorev_id: int) -> str:
    """Verilen ID'li görevi 'tamamlandı' olarak işaretler.

    Parametreler:
        gorev_id: gorev_ekle ile dönen ID değeri.
    """
    for g in _gorevler:
        if g["id"] == gorev_id:
            if g["tamamlandi"]:
                return f"#{gorev_id} zaten tamamlanmış."
            g["tamamlandi"] = True
            return f"#{gorev_id} '{g['baslik']}' tamamlandı olarak işaretlendi."
    return f"Hata: #{gorev_id} ID'li görev bulunamadı."


@mcp.tool()
def gorev_listele(sadece_acik: bool = False) -> str:
    """Mevcut görev listesini döner.

    Parametreler:
        sadece_acik: True ise yalnızca tamamlanmamış görevleri listeler.
    """
    if not _gorevler:
        return "Görev listesi boş."

    secili = [g for g in _gorevler if (not sadece_acik or not g["tamamlandi"])]
    if not secili:
        return "Açık görev kalmadı, tebrikler!"

    satirlar = [f"Toplam {len(secili)} görev:"]
    for g in secili:
        durum = "[x]" if g["tamamlandi"] else "[ ]"
        satirlar.append(f"  {durum} #{g['id']} {g['baslik']}")
    return "\n".join(satirlar)


# --- .env'den okuyan tool örneği ----------------------------
# MCP sunucularında token / API key gibi gizli değerler genellikle .env
# dosyasına konulur ve `python-dotenv` ile süreç ortamına yüklenir.
# Aşağıdaki tool, DEMO_API_KEY ve DEMO_USER ortam değişkenlerini OKUR.
# Inspector'dan çağırarak "env yokken ne olur, varken ne olur" senaryosunu
# kendi gözlerinle görebilirsin.


def _maskele(deger: str, gosterilecek: int = 4) -> str:
    """Bir gizli değerin sadece son birkaç karakterini gösterir."""
    if not deger:
        return "(boş)"
    if len(deger) <= gosterilecek:
        return "*" * len(deger)
    return "*" * (len(deger) - gosterilecek) + deger[-gosterilecek:]


@mcp.tool()
def kimligimi_dogrula() -> str:
    """.env içindeki DEMO_API_KEY'i okuyarak basit bir doğrulama yapar.

    Senaryo:
      - .env dosyası yoksa veya DEMO_API_KEY tanımsızsa hata mesajı döner.
      - DEMO_API_KEY = "demo-1234" ise "geçerli kullanıcı" simülasyonu yapar.
      - Başka bir değer ise "geçersiz" döner.

    Bu, gerçek hayattaki "Bearer token / API key ile dış sisteme istek atan
    tool'un nasıl olur?" sorusunun en basit hâlidir.
    """
    api_key = os.environ.get("DEMO_API_KEY", "").strip()
    user = os.environ.get("DEMO_USER", "").strip() or "anonim"

    if not api_key:
        return (
            "Hata: DEMO_API_KEY ortam değişkeni tanımlı değil.\n"
            "Çözüm: .env.example dosyasını .env olarak kopyala ve değerleri doldur."
        )

    if api_key == "demo-1234":
        return (
            f"OK — Kimlik doğrulandı.\n"
            f"  Kullanıcı : {user}\n"
            f"  API key   : {_maskele(api_key)}\n"
            f"  (Bu sadece bir demo; gerçek API çağrısı yapılmadı.)"
        )

    return (
        f"FAIL — Geçersiz API key.\n"
        f"  Kullanıcı     : {user}\n"
        f"  Verilen key   : {_maskele(api_key)}\n"
        f"  Beklenen      : 'demo-1234' (sadece bu demo için)"
    )


# ============================================================
# 2) RESOURCES - LLM'in okuyabileceği context kaynakları
# ============================================================
#
# Resource'lar tool gibi "çağrılan" şeyler değildir. LLM (veya kullanıcı)
# bir URI'yi okur ve içeriğini context'ine alır. Konfigürasyon, doküman,
# veritabanı kayıtları gibi statik/yarı-statik veriler için idealdir.
# ============================================================


@mcp.resource("config://app")
def app_config() -> str:
    """Uygulamanın statik ayarlarını döner."""
    return (
        "App: InspectorDemoSunucusu\n"
        "Versiyon: 1.0.0\n"
        "Dil: Türkçe\n"
        "Log seviyesi: INFO\n"
        "Maks görev sayısı: sınırsız (bellekte tutulur)\n"
    )


@mcp.resource("docs://mcp-nedir")
def mcp_nedir() -> str:
    """MCP konseptini kısaca anlatan bir doküman."""
    return (
        "Model Context Protocol (MCP), LLM'lerin dış dünya ile (API, dosya,\n"
        "veritabanı vb.) standart bir şekilde konuşmasını sağlayan açık\n"
        "kaynaklı bir protokoldür. Bir MCP sunucusu üç tür yetenek sunar:\n"
        "  - Tools     : LLM'in çağırabildiği fonksiyonlar.\n"
        "  - Resources : LLM'in okuyabildiği veri kaynakları.\n"
        "  - Prompts   : Kullanıcı için hazır prompt şablonları.\n"
    )


@mcp.resource("env://status")
def env_status() -> str:
    """Tanımlı olan demo env değişkenlerini (maskelenmiş) gösterir.

    Inspector'da bu kaynağı Read ettiğinde .env dosyanın doğru yüklenip
    yüklenmediğini hızlıca anlarsın. Gerçek değer GÖSTERİLMEZ; sadece son
    4 karakter görünür.
    """
    izlenen = ["DEMO_API_KEY", "DEMO_USER", "DEMO_BASE_URL"]
    satirlar = ["# Demo ortam değişkenleri:"]
    for k in izlenen:
        v = os.environ.get(k, "").strip()
        if not v:
            satirlar.append(f"  {k:<14} = (tanımsız)")
        else:
            satirlar.append(f"  {k:<14} = {_maskele(v)}")
    return "\n".join(satirlar)


@mcp.resource("tasks://hepsi")
def tasks_resource() -> str:
    """Anlık görev listesinin tamamını JSON benzeri formatta döner.

    Bu resource, gorev_ekle / gorev_tamamla tool'ları ile dinamik olarak
    değişir. Inspector'da 'Resources' sekmesinden tekrar 'Read' yaparak
    güncel halini görebilirsin.
    """
    if not _gorevler:
        return "[]"
    satirlar = ["["]
    for i, g in enumerate(_gorevler):
        virgul = "," if i < len(_gorevler) - 1 else ""
        satirlar.append(
            f'  {{"id": {g["id"]}, "baslik": "{g["baslik"]}", '
            f'"tamamlandi": {str(g["tamamlandi"]).lower()}}}{virgul}'
        )
    satirlar.append("]")
    return "\n".join(satirlar)


# ============================================================
# 3) PROMPTS - Kullanıcı için hazır prompt şablonları
# ============================================================
#
# Prompt'lar, son kullanıcının (örn. Claude Desktop'ta seni kullanan kişi)
# bir işi başlatmak için tıklayıp parametre girebileceği hazır şablonlardır.
# LLM'in kendisi bunları doğrudan "çağırmaz", kullanıcı seçer.
# ============================================================


@mcp.prompt()
def kod_inceleme_prompt(dil: str = "Python", odak: str = "performans") -> str:
    """Bir kod parçasını incelemek için hazırlanmış prompt şablonu.

    Parametreler:
        dil: İncelenecek kodun dili (Python, TypeScript, Go ...).
        odak: İnceleme odağı (performans, güvenlik, okunabilirlik ...).
    """
    return (
        f"Sen kıdemli bir {dil} geliştiricisisin. Aşağıdaki kodu özellikle "
        f"'{odak}' açısından incele. Bulduğun her sorun için (1) sorunu, "
        f"(2) nedenini, (3) önerdiğin düzeltmeyi madde madde yaz. "
        f"En sonunda ise 1-10 arası genel bir kalite puanı ver.\n\n"
        f"```{dil.lower()}\n# kodu buraya yapıştır\n```"
    )


@mcp.prompt()
def ozetle_prompt(uzunluk: str = "kisa") -> str:
    """Bir metni özetlemek için prompt şablonu.

    Parametreler:
        uzunluk: 'kisa' | 'orta' | 'detayli'.
    """
    eslesme = {
        "kisa": "1-2 cümlelik tek paragraf",
        "orta": "5-6 cümlelik tek paragraf",
        "detayli": "madde madde, başlıklarla ayrılmış detaylı",
    }
    stil = eslesme.get(uzunluk, eslesme["kisa"])
    return (
        f"Aşağıdaki metni {stil} bir biçimde Türkçe özetle. "
        "Önemli sayısal verileri ve kişi/yer/şirket isimlerini koru.\n\n"
        "---\n<metni buraya yapıştır>\n---"
    )


# ============================================================
# Sunucuyu başlat
# ============================================================
if __name__ == "__main__":
    # stdio = MCP Inspector ve Claude Desktop'ın beklediği standart kanal.
    mcp.run(transport="stdio")
