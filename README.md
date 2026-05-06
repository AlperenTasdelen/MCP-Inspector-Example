# MCP Inspector Example

Sıfırdan Model Context Protocol (MCP) öğrenmek isteyenler için **uçtan uca,
çalışır durumda, Türkçe yorumlanmış** bir örnek MCP sunucusu. Bu repo;

- Bir MCP sunucusunun nasıl yazıldığını,
- Sunucudaki **Tools / Resources / Prompts** kavramlarının üçünün de nasıl
  görüneceğini,
- Yazdığın sunucuyu **MCP Inspector** ile tarayıcı üzerinden nasıl test
  edeceğini

tek bir dosyada gösterir.

> Hedef: "Klonla → kur → `npx ... inspector` çalıştır → arayüzde tıkla, dene".
> Üç dakikada MCP'nin ne olduğunu hissetmen.

---

## İçindekiler

1. [MCP nedir, ne işe yarar?](#mcp-nedir-ne-işe-yarar)
2. [Bu repoda ne var?](#bu-repoda-ne-var)
3. [Gereksinimler](#gereksinimler)
4. [Kurulum](#kurulum)
5. [Sunucuyu çalıştırma](#sunucuyu-çalıştırma)
6. [MCP Inspector ile inceleme](#mcp-inspector-ile-inceleme)
7. [Inspector'da neyi nereden test edeceksin?](#inspectorda-neyi-nereden-test-edeceksin)
8. [Claude Desktop / Cursor'a bağlama](#claude-desktop--cursora-bağlama)
9. [Kendi tool'unu nasıl eklersin?](#kendi-toolunu-nasıl-eklersin)
10. [Sık karşılaşılan sorunlar (Troubleshooting)](#sık-karşılaşılan-sorunlar-troubleshooting)

---

## MCP nedir, ne işe yarar?

**Model Context Protocol (MCP)**, Anthropic öncülüğünde geliştirilen,
LLM'lerin (Claude, GPT vs.) dış dünya ile **standart** bir şekilde konuşmasını
sağlayan açık kaynak bir protokoldür. USB-C nasıl tek tip bir kabloyla onlarca
cihazı bilgisayara bağlıyorsa, MCP de tek tip bir arayüzle LLM'leri
fonksiyonlara, dosyalara, API'lara bağlar.

Bir MCP sunucusu üç tür yetenek sunar:

| Tür | Ne işe yarar? | Kim çağırır? |
| --- | --- | --- |
| **Tools** | LLM'in **çağırabildiği** fonksiyonlar (örn. `oc_list_pods`, `get_weather`). | LLM'in kendisi. |
| **Resources** | LLM'in **okuyabildiği** veri / context (örn. `config://app`). | LLM (veya kullanıcı) URI ile okur. |
| **Prompts** | Kullanıcı için **hazır prompt şablonları** (parametre alabilen). | Son kullanıcı, UI'dan seçer. |

> Kısaca: Tool **yaptırır**, Resource **gösterir**, Prompt **başlatır**.

---

## Bu repoda ne var?

```
MCP-Inspector-Example/
├── server.py          # MCP sunucusu (Tools + Resources + Prompts örnekleri)
├── requirements.txt   # Python bağımlılıkları (mcp[cli], python-dotenv)
├── .env.example       # Token / kullanıcı gibi gizli değerler için şablon
├── .gitignore
└── README.md          # Bu dosya
```

`server.py` içinde:

- **Tools**: `selamla`, `topla`, `simdiki_zaman`, `zar_at`, `gorev_ekle`,
  `gorev_tamamla`, `gorev_listele`, `kimligimi_dogrula` (`.env`'den okur)
- **Resources**: `config://app`, `docs://mcp-nedir`, `tasks://hepsi`,
  `env://status` (env değişkenlerinin maskelenmiş hâli)
- **Prompts**: `kod_inceleme_prompt`, `ozetle_prompt`

---

## Gereksinimler

- **Python 3.10+** (3.11 önerilir)
- **Node.js 18+** ve `npx` (sadece MCP Inspector'ı çalıştırmak için; sunucunun
  kendisi sadece Python ile çalışır)

Sürümlerini doğrula:

```bash
python3 --version
node -v
npx -v
```

---

## Kurulum

```bash
# 1) Repo'yu klonla
git clone https://github.com/AlperenTasdelen/MCP-Inspector-Example.git
cd MCP-Inspector-Example

# 2) Sanal ortam oluştur (önerilir)
python3 -m venv venv
source venv/bin/activate         # Windows: venv\Scripts\activate

# 3) Bağımlılıkları yükle
pip install -r requirements.txt

# 4) Token / API key gibi değerler için .env hazırla
cp .env.example .env
# sonra .env'yi açıp DEMO_API_KEY, DEMO_USER vb. doldur
```

Bittiğinde elinde çalışmaya hazır bir Python ortamı olacak.

> **`.env` notu:** `.env` dosyası `.gitignore` içindedir, repo'ya
> commit'lenmez — token'ların asla GitHub'a sızmaz. Diğer geliştiricilere
> hangi değişkenleri doldurmaları gerektiğini göstermek için sadece
> `.env.example` dosyası repo'ya konur. (Bu repodaki `kimligimi_dogrula`
> tool'u ve `env://status` resource'u, bu dosyayı doğru yükleyip
> yüklemediğini Inspector üzerinden kolayca test etmen için var.)

---

## Sunucuyu çalıştırma

MCP sunucuları "stdio" üzerinden konuşur — yani **terminale yazdırılan bir
çıktı görmemen normaldir**. Sunucu, kendisini çağıran bir istemci (Inspector,
Claude Desktop, Cursor vs.) bekler.

İki seçeneğin var:

### Seçenek A — Sadece çalışıp çalışmadığını test et

```bash
python server.py
```

Hata vermiyorsa hazır demektir. `Ctrl + C` ile kapat ve aşağıdaki Inspector
adımına geç.

### Seçenek B — Doğrudan Inspector'la başlat (önerilen)

Aşağıdaki komut hem sunucuyu başlatır hem de tarayıcıda Inspector arayüzünü
açar.

```bash
npx @modelcontextprotocol/inspector python server.py
```

> İlk çalıştırmada `npx`, Inspector paketini indireceği için biraz vakit
> alabilir.

---

## MCP Inspector ile inceleme

MCP Inspector, yazdığın sunucuyu **Claude veya Cursor olmadan** tarayıcıdan
test etmeni sağlayan resmi araçtır. Tool'lara form üzerinden parametre
gönderir, dönen cevabı görürsün; geliştirme döngünü çok hızlandırır.

```bash
npx @modelcontextprotocol/inspector python server.py
```

Komutu çalıştırdığında terminalde şuna benzer bir çıktı görürsün:

```
MCP Inspector is up and running at http://localhost:6274
```

Tarayıcı çoğu zaman otomatik açılır; açılmadıysa o adresi kendin gir.

> İlk açılışta sol üstten **Connect** demen yeterli. Inspector senin için
> sunucuyu başlatıp stdio bağlantısını kurar.

### Inspector arayüzü kabaca şöyle görünür:

- **Sol panel**: Bağlantı bilgileri (transport, komut, argümanlar) ve
  bağlanma butonu.
- **Üst sekmeler**: `Tools`, `Resources`, `Prompts`, `Sampling`, `Roots`,
  `Notifications` …
- **Sağ panel**: Seçtiğin tool'un parametre formu ve dönen response.

---

## Inspector'da neyi nereden test edeceksin?

### 1) Tools sekmesi

Üstten **Tools** sekmesine tıkla. Sunucudaki tüm tool'lar listelenir:
`selamla`, `topla`, `zar_at`, `gorev_ekle`, … 

Mesela `topla`'yı dene:

1. Sol listede `topla` aracını seç.
2. Sağdaki formda `a = 7`, `b = 5` gir.
3. **Run Tool** butonuna bas.
4. Aşağıda `12` döndüğünü göreceksin.

`zar_at` ile daha eğlenceli bir test:

```
yuz_sayisi = 20
adet       = 3
```

`Run Tool` → JSON cevap (atılan zarlar + toplam).

### 2) Stateful tool'lar (görev listesi)

Sırasıyla şunları çalıştır:

1. `gorev_ekle` → `baslik = "MCP makalesi yaz"`
2. `gorev_ekle` → `baslik = "Inspector demo videosu çek"`
3. `gorev_listele` → iki görevi de görmen lazım.
4. `gorev_tamamla` → `gorev_id = 1`
5. `gorev_listele` → birinci görev `[x]` ile işaretli gelir.

Bu kısım sana, MCP sunucularının **bellekte state tutabildiğini** ama sunucu
durunca bu bilginin **uçtuğunu** gösterir. Gerçek hayatta DB / dosya
kullanmalısın.

### 3) Resources sekmesi

`Resources` sekmesinde 4 kayıt göreceksin:

- `config://app`
- `docs://mcp-nedir`
- `tasks://hepsi`
- `env://status`

Bir tanesine tıklayıp **Read** dediğinde içeriğini göreceksin. Görev
listesini değiştirip `tasks://hepsi`'yi tekrar **Read** edersen güncel halini
görürsün — yani bir resource statik olmak zorunda değil, **dinamik** de
olabilir.

`env://status`'i okuyarak `.env` dosyandaki demo değişkenlerin (DEMO_API_KEY,
DEMO_USER, DEMO_BASE_URL) yüklenip yüklenmediğini kontrol edebilirsin.
Değerler maskelenir; sadece son 4 karakter görünür.

### 4) `.env` ile çalışan tool'u test et

`Tools` sekmesinde `kimligimi_dogrula` tool'unu seç ve **Run Tool** bas.
Üç senaryoyu sırayla deneyebilirsin:

| Senaryo | `.env` durumu | Beklenen çıktı |
| --- | --- | --- |
| 1. `.env` yok / boş | Hiçbir değer set değil | "DEMO_API_KEY tanımlı değil" hatası |
| 2. Yanlış token | `DEMO_API_KEY=baska-bir-sey` | "Geçersiz API key" |
| 3. Doğru token | `DEMO_API_KEY=demo-1234` | "OK — Kimlik doğrulandı" |

> Senaryoyu değiştirdiğinde Inspector'da **Disconnect → Connect** yapman
> gerekir; çünkü `.env` sunucu **başlarken** okunur, çalışırken değil.
> Gerçek hayatta da değişikliği görmek için süreci yeniden başlatırsın.

### 5) Prompts sekmesi

`Prompts` altında `kod_inceleme_prompt` ve `ozetle_prompt` görünür. Birini
seçip parametre ver (`dil = "Go"`, `odak = "güvenlik"` gibi); sana hazır
prompt metnini gösterir. Claude Desktop'ta bu prompt'lar kullanıcı için bir
**slash menüsünde** çıkar.

### 6) Notifications / Server Logs

Inspector'ın alt kısmındaki **Server Notifications / Logs** alanı, sunucudan
gelen `stderr` / log çıktısını gösterir. Tool içine `print(..., file=sys.stderr)`
yazıp ne olduğunu gözlemleyebilirsin (stdout MCP protokolü için ayrılmıştır,
oraya yazma!).

---

## Claude Desktop / Cursor'a bağlama

Inspector'da çalıştığını doğruladıysan, sunucunu gerçek bir LLM istemcisine
bağlayabilirsin.

### Claude Desktop

`~/Library/Application Support/Claude/claude_desktop_config.json` dosyasını
açıp aşağıdakine benzer bir blok ekle (yolu kendi makinene göre güncelle):

```json
{
  "mcpServers": {
    "inspector-demo": {
      "command": "/MUTLAK/YOL/MCP-Inspector-Example/venv/bin/python",
      "args": ["/MUTLAK/YOL/MCP-Inspector-Example/server.py"]
    }
  }
}
```

Önemli notlar:

- `command` alanı **mutlaka mutlak yol** olmalı (Claude Desktop'ın PATH'i
  senin shell'inkiyle aynı değil).
- Sanal ortam (`venv`) kullanıyorsan o ortamın `python` binary'sini ver.
- Konfigürasyonu kaydedip Claude Desktop'ı **tamamen kapatıp yeniden aç**.

Claude'a şu tarz şeyler sorabilirsin:

> "İnspector demo sunucusundaki `topla` aracıyla 17 + 28 hesaplar mısın?"
>
> "Görev listeme 'akşam koşusuna çık' ekle ve sonra listemi göster."

### Cursor

`Cursor → Settings → MCP → Add new MCP server` üzerinden de aynı blok mantığı
ile ekleyebilirsin.

---

## Kendi tool'unu nasıl eklersin?

Tek yapman gereken `server.py` içine yeni bir fonksiyon yazıp `@mcp.tool()`
ile süslemek:

```python
@mcp.tool()
def hava_durumu(sehir: str) -> str:
    """Verilen şehrin hava durumunu döndürür (demo)."""
    return f"{sehir} için hava: güneşli, 24°C."
```

İpuçları:

1. **Docstring çok önemlidir.** LLM tool'u ne zaman çağıracağına bu metne
   bakarak karar verir. Kısa, net ve "ne işe yarar / hangi parametreyi
   bekler" bilgisini ver.
2. **Type hints ekle.** `sehir: str`, `adet: int`, `tarih: datetime.date`
   gibi tip bilgileri Inspector'da otomatik form üretmek için kullanılır.
3. Hata durumlarında `raise ValueError("...")` at; Inspector ve LLM bunu
   anlamlı bir mesaj olarak görür.
4. Yan etki yapan tool'lar (silen, scale eden, e-posta gönderen) için
   docstring'in başına **YAZMA OPERASYONU** gibi büyük harfli bir uyarı
   yazmak iyi bir alışkanlık.

Resource eklemek için:

```python
@mcp.resource("notes://gunluk")
def gunluk_notlar() -> str:
    return "Bugün öğrendiklerim:\n- MCP\n- Inspector\n- Görev listesi"
```

Prompt eklemek için:

```python
@mcp.prompt()
def email_yaz(konu: str, ton: str = "resmi") -> str:
    """Verilen konu ve tonda taslak e-posta üretir."""
    return f"{ton} bir tonla, '{konu}' konulu kısa bir e-posta yaz."
```

Kaydet, sunucuyu (Inspector dahil) yeniden başlat — Inspector listede
otomatik olarak göreceksin.

---

## Sık karşılaşılan sorunlar (Troubleshooting)

**1) `npx @modelcontextprotocol/inspector ...` komutu hiç çalışmadı**

`Node.js / npx` kurulu değil veya çok eski. `node -v` çıktısı en az `v18`
olmalı. Yoksa [nodejs.org](https://nodejs.org) üzerinden LTS sürümünü kur.

**2) Inspector'da "Failed to connect" / "Server crashed"**

- `python server.py` komutunu **kendi başına** çalıştır, hata mesajını oku
  (genelde Python tarafındaki bir import / typo hatasıdır).
- `pip install -r requirements.txt` adımını atlamış olabilirsin.
- Doğru `python` mu çalışıyor? `which python` ile sanal ortamdaki binary'yi
  kullandığından emin ol.

**3) Inspector açılıyor ama tool'larım listede yok**

Sunucuyu Inspector başlatmadan önce kaydetmiş olabilirsin. `server.py`'yi
kaydedip Inspector tarayıcı sekmesini yenile veya **Disconnect → Connect**
yap.

**4) Claude Desktop sunucumu görmüyor**

- `claude_desktop_config.json` JSON olarak geçerli mi? (eksik virgül vs.)
- `command` alanında **mutlak yol** kullandın mı?
- Konfigürasyon değiştikten sonra Claude'u tamamen kapatıp açtın mı?

**5) `print()` çağrılarım Inspector'da görünmüyor**

`stdout` MCP protokolüne ayrılmıştır; oraya `print` yazarsan bağlantı
bozulabilir. Loglamak için `print(..., file=sys.stderr)` veya `logging`
modülünü kullan; çıktı Inspector'da **Server Logs** panelinde görünür.

---

## Lisans

Bu repo eğitim amaçlıdır, dilediğin gibi kopyalayıp türevini yayımlayabilirsin.

## Faydalı bağlantılar

- [Model Context Protocol resmi sitesi](https://modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector)
