# CreativeForge Intelligence Studio v3.0 — ComfyUI Derin Hibrit Entegrasyon Master Planı

Bu doküman, açık kaynak dünyasının en olgun difüzyon modeli yürütme motoru olan **ComfyUI**'ın; CreativeForge platformunun kurumsal, dayanıklı (durable) ve çok kullanıcılı stüdyo mimarisine **kusursuz bir "İki Katmanlı Hibrit (Two-Tier Hybrid)"** modelle entegre edilmesi için tasarlanmış **5 Bağımsız Paralel Ajan (Agent)** uygulama planını ve her bir ajanın doğrudan yürütülmeye hazır eksiksiz promptlarını içerir.

---

## 1. MİMARİ VİZYON: İKİ KATMANLI HİBRİT GRAF (TWO-TIER HYBRID GRAPH)

ComfyUI'ın eski usul `LiteGraph.js` (Canvas 2D) web arayüzü projeye **kopyalanmayacaktır**. Bunun yerine ComfyUI'ın süper olgun **Python Çalıştırma Motoru (Dependency Execution & VRAM Caching)** ve **JSON Sözleşmesi**, bizim modern **Next.js 14 + React Flow** mimarimizle birleştirilecektir.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                      CREATIVEFORGE STUDIO (Next.js 14 + React Flow)                    │
│                                                                                        │
│  TIER 1: MAKRO KAMPANYA AKIŞI (React Flow Ana Canvas)                                  │
│  ┌──────────────┐     ┌──────────────┐     ┌─────────────────┐     ┌────────────────┐  │
│  │ Market Trend │ ──> │ Game DNA     │ ──> │ Image Generator │ ──> │ Quality Gate 7 │  │
│  │ Synthesis    │     │ Truth Lock   │     │ (Comfy Hybrid)  │     │ & Export       │  │
│  └──────────────┘     └──────────────┘     └────────┬────────┘     └────────────────┘  │
└─────────────────────────────────────────────────────┼──────────────────────────────────┘
                                                      │ Çift Tıkla / Inspector
                                                      ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│  TIER 2: MİKRO MODEL GRAFI (ComfyUI Sub-Canvas / React Flow Native Nodes)              │
│                                                                                        │
│  ┌──────────────────┐    ┌─────────────────┐    ┌──────────────┐    ┌───────────────┐  │
│  │ CheckpointLoader │─M─>│ PromptEncode (+)│─C─>│   KSampler   │─L─>│   VAEDecode   │  │
│  │ (SDXL / Flux)    │─V─>│ (Game DNA Hook) │    │ (Steps, CFG) │    │  (Latent->PNG)│  │
│  └──────────────────┘    └─────────────────┘    └──────────────┘    └───────┬───────┘  │
│           │                                                                 │          │
│           └─── ControlNet / LoRA Sub-branches ──────────────────────────────┘          │
└─────────────────────────────────────────────────────┬──────────────────────────────────┘
                                                      │ Bidirectional Transpiler
                                                      ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│  HEADLESS BACKEND MOTORU (services/worker-image + ComfyUI Daemon)                      │
│  • ComfyUI WebSocket & REST API (/prompt, /history, /view)                             │
│  • Canlı KSampler adımları (14/25) -> SSE Outbox -> Observatory Ekranı                │
│  • AST Güvenlik Filtresi (Zararlı Python / Custom Node Engelleme)                      │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### Temel Mimari Kazanımlar
1. **Sıfır Miras Borç:** `LiteGraph.js` kullanılmaz; tüm düğümler DOM ve React Flow (`@xyflow/react`) tabanlıdır.
2. **Kara Kutu Kırıldı:** Sabit tek bir prompt yerine, kullanıcı ControlNet, FaceID, Inpainting ve LoRA zincirlerini görsel olarak düzenleyebilir.
3. **Tam Bütünlük & Telemetri:** Üretim anındaki KSampler adımları ve ara resimler (previews) anında WebSocket üzerinden yakalanıp SSE ile Observatory'ye ve Execution Ledger'a iletilir.
4. **Kurumsal Güvenlik:** İçe aktarılan ComfyUI JSON iş akışları, AST güvenlik filtresinden geçirilerek rastgele sistem çağrısı yapan veya izinsiz custom node çalıştıran akışlar engellenir.

---

## 2. 5 PARALEL AJAN GÖREV DAĞILIMI

| Ajan | Uzmanlık Alanı | Sorumlu Olduğu Dizinler | Temel Çıktılar |
|---|---|---|---|
| **Agent H1** | Comfy Bridge & Bidirectional Transpiler | `packages/comfy-bridge/` | ComfyUI JSON <-> React Flow çift yönlü çevirici, Port renk/tip uyumluluğu, `/object_info` dinamik node içe aktarımı |
| **Agent H2** | Daemon Supervisor, WebSocket & Execution Engine | `services/worker-image/` | ComfyUI process supervisor, WebSocket canlı ilerleme dinleyicisi, dinamik template binder, 4 hazır prodüksiyon preset'i |
| **Agent H3** | Data Contracts, Storage & Preset API Gateway | `packages/contracts/`, `services/api/app/db/`, `services/api/app/modules/comfy/` | Pydantic modelleri, PostgreSQL `comfy_presets` şeması, Alembic migration, Preset & Model Catalog REST API'leri |
| **Agent H4** | Workflow Security AST Linter & Quality Gates | `services/worker-evaluation/`, `services/api/app/modules/evaluations/` | AST güvenlik filtresi (zararlı node/kod tespiti), Game DNA CLIP stil tutarlılık kapısı, Görsel artefakt dedektörü |
| **Agent H5** | Frontend Sub-Canvas, Custom Nodes & Live Studio | `apps/web/` | React Flow Comfy Sub-Canvas modalı, Özel renkli Comfy node kartları, Canlı step ilerleme çubuğu, JSON Import/Export |

---

## 3. AJAN PROMPTLARI (BAĞIMSIZ ÇALIŞMAYA HAZIR)

Aşağıdaki 5 prompt, ilgili ajanlara bağımsız olarak verilip paralel şekilde inşa edilmelerini sağlayacak tüm girdi, çıktı, şema ve kabul kriterlerini eksiksiz içerir.

---

### PROMPT 1: AGENT H1 — COMFY BRIDGE & BIDIRECTIONAL TRANSPILER ARCHITECT

```markdown
# GÖREV: AGENT H1 — ComfyUI JSON ve React Flow Çift Yönlü Çevirici ve Düğüm Köprüsü

## 1. ROL VE MİSYON
Sen CreativeForge platformunun Baş Düğüm Sistemleri ve Dil/Graf Derleme Mühendisisin (Principal Graph Systems & Transpiler Engineer).
Görevin; ComfyUI'ın standart API JSON formatı ile React Flow (`@xyflow/react`) görsel graf nesneleri arasında kayıpsız, çift yönlü (bidirectional) dönüşüm yapan derleyici paketini (`packages/comfy-bridge/`) sıfırdan inşa etmektir.

## 2. ÇALIŞMA ALANIN VE DİZİN YAPISI
Yalnızca şu dizinde çalışacaksın:
- `packages/comfy-bridge/`
  - `__init__.py`
  - `types.py` (Port tipleri, Comfy şemaları)
  - `transpiler.py` (Comfy JSON <-> React Flow JSON çeviricisi)
  - `introspection.py` (ComfyUI /object_info API'sinden şema çıkarma)
  - `validator.py` (ComfyUI bağlantı ve tip doğrulama)
  - `presets/` (Test ve standart iş akışı referansları)
- `tests/test_comfy_bridge.py`

## 3. DETAYLI TEKNİK GEREKSİNİMLER

### 3.1 ComfyUI Tip Sistemi ve Port Standartları (`types.py`)
ComfyUI'ın kullandığı tüm temel veri tiplerini ve React Flow renk kodlarını tanımla:
- `MODEL` (Açık Mor: `#b197fc`)
- `CLIP` (Sarı: `#ffd43b`)
- `VAE` (Kırmızı: `#ff6b6b`)
- `CONDITIONING` (Turuncu: `#ffa94d`)
- `LATENT` (Mor: `#da77f2`)
- `IMAGE` (Mavi: `#4dabf7`)
- `MASK` (Gri: `#ced4da`)
- `CONTROL_NET` (Yeşil: `#51cf66`)
- `INT`, `FLOAT`, `STRING`, `BOOLEAN`, `COMBO` (Parametre tipleri)

### 3.2 Çift Yönlü Çevirici Motoru (`transpiler.py`)
1. `comfy_to_react_flow(comfy_json: dict) -> ReactFlowGraph`:
   - Her ComfyUI düğümünü (`class_type`, `inputs`) özel bir React Flow düğümüne dönüştürür.
   - Girdi bağlantılarını (`["node_id", output_index]`) React Flow kenarlarına (`source`, `target`, `sourceHandle`, `targetHandle`) dönüştürür.
   - Skaler parametreleri (cfg, steps, seed, text vb.) `node.data.parameters` altına yerleştirir.
   - Otomatik hiyerarşik yerleşim (Sugiyama / Dagre layout algoritması veya sütun bazlı X/Y hesaplama) ile düğümleri görsel olarak hizalar.
2. `react_flow_to_comfy(react_flow_graph: dict) -> dict`:
   - React Flow üzerindeki düğüm ve kenarları ComfyUI `/prompt` API'sinin beklediği geçerli dictionary formatına dönüştürür.
   - Boşta kalan (unconnected) zorunlu portları tespit eder ve açık hata üretir.

### 3.3 Dinamik Node İçe Aktarımı ve Şema Çıkarıcı (`introspection.py`)
- `ComfySchemaExtractor`:
  - Yerel veya uzak ComfyUI sunucusunun `GET /object_info` uç noktasını okur (veya önbellekteki şemayı yükler).
  - Her bir `class_type` için zorunlu girdileri (`required`), opsiyonel girdileri (`optional`) ve çıktı tiplerini (`RETURN_TYPES`) ayrıştırır.
  - Bu şemayı React Flow'un anlayacağı dinamik bileşen tanımlarına dönüştürür.

### 3.4 Bağlantı ve Tip Doğrulayıcı (`validator.py`)
- `validate_comfy_edge(source_node, target_node, source_handle, target_handle)`:
  - `MODEL` sadece `MODEL` portuna, `CONDITIONING` sadece `CONDITIONING` portuna bağlanabilir.
  - Tip uyumsuzluğunda `ComfyTypeMismatchError` fırlatır.
  - Döngü (cycle) tespit edildiğinde `ComfyCycleError` fırlatır (ComfyUI grafı kesinlikle yönlü ve asiklik olmalıdır).

## 4. KABUL VE DOĞRULAMA KRİTERLERİ
- Geçerli bir ComfyUI API JSON dosyası `comfy_to_react_flow` ile çevrilip tekrar `react_flow_to_comfy` yapıldığında orijinal JSON ile mantıksal olarak %100 özdeş olmalıdır.
- Hatalı bir bağlantı (ör. `IMAGE` portundan `MODEL` girişine) açık bir tip hatası üretmelidir.
- Tüm testler `pytest tests/test_comfy_bridge.py` altında %100 başarılı geçmelidir.
```

---

### PROMPT 2: AGENT H2 — COMFYUI DAEMON SUPERVISOR, WEBSOCKET STREAMING & TEMPLATE WORKER

```markdown
# GÖREV: AGENT H2 — ComfyUI Daemon Süreç Yöneticisi, WebSocket Canlı İlerleme ve Dinamik Şablon Motoru

## 1. ROL VE MİSYON
Sen CreativeForge platformunun Baş Medya Altyapısı ve Dağıtık Sistemler Mühendisisin (Principal Media Infrastructure & Distributed Runtime Architect).
Görevin; `services/worker-image/` dizinini ComfyUI'ı yerel veya uzak GPU ortamlarında bir işletim sistemi süreci olarak denetleyen, canlı WebSocket ilerlemesini yakalayan ve dinamik parametre bağlama yeteneğine sahip üretim seviyesi bir motora dönüştürmektir.

## 2. ÇALIŞMA ALANIN VE DİZİN YAPISI
Yalnızca şu dizinlerde çalışacaksın:
- `services/worker-image/`
  - `daemon.py` (ComfyUI Process Supervisor & Health Monitor)
  - `ws_client.py` (Real-time WebSocket Progress Listener)
  - `template_engine.py` (Dynamic Variable Interpolation)
  - `presets/` (4 adet üretime hazır Match-3, Karakter, ControlNet ve IP-Adapter şablonu)
  - `worker.py` & `adapters/comfyui_adapter.py` (Genişletilmiş adaptör)
- `tests/test_comfy_daemon_and_worker.py`

## 3. DETAYLI TEKNİK GEREKSİNİMLER

### 3.1 ComfyUI Daemon Supervisor (`daemon.py`)
- `ComfyDaemonSupervisor`:
  - `ComfyUI/main.py` dosyasını yapılandırılabilir parametrelerle (GPU seçimi, `--listen`, `--port 8188`, `--highvram / --lowvram`) arka plan süreci (subprocess) olarak başlatır ve izler.
  - Health check: `GET /system_stats` uç noktasına periyodik ping atar; yanıt vermezse otomatik yeniden başlatır (graceful restart).
  - VRAM ve donanım kullanımını (GPU % ve bellek) raporlar.
  - Process teardown: Uygulama kapandığında yetim süreç (zombie process) bırakmadan temiz sonlanır.

### 3.2 WebSocket Canlı İlerleme İstemcisi (`ws_client.py`)
- `ComfyWebSocketListener`:
  - `ws://<comfy_url>/ws?clientId=<client_id>` bağlantısını yönetir.
  - Canlı ComfyUI olaylarını ayrıştırır:
    1. `status`: Kuyrukta bekleyen iş sayısı.
    2. `execution_start`: İşleme başlanan `prompt_id`.
    3. `progress`: Aktif düğümdeki (özellikle KSampler) anlık adım sayısı: `value / max` (ör. `14 / 25`).
    4. `executing`: Şu an yürütülen `node_id`.
    5. `executed`: Tamamlanan düğüm ve önizleme resim bilgisi.
    6. `execution_error`: Hata detayı ve Python traceback'i.
  - Bu olayları CreativeForge `EventEnvelope` formatına dönüştürüp SSE Outbox kuyruğuna besler (`COMFY_STEP_PROGRESS`, `COMFY_PREVIEW_FRAME`).

### 3.3 Dinamik Şablon Değişken Motoru (`template_engine.py`)
- `ComfyTemplateEngine.bind_variables(template_json: dict, variables: dict) -> dict`:
  - Şablon içerisindeki dinamik belirteçleri çözer:
    - `${prompt}`, `${negative_prompt}`, `${seed}`
    - `${width}`, `${height}`, `${steps}`, `${cfg}`
    - `${style_tokens}`, `${lora_name}`, `${lora_strength}`
  - Güvenlik: Sayısal beklenen alanlara (seed, cfg) string enjeksiyonu yapılmasını engeller; tip doğrulamasını garanti eder.

### 3.4 4 Hazır Üretim Şablonu (`presets/`)
Aşağıdaki 4 JSON dosyasını eksiksiz ComfyUI API JSON formatında oluştur:
1. `match3_gem_icons_sdxl.json`: Şeffaf/izole arka planda yüksek kaliteli Match-3 mücevher, karo ve şeker spriteları üreten SDXL iş akışı.
2. `game_hero_portrait_flux.json`: Oyun kapak görseli için Flux/SDXL tabanlı stilize karakter portre şablonu.
3. `controlnet_canny_layout.json`: Referans sahnenin Canny kenar çizgilerini alıp aynı kompozisyonda reklam görseli üreten ControlNet şablonu.
4. `ipadapter_gamedna_consistency.json`: Referans oyun görselinin stilini ve renk paletini yeni sahneye aktaran IP-Adapter şablonu.

## 4. KABUL VE DOĞRULAMA KRİTERLERİ
- Daemon supervisor mock veya gerçek süreçte hatasız ayağa kalkmalı, health check başarılı dönmelidir.
- WebSocket istemcisi gönderilen mock olay akışını (1'den 25'e kadar KSampler ilerlemesi) sırayla ve kayıpsız yakalamalıdır.
- Şablon motoru `${prompt}` ve `${seed}` alanlarını tip hatası olmadan başarıyla derlemelidir.
```

---

### PROMPT 3: AGENT H3 — DATA CONTRACTS, STORAGE & PRESET API GATEWAY

```markdown
# GÖREV: AGENT H3 — Veri Sözleşmeleri, Veritabanı Şeması, Şablon Kütüphanesi ve REST API Uç Noktaları

## 1. ROL VE MİSYON
Sen CreativeForge platformunun Baş Veritabanı ve API Mimarisin (Principal Backend & Storage Engineer).
Görevin; ComfyUI şablonlarının, model kataloğunun ve dinamik değişken bağlarının PostgreSQL veritabanında saklanmasını, Pydantic v2 sözleşmelerini ve FastAPI REST API uç noktalarını (`services/api/app/modules/comfy/`) kurmaktır.

## 2. ÇALIŞMA ALANIN VE DİZİN YAPISI
Yalnızca şu dizinlerde çalışacaksın:
- `packages/contracts/comfy_contracts.py`
- `services/api/app/db/models/comfy.py` (SQLAlchemy modelleri)
- `services/api/app/db/migrations/` (Alembic migration dosyası)
- `services/api/app/modules/comfy/` (CRUD servisi ve API routerları)
- `services/api/app/api/v1/comfy.py`
- `tests/test_comfy_api_and_db.py`

## 3. DETAYLI TEKNİK GEREKSİNİMLER

### 3.1 Pydantic v2 Sözleşmeleri (`packages/contracts/comfy_contracts.py`)
- `ComfyPresetRecord`:
  - `preset_id`: str (UUID)
  - `name`: str (ör. "Match-3 Neon Gemstones")
  - `category`: str ("icon", "character", "background", "layout")
  - `description`: str
  - `is_builtin`: bool
  - `version`: str
  - `workflow_json`: Dict[str, Any]
  - `exposed_variables`: List[ComfyVariableSpec] (`name`, `type`, `default`, `description`, `min_val`, `max_val`)
  - `created_at`, `updated_at`: datetime
- `ComfyModelCatalogItem`:
  - `model_id`: str
  - `filename`: str (ör. "dreamshaperXL_v21.safetensors")
  - `model_type`: Literal["checkpoint", "lora", "controlnet", "vae", "upscaler"]
  - `sha256`: str
  - `size_bytes`: int
  - `vram_requirement_mb`: int
  - `is_downloaded`: bool
- `ComfyExecutionProgressEvent`:
  - `run_id`, `node_id`, `step`, `total_steps`, `percentage`, `preview_base64`

### 3.2 SQLAlchemy 2.0 Veritabanı Tabloları (`comfy.py`)
- `comfy_presets`: `(id, name, category, is_builtin, created_at)`
- `comfy_preset_versions`: `(id, preset_id, version, workflow_json, exposed_variables, checksum)`
- `comfy_models`: `(id, filename, model_type, sha256, is_downloaded, size_bytes)`
- Alembic migration dosyasını oluştur ve indeksleri ekle (`preset_id`, `category`, `model_type`).

### 3.3 FastAPI REST API Ağ Geçidi (`api/v1/comfy.py`)
Aşağıdaki uç noktaları eksiksiz oluştur:
- `GET /api/v1/comfy/presets`: Filtreli şablon listesi (kategori, dahili/özel).
- `POST /api/v1/comfy/presets`: Yeni ComfyUI şablonu yükleme/oluşturma (JSON doğrulaması ile).
- `GET /api/v1/comfy/presets/:id`: Şablon detayı ve maruz kalan değişkenler.
- `POST /api/v1/comfy/presets/:id/test-run`: Belirli değişkenlerle anlık test render'ı tetikleme.
- `GET /api/v1/comfy/models`: Sunucuda yüklü olan checkpoint, LoRA ve ControlNet modelleri listesi.
- `POST /api/v1/comfy/models/scan`: Disk üzerindeki modelleri tarayıp veritabanını senkronize etme.

## 4. KABUL VE DOĞRULAMA KRİTERLERİ
- Geçersiz bir Comfy JSON yüklendiğinde API `422 Unprocessable Entity` dönmeli ve şema hatasını bildirmelidir.
- Şablon eklendiğinde `comfy_presets` ve `comfy_preset_versions` tablolarına atomik yazılmalıdır.
- Model tarama uç noktası model tiplerini doğru kategorize etmelidir.
```

---

### PROMPT 4: AGENT H4 — SECURITY SANDBOX, WORKFLOW AST LINTER & VISUAL QUALITY GATES

```markdown
# GÖREV: AGENT H4 — İş Akışı AST Güvenlik Filtresi, Zararlı Node Engelleme ve Görsel Tutarlılık Kapısı

## 1. ROL VE MİSYON
Sen CreativeForge platformunun Baş Güvenlik ve Kalite Güvence Mühendisisin (Principal Security & Visual QA Engineer).
Görevin; sisteme dışarıdan yüklenecek ComfyUI iş akışlarının sunucu güvenliğini tehdit etmesini önleyen statik AST linter motorunu ve üretilen görsellerin Game DNA ile uyumunu denetleyen Gate 4/5 görsel kalite kapısını (`services/worker-evaluation/`) kurmaktır.

## 2. ÇALIŞMA ALANIN VE DİZİN YAPISI
Yalnızca şu dizinlerde çalışacaksın:
- `services/worker-evaluation/gates/comfy_security_gate.py`
- `services/worker-evaluation/gates/comfy_visual_consistency_gate.py`
- `services/worker-evaluation/security_rules.py`
- `services/api/app/modules/evaluations/comfy_evaluator.py`
- `tests/test_comfy_security_and_qa.py`

## 3. DETAYLI TEKNİK GEREKSİNİMLER

### 3.1 ComfyUI AST Güvenlik Filtresi (`comfy_security_gate.py`)
Kullanıcıların dışarıdan yüklediği ComfyUI JSON dosyalarında bulunabilecek saldırı vektörlerini tara:
1. **İzinsiz Custom Node Engeli:**
   - Yalnızca `APPROVED_COMFY_NODE_ALLOWLIST` listesinde yer alan standart ve güvenli node sınıflarına (`KSampler`, `CheckpointLoaderSimple`, `CLIPTextEncode`, `VAEDecode`, `ControlNetApply`, `IPAdapterApply`, `EmptyLatentImage` vb.) izin ver.
   - Rastgele Python kodu çalıştıran (`PythonExec`, `RunCommand`, `CustomScript`) veya işletim sistemine dosya yazan/okuyan (`SaveImageToSystemPath`, `LoadExternalFile`) düğümler tespit edildiğinde `WORKFLOW_SECURITY_VIOLATION` hatası üret ve iş akışını anında reddet.
2. **Yol Manipülasyonu ve SSRF Koruması:**
   - Model adı veya dosya referansı alanlarında `../`, `..\\`, `C:\\`, `/etc/passwd` gibi path traversal örüntülerini yakala.
   - Harici URL'den model/görsel çekmeye çalışan düğümlerde alan adı allowlist denetimi uygula.

### 3.2 Game DNA Görsel ve Stil Tutarlılık Kapısı (`comfy_visual_consistency_gate.py`)
ComfyUI tarafından üretilen `ImageAsset` çıktısını Game DNA profil kriterleriyle denetle:
- **Renk Paleti Doğrulaması:** Üretilen görselin renk histogramını Game DNA `palette` renkleriyle karşılaştırır; sapma eşiği aşılırsa uyarır.
- **Artefakt ve Bozukluk Tespiti:**
  - Kenar keskinliği (Laplacian varyansı ile bulanıklık tespiti).
  - Kontrast ve pozlama kontrolü (aşırı karanlık veya aşırı patlamış kareler).
- **Stil Uyum Skoru:** Game DNA stil etiketleri (`style_tokens`) ile görsel metadata'sı arasındaki uyumu puanlar (0.00 - 1.00).

## 4. KABUL VE DOĞRULAMA KRİTERLERİ
- İçinde izinsiz dosya okuma veya komut çalıştırma düğümü olan sentetik bir JSON yüklendiğinde güvenlik kapısı geçişe izin vermemeli ve tehlikeli düğüm adını raporda belirtmelidir.
- Path traversal içeren model adları (`../../secret.ckpt`) güvenlik filtresini aşamamalıdır.
- Bozuk veya aşırı bulanık görseller görsel kalite kapısından elenmelidir.
```

---

### PROMPT 5: AGENT H5 — FRONTEND SUB-CANVAS, CUSTOM COMFY NODES & LIVE STUDIO

```markdown
# GÖREV: AGENT H5 — React Flow Comfy Alt-Canvas Editörü, Özel Renkli Düğümler ve Canlı İlerleme Arayüzü

## 1. ROL VE MİSYON
Sen CreativeForge platformunun Baş Kullanıcı Deneyimi ve Frontend Mimarisin (Principal Frontend & Canvas Architect).
Görevin; Next.js 14 web uygulamasında (`apps/web`), kullanıcının `Image Generator` düğümüne tıkladığında açılan, React Flow tabanlı görsel ComfyUI alt-graf editörünü, özel renkli bağlantı portlarını ve canlı WebSocket ilerleme göstergesini inşa etmektir.

## 2. ÇALIŞMA ALANIN VE DİZİN YAPISI
Yalnızca şu dizinde çalışacaksın:
- `apps/web/`
  - `components/comfy/`
    - `ComfySubCanvasModal.tsx` (Alt-graf modal/drawer penceresi)
    - `ComfyCustomNode.tsx` (Özel renkli handle'lara sahip React Flow node kartı)
    - `ComfyPresetSelector.tsx` (Şablon seçici ve galeri)
    - `ComfyVariablePanel.tsx` (Dinamik değişkenler formu)
    - `ComfyLiveProgress.tsx` (Canlı KSampler adım çubuğu ve ara önizleme)
    - `ComfyJsonImporter.tsx` (Sürükle-bırak JSON içe/dışa aktarma)
  - `lib/comfy/` (WebSocket dinleyici, Comfy tip tanımları, React Flow adaptörü)
  - `app/projects/[projectId]/studio/page.tsx` (Entegrasyon noktası)

## 3. DETAYLI TEKNİK GEREKSİNİMLER

### 3.1 ComfyUI Alt-Canvas Modalı (`ComfySubCanvasModal.tsx`)
- Ana stüdyoda `Image Generator` düğümüne tıklandığında veya "Customize Pipeline" denildiğinde açılır.
- İçerisinde bağımsız bir `@xyflow/react` (React Flow) canvas'ı barındırır.
- Kullanıcı sol panelden düğüm ekleyebilir (Model, KSampler, VAE, ControlNet, LoRA vb.).

### 3.2 Özel Comfy Düğüm Kartı (`ComfyCustomNode.tsx`)
- ComfyUI'ın standart renk kodlamasını eksiksiz uygular:
  - `MODEL`: Açık Mor port handle
  - `CLIP`: Sarı port handle
  - `VAE`: Kırmızı port handle
  - `CONDITIONING`: Turuncu port handle
  - `LATENT`: Mor port handle
  - `IMAGE`: Mavi port handle
- Düğüm gövdesinde interaktif kontroller:
  - Sayısal parametreler için kaydırıcılar (Slider) ve sayı kutuları (CFG, Steps, Seed).
  - Metinler için otomatik genişleyen Textarea (Positive / Negative Prompt).
  - Model seçimi için aranabilir Select bileşeni.

### 3.3 Şablon Galerisi & Sürükle-Bırak İçe Aktarma (`ComfyPresetSelector.tsx` & `ComfyJsonImporter.tsx`)
- Kullanıcı önceden tanımlı 4 şablonu (Match-3 Gems, Hero Portrait, ControlNet, IP-Adapter) tek tıkla tuvale yükleyebilir.
- Dışarıdan ComfyUI masaüstü uygulamasından kaydedilmiş bir `.json` dosyasını tuvale sürükleyip bıraktığında dosya ayrıştırılıp anında React Flow düğümlerine dönüştürülür.
- "Export Comfy API JSON" düğmesi ile tuvaldeki akış standart Comfy formatında indirilebilir.

### 3.4 Canlı İlerleme ve Önizleme Paneli (`ComfyLiveProgress.tsx`)
- Üretim başladığında WebSocket/SSE olaylarını dinler:
  - Adım ilerleme çubuğu: `KSampler Step 16 / 25 (%64)`.
  - Üretim sırasında gelen ara latent önizleme karesi (Real-time thumbnail stream).
  - Hata oluşursa düğüm üzerinde kırmızı hata rozeti ve detaylı log penceresi.

## 4. KABUL VE DOĞRULAMA KRİTERLERİ
- React Flow üzerinde düğümler hatasız bağlanmalı, renkli portlar doğru tipleri temsil etmelidir.
- Masaüstünden ComfyUI JSON dosyası sürüklendiğinde doğru pozisyonlarda düğümler oluşmalıdır.
- WebSocket simülasyonunda ilerleme çubuğu akıcı şekilde %0'dan %100'e dolmalı ve tamamlanan görsel ekrana gelmelidir.
- TypeScript derlemesinde hiçbir hata olmamalıdır (`npm run build` hatasız tamamlanmalıdır).
```

---

## 4. BAĞIMSIZ DOĞRULAMA VE ENTEGRASYON KONTROL LİSTESİ

Ajanlar işlerini bitirdiğinde sistem aşağıdaki entegrasyon zinciri ile doğrulanır:

1. **Ajan H1 & Ajan H3:** Agent H3'ün API'sine gelen ComfyUI JSON dosyası, Agent H1'in `comfy_bridge` motoru ile doğrulanır ve şeması çıkarılır.
2. **Ajan H1 & Ajan H5:** Agent H5'in Next.js arayüzündeki React Flow düğümleri, Agent H1'in `react_flow_to_comfy` transpiler'ı ile standart ComfyUI JSON formatına dönüştürülür.
3. **Ajan H2 & Ajan H4:** Agent H4'ün güvenlik filtresinden onay alan JSON akışı, Agent H2'nin dinamik şablon motoruna iletilir; değişkenler bağlanıp ComfyUI Daemon'ına gönderilir.
4. **Ajan H2 & Ajan H5:** Agent H2'nin WebSocket üzerinden yakaladığı KSampler adım olayları (`progress`), Agent H5'in canlı ilerleme çubuğunda anlık olarak gösterilir.
5. **Ajan H4 & Ana Pipeline:** Üretilen görsel Agent H4'ün Game DNA stil kapısından başarıyla geçerse ana orkestratördeki sonraki düğüme (`Playable Spec` veya `Remotion Render`) aktarılır.

Bu plan, ComfyUI'ın tüm gücünü platformun kurumsal yapısını bozmadan içeri alacak eksiksiz bir hibrit dönüşüm kılavuzudur.
