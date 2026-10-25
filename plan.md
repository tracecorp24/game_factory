# CreativeForge Intelligence Studio v3.0 — 6 Paralel Ajan Uygulama Planı ve Prompt Rehberi

Bu doküman, **CreativeForge Intelligence Studio v3.0 Master Planı** doğrultusunda sistemin sıfırdan, eksiksiz ve üretim standartlarında kurulabilmesi için tasarlanmış **6 Bağımsız Paralel Ajan (Agent)** iş bölümünü ve her bir ajanın doğrudan yürütülmeye hazır eksiksiz promptlarını içerir.

---

## 1. MİMARİ VE PARALELLEŞTİRME STRATEJİSİ

Proje, birbirini bloklamadan paralel geliştirilebilecek 6 dikey uzmanlık alanına (workstream) ayrılmıştır. Ajanların senkronizasyon beklemeden çalışabilmesi için paylaşılan veri sözleşmeleri (**Data Contracts**) peşinen tanımlanmıştır.

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│                           CREATIVEFORGE MONOREPO                                  │
├─────────────────────┬─────────────────────────────────────┬───────────────────────┤
│ AGENT 1: VERİ &     │ AGENT 2: İŞ AKIŞI ORKESTRASYON      │ AGENT 3: TREND,       │
│ SÖZLEŞME ÇEKİRDEĞİ  │ VE MODEL MALİYET GATEWAY'İ          │ KONSEPT & GAME DNA    │
│                     │                                     │                       │
│ • Pydantic Şemaları │ • Temporal Workflow/Activity        │ • Trend Intelligence  │
│ • PostgreSQL Şeması │ • DAG Engine & Node Registry        │ • Evidence Resolver   │
│ • Execution Ledger  │ • LiteLLM Gateway & Budget Guard    │ • Creative Hypothesis │
│ • Outbox Tablosu    │ • Run Manifest & Retry Lifecycle    │ • Game DNA Profil     │
│ • Veri Göçleri      │ • İdempotency & Fallback            │ • Deney Motoru (A/B)  │
├─────────────────────┼─────────────────────────────────────┼───────────────────────┤
│ AGENT 4: MULTIMODAL │ AGENT 5: KALİTE KAPILARI,           │ AGENT 6: FRONTEND     │
│ MEDYA & PLAYABLE    │ ANALİTİK & API SERVİSİ              │ STUDIO & OBSERVATORY  │
│                     │                                     │                       │
│ • ComfyUI Adapter   │ • 7 Kademeli Quality Gates          │ • Next.js 14 App      │
│ • Remotion Video    │ • LLM Judge & Rubric Engine         │ • React Flow Canvas   │
│ • Phaser Match-3    │ • Analytics Materialized Rollups    │ • Agent Observatory  │
│ • Playwright Test   │ • SSE Outbox Relay & Canlı Akış     │ • Concept Gallery     │
│ • Güvenli Sandbox   │ • FastAPI REST API Uç Noktaları     │ • Ledger Explorer     │
└─────────────────────┴─────────────────────────────────────┴───────────────────────┘
```

---

## 2. ORTAK SÖZLEŞMELER (SHARED CONTRACTS) VE STANDARTLAR

Ajanların bağımsız çalışabilmesi için tüm modellerde aşağıdaki standartlar esastır:
1. **Kimlikler:** UUIDv7 veya standart UUID stringleri (`run_id`, `node_execution_id`, `attempt_id`, `artifact_id`, `event_id`).
2. **Zaman Damgaları:** UTC ISO 8601 string (`YYYY-MM-DDTHH:MM:SS.sssZ`).
3. **EventEnvelope:** Tüm olaylar standart `EventEnvelope` yapısında `run_events` ve `outbox_events` tablolarına yazılır.
4. **Token & Maliyet Prensibi:** `provider_reported` ile `estimated` kesin olarak ayrılır. Cache tokenlar total input'a dahilse çift sayılmaz. Bilinmeyen medya maliyetleri `unknown` olur, asla 0 sayılmaz.
5. **İzole Çalışma:** Her ajan yalnızca kendi klasör alanında dosya oluşturur veya düzenler.

---

## 3. AJAN GÖREV DAĞILIMI ÖZETİ

| Ajan | Rol | Sorumlu Olduğu Dizinler | Temel Çıktılar |
|---|---|---|---|
| **Agent 1** | Data Architecture, Core Contracts & Ledger | `packages/contracts/`, `services/api/app/db/`, `services/api/app/modules/ledger/`, `packages/test-fixtures/` | Pydantic modelleri, SQLAlchemy modelleri, Alembic migration, Ledger/Outbox servisi |
| **Agent 2** | Workflow Orchestrator, Node Engine & Model Gateway | `services/worker-orchestrator/`, `packages/node-registry/`, `services/api/app/modules/budgets/` | Temporal workflowları, DAG çözümleyici, LiteLLM gateway, bütçe kısıtı, RunManifest |
| **Agent 3** | Intelligence, Creative Hypothesis & Game DNA | `services/worker-trends/`, `services/api/app/modules/intelligence/`, `concepts/`, `game_dna/`, `experiments/` | Trend adapterları, Evidence resolver, Game DNA spec, Konsept puanlama, A/B deney |
| **Agent 4** | Multimodal Creative Production & Playable Sandbox | `services/worker-image/`, `services/worker-video/`, `services/worker-playable/`, `packages/media-presets/` | ComfyUI adapter, Remotion video composition, Phaser Match-3 kod üreteci, Playwright test |
| **Agent 5** | Quality Gates, Evaluation, Analytics & API Gateway | `services/worker-evaluation/`, `services/worker-event-relay/`, `services/api/app/modules/evaluations/`, `analytics/`, `api/v1/` | 7 Gate QA motoru, LLM Judge, Analytics rollup sorguları, SSE relay, FastAPI routerları |
| **Agent 6** | Frontend Studio, Canvas, Observatory & Dashboards | `apps/web/` | Next.js arayüzü, React Flow workflow editörü, Canlı Agent Galaxy Observatory, Ledger & Analytics ekranları |

---

## 4. AJAN PROMPTLARI (KOPYALANIP DOĞRUDAN VERİLEBİLİR)

Aşağıdaki 6 prompt, ilgili ajanlara bağımsız olarak verilecek şekilde tüm gereksinimleri, şemaları ve test kriterlerini içerecek biçimde eksiksiz olarak hazırlanmıştır.

---

### PROMPT 1: AGENT 1 — DATA ARCHITECTURE, CORE CONTRACTS & APPEND-ONLY LEDGER

```markdown
# GÖREV: AGENT 1 — Veri Mimarisi, Pydantic Sözleşmeleri, Veritabanı Şeması ve Execution Ledger Servisi

## 1. ROL VE MİSYON
Sen CreativeForge Intelligence Studio v3.0 platformunun Baş Veri ve Altyapı Mühendisisin (Principal Data & Storage Architect).
Görevin; platformun tüm veri tiplerini (`packages/contracts`), ilişkisel PostgreSQL veritabanı şemasını (`services/api/app/db`), append-only Event Ledger ve Transactional Outbox motorunu (`services/api/app/modules/ledger`) sıfırdan, eksiksiz ve üretim standartlarında inşa etmektir.

## 2. ÇALIŞMA ALANIN VE DİZİN YAPISI
Yalnızca şu dizinlerde çalışacaksın:
- `packages/contracts/`
- `services/api/app/db/`
- `services/api/app/modules/ledger/`
- `packages/test-fixtures/`
- Proje kökü: `pyproject.toml`, `.env.example`, `docker-compose.yml` (Postgres, pgvector servis tanımları)

## 3. DETAYLI TEKNİK GEREKSİNİMLER

### 3.1 Pydantic v2 Veri Sözleşmeleri (`packages/contracts/`)
Aşağıdaki tüm şemaları Pydantic v2 modelleri olarak tanımla:
1. `EventEnvelope`:
   - `event_id`: str (UUIDv7/UUID)
   - `event_type`: str (taxonomy enum: `REQUEST_RECEIVED`, `WORKFLOW_VERSION_CREATED`, `RUN_CREATED`, `RUN_STARTED`, `NODE_STARTED`, `NODE_FINISHED`, `ATTEMPT_STARTED`, `ATTEMPT_FAILED`, `RETRY_SCHEDULED`, `MODEL_CALL_STARTED`, `MODEL_CALL_FINISHED`, `ARTIFACT_CREATED`, `QUALITY_GATE_PASSED`, `QUALITY_GATE_FAILED`, vb.)
   - `schema_version`: int (varsayılan 1)
   - `occurred_at`: datetime (UTC)
   - `recorded_at`: datetime (UTC)
   - `project_id`, `campaign_id`, `request_id`, `run_id`: str
   - `run_seq`: int (monoton artan sıra no)
   - `workflow_version_id`, `node_execution_id`, `attempt_id`, `agent_id`: Optional[str]
   - `trace_id`, `span_id`, `actor_type`, `actor_id`: Optional[str]
   - `correlation_id`, `causation_event_id`: Optional[str]
   - `payload_preview`: Dict[str, Any]
   - `payload_ref`: Optional[str]
   - `redaction_level`: str ("metadata_only" | "sanitized" | "full_content")
   - `integrity_hash`: str (SHA256)
2. `TokenUsageRecord`:
   - `input_tokens`, `output_tokens`, `total_tokens`: int
   - `cached_input_tokens`, `cache_creation_tokens`: Optional[int]
   - `reasoning_tokens`: Optional[int]
   - `billable_input_units`, `billable_output_units`, `billable_media_units`: float
   - `usage_source`: Literal["provider_reported", "estimated", "invoice_reconciled", "missing"]
3. `CostEntryRecord`:
   - `amount`: float
   - `currency`: str (varsayılan "USD")
   - `cost_kind`: Literal["llm_token", "image_generation", "video_generation", "compute_second"]
   - `status`: Literal["estimated", "actual", "reconciled"]
4. `ArtifactRecord`:
   - `artifact_id`: str
   - `run_id`: str
   - `type`: Literal["image", "video", "playable_zip", "concept_board", "evaluation_report", "manifest"]
   - `storage_ref`: str
   - `sha256`: str
   - `bytes`: int
   - `media_meta`: Dict[str, Any]
5. `RunManifestRecord`:
   - Tüm frozen versiyonları, girdi hash'lerini ve environment bilgisini tutan model.

### 3.2 SQLAlchemy 2.0 Modelleri ve Alembic Migration (`services/api/app/db/`)
Master Plan Bölüm I1'de yer alan tüm ilişkisel tabloları eksiksiz oluştur:
- `organizations`, `users`, `memberships`, `workspaces`, `projects`, `campaigns`
- `source_registry`, `source_sync_jobs`, `raw_snapshots`, `trend_observations`, `trend_reports`
- `game_profiles`, `game_profile_versions`, `asset_rights`
- `creative_hypotheses`, `concept_boards`, `concept_decisions`
- `workflows`, `workflow_versions`, `requests`, `runs`, `run_manifests`
- `run_events`: `(run_id, run_seq)` UNIQUE kısıtı, append-only!
- `outbox_events`: `dispatched_at` NULL olanlar için partial index.
- `node_executions`, `attempts`: `(node_execution_id, attempt_no)` UNIQUE kısıtı.
- `agent_sessions`, `model_invocations`, `usage_records`, `price_catalog_versions`, `cost_entries`, `tool_calls`
- `artifacts`, `artifact_lineage` (composite PK: `parent_artifact_id`, `child_artifact_id`, `relation_type`)
- `quality_gate_results`, `evaluations`, `human_reviews`
- `experiments`, `experiment_variants`, `experiment_outcomes`
- `prompt_templates`, `prompt_versions`, `model_policies`, `context_bundles`, `audit_events`
- `analytics_rollups_hourly`
- Veritabanı bağlantısı için async SQLAlchemy engine (`asyncpg` / `psycopg3`), sessionmaker ve Alembic göç dosyalarını hazırla.

### 3.3 Transactional Ledger & Outbox Motoru (`services/api/app/modules/ledger/`)
- `LedgerService.record_event(session, event: EventEnvelope, raw_payload: dict = None)`:
  - Aynı PostgreSQL transaction'ı içinde hem `run_events` tablosuna hem de `outbox_events` tablosuna atomik yazım gerçekleştirir.
  - İlgili `run_id` için son `run_seq` değerini thread-safe / optimistic locking veya serial sequence ile monoton artırır.
  - Payload içeriğinin SHA256 integrity hash'ini hesaplar.
  - Hassas veriler (API key, PII) için redaction uygular.
- `LedgerService.get_run_events(run_id, since_seq=0)`:
  - Sıralı olay akışını döner.

### 3.4 Test Fixtures (`packages/test-fixtures/`)
- Master Plan Bölüm I3'teki 10 adımlı senaryoyu (`run_88` simülasyonu) birebir üreten sentetik JSONL event veri seti (`observatory-demo-events.jsonl`).

## 4. KABUL VE DOĞRULAMA KRİTERLERİ
- Pydantic modelleri `pytest` ile test edilmeli, geçersiz event tipleri doğrulamadan geçememelidir.
- Alembic migration'ı çalıştırıldığında tüm 38+ tablo ve indeksler hatasız oluşmalıdır.
- `record_event` çağrıldığında `run_events` ve `outbox_events` aynı transaction içinde yazılmalı; `run_seq` monoton artmalıdır.
```

---

### PROMPT 2: AGENT 2 — WORKFLOW ORCHESTRATION, TEMPORAL ENGINE & MODEL GATEWAY

```markdown
# GÖREV: AGENT 2 — Workflow Orchestrator, Temporal Durable Execution ve Model Cost Gateway

## 1. ROL VE MİSYON
Sen CreativeForge platformunun Baş Sistem ve Orkestrasyon Mühendisisin (Principal Workflow & Infrastructure Engineer).
Görevin; Master Plan Bölüm D, G, M09 ve M10'da tanımlanan iş akışı orkestrasyon motorunu (`services/worker-orchestrator`), Node Registry ve Port Sözleşmelerini (`packages/node-registry`) ve LiteLLM tabanlı Model Gateway ile bütçe kontrolcüsünü (`services/api/app/modules/budgets`) inşa etmektir.

## 2. ÇALIŞMA ALANIN VE DİZİN YAPISI
Yalnızca şu dizinlerde çalışacaksın:
- `packages/node-registry/`
- `services/worker-orchestrator/`
- `services/api/app/modules/budgets/`
- `services/api/app/modules/workflows/` (workflow execution servis katmanı)

## 3. DETAYLI TEKNİK GEREKSİNİMLER

### 3.1 Node Registry ve Port Doğrulama (`packages/node-registry/`)
Master Plan Bölüm G'deki tüm 28 node tipini tanımla:
- Node tipleri: `Source Fetch`, `Deduplicate`, `Genre Classifier`, `Ad Pattern Extract`, `Trend Synthesis`, `Game Asset Import`, `Game DNA Extract`, `Human Confirm Mechanics`, `Creative Brief`, `Hypothesis Generate`, `Hypothesis Rank`, `Concept Board Render`, `User Select Board`, `Prompt Builder`, `Image Generator`, `Storyboard Planner`, `Video Generator`, `Remotion Render`, `Playable Spec`, `Phaser Codegen`, `Sandbox Build`, `Browser QA`, `Schema Validate`, `Visual QA`, `Mechanics QA`, `Similarity Risk`, `Quality Gate`, `Human Approval`, `Branch`, `Merge`, `Retry Policy`, `Budget Gate`, `Artifact Save`, `Export`.
- Her node için: `input_ports`, `output_ports`, `executor` (agent/worker/human), `retry_policy` (max_attempts, backoff), `timeout`.
- `validate_edge(source_node, target_node, edge)` fonksiyonu: Tip uyumsuzluklarını ve döngüleri (cycle detection) tespit edip net hata fırlatmalıdır.

### 3.2 Temporal Durable Orchestration (`services/worker-orchestrator/`)
- Temporal Python SDK kullanarak `CreativePipelineWorkflow` oluştur:
  - DAG grafını topolojik olarak sıralar ve bağımsız düğümleri paralel çalıştırır.
  - Her düğüm için Temporal Activity tetikler.
  - Sinyaller (Signals): `PauseSignal`, `ResumeSignal`, `CancelSignal`, `HumanApprovalSignal`.
  - Sorgular (Queries): `GetRunStateQuery`, `GetCurrentNodeExecutionsQuery`.
  - Hata ve Tekrar Deneme: Activity hata verdiğinde `ATTEMPT_FAILED` ve `RETRY_SCHEDULED` üretir; `max_attempts` dolunca `RETRY_EXHAUSTED` ile kontrollü durur.
  - İnsan Onay Düğümü: `Human Approval` düğümünde workflow `HumanApprovalSignal` gelene kadar bekleme durumuna geçer.

### 3.3 Run Manifest Engine (`M10`)
- Bir run başladığında, `RunManifestBuilder`:
  - `workflow_version_id`, `game_profile_version_id`, prompt versiyonları, model ayarları ve kaynak hash'lerini dondurarak (`freeze`) immutable bir manifest nesnesi üretir ve SHA256'sını hesaplar.
  - Run devam ederken workflow şablonunda yapılacak değişiklikler aktif run'ı etkileyemez.

### 3.4 Model Cost Gateway & Budget Controller (`M09` & `services/api/app/modules/budgets/`)
- LiteLLM wrapper servisi:
  - Model rotalama: İstenen yeteneğe (text, vision, structured output) ve bütçe kısıtına göre model seçimi.
  - Bütçe Denetçisi (`BudgetGuard`):
    - Run, proje ve workspace bazında tanımlı hard limit ve soft limit kontrolleri.
    - Tahmini maliyet bütçeyi aşıyorsa çağrıyı çalıştırmadan `BUDGET_BLOCKED` hatası üretir.
  - Usage & Cost Muhasebesi:
    - Sağlayıcı yanıtındaki `usage` nesnesinden `input_tokens`, `output_tokens`, `cached_tokens` değerlerini okur.
    - `PriceCatalog` tablosundaki birim fiyatlarla eşleştirerek `CostEntry` üretir.
    - Asla double-counting yapmaz; cached tokenlar net ayrıştırılır.
  - Dynamic Fallback: Bir sağlayıcı rate limit veya 5xx hatası verdiğinde allowlist içindeki yedek modele düşer ve `MODEL_FALLBACK_USED` kaydı oluşturur.

## 4. KABUL VE DOĞRULAMA KRİTERLERİ
- Geçersiz tipteki bir edge React Flow grafından geçirildiğinde `validate_edge` açık bir hata üretmelidir.
- Temporal workflow'u mock activity'ler ile çalıştırıldığında pause/resume/cancel sinyallerine anında ve tutarlı yanıt vermelidir.
- Yapay bir activity hatasında attempt sayısı artmalı, exponential backoff ile tekrar denenmelidir.
- Bütçe aşıldığında model çağrısı bloke edilmeli ve `BUDGET_BLOCKED` olayı tetiklenmelidir.
```

---

### PROMPT 3: AGENT 3 — TREND INTELLIGENCE, CREATIVE HYPOTHESIS & GAME DNA ENGINE

```markdown
# GÖREV: AGENT 3 — Trend Intelligence, Creative Hypothesis & Ranking, Game DNA ve Deney Motoru

## 1. ROL VE MİSYON
Sen CreativeForge platformunun Baş Oyun Stratejisti ve Yapay Zeka Ajan Mühendisisin (Lead Game Strategist & AI Agent Engineer).
Görevin; Master Plan M01 (Trend Intelligence & Evidence), M02 (Creative Hypothesis & Concept Boards), M04 (Game DNA) ve M03 (Experimentation) modüllerini eksiksiz inşa etmektir.

## 2. ÇALIŞMA ALANIN VE DİZİN YAPISI
Yalnızca şu dizinlerde çalışacaksın:
- `services/worker-trends/`
- `services/api/app/modules/intelligence/`
- `services/api/app/modules/game_dna/`
- `services/api/app/modules/concepts/`
- `services/api/app/modules/experiments/`
- `packages/prompts/` (versioned LLM prompt şablonları)

## 3. DETAYLI TEKNİK GEREKSİNİMLER

### 3.1 M01 — Trend Intelligence & Evidence Engine (`services/worker-trends/`)
- `SourceAdapter` arayüzü:
  - `AppleChartsAdapter`: Apple App Store Top Free/Paid iPhone Games listesini çeker/parse eder.
  - `CsvImportAdapter`: Kullanıcının yüklediği CSV trend/reklam verilerini doğrular ve içe aktarır.
  - ToS & İzin kontrolü: Yetkisiz scraping yapılmaz; erişim yoksa `manual_import_required` moduna düşer, asla sahte veri üretmez.
- `TrendIngestionService`:
  - Ham veriyi `RawSnapshot` olarak kaydeder, içerik SHA256 ile deduplicate eder.
  - `GenreClassifier`: Oyunları türlerine ve mekanik kalıplarına ayırır.
  - `EvidenceResolver`: Her trend içgörüsünü somut bir gözleme bağlar; `confidence` seviyesini (`low`, `medium`, `high`) hesaplar.
  - Çıktı: `TrendReport` nesnesi.

### 3.2 M04 — Game DNA & Brand Consistency (`services/api/app/modules/game_dna/`)
- `GameProfileService`:
  - `GameProfileVersion` modelini yönetir: `mechanics_spec` (Match-3, Merge, Sorting presetleri), `style_tokens`, `palette`, `character_refs`, `brand_constraints`, `do_not_generate`, `allowed_ad_claims`.
  - Stil analizi: Yüklenen referans görsellerden stil etiketleri önerir.
  - Sürüm dondurma (`freeze`): Onaylanan profil yeni bir `version` ID alır; eski run'ların profilleri kesinlikle değiştirilemez.
  - Mechanic Validator: Oyun mekanikleri ile reklam vaatleri arasındaki tutarlılığı denetler.

### 3.3 M02 — Creative Hypothesis, Ranking & Concept Boards (`services/api/app/modules/concepts/`)
- `IdeationAgent`:
  - `TrendReport` + `GameProfileVersion` alarak 3 ila 8 adet özgün `CreativeHypothesis` üretir.
  - Her hipotez: `audience`, `genre`, `intended_hook`, `emotional_arc`, `evidence_refs`, `creative_mechanism`, `primary_metric`, `falsification_condition`, `limitations`, `novelty_rationale`.
- Heuristic Ranking Engine:
  - Master Plan'daki formülü uygular:
    `Score = 0.25*evidence + 0.20*game_fit + 0.20*novelty + 0.15*feasibility + 0.10*hook_clarity + 0.10*cost_fit`
  - Skorun bileşenlerini ve gerekçesini açıklar; kalibre edilmemiş skoru asla "tahmini CTR" olarak adlandırmaz.
- Mockup Board Generator:
  - Her konsept için kart yapısını hazırlar: Oyun sahnesi layout'u + reklam hook karesi tanımı + açıklama + metrikler.
- `DecisionCaptureService`:
  - Kullanıcının `select`, `reject`, `regenerate` eylemlerini gerekçesiyle kaydeder (`CONCEPT_SELECTED` olayı).

### 3.4 M03 — Experimentation & Learning Loop (`services/api/app/modules/experiments/`)
- `ExperimentPlanner`:
  - A/B test planı: Tek değişkenli varyant türetimi (Hook, CTA, Renk Paleti).
  - Ayrım kuralı: `offline` (sentetik QA/puanlama) ile `real_campaign` (gerçek CSV metrikleri) net olarak ayrılır.
  - Metrik hesaplayıcı: CPI = spend/installs, CTR = clicks/impressions, IPM = installs/impressions*1000. Paydası sıfır olan değerler `None`/`null` döner.

## 4. KABUL VE DOĞRULAMA KRİTERLERİ
- Bir trend önerildiğinde arkasındaki `evidence_url` ve `observed_at` bilgisi doğrulanabilir olmalıdır.
- Game DNA sürümü güncellendiğinde önceki versiyon immutable kalmalıdır.
- Heuristic skorlama fonksiyonu tüm bileşenleri 0..1 aralığında normalize edip ağırlıklı toplamı hesaplamalıdır.
- Paydası 0 olan CTR veya CPI hesaplamaları hata vermemeli, `null` dönmelidir.
```

---

### PROMPT 4: AGENT 4 — MULTIMODAL CREATIVE PRODUCTION & ISOLATED PLAYABLE SANDBOX

```markdown
# GÖREV: AGENT 4 — Multimodal Medya Üretimi (Image, Video) ve İzole Playable Prototip Sandbox'ı

## 1. ROL VE MİSYON
Sen CreativeForge platformunun Baş Medya ve Oyun Motoru Mühendisisin (Principal Creative Media & Game Engine Architect).
Görevin; Master Plan CORE Asset Generation bölümünde tanımlanan Görsel Üretim Adaptörünü (`services/worker-image`), Remotion tabanlı Video Montaj Hattını (`services/worker-video`), Phaser.js HTML5 Playable Mini-Game Üretim Motorunu ve Playwright Browser Sandbox Test Sistemini (`services/worker-playable`) kurmaktır.

## 2. ÇALIŞMA ALANIN VE DİZİN YAPISI
Yalnızca şu dizinlerde çalışacaksın:
- `services/worker-image/`
- `services/worker-video/`
- `services/worker-playable/`
- `packages/media-presets/` (orijinal Match-3 oyun şablonu ve assetleri)

## 3. DETAYLI TEKNİK GEREKSİNİMLER

### 3.1 Görsel Üretim Adaptörü (`services/worker-image/`)
- `ImageWorker`:
  - `ComfyUIAdapter`: ComfyUI HTTP (`/prompt`, `/history`, `/view`) ve WebSocket API'si ile entegre çalışan işçi. Prompt hash'i ve queue ID'sini saklar.
  - `MockImageAdapter`: Local testler ve GPU bulunmayan ortamlar için SVG/Canvas tabanlı, üzerinde konsept adı, hook metni ve timestamp bulunan geçerli PNG placeholder görselleri üreten deterministik mock adaptör.
  - Üretilen her görsel için SHA256, boyut, çözünürlük, aspect ratio metadata'sı çıkarılır ve `ImageAsset` artifact'ı oluşturulur.
  - Storage: Yerel dosya sistemi (dev) ve S3-compatible storage soyutlaması (`StorageClient`).

### 3.2 Remotion Video Kompozisyon Hattı (`services/worker-video/`)
- `VideoWorker`:
  - Remotion tabanlı 9:16 dikey video şablonu (`packages/media-presets/video-templates/`):
    - 0-3. saniyeler: Dikkat çekici Hook metni ve dinamik görsel giriş animasyonu.
    - 3-10. saniyeler: Oyun içi mekanik simülasyonu / görsel geçişler.
    - 10-15. saniyeler: "Play Now / Hemen Oyna" CTA endcard animasyonu.
  - Remotion CLI / SSR Bundle render entegrasyonu: Storyboard verisinden MP4 video çıktısı derler.
  - Video probe: FFmpeg/ffprobe wrapper ile süre, codec, bitrate ve fps doğrulaması yapar.

### 3.3 HTML5 Playable Prototip Motoru (`services/worker-playable/`)
- Orijinal Match-3 Şablonu (`packages/media-presets/playable-templates/match3/`):
  - Phaser 3 ve TypeScript ile yazılmış, mobil uyumlu (responsive), 8x8 grid üzerinde taş eşleştirme mekaniği.
  - 3'lü eşleşmede patlama efekti, skor sayacı, hamle sınırı ve oyun sonu CTA ekranı.
- `PlayableCodeGenerator`:
  - `PlayableSpec` (hedef skor, hamle sayısı, renk paleti, asset ref'leri) alarak şablon kodunu dinamik olarak derler ve tekil bir `bundle.html` veya ZIP paketi haline getirir.
- İzole Sandbox Çalıştırıcı (`SandboxBuildRunner`):
  - Üretilen TypeScript/Phaser kodunu izole bir geçici dizinde (disposable sandbox) derler (`esbuild` veya `vite`).
  - Güvenlik: Harici ağ erişimi engellenir, kaynak tüketim sınırı (CPU/RAM timeout) uygulanır.
  - Çıktı: `PlayableBundle` artifact'ı (ZIP ve entrypoint index.html).

### 3.4 Playwright Browser QA Sandbox (`services/worker-playable/test/`)
- `PlaywrightRunner`:
  - Headless Chromium üzerinde mobil viewport (iPhone 14 / Pixel 7 boyutları) ayarlar.
  - `bundle.html` dosyasını tarayıcıda açar:
    - Sayfa yükleme süresini ve HTTP hatalarını kontrol eder.
    - Tarayıcı konsolundaki tüm JavaScript runtime error'larını yakalar.
    - Ekranda simüle edilmiş dokunma/sürükleme (touch/swipe/drag) hareketleri ile oyun mekaniğini test eder.
  - Çıktı: `BrowserTestReport` (pass/fail, loglar, screenshot).

## 4. KABUL VE DOĞRULAMA KRİTERLERİ
- Görsel üretici çağrıldığında geçerli bir PNG dosyası ve SHA256 checksum'ı üretilmelidir.
- Remotion şablonu geçerli bir 9:16 MP4 render edebilmelidir.
- Playable üreteci hatasız bir `index.html` üretmeli; Playwright testi bu dosyayı açıp JS hatası olmadan dokunma etkileşimini tamamlayabilmelidir.
- Sandbox derleme adımı sonsuz döngü veya bellek aşımı durumunda timeout ile kontrollü sonlanmalıdır.
```

---

### PROMPT 5: AGENT 5 — QUALITY GATES, EVALUATION, ANALYTICS & FASTAPI GATEWAY

```markdown
# GÖREV: AGENT 5 — Çok Katmanlı Kalite Kapıları, LLM Judge, Analitik Motoru ve FastAPI REST/SSE Gateway

## 1. ROL VE MİSYON
Sen CreativeForge platformunun Baş Kalite, Analitik ve API Gateway Mühendisisin (Principal QA, Analytics & API Gateway Engineer).
Görevin; Master Plan M07 (Multi-Layer Quality Gates), M12 (Analytics & Reporting Dashboard backend), SSE Outbox Event Relay (`services/worker-event-relay`) ve tüm modülleri dış dünyaya bağlayan ana FastAPI REST API ağ geçidini (`services/api`) inşa etmektir.

## 2. ÇALIŞMA ALANIN VE DİZİN YAPISI
Yalnızca şu dizinlerde çalışacaksın:
- `services/worker-evaluation/`
- `services/worker-event-relay/`
- `services/api/app/modules/evaluations/`
- `services/api/app/modules/analytics/`
- `services/api/app/api/v1/`
- `services/api/app/main.py`

## 3. DETAYLI TEKNİK GEREKSİNİMLER

### 3.1 M07 — Çok Katmanlı Kalite ve Uyumluluk Kapıları (`services/worker-evaluation/`)
Sıralı 7 Kalite Kapısını (Gate Pipeline) uygula:
1. `SchemaGate`: Çıktı artifact'ının şema versiyonu ve zorunlu alan doğrulaması.
2. `TechnicalGate`: Dosya boyutu, format bütünlüğü, Playwright build/test raporu (sıfır JS hatası).
3. `GameTruthGate`: Reklam iddiası ile Game DNA mekanik gerçeği arasındaki uyum (yanıltıcı oynanış engeli).
4. `VisualGate`: Çözünürlük, aspect ratio (ör. 9:16), kontrast, CTA metninin okunabilirliği.
5. `SimilarityGate`: Perceptual hash (pHash) ve cosine similarity ile referans korpusu taraması; benzerlik eşiği aşılırsa `warning` bayrağı üretir.
6. `LLMJudgeGate`: Rubrik tabanlı, gerekçeli LLM değerlendirmesi (0-5 arası puanlama, puan gerekçesi, golden prompt referansı).
7. `HumanReviewGate`: Kritik veya başarısız durumlarda insan onay kuyruğuna iş atar; gerekçeli onay/ret kararını bekler.
- Çıktı: `EvaluationReport` artifact'ı ve `QUALITY_GATE_PASSED` / `QUALITY_GATE_FAILED` eventleri.

### 3.2 M12 — Analytics & Reporting Engine (`services/api/app/modules/analytics/`)
Master Plan Bölüm M12'deki metrik formüllerini PostgreSQL aggregate ve rollup sorguları olarak kodla:
- KPI'lar:
  - `run_success_rate = completed_runs / terminal_runs` (cancelled ayrıca belirtilir).
  - `node_retry_rate = retried_node_executions / all_node_executions`.
  - `cost_per_approved_artifact = allocated_cost / approved_artifact_count` (sıfır paydaya `null`).
  - `token_total = SUM(reported_or_estimated)` (cached inputlar çift sayılmaz).
  - `unpriced_call_ratio = unpriced_invocations / all_invocations` (bilinmeyen maliyet 0 yapılmaz).
  - `p50_latency`, `p95_latency` gerçek süreler üzerinden.
- Filtreler: `project_id`, `campaign_id`, tarih aralığı, `workflow_version`, `model`, `agent`.
- Çıktı formatı: JSON API yanıtı ve CSV/JSONL dışa aktarma (export) desteği.

### 3.3 Transactional Outbox & Canlı SSE Relay (`services/worker-event-relay/`)
- `EventRelayWorker`:
  - `outbox_events` tablosundaki henüz dağıtılmamış (`dispatched_at IS NULL`) olayları dinler/çeker.
  - Olayları ilgili `run_id` kanalına yönlendirir.
- SSE Endpoint (`GET /api/v1/runs/:r/events/stream`):
  - `Last-Event-ID` veya `since_seq` parametresi ile bağlantı koptuğunda istemcinin kaçırdığı eventleri sıralı olarak yeniden gönderir.
  - Wire formatı: `id: <run_id>:<run_seq>\nevent: <event_type>\ndata: <json>\n\n`.

### 3.4 FastAPI REST API Gateway (`services/api/app/api/v1/`)
Master Plan Bölüm J'de listelenen tüm REST uç noktalarını oluştur:
- `/projects`: CRUD işlemleri.
- `/trends/sources`, `/trends/sync`, `/projects/:p/trends`: Kaynak ve trend sorguları.
- `/games/:g/versions`: Game DNA sürümleri.
- `/projects/:p/concepts/generate`, `/concepts/:id/decision`: Konsept üretimi ve kullanıcı kararı.
- `/workflows`, `/workflows/:w/publish`: İş akışı tasarımı ve yayınlama.
- `/workflows/:w/runs`, `/runs/:r`, `/runs/:r/pause`, `/resume`, `/cancel`: Çalıştırma kontrolleri.
- `/runs/:r/events`, `/runs/:r/model-calls`, `/runs/:r/attempts`, `/runs/:r/artifacts`: Detaylı izleme.
- `/artifacts/:a`, `/artifacts/:a/preview-ticket`, `/artifacts/:a/review`: Artifact ve QA işlemleri.
- `/analytics/overview`, `/costs`, `/agents`, `/artifacts`, `/quality`: Analitik metrikleri.
- `/runs/compare?left=...&right=...`: İki run arasındaki diff karşılaştırması.

## 4. KABUL VE DOĞRULAMA KRİTERLERİ
- Hatalı bir artifact (ör. JS hatası veren playable) TechnicalGate'ten geçememeli ve pipeline durmalıdır.
- SSE endpoint'ine `since_seq=5` ile bağlanıldığında 6. sıradan itibaren tüm eventler sırayla akmalıdır.
- Analitik sorguları sıfıra bölme durumlarında `null` dönmeli, cache tokenları iki kez toplamamalıdır.
- FastAPI OpenAPI Swagger dökümantasyonu (`/docs`) tüm uç noktaları eksiksiz göstermelidir.
```

---

### PROMPT 6: AGENT 6 — FRONTEND STUDIO, CANVAS, OBSERVATORY & DASHBOARDS

```markdown
# GÖREV: AGENT 6 — Next.js Web Shell, React Flow Workflow Studio, Agent Observatory ve Analitik Ekranları

## 1. ROL VE MİSYON
Sen CreativeForge platformunun Baş Kullanıcı Deneyimi ve Frontend Mimarisin (Principal Frontend & UI/UX Engineer).
Görevin; Master Plan Bölüm B, D1 ve M'de tarif edilen modern, temiz ve yüksek performanslı Next.js 14+ tabanlı web uygulamasını (`apps/web`) kurmaktır.

## 2. ÇALIŞMA ALANIN VE DİZİN YAPISI
Yalnızca şu dizinde çalışacaksın:
- `apps/web/`
  - `app/`: Next.js App Router sayfaları
  - `components/`: UI bileşenleri (workflow, observatory, concepts, analytics, ledger, ui)
  - `lib/`: API client, SSE dinleyici, şemalar, state yönetimi

## 3. DETAYLI TEKNİK GEREKSİNİMLER

### 3.1 Teknoloji Yığını ve Temel Kabuk
- Next.js 14+ (App Router), TypeScript, Tailwind CSS, shadcn/ui bileşenleri.
- State Yönetimi: Zustand (client/UI state), TanStack Query (server caching).
- Sol Navigasyon Menüsü (`Sidebar`):
  - Overview (`/app`)
  - Trend Intelligence (`/projects/:p/intelligence`)
  - Concept Gallery (`/projects/:p/concepts`)
  - Game DNA (`/projects/:p/game-dna`)
  - **Studio** (`/projects/:p/studio` - Workflow ve Agents sekmeleri)
  - Artifact Library (`/projects/:p/artifacts`)
  - Experiments (`/projects/:p/experiments`)
  - **Execution Ledger** (`/projects/:p/ledger`)
  - **Analytics** (`/projects/:p/analytics`)
  - Quality Center (`/projects/:p/quality`)

### 3.2 Sekme 1: Workflow Studio (`/projects/:p/studio?tab=workflow`)
- Üst Bar: Workflow sürümü, Validate, Dry Run, Run, Pause, Cancel düğmeleri, onaylı bütçe ve canlı durum rozeti.
- Sol Node Paleti: Kategorize edilmiş sürüklenebilir düğümler (Market, Game DNA, Concept, Generation, Evaluation, Control, Export).
- Orta Canvas: `@xyflow/react` (React Flow) kütüphanesi:
  - Özel düğüm kartları (Custom Nodes): Tip uyumlu giriş/çıkış portları (renkli handle'lar), durum rozetleri (bekliyor, çalışıyor, başarılı, hatalı).
  - Geçersiz bağlantılarda kırmızı uyarı çizgisi, döngü engelleme.
- Sağ Inspector Paneli: Seçili node için parametreler, prompt sürümü, model seçimi, timeout, max retry, tahmini maliyet ve girdi kaynakları.
- Alt Drawer: Canlı yürütme kuyruğu, loglar, anlık token delta sayacı.

### 3.3 Sekme 2: Agent Observatory (`/projects/:p/studio?tab=agents&run=:r`)
- Merkez Çekirdek: "Orchestration Core" görseli; etrafında halkalar halinde dizilmiş Ajan Kümeleri (Insight, Strategy, Production, QA, Control).
- Canlı SSE Entegrasyonu:
  - `GET /api/v1/runs/:r/events/stream` bağlantısını dinler; koparsa `Last-Event-ID` ile otomatik yeniden bağlanır.
  - Gelen eventlere göre ajan kartlarının durumunu günceller (`idle → queued → running → waiting → completed / failed`).
  - Ajanlar arasındaki veri akışını gösteren hareketli parçacık (pulse) animasyonları: Yalnızca gerçek event geldiğinde tetiklenir!
  - Reduced-motion desteği ve tema seçeneği (Sade Operasyon Modu / Siber Neon Modu).
- Zaman Çizelgesi (Time-Travel Timeline): Geçmiş bir run'ın eventlerini zaman çizgisinde kaydırarak adım adım tekrar oynatma (replay) yeteneği.

### 3.4 Concept Gallery & Game DNA Arayüzü
- Concept Gallery (`/projects/:p/concepts`):
  - 3-8 adet interaktif Konsept Kartı: Mockup görseli, reklam hook ilk karesi, hedef kitle, hipotez açıklaması, kanıt bağlantıları, güven skoru, tahmini maliyet.
  - "Select & Build Workflow" düğmesi: Seçilen konsepti sabitleyerek otomatik workflow taslağı oluşturur.
- Game DNA (`/projects/:p/game-dna`):
  - Mekanik düzenleyici (Match-3 grid ayarları, kurallar), renk paleti seçici, karakter varlıkları yükleme alanı ve sürüm geçmişi tablosu.

### 3.5 Execution Ledger Explorer & Analytics Dashboard
- Execution Ledger (`/projects/:p/ledger`):
  - Sayfalanmış, filtrelenebilir (event_type, agent, status) olay tablosu.
  - Seçilen satır için JSON payload inceleyici, SHA256 integrity hash'i ve trace bağlantısı.
- Analytics Dashboard (`/projects/:p/analytics`):
  - Recharts veya ECharts ile çizilmiş grafikler: Token & Maliyet kırılımı, Model çağrı şelalesi (retry waterfall), Ajan gecikme dağılımları (p50/p95), QA geçiş oranları.
  - Bilinmeyen maliyetler "unknown" rozeti ile gösterilmeli, asla $0 olarak sunulmamalıdır.

## 4. KABUL VE DOĞRULAMA KRİTERLERİ
- React Flow üzerinde düğümler sürüklenip bağlanabilmeli, uyumsuz tipler bağlandığında kullanıcı uyarılmalıdır.
- SSE bağlantısı üzerinden gelen mock event akışı (`observatory-demo-events.jsonl`) Observatory ekranında ajanları canlı olarak aydınlatmalı ve durumlarını değiştirmelidir.
- Sayfa yenilendiğinde veya bağlantı koptuğunda SSE kayıpsız devam etmelidir.
- Tüm ekranlar responsive olmalı, TypeScript derlemesinde hiçbir tip hatası bulunmamalıdır (`npm run build` hatasız tamamlanmalıdır).
```

---

## 5. BAĞIMSIZ DOĞRULAMA VE ENTEGRASYON KONTROL LİSTESİ

Her ajan işini tamamladığında aşağıdaki entegrasyon matrisi üzerinden doğrulanır:

1. **Ajan 1 & Ajan 2 Entegrasyonu:** Temporal worker'ları, Ajan 1'in ürettiği SQLAlchemy ve Pydantic `EventEnvelope` nesnelerini kullanarak `run_events` ve `outbox_events` tablolarına hatasız yazar.
2. **Ajan 2 & Ajan 3 Entegrasyonu:** Trend ve Game DNA activity'leri Temporal DAG tarafından başarıyla tetiklenir ve `CreativeHypothesis` çıktıları `ContextBundle` olarak iletilir.
3. **Ajan 2 & Ajan 4 Entegrasyonu:** Production düğümleri (ComfyUI, Remotion, Phaser) activity olarak çağrılır; üretilen artifact'lar S3/yerel depolamaya yazılarak hash'lenir.
4. **Ajan 4 & Ajan 5 Entegrasyonu:** Üretilen `PlayableBundle` dosyası Ajan 5'in 7 Kademeli Quality Gate'inden geçirilir; Playwright test sonuçları `EvaluationReport` tablosuna işlenir.
5. **Ajan 5 & Ajan 6 Entegrasyonu:** Ajan 5'in `EventRelayWorker` servisi SSE üzerinden eventleri yayar; Ajan 6'nın Next.js Observatory ekranı bu akışı yakalayıp görselleştirir.

Bu plan, 6 ajanın sıfır sürtünmeyle aynı anda çalışmasını sağlayacak eksiksiz bir üretim yönergesidir.
