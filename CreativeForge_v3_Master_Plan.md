# CreativeForge Intelligence Studio v3.0 — MASTER PRODUCT & ENGINEERING PLAN

**Tarih:** 25 Ekim 2026  
**Durum:** Tasarım / hedef mimari; uygulandı anlamına gelmez  
**Amaç:** Trend sinyallerinden kanıta dayalı, özgün oyun/reklam konseptlerine; seçilen konseptten görsel, video ve temel HTML5 oynanabilir prototipe; eksiksiz operasyonel kayıt, canlı ajan izleme, değerlendirme ve deneysel öğrenmeye uzanan uçtan uca AI platformu.

> **Kapsam kararı:** Kullanıcının seçtiği #1, #2, #3, #4, #5, #6, #7, #9, #10 eksiksiz dahildir. Ayrıca kapsamlı **Execution Ledger (#11)** ve **Analytics & Reporting (#12)** birinci sınıf modüllerdir. #8'deki ileri düzey reklam ağına özel derleyici **bu sürümün kapsamında değildir**; fakat temel HTML/ZIP playable, PNG, MP4 export ve browser test, Creative Production çekirdeğinin parçasıdır.

## A. Proje ilkeleri ve tanım

- **Önce kanıt, sonra üretim:** Her trend önerisi kaynak, gözlem zamanı, bölge, veri erişim yöntemi ve güven/eksiklik açıklaması içerir. Reklam kütüphanesinde görünürlük, dönüşüm/CTR performansı ile karıştırılmaz.
- **İnsan seçimli konsept:** Trend -> hipotez -> en az üç konsept kartı -> onay -> üretim. Fikirler gerçek bir oyunun reklam kreatifleri olabilir; ayrı bir 'Game Discovery' modu yeni oyun konseptleri üretir. Bu iki hedef UI ve şemada ayrılır.
- **Gerçek ajan yürütmesi:** Observatory animasyonu, sahte 'thinking' metinlerinden değil zaman damgalı gerçek yürütme olaylarından beslenir. Modelin gizli düşünce zincirini gösterdiğini iddia etmez.
- **Her operasyon izlenebilir:** Kullanıcı talebi, kaynak snapshot'ı, model çağrısı, retry, token, fiyat, tool, artifact, değerlendirme, insan aksiyonu, export, ayar/sürüm değişikliği kendi ID'leriyle bağlantılıdır.
- **Temel iş verisi != telemetry:** PostgreSQL append-only event ledger ürün gerçeğidir; OpenTelemetry trace hata ayıklama katmanıdır. Trace kaybolsa bile ledger ve artifacts ayakta kalır.
- **Güvenli ve sorumlu tasarım:** Lisansları doğrulanmış kaynak ve varlıklar, izinli veri alımı, prompt injection savunması, izolasyonlu kod derleme, kişisel veri ve sır maskelemesi.
- **Reproducibility nüansı:** Sürüm, seed, prompt, model, giriş ve asset lineage saklanır; üçüncü taraf nondeterministic modellerde bit düzeyinde aynı üretim garanti edilmez. 'Replay' olayı yeniden gösterme, 'Rerun' gerçekten tekrar hesaplamadır.
- **Sadelik:** Her iş için ayrı LLM-agent açmak şart değildir. Deterministik toplama, skorlama, fiyatlama, validasyon gibi işlerde kod kullanılır; gerçek karar/üretim gerektiren yerlerde LLM kullanılır.

### A1. Resmi kapsam modülleri

| Kimlik | Modül | Sahip sistem | Kullanıcı ekranı | Ana çıktısı |
|---|---|---|---|---|
| M01 | Trend Intelligence & Evidence | `intel-service` | Trend Intelligence | `TrendSnapshot`, `TrendReport` |
| M02 | Creative Hypothesis & Ranking | `concept-service` | Concept Gallery | `CreativeHypothesis`, `ConceptBoard` |
| M03 | Experimentation & Feedback | `experiment-service` | Experiments | `ExperimentPlan`, `ExperimentResult` |
| M04 | Game DNA & Brand Consistency | `game-profile-service` | Game DNA | `GameProfileVersion` |
| M05 | Shared Agent Memory & Typed Artifacts | `agent-runtime` | Workflow / Agent detail | `ContextBundle`, typed artifact |
| M06 | Agent Observatory | `observatory-service` | Agent Observatory | live graph, timeline, run replay |
| M07 | Quality & Originality Gates | `quality-service` | Quality Center | `EvaluationReport`, gate decisions |
| M09 | Cost-Aware Orchestration | `model-gateway` | Analytics / Models | `UsageRecord`, `CostEntry` |
| M10 | Reproducibility & Secure Execution | `execution-service` | Runs / Versions / Security | `RunManifest`, sandbox test report |
| M11 | **Execution Ledger** | `ledger-service` | Execution Ledger | append-only ordered events |
| M12 | **Analytics & Reporting** | `analytics-service` | Analytics | trend, cost, latency, retry, artifacts, agent metrics |
| CORE | Image, Video, HTML5 Prototype | `creative-workers` | Workflow / Artifact Library | image, mp4, html/zip |

## B. Kullanıcı deneyimi, sayfalar ve URL haritası

**Temel hiyerarşi:** Organizasyon > Workspace > Project > Game Profile / Creative Campaign > Workflow > Run > Node Execution > Attempt / Model Invocation / Artifact.

### B1. Sol navigasyon ve sayfalar

| Menü / route örneği | Sekmeler/alt paneller | Başlıca gösterim | Kullanıcı eylemleri | Kayıt olayı |
|---|---|---|---|---|
| `/app` Overview | My Projects, Recent Activity, Alerts | proje listesi, son run, bütçe özeti, son konseptler | proje aç, kopyala, yeni kampanya | `PROJECT_CREATED` |
| `/projects/:p/intelligence` Trend Intelligence | Sources, Trends, Snapshots, Evidence, Scout Jobs | ülke/kategori/dönem filtreleri, kaynak tablosu, fark grafiği | tarama başlat, CSV içe al, snapshot onayla | `SOURCE_SYNC_*`, `TREND_REPORT_CREATED` |
| `/projects/:p/concepts` Concept Gallery | Ranked, Boards, Compare, Decisions | 3-8 mockup kartı, hipotez, rank, belirsizlik, yaratım maliyeti | seç, reddet, birleştir, varyant üret, nedenini yaz | `CONCEPT_*` |
| `/projects/:p/game-dna` Game DNA | Mechanics, Characters, Style, Constraints, Versions | oyun tanımı, mechanic spec, varlık kütüphanesi ve stil referansı | yeni profil sürümü, asset yükle, onayla | `GAME_PROFILE_VERSION_CREATED` |
| `/projects/:p/studio?tab=workflow` **Workflow Studio** | Canvas, Templates, Inspector, Queue, Preview | ComfyUI tarzı düğümler/kenarlar, hata durumları, input/output portları | node ekle/bağla, doğrula, çalıştır, durdur, onay beklet | `WORKFLOW_*`, `RUN_*` |
| `/projects/:p/studio?tab=agents&run=:r` **Agent Observatory** | Galaxy, Timeline, Activity, Compare, Inspector | merkez çekirdek + agent kutuları, gerçek event hareketleri, token maliyeti | ajan seç, trace aç, filtrele, replay, pause/resume | `OBSERVATORY_VIEWED`, `RUN_CONTROL_*` |
| `/projects/:p/artifacts` Artifact Library | Gallery, Lineage, Versions, Export | görsel/video/HTML preview; kaynak, checksum, provenance | indir, karşılaştır, işaretle, silme talebi | `ARTIFACT_*` |
| `/projects/:p/experiments` Experiments | Plans, Variants, Outcomes, Analysis | A/B planları, test hipotezleri, içe aktarılan gerçek metrikler | deney tanımla, varyant bağla, CSV içe al, sonuç incele | `EXPERIMENT_*` |
| `/projects/:p/ledger` **Execution Ledger** | Requests, Runs, Events, Models, Tools, Retries, Audits | tüm kayıtlar; filtre, arama, ilişki gezgini, export | run aç, diff, incele, JSONL/CSV indir | `AUDIT_EXPORT_REQUESTED` |
| `/projects/:p/analytics` **Analytics Dashboard** | Overview, Token & Cost, Agents, Workflow, Assets, QA, Experiments | KPI, zaman serileri, drilldown, segmentler | tarih/model/agent kırılımı, rapor export | `REPORT_EXPORTED` |
| `/projects/:p/quality` Quality Center | Gates, Human Reviews, Similarity, Rejections | teknik test, LLM judge, rubric, insan onayı | değerlendir, gerekçeli onay/red, yeniden dene | `EVALUATION_*`, `APPROVAL_*` |
| `/projects/:p/runs/:r` Run Detail | Summary, DAG, Timeline, Calls, Artifacts, Costs, Replay | tek çalıştırmanın uçtan uca anatomisi | manifest indir, rerun, compare | `RUN_DETAIL_OPENED` |
| `/settings/models` Model Registry | Providers, Models, Pricing, Routing, Budgets | sağlayıcı/parametre, fiyat, cache, API key statüsü | model politikası ayarla, bütçe onayla | `MODEL_POLICY_CHANGED` |
| `/settings/security` Security & Governance | Permissions, Retention, Secrets, Sandboxes, Audit | erişimler, saklama, redaksiyon, tehlike politikaları | rol ata, retention değiştir | `SECURITY_CONFIG_CHANGED` |

### B2. Studio — Sekme 1: Workflow Studio detaylı alan düzeni

- **Üst bar:** project/campaign seçimi, `workflow_version`, kaydet, compare, Validate, Dry Run, Run, Pause, Cancel, approved budget, live status.
- **Sol node palette:** Market Intelligence, Game DNA, Ideation, Generation, Evaluation, Human, Control, Export. Arama ve kategoriler.
- **Orta canvas:** React Flow graph; typed ports (ör. `ConceptSpec` -> `ImageAssetRequest`), parametre badge'i, başarısız node kırmızı, çalışan node animasyonlu, tamamlanmış node yeşil.
- **Sağ inspector:** seçili node için input sources, schema, model, prompt version, timeout, max retry, token/cost estimate, output preview, önceki denemeler.
- **Alt drawer:** Queue, Execution Log, Artifacts, QA, Events, token delta; otomatik scroll kapatma.
- **Template galerisi:** `Trend → Concept → Mockup`, `Selected Concept → Static Ad`, `Selected Concept → Video Ad`, `Selected Concept → Basic Playable`, `Full Campaign`.
- **Temel etkileşim:** node bağlantısı tip uyumluluğu; graph cycle kontrolü; her `Run` dondurulmuş workflow versiyonuna bağlıdır, çalışırken canvas düzenlemesi mevcut run'ı değiştirmez.

### B3. Studio — Sekme 2: Agent Observatory detaylı alan düzeni

- **Merkez:** görsel Orchestration Core; etrafında agent/worker kümeleri. Referans görselin neon hissi esin olabilir; gerçek UI modern kontrol paneli olarak kalır.
- **Bağlantı animasyonu:** görev yönlendirme=`TASK_DISPATCHED`, aktif model=`MODEL_CALL_STARTED`, tool=`TOOL_CALL_STARTED`, çıktı=`ARTIFACT_CREATED`; event yoksa animasyon yok.
- **Agent kartı:** avatar/icon, role, task, state, tool/model, input artifact ref, output artifact ref, elapsed, token billed/estimated, cost, retries.
- **Durum makinesi:** `idle → queued → running → waiting_tool / waiting_human → completed / failed / cancelled`; retry ayrı olay ve attempt sayısı olarak gösterilir.
- **Sağ inspector:** input-output özeti, tool arguments (redacted), model response excerpt izinli içerik, trace ID, maliyet, error, artifact preview, ilgili ledger linki.
- **Alt panel:** canlı timeline / filtreli event akışı; her olay için kaynak servis, timestamp, latency, severity, `event_id`.
- **Kontroller:** gerçek Pause/Resume/Cancel, `Step` yalnızca replay veya developer debug modunda; geçmiş eventleri zaman çizgisinden tekrar animasyonla oynatma; frozen snapshot compare.
- **Gözlemlenebilirlik notu:** hidden chain-of-thought saklanmaz veya görünür kılınamaz; saklanan veriler gerçek API giriş/çıkışları, tool sonuçları, yürütme olayları ve modelin açıkça döndürdüğü özetlerdir.

### B4. Concept Gallery — mockup kartı anatomisi

Kart: özgün oyun ekranı mockup'ı + örnek ad hook ilk karesi + konsept adı + kategori + oynanış spec bağlantısı + hedef kitle + hipotez + kanıt kaynakları + trend confidence + üretim güçlüğü + tahmini maliyet (birim/para birimi) + originality flags + format uyumu + `Select & Build Workflow` düğmesi. Bir kartın seçilmesi hem `CONCEPT_SELECTED` event'ini yaratır hem de Game DNA sürümünü sabitleyen Workflow draft oluşturur.

## C. Baştan sona kullanıcı yolculukları

### C1. Yeni bir oyun fikrini keşfetme
1. Kullanıcı ülke, platform, genre, zaman penceresi ve kaynak seçer.
2. Trend ingestion, lisans ve erişim kontrollerini aşabilen kaynaklardan snapshot toplar.
3. Normalize / deduplicate / provenance / confidence işlemleri yapılır.
4. Genre + ad creative pattern analizleri `TrendReport` üretir; belirsiz/kayıtsız veri açıkça işaretlenir.
5. `Hypothesis Engine` 3–8 özgün fikir üretir ve heuristic puanlar.
6. Kullanıcı mockup kartlarından birini seçer, değiştirir veya reddeder.
7. Seçim bir `GameProfileDraft` ve yaratıcı üretim workflow'uyla ilişkilendirilir.
8. İnsan onayından sonra image/video/playable üretimi yürütülür.
9. QA, artifact, cost, agent ve audit kayıtları kalıcıdır.

### C2. Var olan oyun için reklam kreatifi
1. Kullanıcı oyunun hak sahibi olduğunu doğruladığı game asset'leri ve gerçek mechanic spec'i yükler.
2. `Game DNA` görsel stil önerisini çıkarır; kullanıcı gerçek oyun mekaniğini doğrular.
3. Trend engine yalnızca uygun reklam hook'larını önerir, gameplay gerçeğini değiştirmez.
4. Kullanıcı konsepti seçer; creative brief ve budget belirler.
5. Generator image/video/basic playable varyantları oluşturur; her output lineage ile kaydedilir.
6. Deterministik test + LLM-assisted QA + human review yapılır.
7. Varyantlar artifact gallery'den indirilir; deney planı hazırlanır.

### C3. Hata analizi örneği
`request_id` -> `run_id` -> `node_execution_id` -> `attempt_id` -> `model_call_id` -> `tool_call_id` -> `artifact_id` -> `evaluation_id`. Dashboard'da başarısız video oluşturma çağrısı seçilince ilk input brief'i, prompt/template versiyonu, model adı, retry nedeni, fiyat durumu, son artifact ve root cause görülebilmelidir.

## D. Katmanlı sistem mimarisi

```
Next.js App Shell + React Flow + Observatory UI + Analytics
     │ REST writes / SSE reads
FastAPI API & Auth + Command Validation + Read Queries
     ├── Project/Game/Concept/Trend services
     ├── Workflow Controller ──> Temporal Workflows / Activities
     │      ├── Trend & Intelligence Workers
     │      ├── AI Agent Runtime + Typed Memory
     │      ├── LiteLLM Model Gateway / Budgets
     │      ├── ComfyUI / Image API Adapters
     │      ├── Remotion / Video API Adapters
     │      ├── Phaser Build + Browser QA Sandbox
     │      └── Evaluation & Human Approval
     ├── Transactional PostgreSQL Ledger / Outbox
     │      ├── Project + Workflow state
     │      ├── Node attempts + Model calls + Usage / Cost
     │      ├── Artifact manifests / Lineage
     │      └── Read models / Analytics
     ├── S3 Artifacts / previews / bundles
     └── Event Relay ──> SSE ──> real-time UI
OTel spans / metrics ──> Phoenix   (diagnostic trace, not ledger)
```

**Mantıksal servisleri ilk gün ayrı deployment yapmak zorunda değiliz:** FastAPI içinde modüler monolit, Temporal worker'ları ve ilgili medya/sandbox işçileri olarak başlarız. İstek hacmi artınca worker havuzlarını ayırırız. API, kullanıcının doğrudan Temporal yönetimini bypass etmesine izin vermez.

### D1. Seçilen teknoloji yığını

| Alan | Varsayılan teknoloji | Alternatif / not |
|---|---|---|
| Frontend | Next.js + TypeScript + Tailwind + shadcn/ui | React SPA da mümkün |
| Node editor | React Flow (`@xyflow/react`) | ComfyUI arayüzünü fork etmiyoruz |
| UI state | Zustand + TanStack Query | server state/client state ayrımı |
| Charts | Recharts / ECharts | yüksek hacimde agregasyon server-side |
| API | FastAPI + Pydantic v2 + SQLAlchemy + Alembic | OpenAPI'den TS tip üretimi |
| Orchestration | Temporal + Python SDK | Temporal history, özel ledger'ın yerine geçmez |
| Model gateway | LiteLLM adapter + internal metering | lisans ve provider uyumluluğu kontrolü |
| Telemetry | OpenTelemetry / OpenInference + Phoenix | Langfuse alternatif; ikisini aynı anda kurma zorunluluğu yok |
| DB | PostgreSQL + pgvector | tam metin + vektör hibrit retrieval |
| Artifact storage | yerel dosya (dev) / S3-compatible (prod) | immutable key + sha256 |
| Live | transactional outbox + SSE (Last-Event-ID) | iş büyürse Redis Streams ara katman |
| Image | ComfyUI + provider-specific image APIs | self-host model GPU opsiyonel |
| Video | Remotion + generative video provider adapter | Remotion kendi başına diffusion değildir |
| Playable | Phaser + TypeScript + Playwright | izole build sandbox |
| Security | OIDC provider / JWT; RBAC; secret store | local dev'de tek kullanıcı opsiyonu |
| Deploy | Docker Compose local; CI/CD GitHub Actions | sonradan Kubernetes şart değil |

## E. 9 geliştirme + core + özel telemetry için ayrıntılı iş paketleri

### M01 — Trend Intelligence & Evidence Engine
**Hedef:** Veri kaynağı belli, tarihli ve kanıtlı trend önerileri.

**Bileşenler:** `Source Registry`, `Connector Adapters`, `Ingestion Scheduler`, `Raw Snapshot Store`, `Normalizer`, `Deduplicator`, `Genre Classifier`, `Creative Pattern Miner`, `Evidence Resolver`, `Trend Report Generator`, `Confidence Calibrator`.

**Kaynak politikası:** Apple App Store resmi chart sayfaları, izinli uygulama/rank verileri, TikTok Creative Center gibi açıkça gösterilen reklam örnekleri ve kullanıcı CSV import'ları potansiyel kaynaklardır. Her kaynak için erişim şartları/API izni doğrulanmalıdır. Public sayfanın varlığı otomatik sınırsız scraping veya metrik API yetkisi demek değildir. Erişim yoksa `manual/imported` moduna düş; sahte veri oluşturma.

**Ölçütler:** `source_id`, `collection_method`, `observed_at`, `region`, `platform`, `genre`, `rank_snapshot`, `creative_tags`, `confidence`, `evidence_url`, `license_note`, `missingness`.

**Geliştirme işleri:**
- [ ] Kaynak sözleşmesi `SourceAdapter.fetch()` ve izin/ToS kontrol tablosu.
- [ ] Snapshot deduplication için içerik hash, zaman/bölge anahtarı.
- [ ] Zaman serisi normalize; kaynaklar arası rank ile performans ayrımını zorunlu kıl.
- [ ] Genre/mechanic sınıflandırma; etiketler insan tarafından düzeltilebilir.
- [ ] Insight'lara kanıt linki ve `low/medium/high` güven statüsü bağla.
- [ ] Veri eksikliğini kullanıcıya göster; kaynak devre dışıysa gracefully degrade.
- [ ] Trend UI: karşılaştırma, source inspector, snapshot diffs.

**Definition of Done:** Her önerilen trend en az bir doğrulanabilir gözleme bağlanır; kaynak kapatılırsa sistem uydurma veri üretmez; ilgili gözlem snapshot'ı run sonrası da açılabilir.

### M02 — Creative Hypothesis, Ranking & Concept Boards
**Hedef:** Hipotezi ve gerekçesi açık özgün konseptler, kullanıcı onayı.

**Bileşenler:** `Ideation Agent`, `Creative Angle Generator`, `Hypothesis Builder`, `Constraint Validator`, `Ranking Engine`, `Concept Board Image Generator`, `Decision Capture`.

**Hipotez sözleşmesi:** audience, game genre, intended hook, problem/desired emotional arc, evidence_refs, expected creative mechanism, primary metric, falsification condition, limitations, novelty rationale.

**Puan örneği (başlangıç heuristiği, tahmin edilen CTR değil):** `0.25 evidence + 0.20 game_fit + 0.20 novelty + 0.15 feasibility + 0.10 hook_clarity + 0.10 cost_fit`. Tüm eksenler 0..1 normalize; eksik evidence için confidence kırılımı; ağırlıklar admin config'te versiyonlanır. Kullanıcı kendi ağırlıklarını değiştirebilir. Benchmark'la kalibrasyon olmadan skoru performans olasılığı olarak gösterme.

**Geliştirme işleri:**
- [ ] Structured `CreativeHypothesis` Pydantic schema ve versiyon.
- [ ] Seçilen genre ve Game DNA'ya göre konsept strateji promptu.
- [ ] Negatif/pozitif kısıt validasyonu ve uygunsuz fikir reddi.
- [ ] Mockup board (oyun sahnesi + reklam hook karesi + açıklama + metadata).
- [ ] Rank rationale + evidence links + source confidence breakdown.
- [ ] Karşılaştırma, `select`, `reject`, `regenerate` ve gerekçeli override.
- [ ] Her seçimin `concept_id`, `version`, `actor`, `timestamp`, `reason` audit kaydı.

**Definition of Done:** Aynı brief için en az üç farklı konsept board'u açılabilir; her konsept hangi sinyallerden üretildiğini gösterir; seçim immutable workflow draft'a bağlanır.

### M03 — Experimentation & Learning Loop
**Hedef:** Farklı kreatif varyantlarının karşılaştırılabilir, ölçülebilir deneyi.

**Bileşenler:** `Experiment Planner`, `Variant Generator`, `Measurement Schema`, `Outcome Import`, `Statistical Analysis`, `Learning Memory`.

**Deney modları:** (i) `offline` — sentetik brief/QA/human acceptance, (ii) `real_campaign` — kullanıcı tarafından yetkili kampanya CSV/API verisi. Bu ayrım zorunludur; offline kalite puanı gerçek CTR/CPI değildir.

**Ölçütler:** `variant_id`, kreatif tek-değişken farkı, randomization/allocation note, impressions, clicks, installs, spend, region, attribution window, device, date range; tıklama ve kurulum metrikleri ancak uygun gerçek veri ile hesaplanır. CPI=spend/installs, CTR=clicks/impressions, IPM=installs/impressions*1000; paydası sıfır olan metrikler `null`.

**Geliştirme işleri:**
- [ ] A/B hipotezi ve baseline seçme.
- [ ] Hook/CTA/visual tek değişkenli varyant planı.
- [ ] CSV schema validator ve metadata leakage kontrolü.
- [ ] Güven aralığı, örneklem büyüklüğü, değişken kontrolü; 'kazanan' erken ilan edilmez.
- [ ] Offline/real sonucu farklı rozet ve grafiklerde göster.
- [ ] Sonuçların `LearningInsight` olarak yeniden konsept üretimine beslenmesi.
- [ ] Tek başına korelasyonu nedensellik olarak sunma.

**Definition of Done:** Aynı deneyde iki varyantın maliyet/kalite/performans karşılaştırması yapılır; gerçek veri olmadan performans iddiası gösterilmez.

### M04 — Game DNA & Brand Consistency
**Hedef:** Oyun mekanikleriyle görsellerin ve reklamların tutarlı kalması.

**Model:** `GameProfileVersion` = `mechanics_spec`, `genres`, `board_rules`, `target_audience`, `style_tokens`, `palette`, `character_refs`, `sprite_manifest`, `sound_rules`, `brand_constraints`, `do_not_generate`, `allowed_ad_claims`, `asset_rights`, `approval_status`.

**Geliştirme işleri:**
- [ ] Görsel upload sonrası model tabanlı stil önerisi; mekanikleri otomatik kesin bilgi sayma.
- [ ] Mechanic spec form/editor ve validasyon; match-3, merge, sorting gibi örnek preset.
- [ ] Referans görsel/karakter/sprite kütüphanesi ve hak/izin metadata.
- [ ] Renk, aspect ratio, karakter kimliği, görsel ton, yasak öğeler.
- [ ] Her konsept/asset/run için `game_profile_version_id` freeze.
- [ ] Cross-modal consistency checker (image/video/playable).
- [ ] Değişiklikte diff ve etkilenen downstream node'ları göstermek.

**Definition of Done:** Bir profilin versiyonu değişince eski run etkilenmez; QA raporu stil/mechanics uyumunu raporlar.

### M05 — Shared Agent Memory, Typed Handoff & Blackboard
**Hedef:** Ajanlar arasında güvenilir, maliyet kontrollü ve yeniden üretilebilir context aktarımı.

**Bellek katmanları:**
1. **Run-local working context:** kısa yaşayan, özel run'a ait referanslar; büyük payload yerine artifact ID.
2. **Project factual memory:** onaylı Game DNA, kurallar, branding, geri bildirim.
3. **Evidence retrieval:** pgvector + PostgreSQL FTS; kaynak ve alıntı ID'si birlikte döner.
4. **Learning memory:** deney sonuçları ve insan değerlendirmesi; henüz doğrulanmamış hipotezler ayrı statüde.

**İşleyiş:** `ContextSelector` en alakalı referansları toplar -> token budget hesaplar -> `ContextBundle` yaratır -> agent validated `OutputSchema` üretir -> artifact store'a immutable sürüm yazar -> pointer üzerinden handoff yapılır.

**Geliştirme işleri:**
- [ ] `ArtifactBase {id, schema_version, content_hash, producer_id, parent_ids}`.
- [ ] Pydantic schema registry ve `validate_edge(from_output, to_input)`.
- [ ] `ContextBundle` ile source pointer, snippet, relevance, token_budget.
- [ ] Blackboard: sadece versioned write, optimistic locking; paylaşımda yetki kontrolü.
- [ ] Retrieval dedup ve freshness; context budget aşımında priority truncation.
- [ ] Handoff failsafe: schema validation fail -> repair attempt -> bounded retry -> human escalation.
- [ ] Deterministik node'larda LLM kullanımı kaldır; işin doğasına göre executor seç.

**Definition of Done:** Yanlış tipte edge compile edilmiyor; eski artifact değiştirilmiyor; her agent'a hangi memory girişinin verildiği görülebiliyor.

### M06 — Agent Observatory: canlı ve tekrar oynatılabilir ajan operasyon merkezi
**Hedef:** MagmaLabs referans görselindeki merkezden çevreye yayılan ajan topolojisini gerçek execution telemetry ile gösterme.

**Mimari:** `LedgerOutboxRelay` -> `SSE /events?run_id=...` -> client state projection -> SVG/Canvas/WebGL agent network renderer. React Flow görsel editor; agent galaksisi için özel bir render katmanı tercih edilebilir (React + SVG, gerektiğinde PixiJS); zorunlu ağır 3D engine yoktur.

**Visual language:** Merkez `Creative Core`, dış halkalar: Data & Insight, Strategy, Asset Production, QA & Governance. Kenarlar veri bağımlılıklarını gösterir; hareketli sinyaller gerçekten `TASK_DISPATCHED`, `MODEL_CALL_*`, `ARTIFACT_*`, `TOOL_CALL_*` eventleriyle tetiklenir. Her renk/animasyon için erişilebilir metin ve reduced-motion modu vardır.

**Geliştirme işleri:**
- [ ] Ajana ait gerçek state machine ve event -> visual reducer.
- [ ] SSE Last-Event-ID ile reconnect/replay ve per-run `seq` sıralama.
- [ ] Aktif node seçince o `node_execution_id` detay inspector'u.
- [ ] Time travel (yalnızca gösterim) + run compare.
- [ ] Pause/Resume/Cancel komutlarını API -> Temporal Signal/Update -> audit olayına bağla.
- [ ] `Step` düğmesini historical replay için veya developer breakpoint kontrollü modda tut; canlı modelin iç adımlarında durduğunu iddia etme.
- [ ] Sade görünüm (operations) ile neon görünüm (presentation) tema seçenekleri.
- [ ] Demo Mode yalnızca sentetik event fixture ile ve kalıcı görünür `SIMULATION` bandı ile gösterilsin.

**Definition of Done:** Bir ajan retry yaptığında ekranda ayrı attempt ve neden görünür; reconnect sonrası event kaybı olmaz; tarihsel replay aynı event dizisine dayanır.

### M07 — Multi-Layer Quality, Compliance & Originality Gates
**Hedef:** Üretimin düzgün çalışması, brief uyumu, görsel tutarlılık, özgünlük riski ve insan onayı.

**Gate sırası:**
1. **Schema Gate:** Output tipi, zorunlu alanlar, referanslar, media metadata.
2. **Technical Gate:** render/build, kaynak dosya varlığı, HTTP hata, tarayıcı responsive, playable input interaction, runtime JS error.
3. **Game Truth Gate:** mekanik gerçeği, yanıltıcı oynanış olmaması, Game DNA kısıtları.
4. **Visual/Audio Gate:** kalite, çözünürlük, CTA okunurluğu, tema tutarlılığı, ses seviyesi temel kontroller.
5. **Similarity/IP Risk Gate:** perceptual hash, embedding similarity, karakter/logo eşleşme uyarıları; otomatik hukuki kesinlik yok.
6. **LLM Judge:** rubrik bazlı, gerekçeli/kanıtlı değerlendirme; model veya rubric sürümü kaydedilir.
7. **Human Review:** kritik/belirsiz çıktı için onay/ret/yorum; zorunlu durumları konfigüre et.

**Geliştirme işleri:**
- [ ] Gate rule registry, `gate_version`, severity, threshold, actionable failure code.
- [ ] Deterministik testleri model değerlendirmesinden ayır; 0/1 technical failure ile 0-5 subjective score ayrı.
- [ ] LLM judge seti için örnek golden dataset, kör insan kontrolü, disagreement ölçümü.
- [ ] Similarity uyarısında asset/reference provenance sakla, gerçek telif garantisi verme.
- [ ] Targeted regeneration yalnızca hatalı node alt grafını etkiler; max retry ve max budget uygulansın.
- [ ] Human reviewer gerekçesi ve artifact sürümü immutable kayıtlansın.

**Definition of Done:** Kırık playable başarıyla export edilmez; QA skorunu hangi input ve rubrik ile aldığı görülebilir; insan reddi düzeltme akışını başlatır.

### M09 — Cost-Aware Routing, Budget & Model Operations
**Hedef:** Her çağrıyı maliyet/latency/kalite politikasıyla yönlendirmek, finansal yükü görünür kılmak.

**Model Registry alanları:** `provider`, `model_id`, `capabilities`, `context_window`, `supports_schema`, `pricing_version`, `rate_limit`, `quality_tier`, `enabled`, `data_policy`, `concurrency_limit`. Pricing birimi: input/output token, cached token, image, output resolution, generated second, provider credit, GPU-second vb.

**Rotalama:** görev tipi -> quality floor / schema / data policy -> fiyat ve hız uygun adaylar -> per-run estimated upper bound -> seçilen model -> provider response actual usage -> invoice reconciliation. Model fallback sırasında kendiliğinden hassas verinin başka bir sağlayıcıya gitmesini engelleyen allowlist.

**Geliştirme işleri:**
- [ ] Model gateway adapter (LiteLLM text) + özel image/video metering.
- [ ] `PriceCatalog` para birimi/birim/effective_at ve değişmeyen fiyat snapshot'ı.
- [ ] Tenant/project/run/agent bazında budget threshold (soft alert + hard deny).
- [ ] Token estimation yalnızca ön tahmin; actual usage gelince ayrı status.
- [ ] Cache-hit sayaçları, provider-reported cached input ayrımı, billable miktar.
- [ ] Dynamic fallback rule; timeout/retry count ve backoff jitter.
- [ ] Maliyet alarmı: budget %80, %100, atypical spikes, unknown pricing.
- [ ] Prompt/template ve output kalite değişimlerini model değişimi karşılaştırmalarına bağla.

**Definition of Done:** Kullanıcı X para birimi bütçe koyduğunda yeni işlerin kabul politikası buna uyar; maliyeti bilinmeyen medya çağrıları `unpriced`, asla sıfır gösterilmez.

### M10 — Reproducibility, Versioning, Safe Execution
**Hedef:** Her run için frozen manifest, güvenli kod yürütme, sürüm karşılaştırması ve failure recovery.

**`RunManifest` içerikleri:** `run_id`, project/campaign, request snapshot hash, workflow_version, node_registry_versions, prompt_versions, GameDNA_version, trend_snapshot_ids, source licenses, model_requested/resolved/version, parameters, random seeds (varsa), pricing_snapshot, code commit SHA, input artifact SHA, environment image digest, evaluation rubric versions.

**Geliştirme işleri:**
- [ ] Her Run girişinde manifest freeze; işlem ortasında settings değişikliği eski run'a etki etmez.
- [ ] Append-only revisions; workflow graph JSON diff, replay vs rerun seçeneği.
- [ ] Retry idempotency key, non-repeatable side-effect guard, external call reconciliation.
- [ ] Playable build için ayrılmış disposable sandbox, en az ayrı kullanıcı/namespace, read-only rootfs, no host mounts, kaynak sınırı, ağ çıkışı default deny, süresi dolan workspace imhası.
- [ ] Uzak URL fetch işlerinde allowlist, SSRF koruması, içerik türü/boyut doğrulama.
- [ ] Secrets yalnızca server side; generated code'a ve prompt'a secret geçirilmeyecek.
- [ ] Sürüm saklama ve audit; üretim hash zincirine opsiyonel tamper-evidence ekle.
- [ ] Sandbox güvenliğinin yalnızca Docker ile mutlak sağlanamayacağını kabul et; yüksek riskte microVM sandbox sağlayıcısı tercih et.

**Definition of Done:** Aynı run'a ait manifest export edilebilir, kaynak sürüm bulunabilir; üretilen kodun host secret/ağ erişimi güvenlik testlerinde engellenir.

### CORE — Creative Asset Generation
**Image:** ConceptSpec -> prompt/constraints -> ComfyUI JSON/API veya image provider -> ImageAsset -> thumbnail & metadata -> QA. ComfyUI queue/job ID ve prompt hash kaydedilir.

**Video:** Creative storyboard -> shot plan -> image/video provider -> Remotion composition (metin, CTA, zamanlama, geçiş, ses) -> MP4/GIF preview -> QA. Remotion ile kod tabanlı render ile gerçek generative video modelini ayrı ürün kabiliyeti olarak belirt.

**Basic Playable:** `GameMechanicsSpec` + Sprite Manifest -> codegen template seçimi -> TypeScript/Phaser source -> restricted sandbox build -> Playwright test -> preview -> HTML/ZIP export. Bu yalnızca temel prototip export'udur, reklam ağlarına tam uyumluluk/otomatik yayınlama garantisi vermez.

**Geliştirme işleri:**
- [ ] ComfyUI adapter + placeholder mock provider (demo etiketli).
- [ ] Önce tek match-3, merge/sort daha sonraki preset.
- [ ] Remotion için 9:16 preview composition ve temel giriş/CTA animasyonları.
- [ ] Model-generated assets için içerik/provenance metadata.
- [ ] Artifact manifest ve tüm oluşturma giriş/çıkış kayıtları.
- [ ] CDN değil kısa süreli signed download URL; canlı bundle browser sandbox içinde önizlenir.

### M11 — Execution Ledger (BİRİNCİ SINIF ÇEKİRDEK)
**Hedef:** Kullanıcının talep ettiği 'hangi istek nasıl istendi, ne yaptı, kaç token, kaç artifact, kaç deneme, ne kadar maliyet, hangi model/ajan, hangi kaynak ve hangi onay' sorularının tamamını cevaplamak.

**Kritik prensip:** Her API, agent, worker ve kullanıcı eylemi standart `EventEnvelope` + ilgili ilişkisel kaydı oluşturur. OLTP business tables yalnızca gerçeğe dönük sorguları tutar; append-only ledger ise olayların zaman çizgisidir. İkisi **aynı PostgreSQL transaction** veya atomic state+outbox yaklaşımıyla tutarlı yazılır. Temporal activity dış çağrıyı tamamladıktan sonra event yazmada başarısız kalırsa idempotency/reconciliation politikası uygulanır.

**Event envelope — zorunlu alanlar:**
```json
{
  "event_id":"evt_01...",
  "event_type":"MODEL_CALL_FINISHED",
  "schema_version":1,
  "occurred_at":"2026-10-25T12:00:00Z",
  "recorded_at":"2026-10-25T12:00:00.310Z",
  "project_id":"proj_123",
  "campaign_id":"camp_123",
  "request_id":"req_123",
  "run_id":"run_123",
  "run_seq":42,
  "workflow_version_id":"wfv_123",
  "node_execution_id":"ne_123",
  "attempt_id":"att_2",
  "agent_id":"concept_agent",
  "trace_id":"012345...",
  "span_id":"abc123...",
  "actor_type":"worker",
  "actor_id":"model_gateway",
  "correlation_id":"corr_123",
  "causation_event_id":"evt_01previous",
  "payload_ref":"obj://private/event-payload-sha256",
  "payload_preview":{"model":"example-text-model","usage_status":"provider_reported"},
  "redaction_level":"metadata_only",
  "integrity_hash":"sha256:..."
}
```
*Yukarıdaki kayıt şematik örnektir, çalıştırılmış gerçek bir çağrı değildir.*

**Event taxonomy:**
- Request & approvals: `REQUEST_RECEIVED`, `BRIEF_VERSION_CREATED`, `USER_INPUT_CHANGED`, `CONCEPT_SELECTED`, `CONCEPT_REJECTED`, `APPROVAL_REQUESTED`, `APPROVAL_GRANTED`, `APPROVAL_DENIED`.
- Trend: `SOURCE_SYNC_QUEUED`, `SOURCE_SYNC_STARTED`, `SOURCE_FETCHED`, `SOURCE_FETCH_FAILED`, `TREND_SNAPSHOT_CREATED`, `TREND_REPORT_CREATED`.
- Workflow: `WORKFLOW_VERSION_CREATED`, `RUN_CREATED`, `RUN_QUEUED`, `RUN_STARTED`, `RUN_PAUSED`, `RUN_RESUMED`, `RUN_CANCELLED`, `RUN_COMPLETED`, `RUN_FAILED`.
- Agent and node: `TASK_DISPATCHED`, `AGENT_STARTED`, `AGENT_FINISHED`, `NODE_STARTED`, `NODE_FINISHED`, `NODE_FAILED`, `ATTEMPT_STARTED`, `ATTEMPT_FAILED`, `RETRY_SCHEDULED`, `RETRY_EXHAUSTED`.
- Model: `MODEL_ROUTE_SELECTED`, `MODEL_CALL_STARTED`, `MODEL_CALL_FINISHED`, `MODEL_CALL_FAILED`, `MODEL_USAGE_RECORDED`, `MODEL_USAGE_CORRECTED`, `MODEL_FALLBACK_USED`.
- Tools/artifacts: `TOOL_CALL_STARTED`, `TOOL_CALL_FINISHED`, `TOOL_CALL_FAILED`, `ARTIFACT_CREATED`, `ARTIFACT_VALIDATED`, `ARTIFACT_REVISED`, `ARTIFACT_EXPORTED`, `ARTIFACT_DELETION_REQUESTED`.
- QA / cost / governance: `EVALUATION_CREATED`, `QUALITY_GATE_PASSED`, `QUALITY_GATE_FAILED`, `COST_ESTIMATED`, `COST_COMMITTED`, `COST_RECONCILED`, `BUDGET_ALERTED`, `BUDGET_BLOCKED`, `POLICY_VIOLATION_BLOCKED`, `SETTINGS_CHANGED`, `DATA_REDACTED`.

**Önemli kimlik ayrımı:** `run_id` mantıksal workflow çalıştırma; `node_execution_id` DAG node yürütümü; `attempt_id` her tekrar denemede farklı; `model_invocation_id` her fiziksel sağlayıcı isteği; `artifact_id` her immutable çıktı. Bir node 3 kez denerse 3 attempt ve koşula göre 3 model invocation oluşur; 'logical node' bir kez sayılır. İdempotent replay tüketici iki kez event alırsa analytics çift saymaz.

**Prompt ve response saklama politikası:** Kullanıcının isteği *açık rızası/ayarına göre* şifreli tam gövde veya maskelenmiş içerik referansıyla saklanabilir. Varsayılan telemetry payload metadata-only; API key/PII/özel ticari veri ve modelin erişilemeyen gizli internal reasoning içeriği tutulmaz. Tam metin görüntüleme RBAC+audit+retention'a bağlıdır. İş kaydı 'her şeyi' teknik olarak mümkün olan, izinli ve güvenli kapsamda ifade eder.

**Token usage — ayrıştırılmış alanlar:**
- `input_tokens`, `output_tokens`, `total_tokens` (provider-reported veya estimated flag);
- `cached_input_tokens`, `cache_creation_tokens`, modality breakdown (`text/image/audio`), `reasoning_tokens` **yalnızca provider döndürürse**;
- `billable_input_units`, `billable_output_units`, `billable_media_units`, `billable_seconds`, `unit_name`;
- `usage_source` = `provider_reported` | `estimated` | `invoice_reconciled` | `missing`;
- `price_snapshot_id`, `currency`, `estimated_cost`, `actual_cost`, `billed_cost`, `confidence`.

**No double count:** cache token bileşenleri total input'a zaten dahil olabileceği için ikinci kez eklenmez. Retry maliyeti node'ın **tüm fiziksel invocation** kayıtları üzerinden toplanır. Streaming usage son eventte geliyorsa `pending` -> `final` güncellenir; başarısız ama ücretli provider çağrıları muhasebeden düşürülmez. Image/video token dışı faturalar ayrı birimde saklanır; bilinmiyorsa `unknown`, sıfır değil.

**Bütün giriş/çıkış kayıtları:**
`original_user_request` (encrypted/ref), `normalized_brief`, `client_request_id`, actor, timestamp, locale; context inputs (source IDs), node parameters, prompt/template version, tool args/result (sanitized), provider request ID, response metadata, generated files (S3 URI & SHA), reviewer events, retries and failure codes, total cost, final outputs and manifest.

**Outbox & delivery:** Tek transaction'da ledger event ve `outbox_event` yaz; relay SSE'ye yayımlar; at-least-once semantiğiyle duplicate kabul edilir fakat `event_id` ile de-duplicate edilir; her `run_seq` monoton ve unique'dir. `Last-Event-ID` veya `since_seq` ile kopan istemci boşluğu doldurur.

**Retention (önerilen ayarlanabilir varsayılan):** audit metadata 365 gün; runtime events 180 gün; encrypted prompt/response content 30 gün; artifacts 180 gün; trace details 30 gün. Organizasyon ihtiyaçları, lisans, GDPR/KVKK yükümlülükleri ve kullanıcı silme talepleri önceliklidir. Tüm süreler ürün config'i olmalıdır, hiçbir veri 'sonsuz' varsayılan saklanmamalıdır.

**Definition of Done:** Tek `run_id` ile tüm request, node, attempt, tool, model, token, cost, artifact ve approval kayıtları join edilebilir ve indirilebilir; sahte token verisi yazılmaz; event stream reconnect'te kayıp yaşanmaz.

### M12 — Analytics & Reporting Dashboard
**Hedef:** Executions Ledger'dan sorgu/ağırlıklandırma tutarlılığı olan ölçülebilir dashboard, filtreler ve açıklanabilir KPI'lar.

**Sayfa bölümleri ve metric formülleri:**

| Dashboard sekmesi | KPI'lar | Kaynak tablolar | Drilldown |
|---|---|---|---|
| Overview | total runs, completed/failed/cancelled, unique briefs, artifacts, total known spend | `runs`, `requests`, `artifacts`, `cost_entries` | Run Detail |
| Token & Cost | input/output/cached tokens, known spend, cost per successful run, unpriced invocations | `model_invocations`, `usage_records`, `cost_entries` | Model Call Detail |
| Agents | task count, success rate, p50/p95 latency, errors, retries, avg token, agent cost | `agent_sessions`, `node_executions`, `attempts` | Agent Observatory |
| Workflows | run throughput, critical path, bottleneck nodes, failed DAG branches, version comparison | `runs`, `node_executions`, `workflow_versions` | Workflow Studio / Diff |
| Assets | images/video/playables created, approved/rejected, bytes, reuse, generation time/cost | `artifacts`, `artifact_lineage`, `evaluations` | Artifact Library |
| Quality | gate pass %, rubric score distribution, judge-human agreement, root causes | `evaluations`, `quality_gate_results`, `human_reviews` | Quality Center |
| Experiments | offline approval score, real CTR/IPM/CPI when available, allocation, intervals | `experiments`, `experiment_variants`, `outcome_metrics` | Experiment Detail |
| Reliability | SLO success, MTTR approximation, retries/recovery, queue wait, idempotency duplicates | `runs`, `attempts`, `run_events` | Run Detail |
| Data Sources | source freshness, coverage, errors, missingness, evidence count | `trend_sources`, `trend_observations`, `source_sync_jobs` | Trend Inspector |

**Filtreler:** date range, project, campaign, workflow version, source, region, category, agent, node, model, provider, output type, run status, evaluation outcome, usage status, currency. İndirme: CSV (tablolar), JSONL (olaylar), PDF rapor opsiyonel gelecek aşama.

**KPI tanımları (yanlış sunumu önlemek için):**
- `run_success_rate = completed_runs / terminal_runs`, terminal = completed+failed+cancelled (cancelled'ı ayrıca raporla; gerekirse başarısız dışı da görüntüle).
- `node_retry_rate = retried_node_executions / all_node_executions`.
- `retry_attempts_total = sum(max(attempt_count-1, 0))`; aynı attempt hem logical retry hem model retry olarak iki kez sayılmaz.
- `cost_per_approved_artifact = allocated_known_cost / approved_artifact_count`, ortak DAG maliyeti için allocation policy açıkça belirtilir; sıfır paydaya `null`.
- `token_total = SUM(provider_reported_or_estimated)` ve `estimated_token_share` ayrı gösterilir; cached input toplamları ikinci kez toplanmaz.
- `unpriced_call_ratio = unpriced_invocations / all_invocations`; unknown cost hiçbir grafikte sıfır olarak yer almaz.
- `p95_latency` gerçek measured durations üzerinden; queue wait ayrı.
- `QA_pass_rate = passed_gate_executions / all_final_gate_executions`.
- CTR/CPI/IPM yalnızca gerçek outcome veri alanları mevcutsa ve kaynak/attribution netse gösterilir.

**Geliştirme işleri:**
- [ ] SQL materialized views / incremental aggregation / gerektiğinde yeniden hesaplama.
- [ ] Date/model/agent/workflow filtreli ilk 7 temel dashboard.
- [ ] Model call detail and retry waterfall grafikleri.
- [ ] Run compare (same brief different workflow/model) fark paneli.
- [ ] Export audit + row-level permission.
- [ ] CSV/JSONL export, scheduled daily summaries ileriki faz.
- [ ] Grafikte her metriğin tanımını tooltip olarak açıkla.

**Definition of Done:** Dashboard sayıları aynı run'a ait ilişkisel kayıtlarla doğrulanır; örneğin 2 retry sonucu 3 fiziksel çağrı maliyeti görünür; kullanıcı tıklayarak ilgili satıra ulaşır.

## F. Agent/worker kataloğu ve iş yükü sahipliği

**Orkestrasyon politikası:** Agent = LLM destekli karar/üretim yapan sorumluluk birimi; Worker = deterministik hesap, aktarım veya derleme yapan işlemdir. Sistemin ekranda gösterdiği her kutu 'LLM-agent' değildir; türü ayrı belirtilir.

| ID | Agent / worker | Tür | Sorumluluk | Input → Output | Güvenli tamamlanma koşulu |
|---|---|---|---|---|---|
| A01 | Trend Scout | Connector worker | izinli kaynaklardan veri | `SourceQuery` → `TrendSnapshot` | evidence ve source hash mevcut |
| A02 | Genre Analyst | hybrid agent | genre/mechanic gruplama | `TrendSnapshot` → `GenreReport` | kaynağa dayalı sınıflandırma |
| A03 | Creative Pattern Miner | hybrid agent | hook/CTA kalıp çıkarma | `CreativeEvidence[]` → `PatternReport` | evidence_refs zorunlu |
| A04 | Insight Synthesizer | LLM agent | özetlenmiş trend çıkarımı | reports → `TrendReport` | belirsizlik saklanır |
| A05 | Game DNA Extractor | vision agent | stil ve asset özellikleri | `GameAssets` → `GameProfileDraft` | insan mechanic doğrulaması |
| A06 | Creative Strategist | LLM agent | test edilebilir fikir hipotezleri | `TrendReport+GameProfile` → `Hypothesis[]` | constraint validator |
| A07 | Concept Ranking | deterministic | çok ölçütlü ağırlıklı skor | `Hypothesis[]` → `RankedConcepts` | açıklanabilir skor |
| A08 | Mockup Board Designer | image+layout worker | konsept kartları | `ConceptSpec` → `ConceptBoard[]` | preview + cost kaydı |
| A09 | Asset Prompt Builder | LLM agent | image/video prompt planlama | `Concept+GameDNA` → `AssetPlan` | typed output |
| A10 | Image Production | provider worker | sprite/scene yaratma | `AssetPlan` → `ImageAsset[]` | artifact SHA+usage |
| A11 | Video Producer | media worker | video klip ve kompozisyon | `Storyboard` → `VideoAsset` | render probe |
| A12 | Playable Planner | LLM agent | basit oyun mekanik spec | `GameSpec+Concept` → `PlayableSpec` | rules validated |
| A13 | Playable Code Agent | code agent | Phaser template/kod üretimi | `PlayableSpec+Assets` → `SourceBundle` | schema + lint/build |
| W14 | Sandbox Build Runner | secured worker | build, test, report | `SourceBundle` → `BuildReport` | isolated environment |
| A15 | Creative QA Evaluator | hybrid | rubric & technical QA | `Artifact+Brief` → `EvaluationReport` | deterministic gates pass |
| W16 | Similarity Checker | deterministic+ML | originality risk sinyalleri | `Asset+ReferenceCorpus` → `SimilarityRisk` | threshold + human warning |
| W17 | Experiment Analyzer | statistical worker | variant performance | `OutcomeDataset` → `ExperimentResult` | data quality checks |
| W18 | Cost Controller | deterministic worker | quota, pricing, circuit breaker | `CallEstimate+Budget` → `Allow/Deny` | budget policy |
| W19 | Orchestration Core | deterministic orchestrator | DAG scheduling, branch, checkpoint, retry | `WorkflowRun` → `RunState` | durable/idempotent |
| W20 | Ledger Writer | deterministic infra worker | events/outbox/cost/artifacts | actions → `LedgerEvents` | DB commit |

**Kümeler:** `Insight` A01–A04; `Strategy` A05–A08; `Production` A09–A13; `QA` W14–W17; `Control` W18–W20. Observatory renk/şekilleri bu kategoriden türetilir. Görselleştirilen gerçek çalışma birimleri `agent_id`, `task_id`, `node_execution_id` ile eşleştirilir.

## G. Node kataloğu — tüm portlar ve koşullar

**Temel port tipleri:** `SourceQuery`, `TrendSnapshot`, `TrendReport`, `GameAssets`, `GameProfileVersion`, `CreativeHypothesis[]`, `RankedConcepts`, `ConceptSpec`, `ConceptBoard[]`, `ApprovalDecision`, `AssetPlan`, `ImageAsset[]`, `Storyboard`, `VideoAsset`, `PlayableSpec`, `SourceBundle`, `PlayableBundle`, `EvaluationReport`, `ExperimentPlan`, `ExperimentResult`, `ExportManifest`.

| Kategori | Node tipi | Zorunlu input → output | Executor | UI inspector parametreleri |
|---|---|---|---|---|
| Market | Source Fetch | SourceQuery → TrendSnapshot | worker | region, period, connector |
| Market | Deduplicate | Snapshot[] → Snapshot | worker | similarity, key |
| Market | Genre Classifier | Snapshot → GenreReport | hybrid | taxonomy, threshold |
| Market | Ad Pattern Extract | CreativeEvidence[] → PatternReport | hybrid | hook tags, batch |
| Market | Trend Synthesis | GenreReport + PatternReport → TrendReport | agent | model, prompt version |
| Profile | Game Asset Import | files → GameAssets | worker | rights, format |
| Profile | Game DNA Extract | GameAssets → GameProfileDraft | agent | style constraints |
| Profile | Human Confirm Mechanics | Draft → GameProfileVersion | human | mandatory checklist |
| Concept | Creative Brief | user brief + GameProfile → CreativeBrief | form | audience, goals |
| Concept | Hypothesis Generate | TrendReport + Brief → Hypothesis[] | agent | count, diversity |
| Concept | Hypothesis Rank | Hypothesis[] → RankedConcepts | worker | weights, exclusions |
| Concept | Concept Board Render | Concepts → ConceptBoard[] | agent+worker | mockup count, model |
| Concept | User Select Board | Boards → ConceptSpec | human | selected ID/reason |
| Production | Prompt Builder | ConceptSpec → AssetPlan | agent | prompt/model version |
| Production | Image Generator | AssetPlan → ImageAsset[] | provider worker | model, resolution, seed |
| Production | Storyboard Planner | ConceptSpec → Storyboard | agent | duration, shots |
| Production | Video Generator | Storyboard + Assets → VideoAsset | media worker | provider, seconds |
| Production | Remotion Render | Storyboard + Assets → VideoAsset | worker | resolution/fps |
| Production | Playable Spec | Concept + GameDNA → PlayableSpec | agent | preset, mechanics |
| Production | Phaser Codegen | PlayableSpec + Assets → SourceBundle | agent | template version |
| Production | Sandbox Build | SourceBundle → PlayableBundle | worker | cpu/memory/timeout |
| Production | Browser QA | PlayableBundle → EvaluationReport | worker | browsers, viewports |
| Quality | Schema Validate | any typed artifact → result | worker | schema version |
| Quality | Visual QA | Image/Video + Brief → EvaluationReport | agent | rubric version |
| Quality | Mechanics QA | Playable + GameDNA → EvaluationReport | hybrid | rule set |
| Quality | Similarity Risk | Asset + corpus → risk report | worker | threshold |
| Quality | Quality Gate | EvalReports → Pass/Fail | worker | gate policy |
| Quality | Human Approval | Artifact + QA → ApprovalDecision | human | required reviewers |
| Control | Branch | decision → selected graph edge | worker | expression |
| Control | Merge | typed inputs → output | worker | merge strategy |
| Control | Retry Policy | failure → control signal | worker | retries, backoff |
| Control | Budget Gate | estimate → allow/deny | worker | limits |
| Control | Artifact Save | any output → ArtifactRef | worker | retention/tags |
| Export | PNG/MP4/HTML Export | approved assets → ExportManifest | worker | output type |
| Experiments | Variant Factory | Hypothesis → variants | hybrid | single variable |
| Experiments | Outcome Import | CSV / API → dataset | worker | mapping, attribution |
| Experiments | Experiment Analysis | outcomes → ExperimentResult | worker | confidence settings |

**Node sürüm politikası:** `node_type`, `node_version`, `input_schema_version`, `output_schema_version`, `execution_strategy`, `retry_policy`, `cost_policy`, `timeout`, `can_pause` registry'de tanımlanır. `Human Approval` gibi async wait node, bir Temporal wait state'e karşılık gelir.

## H. Typed artifact sözleşmeleri

| Tip | Asgari alanlar | Hangi modül üretir | Kim tüketir |
|---|---|---|---|
| `TrendSnapshot` | `source_id`, `observed_at`, `region`, `records`, `raw_hash` | M01 | M01/M02 |
| `TrendReport` | `signals`, `evidence_refs`, `confidence`, `limitations` | M01 | M02 |
| `GameProfileVersion` | `mechanics`, `style`, `assets`, `constraints`, `version` | M04 | M02/CORE/M07 |
| `CreativeHypothesis` | `audience`, `hook`, `rationale`, `metric`, `test_plan` | M02 | M02/M03 |
| `ConceptSpec` | `hypothesis_id`, `scene`, `interaction`, `style`, `target_formats` | M02 | CORE |
| `ConceptBoard` | `preview_asset_id`, `concept_id`, `score_components` | M02 | User/CORE |
| `ContextBundle` | `ref_ids`, `context_budget`, `used_tokens`, `provenance` | M05 | Agents |
| `AssetPlan` | `shots`, `prompts`, `constraints`, `model_policy` | CORE | Image/Video |
| `ImageAsset` | `object_ref`, `sha256`, `resolution`, `generation_call_id` | CORE | Video/Playable/QA |
| `VideoAsset` | `object_ref`, `sha256`, `codec`, `duration`, `generation_call_id` | CORE | QA/Export |
| `PlayableSpec` | `template`, `rules`, `inputs`, `winning_condition`, `cta` | CORE | Codegen/QA |
| `PlayableBundle` | `zip_object_ref`, `sha256`, `entrypoint`, `build_report_id` | CORE | QA/Export |
| `EvaluationReport` | `rubric_id`, `gate_results`, `scores`, `judge_id`, `evidence` | M07 | Human/Analytics |
| `ExperimentResult` | `variant_ids`, `metric_values`, `method`, `uncertainty` | M03 | Learning/Analytics |
| `RunManifest` | source+model+code+workflow+artifact versions/hashes | M10 | Runs/Repro |

**Serialization:** Pydantic v2 / JSON Schema. Büyük image/video payload JSON içine konmaz, yalnızca object ref + digest. Her artifact `schema_version` ve `content_hash` taşır; UI'de eski kayıtlar için migration readers gerekir.

## I. PostgreSQL veri modeli — detaylı şema

**Çalışma disiplini:** `uuid`/UUIDv7 veya ULID (tek politika), `created_at` UTC, `updated_at` (mutable tablolarda), `project_id` çoğu tabloda partition key/tenant filtre, FKs, gerekli index, JSONB alanlarında version. Bütün eventleri tek JSONB tablosuna atmak yerine arama ve aggregate için normalized tablolar.

### I1. Tablolar / ana alanlar / indeksler

| Tablo | Temel alanlar | Ana ilişki / index |
|---|---|---|
| `organizations` | id, name, settings_json | PK |
| `users` | id, oidc_subject, display_name | oidc_subject unique |
| `memberships` | org_id, user_id, role | (org,user) unique |
| `workspaces` | id, org_id, name | org FK |
| `projects` | id, workspace_id, name, type | workspace FK |
| `campaigns` | id, project_id, game_profile_id, objective | project FK |
| `source_registry` | id, source_type, access_policy, terms_checked_at | source_type index |
| `source_sync_jobs` | id, source_id, status, started_at, errors | source,status,time |
| `raw_snapshots` | id, source_id, observed_at, object_ref, sha256 | source+time, hash unique scoped |
| `trend_observations` | id, snapshot_id, game_ref, genre, metric_type, value, region | observed_at/region/genre |
| `trend_reports` | id, project_id, snapshot_ids, report_ref, model_call_id | project+time |
| `game_profiles` | id, project_id, active_version_id | project |
| `game_profile_versions` | id, profile_id, version, spec_json, hash, approved_at | (profile,version) unique |
| `asset_rights` | id, asset_id, owner, license_kind, evidence_ref | asset FK |
| `creative_hypotheses` | id, project_id, report_id, spec_json, rank_version | project+report |
| `concept_boards` | id, hypothesis_id, board_artifact_id, score_json | hypothesis FK |
| `concept_decisions` | id, concept_id, user_id, decision, reason, time | concept+time |
| `workflows` | id, project_id, name, active_version_id | project |
| `workflow_versions` | id, workflow_id, version, graph_json, sha256 | workflow+version unique |
| `requests` | id, user_id, campaign_id, original_text_ref, normalized_brief_json | campaign+time |
| `runs` | id, request_id, workflow_version_id, state, started_at, ended_at, run_manifest_id | project+state+time |
| `run_manifests` | id, run_id, json_ref, sha256, code_commit | run unique |
| `run_events` | event_id, run_id, run_seq, event_type, occurred_at, payload_ref, trace_id, causation_id | `(run_id, run_seq)` unique; time+type |
| `outbox_events` | id, event_id, payload, dispatched_at, attempts | undispatched partial index |
| `node_executions` | id, run_id, node_id, node_version, state, timings | run+node |
| `attempts` | id, node_execution_id, attempt_no, state, error_code, backoff_ms, start/end | (node_exec,attempt_no) unique |
| `agent_sessions` | id, run_id, agent_type, node_execution_id, context_bundle_id | run+agent |
| `model_invocations` | id, attempt_id, provider, model_requested, model_resolved, provider_request_id, state, timing | attempt; provider_request_id unique nullable |
| `usage_records` | id, invocation_id, input_tokens, output_tokens, cached_tokens, source, modality_json | invocation+revision |
| `price_catalog_versions` | id, provider, model, effective_from/to, unit_prices_json | provider+model+effective |
| `cost_entries` | id, invocation_id, usage_record_id, price_version_id, amount, currency, cost_kind, status | invocation+cost_kind+status |
| `tool_calls` | id, attempt_id, tool_name, args_ref, result_ref, status, duration | attempt+tool |
| `artifacts` | id, run_id, type, storage_ref, sha256, bytes, media_meta, state | run+type; hash |
| `artifact_lineage` | parent_artifact_id, child_artifact_id, relation_type | composite unique |
| `quality_gate_results` | id, artifact_id, rubric_version_id, gate_type, state, score | artifact+gate |
| `evaluations` | id, run_id, target_artifact_id, rubric_version, report_ref, judge_invocation_id | target+rubric |
| `human_reviews` | id, artifact_id, reviewer_id, decision, reason, reviewed_at | artifact+time |
| `experiments` | id, campaign_id, hypothesis_id, mode, outcome_source | campaign+mode |
| `experiment_variants` | id, experiment_id, artifact_id, variant_controls_json | experiment |
| `experiment_outcomes` | id, variant_id, observations_json, window, source_ref | variant+window |
| `prompt_templates` | id, name, task_kind | unique name+scope |
| `prompt_versions` | id, template_id, version, object_ref, sha256 | (template,version) unique |
| `model_policies` | id, project_id, version, rules_json | project+version |
| `context_bundles` | id, run_id, refs_json, token_budget, selected_token_count | run FK |
| `audit_events` | id, actor_id, action, entity_type/id, redacted_diff, created_at | actor+time, entity |
| `analytics_rollups_hourly` | project_id, hour, dimensions, aggregate_json, watermark_seq | project+hour+dimensions |

**Ek prensipler:**
- Büyük immutable JSON prompt, raw API responses ve video byte'ları S3 objelerinde; DB'de pointer, sha256, encryption key version ve access label.
- `cost_entries` için estimate/final/reconciliation sürümleri tutulur; düzeltme yeni version/adjustment kaydıdır, eski geçmiş silinmez.
- Append-only `run_events`, `audit_events` UPDATE/DELETE kısıtı uygulama rolünde engellenir; yetkili retention job ayrı işlem yürütür.
- Index ve partition: event/veri hacmi büyüyünce `occurred_at` bazında aylık partition; eski partition retention ile silinir. İlk günden gereksiz dağıtık DB yok.
- Transactional outbox publisher başarısız olursa repeat; client event_id dedupe, run_seq gap recovery.
- Çok kiracılı kullanımda workspace/project scope her sorguda enforce, RLS ek koruma.

### I2. Örnek ilişkisel zincir

```
projects
  └─ campaigns
      └─ requests (original user message)
          └─ runs (frozen workflow + manifest)
              ├─ run_events (append-only seq=1...N)
              ├─ node_executions
              │    ├─ attempts (#1, #2, #3...)
              │    │    ├─ model_invocations → usage_records → cost_entries
              │    │    └─ tool_calls
              │    └─ agent_sessions → context_bundles
              ├─ artifacts → artifact_lineage
              ├─ evaluations / quality_gate_results / human_reviews
              └─ experiment_variants / experiment_outcomes
```

### I3. Tek bir run'da audit örneği

1. 14:00:00 kullanıcı `req_7` ile “match-3 rescue concept” brief gönderdi; `REQUEST_RECEIVED`.
2. 14:00:01 sistem `run_88` başladı; `workflow_version_4` ve `game_profile_version_2` freeze edildi.
3. 14:00:03 `concept-agent` başladı; invocation A = 1.200 input, 250 output token (örnek).
4. 14:00:06 `mockup-generator` 2 image asset üretti; `artifact_a`, `artifact_b`, görsel birim maliyeti ayrı.
5. 14:00:15 video node ilk attempt timeout; attempt#1 ve provider request ID kaydedildi; eğer ücretlendirildiyse maliyeti eklenir.
6. 14:00:18 ikinci attempt başladı; fallback model versiyonu ve yeni token/medya usage kaydı.
7. 14:00:28 video artifact oluştu, SHA256 hesaplandı; parent image ID'lerine lineage.
8. 14:00:34 teknik QA passed, originality warning; insan onayı bekliyor.
9. 14:01:12 kullanıcı gerekçeli onay verdi; export başladı.
10. 14:01:13 final run manifest, tüm cost/usage/trace ref ve QA raporuyla tamamlandı.

Bu örnek sayılar gerçek CreativeForge ölçümleri değildir; test fixture olarak kullanılır. Dashboard'da hata veren attempt de dahil bütün fiziksel çağrılar sayılır.

## J. API sözleşmesi ve gerçek zamanlı iletişim

**Auth:** JWT/OIDC, project-level RBAC, API yazma eylemlerinde actor kimliği; mutasyonlara `Idempotency-Key`. Sayfa sorgularında cursor pagination, `from/to`, `status`, `model`, `agent` filtreleri.

| Grup | Endpoint | Fonksiyon |
|---|---|---|
| Projects | `POST /api/v1/projects`, `GET /api/v1/projects/:id` | proje CRUD |
| Sources | `GET /api/v1/trends/sources`, `POST /api/v1/trends/sync` | kaynak seçme ve toplama |
| Trends | `GET /api/v1/projects/:p/trends`, `GET /api/v1/trends/snapshots/:id` | kaynaklı trend sorgulama |
| Game DNA | `POST /api/v1/games/:g/versions`, `GET /api/v1/games/:g/versions/:v` | frozen game profile |
| Concepts | `POST /api/v1/projects/:p/concepts/generate`, `GET /api/v1/projects/:p/concepts` | hipotez/mockup oluşturma |
| Decisions | `POST /api/v1/concepts/:id/decision` | seçim veya ret |
| Workflows | `POST /api/v1/workflows`, `PUT /api/v1/workflows/:w/draft`, `POST /api/v1/workflows/:w/publish` | düzenle/doğrula/yayınla |
| Runs | `POST /api/v1/workflows/:w/runs`, `GET /api/v1/runs/:r` | workflow başlat/incele |
| Controls | `POST /api/v1/runs/:r/pause`, `/resume`, `/cancel`, `/rerun` | idempotent kontrol |
| Events | `GET /api/v1/runs/:r/events?since_seq=N` | tarihsel events |
| Live SSE | `GET /api/v1/runs/:r/events/stream` | canlı Observatory & Workflow updates |
| Calls | `GET /api/v1/runs/:r/model-calls`, `GET /api/v1/model-calls/:id` | prompt/usage/cost metadata |
| Retries | `GET /api/v1/runs/:r/attempts` | attempt listesi |
| Artifacts | `GET /api/v1/runs/:r/artifacts`, `GET /api/v1/artifacts/:a/lineage` | output ve kaynak ilişkisi |
| Previews | `POST /api/v1/artifacts/:a/preview-ticket`, `GET /api/v1/artifacts/:a` | kontrollü görüntüleme |
| QA | `POST /api/v1/artifacts/:a/review`, `GET /api/v1/quality/gates` | onay/ret ve rubric |
| Experiments | `POST /api/v1/experiments`, `POST /api/v1/experiments/:e/outcomes/import` | deney ve sonuç |
| Analytics | `GET /api/v1/analytics/overview`, `/costs`, `/agents`, `/artifacts`, `/quality`, `/reliability` | KPI |
| Compare | `GET /api/v1/runs/compare?left=...&right=...` | run diff |
| Manifest | `GET /api/v1/runs/:r/manifest`, `GET /api/v1/runs/:r/export` | reproducibility bundle |
| Admin | `GET/PUT /api/v1/model-policies`, `GET/PUT /api/v1/retention`, `GET /api/v1/audit` | model/security ayarları |

**SSE örnek event:**
```json
{
  "id":"run_88:42",
  "event":"MODEL_CALL_FINISHED",
  "data":{
    "event_id":"evt_42",
    "run_id":"run_88",
    "run_seq":42,
    "node_execution_id":"ne_video_2",
    "attempt_id":"att_video_2",
    "status":"completed",
    "usage_status":"provider_reported",
    "latency_ms":2780
  }
}
```
**Kontrat notu:** Yukarıdaki gösterim SSE payload'unun JSON örneğidir; gerçek SSE wire formatı `id:`, `event:`, `data:` satırlarından oluşur.

## K. Prompt, model, artifact, eval ve event ilişkisi

**Tek model çağrısı kayıt kuralı:** İstek upstream `NodeAttempt`'te başladığında `ModelInvocation` için immutable `provider_request_id` (varsa) ve `idempotency_key` yazılır. Call sırasında istemci ayrılırsa server çağrısını sonlandırma politikası belirlenir; usage gelmediyse `missing` olarak kalır. `token_count=null` ile `token_count=0` semantik olarak farklıdır.

**Örnek dashboard drilldown yolu:** `Analytics → Agent Cost → A13 Playable Code Agent → run_88 → attempt_2 → model_invocation_5 → usage_record_5 → cost_entry_6 → source_bundle_20 → build_report_4 → final_html_bundle_9`.

**Lineage:** Bir asset'in parent'ları (concept/asset plan/image/model invocation) ayrı `artifact_lineage` bağlantıları; her artifact için `input_hashes`, `generator_version`, `license/provenance` ve `eval_result` ilişki referansları.

**Evaluation kayıt kuralı:** rubric version, judge model version, automatic vs human, reference baselines, score, disagreement, timestamps; aynı artifact farklı rubric ile birden fazla değerlendirme alabilir.

## L. Kullanılacak GitHub repoları — seçim matrisi, entegrasyon ve lisans notları

**Önemli:** Buradaki bağlantılar, CreativeForge'a 'tamamını kopyalayacağımız' projeler değil, sistemin alt teknolojileri veya referans uygulamalarıdır. Birbirinin kopyası birçok orchestration/observability framework'ünü aynı anda kurmuyoruz. Sürüm pinlemeden önce ilgili repoların LICENSE, breaking changes ve dağıtım koşulları kontrol edilmelidir.

| Öncelik | Resmî GitHub repo | Kullanım yeri | Entegrasyon şekli | Not |
|---|---|---|---|---|
| Zorunlu | [xyflow/xyflow](https://github.com/xyflow/xyflow) | Workflow Studio | React Flow npm kütüphanesi | ComfyUI görünümünü kendi UX'imizle kurarız |
| Zorunlu | [fastapi/fastapi](https://github.com/fastapi/fastapi) | API | Python package | REST, OpenAPI, SSE endpoint |
| Zorunlu | [temporalio/sdk-python](https://github.com/temporalio/sdk-python) | Kalıcı orkestrasyon | Python SDK | Workflow/activity retry ve durable state |
| Zorunlu | [temporalio/temporal](https://github.com/temporalio/temporal) | Worker orchestration server | ayrı servis | platform altyapısı; kendi ledger değil |
| Zorunlu | [BerriAI/litellm](https://github.com/BerriAI/litellm) | Model gateway | proxy/SDK | model routing, sağlayıcı adaptörleri; fiyat doğrulaması gerekir |
| Zorunlu | [Comfy-Org/ComfyUI](https://github.com/Comfy-Org/ComfyUI) | Image generation | HTTP / WebSocket worker backend | tüm arayüzünü ürün içine taşımıyoruz |
| Zorunlu | [remotion-dev/remotion](https://github.com/remotion-dev/remotion) | Video composition | JS/TS render worker | **Özel lisans koşulları** kontrol edilmeli |
| Zorunlu | [phaserjs/phaser](https://github.com/phaserjs/phaser) | Playable | JS/TS package | 2D web oyun prototipi |
| Zorunlu | [microsoft/playwright](https://github.com/microsoft/playwright) | E2E & browser QA | browser testing | mobil viewport + input smoke test |
| Zorunlu | [Arize-ai/phoenix](https://github.com/Arize-ai/phoenix) | AI observability | OTLP trace ingestion + UI | teknik tracing/evals, iş ledger'ının alternatifi değil |
| Zorunlu | [Arize-ai/openinference](https://github.com/Arize-ai/openinference) | Agent model/tool spans | Python instrumentation | OTel ile birlikte |
| Zorunlu | [open-telemetry/opentelemetry-collector](https://github.com/open-telemetry/opentelemetry-collector) | Telemetry pipeline | OTLP collector | trace/metric filter/redaction |
| Zorunlu | [pgvector/pgvector](https://github.com/pgvector/pgvector) | Project/evidence memory | PostgreSQL extension | semantic retrieval + SQL joins |
| Zorunlu | [colinhacks/zod](https://github.com/colinhacks/zod) | Frontend contract validation | TypeScript package | backend JSON Schema ile uyum |
| Opsiyonel | [langfuse/langfuse](https://github.com/langfuse/langfuse) | Phoenix alternatifi | ayrı tracing/eval ürünü | aynı anda iki platform kurmayalım |
| Opsiyonel | [grafana/grafana](https://github.com/grafana/grafana) | Infra dashboard | datasource + alerts | ürün dashboard'ını bununla değiştirmeyiz |

**Neden seçtik?** React Flow node/edge, custom handles ve minimap sağlıyor; Temporal uzun süren ve geri kazanılabilir yürütmeye uygun; ComfyUI HTTP/WebSocket ile prompt kuyruklarına eriştiriyor; Remotion programatik video montajı yapıyor; Phaser HTML5 2D oyun ve Playwright tarayıcı testleri sağlıyor; Phoenix/OpenInference trace ile eval deneylerini destekliyor. Bunların tümü kendi resmî açıklamalarıyla doğrulanabilir.

**GitHub kullanma stratejisi:**
- CreativeForge ana kodunu **tek bir yeni monorepo** olarak geliştir; üstteki upstream repolar submodule olarak klonlanmak zorunda değil.
- Frontend paketlerini npm, Python paketlerini uv/pip, özel işçileri image olarak yönet; ComfyUI ve Temporal bağımsız servis.
- Phoenix veya Langfuse'dan tekini ana AI tracing backend olarak seç; varsayılan Phoenix.
- Bir repo kurulumdan önce lisans, kullanım amacı ve ticari kullanımı kontrol et. Özellikle Remotion'un sıradan MIT lisansı olmadığını unutma; ayrıca kullanılan ComfyUI custom node/model ağırlıklarının lisansları ayrı olabilir.
- Trend/reklam verisi toplamak için rastgele scraper repo'su entegre etme; kaynak şartları/API izinleri ve veri provenance sistemi önceliklidir.

### L1. Kaynak ve entegrasyon referansları

- React Flow: https://reactflow.dev/ ; https://github.com/xyflow/xyflow
- ComfyUI server routes: https://github.com/Comfy-Org/docs/blob/main/development/comfyui-server/comms_routes.mdx
- Remotion: https://github.com/remotion-dev/remotion
- Phaser: https://github.com/phaserjs/phaser
- OpenTelemetry GenAI semantic conventions: https://github.com/open-telemetry/semantic-conventions-genai
- Phoenix: https://github.com/Arize-ai/phoenix
- Apple iPhone Games Charts: https://apps.apple.com/tr/iphone/charts/6014
- TikTok Creative Center description: https://ads.tiktok.com/resources/help/article/creative-center

## M. Önerilen CreativeForge kendi GitHub monorepo yapısı

```text
creativeforge-intelligence-studio/
├─ README.md
├─ LICENSE                    # Kendi kodunun lisansı; bağımlılık lisanslarından ayrı
├─ SECURITY.md
├─ CONTRIBUTING.md
├─ .github/
│  ├─ workflows/
│  │  ├─ ci-frontend.yml
│  │  ├─ ci-backend.yml
│  │  ├─ integration-tests.yml
│  │  ├─ dependency-scan.yml
│  │  └─ docker-build.yml
│  └─ ISSUE_TEMPLATE/
├─ apps/
│  └─ web/                     # Next.js UI
│     ├─ app/(workspace)/
│     │  ├─ overview/
│     │  ├─ intelligence/
│     │  ├─ concepts/
│     │  ├─ game-dna/
│     │  ├─ studio/
│     │  ├─ artifacts/
│     │  ├─ experiments/
│     │  ├─ ledger/
│     │  ├─ analytics/
│     │  ├─ quality/
│     │  └─ runs/[runId]/
│     ├─ components/
│     │  ├─ workflow/{canvas,nodes,edges,inspector,templates}/
│     │  ├─ observatory/{core,agent-card,connections,timeline}/
│     │  ├─ concepts/{board-card,comparison,ranking}/
│     │  ├─ analytics/{filters,kpis,charts,cost-waterfall}/
│     │  ├─ ledger/{event-table,event-detail,trace-link}/
│     │  └─ artifacts/{gallery,preview,lineage}/
│     ├─ lib/{api,schemas,events,formatting}/
│     └─ state/
├─ services/
│  ├─ api/                      # FastAPI modular monolith
│  │  ├─ app/modules/
│  │  │  ├─ projects/
│  │  │  ├─ intelligence/
│  │  │  ├─ concepts/
│  │  │  ├─ game_dna/
│  │  │  ├─ workflows/
│  │  │  ├─ agents/
│  │  │  ├─ evaluations/
│  │  │  ├─ experiments/
│  │  │  ├─ ledger/
│  │  │  ├─ analytics/
│  │  │  ├─ budgets/
│  │  │  └─ security/
│  │  ├─ app/db/{models,migrations,repositories}/
│  │  ├─ app/api/v1/
│  │  └─ app/core/{auth,settings,contracts,telemetry}/
│  ├─ worker-orchestrator/       # Temporal workflows + activities
│  ├─ worker-trends/             # connectors, snapshots, analysis
│  ├─ worker-ai/                 # agent runtime, typed handoff, gateway
│  ├─ worker-image/              # ComfyUI/provider adapter
│  ├─ worker-video/              # video provider + Remotion render
│  ├─ worker-playable/           # Phaser build, Playwright, sandbox
│  ├─ worker-evaluation/         # validators, rubric, similarity
│  └─ worker-event-relay/        # outbox -> SSE/event bus
├─ packages/
│  ├─ contracts/                 # Pydantic + generated JSON Schema + TS types
│  ├─ node-registry/             # node definitions / capabilities
│  ├─ prompts/                   # versioned prompt templates
│  ├─ rubrics/                   # versioned eval rubrics
│  ├─ media-presets/             # safe original mini-game templates
│  └─ test-fixtures/             # synthetic events, golden datasets
├─ infrastructure/
│  ├─ docker-compose.yml
│  ├─ otel-collector.yaml
│  ├─ temporal/
│  ├─ postgres/
│  ├─ storage/
│  ├─ phoenix/
│  └─ deployment/
├─ tests/
│  ├─ unit/
│  ├─ contract/
│  ├─ integration/
│  ├─ e2e/
│  ├─ load/
│  ├─ security/
│  └─ golden-datasets/
├─ examples/
│  ├─ match3-original-demo/
│  ├─ trend-to-concept.json
│  ├─ concept-to-playable.json
│  └─ observatory-demo-events.jsonl
└─ docs/
   ├─ product-spec.md
   ├─ page-map.md
   ├─ adr/
   ├─ event-taxonomy.md
   ├─ database-schema.md
   ├─ api-spec.md
   ├─ node-catalog.md
   ├─ metrics-dictionary.md
   ├─ threat-model.md
   ├─ evaluation-plan.md
   └─ roadmap.md
```

**Servis ayırma kuralı:** Önce tek API ve 2–3 worker deployment yeterlidir. Yukarıdaki klasörlerin var olması hepsinin ayrı sunucuya ihtiyaç duyduğu anlamına gelmez. Image/video ağır işleri bağımsız sıraya koy; maliyetleri izlemeyi geliştirme boyunca aktif tut.

## N. Sürümleme, kontrol, kalite, güvenlik ve veri yönetimi

### N1. Yetkilendirme rolleri

| Rol | Okuma | Üretim | Onay | Model/bütçe ayarı | Audit export |
|---|---|---|---|---|---|
| Owner/Admin | tüm workspace | evet | evet | evet | evet |
| Engineer | atanan proje | evet | opsiyonel policy | öneri | kısıtlı |
| Creative Reviewer | konsept ve artifact | sınırlı | evet | hayır | hayır |
| Analyst | trends/experiments/analytics | deney/rapor | hayır | hayır | özet export |
| Viewer | izinli özet | hayır | hayır | hayır | hayır |

Tüm dashboard API'lerinde sunucu taraflı proje/rol kontrolü vardır; frontend button disable yeterli değildir. Yetkisiz trace payload/asset indirmesi engellenir.

### N2. Threat model

| Risk | Saldırı / hata | Önlem / kabul testi |
|---|---|---|
| Prompt injection | taranan reklam açıklaması ajanı yeniden yönlendiriyor | untrusted source boundary, schema, tool allowlist |
| Leakage | model prompt veya log içine key/özel bilgi düşüyor | server-side secrets, redaction, encrypted payload, allowlist |
| SSRF | source URL ile internal servis taranıyor | URL normalization, egress proxy, DNS/IP blocklist/allowlist |
| Generated code | agent zararlı JS/Node kodu üretiyor | microVM/hardened sandbox, no secret mounts, no network by default |
| Budget runaway | hatalı retry döngüsü ücret yakıyor | global/project/run budget, bounded retries, breaker |
| Duplicate billing | outbox veya activity replay aynı maliyeti iki kez yazıyor | idempotent invocation ID and unique constraints |
| Data contamination | import içinde sahte 'başarılı trend' | provenance + quality + human spot-check |
| IP/brand infringement | özgün olmayan ikon/karakterler | provenance, similarity warnings, human approval |
| Private content exposure | dashboard yetki aşımı | RBAC/RLS, signed URL, access audit |
| Misleading dashboard | estimated token/cost actual gibi görünür | `usage_source`, `cost_status`, null/unknown handling |

### N3. Saklama / uyumluluk

- En az `metadata only`, `redacted content`, `full content opt-in` kayıt modları; güvenlik sınırı organisation/project seviyesinde.
- Retention süreleri konfigüre edilebilir; zamanında purge ve silme talebi iş akışı log'lanır.
- `audit_events` saklamak, kullanıcı silme taleplerine karşı mutlak dokunulmazlık iddiası değildir; gerekli mevzuat ve veri minimizasyonu politikası birlikte tasarlanır.
- Medya üretim modelleri için izinli ticari kullanım, eğitim verisi/asset hakları ve çıktı lisans koşulları gözden geçirilir.

## O. Test stratejisi, benchmark ve başarı kriterleri

**Demo fixture ile gerçek benchmark ayrımı:** `demo/fixtures` verisi test UI'yi göstermek için; benchmark raporu ise kodun koştuğu ve ölçüm topladığı ayrı dataset/run manifest'ten üretilir.

| Test katmanı | Test senaryosu | Kabul ölçütü (ilk hedef) |
|---|---|---|
| Unit | token/cache ve fiyat toplama | provider reported + cached sayılarda double count yok |
| Unit | score normalization, missingness | missing evidence `0 success` olmaz |
| Contract | yanlış tip edge | publish reddedilir ve açıklayıcı hata |
| Integration | workflow -> ledger -> outbox | event idempotent, run_seq monoton |
| Integration | provider timeout -> retry | iki attempt, tüm ücretli çağrılar cost'ta |
| Integration | budget exceeded | pahalı çağrı başlamadan deny + alert |
| E2E | trend -> concept -> selection | kaynaklı mockup ve karar izi |
| E2E | concept -> image / video | en az bir gerçek provider artifact |
| E2E | concept -> HTML5 playable | sandbox build + mobil input smoke test |
| E2E | failure -> targeted retry | önceki başarılı asset yeniden hesaplanmaz |
| E2E | pause / resume | durable state korunur |
| E2E | reconnect | Last-Event-ID sonrası atlanmamış event timeline |
| Observability | inspector drilldown | `request→run→node→attempt→call→artifact` kesintisiz |
| Evaluation | QA score human agreement | ölçülen agreement raporunda örneklem sayısı var |
| Security | generated-code network request | sandbox varsayılan deny |
| Security | private object link | yetkisiz erişim reddedilir |
| Recovery | worker kill/restart | iş ya toparlar ya belirgin terminal failure üretir |
| Performance | 10 eşzamanlı demo run | queue wait/latency ölçülür, sistem kilitlenmez |

**İlk portföy benchmark dataset'i:** örneğin 20 farklı özgün puzzle game brief; en az 3 trend sinyal kaynağı türü (izinli/manuel), 3 konsept/brief, 10 playable generation target, 3 QA rubric kategorisi, 2 model stratejisi. Rakamlar hedef test sayılarıdır; henüz elde edilmiş sonuçlar değildir.

**KPI hedefleri başlangıçta başarı iddiası değil kabul ölçütüdür:** E2E build başarısı >80% gibi eşikler veri olmadan garanti edilmez; ilk birkaç koşuyla baseline çıkar, sonraki sprintte ölçülen hedef seti oluştur. Gerçek reklam performansı ancak yetkili deney/outcome verisiyle değerlendirilir.

## P. Uçtan uca geliştirme roadmap — her faz için görevler, bağımlılıklar ve teslim kriterleri

**Öncelikler:** P0 = ilk ciddi portföy sürümü için olmazsa olmaz; P1 = daha ileri platform yeteneği; P2 = opsiyonel ölçekleme. Fazlar ardışık iskelet üzerinde ilerler; ledger, güvenlik ve fiyatlama sona bırakılmaz.

### Faz 0 — Foundation / Engineering Standards (P0)
**Bağımlılıklar:** yok.  
**Deliverable:** `docker compose up` ile app+API+Postgres+Temporal+OTel/Phoenix temel ortamı.

- [ ] Monorepo, CI lint/test/typecheck, environment secrets example.
- [ ] API/Pydantic contracts, DB migrations, UUID/UTC/naming ADR.
- [ ] Local auth single user, ileride RBAC hook.
- [ ] Standard `EventEnvelope`, ledger writer, outbox publisher.
- [ ] `run_id`, `trace_id` correlation; Phoenix OTel smoke trace.
- [ ] Node registry, typed edge validator, model provider mock adapter (açıkça mock).
- [ ] UI layout: sidebar, Studio 2-tab shell, empty dashboards.
- [ ] Demo fixture'ı gerçek veri gibi görünmeyecek şekilde işaretle.

**Gate:** Test isteği `REQUEST_RECEIVED` yazıp SSE'den ekrana gelir; trace ve ledger ID'leri eşleşir.

### Faz 1 — Workflow Studio + Durable Orchestration (P0)
**Bağımlılıklar:** Faz 0.  
**Deliverable:** basit `brief -> structured concept -> approval` workflow gerçek yürütme.

- [ ] React Flow drag/connect/save/publish, graph validator, inspector.
- [ ] Temporal workflow/activity integration; queued/running/waiting/completed state.
- [ ] Pause/resume/cancel, max attempts, exponential backoff.
- [ ] Node attempt, tool call, model invocation, usage and cost DB writes.
- [ ] Workflow version immutability + manifest freeze.
- [ ] Run Detail ilk sürümü; request→node→attempt timeline.
- [ ] SSE reconnect test ve outbox dedupe.

**Gate:** Simüle edilmiş tool failure otomatik retry edilir; her attempt, zaman ve maliyet kaydı anlaşılır biçimde incelenir.

### Faz 2 — Game DNA + Concept Studio (P0)
**Bağımlılıklar:** Faz 1.  
**Deliverable:** brief'ten üç onaylanabilir, yapılandırılmış mockup board.

- [ ] Game DNA upload, game mechanic editor, version & asset rights.
- [ ] Creative hypothesis structured output, constraint checks.
- [ ] Deterministik concept ranking + score explanation.
- [ ] Mockup board gallery, comparison, user selection/override.
- [ ] Seçilen konseptten workflow draft üretimi.
- [ ] Testleri: game mechanics doğruluğu ve selection audit.

**Gate:** Kullanıcı bir konsepti seçince seçimin gerekçesi ve Game DNA sürümü trace edilebilir.

### Faz 3 — Real Asset Generation / Playable (P0)
**Bağımlılıklar:** Faz 2.  
**Deliverable:** en az bir gerçek image API ve bir temel playable workflow.

- [ ] ComfyUI API adapter / gerçek image provider integration.
- [ ] Artifact object storage + sha256 + source lineage.
- [ ] Phaser match-3 starter template, generator, isolated compile.
- [ ] Playwright phone viewport, drag/tap, runtime-error test.
- [ ] Preview & HTML/ZIP download, upload/asset size validation.
- [ ] Remotion composition ile basit MP4 reklam; generative video API P1 genişlemesi.
- [ ] Media credits/seconds ve LLM tokenlarının ayrı cost accounting'i.

**Gate:** `Selected Concept → Generated Assets → QA → User Approved → Download` uçtan uca işler.

### Faz 4 — Trend Intelligence (P0)
**Bağımlılıklar:** Faz 2, veri erişimi izinleri.  
**Deliverable:** tarihli ve kanıtlı trendlerden fikir üretilmesi.

- [ ] Source registry & license policy; manual import fallback.
- [ ] Snapshot ingestion, dedup, normalized observation schema.
- [ ] Genre/classifier, creative pattern extraction, evidence links.
- [ ] Ranking evidence fusion ve uncertainty breakdown.
- [ ] Trend UI source freshness/coverage/errors.
- [ ] Kaynak kesilme, sahte metrik, prompt injection testleri.

**Gate:** Trend raporundaki her sinyal en az bir timestamp'li kaynağa bağlanır; sahte performans metriği üretilmez.

### Faz 5 — Full Observatory + Execution Ledger (P0)
**Bağımlılıklar:** Faz 1–4.  
**Deliverable:** referans görsele yakın ancak tamamen event-driven ajan ekranı ve ledger explorer.

- [ ] Agent topology renderer, state-to-animation mapping, reduced motion.
- [ ] Live timeline, filters, inspector, tool/model/artifact previews.
- [ ] Replay, Run Compare, Pause/Resume/Cancel controls.
- [ ] Requests/Runs/Events/Models/Tools/Retries/Audits ledger sayfaları.
- [ ] Model pricing snapshot / retry waterfall / all artifact provenance.
- [ ] JSONL/CSV export + RBAC log; redaction and retention.
- [ ] Event replay ve 2 browser connection reconciliation test.

**Gate:** Bütün ajan çalışmaları canlıda ve geçmişte aynı event verisine dayanır; user tek `run_id` ile tam izi indirebilir.

### Faz 6 — Multi-Gate Quality + Analytics (P0)
**Bağımlılıklar:** Faz 3, 5.  
**Deliverable:** kalite kapısı, dashboard ve maliyet optimizasyonu.

- [ ] Technical, game truth, visual, originality, human gates.
- [ ] Rubric/golden dataset ve model-judge-human agreement raporu.
- [ ] Cost/usage/agent/workflow/artifact/QA dashboards; drilldown.
- [ ] Price snapshots, per-run budgets, warning/block alerts.
- [ ] p50/p95, retry, failure, cache and unknown-cost semantics.
- [ ] Failure injection & reconciliation tests.

**Gate:** Üç retry içeren işte final artifact sayısı ve toplam maliyet ledger kayıtlarıyla birebir doğrulanır; erişilmemesi gereken payload ekranlarda gösterilmez.

### Faz 7 — Experiments & Feedback (P1)
**Bağımlılıklar:** Faz 2, 3, 6.  
**Deliverable:** ölçülebilir test planları ve sonraki yaratıcı önerilere öğrenme sinyali.

- [ ] A/B planı, kontrol varyantı, tek-değişken üretimi.
- [ ] Offline/real_campaign ayrımı, CSV validation ve attribution metadata.
- [ ] CTR/IPM/CPI hesapları yalnızca gerçek ve tam girdilerle.
- [ ] Trend/experiment feedback store ve evidence scoring update.
- [ ] Experiment comparison report + careful statistical interpretation.

**Gate:** Gerçek veri olmadan performans artırdık iddiası gösterilmez; variant lineage ve test koşulları raporda bulunur.

### Faz 8 — Portfolio & Production Hardening (P1)
**Bağımlılıklar:** bütün P0 gates.  
**Deliverable:** kamuya açık, teknik mülakatta savunulabilir demo ve kurulum rehberi.

- [ ] Sample data, özgün asset'ler, kayıtlı gerçek benchmark ve açık metodoloji.
- [ ] README demo GIF/video, mimari diagram, screenshot, sistem tasarım kararları.
- [ ] GitHub Actions test ve reproducibility manifest export.
- [ ] Rate limiting, backup/restore, secrets rotation, dependency security scan.
- [ ] Deployment/operations runbook ve maliyet politikası.
- [ ] Demo'da fail case gösterme: başarılı üretim kadar controlled recovery.

**Gate:** Yeni makinede açık yönergelerle demo ayağa kalkar; en az bir gerçek image ve playable üretimi tekrar edilebilir test sürecinden geçer.

### P1/P2 ileriye dönük, bu sürüm için zorunlu değil
- Multi-tenant billing, provider invoice ingestion otomasyonu, gelişmiş role policies.
- Yüksek trafik için ClickHouse/columnar warehouse veya time-series analitik ayrımı.
- Birden fazla playable mechanic family, code reuse ve cross-platform paketleme.
- İnsan review queue otomasyonu, collaborative board editing, benchmark suites.
- İleri düzey reklam ağı compiler (#8), ancak kullanıcı kapsamı ayrıca genişletirse.

## Q. Öncelik matrisi / bağımlılıklar

| İş paketi | Öncelik | İhtiyaç duyduğu temel | Gösterilebilir çıktı |
|---|---|---|---|
| Event Ledger & Basic Analytics | P0 | Foundation | request→call→artifact izleme |
| React Flow Editor | P0 | Schema Registry | görsel workflow run |
| Durable Orchestrator | P0 | DB/Event | retry/pause/resume |
| Game DNA | P0 | Artifacts | frozen game profile |
| Creative Boards & Ranking | P0 | Game DNA | seçilebilir mockup kartları |
| Real Image & Playable | P0 | concepts+workers | export edilen çalışan ürün |
| Trend Evidence | P0 | source permission | kaynaklı insight |
| Agent Observatory | P0 | ledger SSE | gerçek agent animasyonu |
| QA & Cost | P0 | run/asset/usage | güvenilir dashboard |
| Experiment Loop | P1 | variants + analytics | feedback-driven suggestion |
| Deployment/Hardening | P1 | feature-complete | güvenilir demo |

**Kritik yol:** Foundation → Typed Workflow & Ledger → Game DNA + Concept → Real Generation → Evaluation & Dashboard → Trend & Experiments. Trend keşif ekranı paralel ilerleyebilir; fakat ilk portföy değerini kanıtlayan şey gerçekten çalışan `Concept → Playable` akışıdır.

## R. Kabul senaryoları / demo hikâyesi

### Demo 1: Discovery
Kullanıcı region Türkiye, platform iOS, kategori puzzle seçer. Trend ekranı tarihli resmi chart gözlemleri ve izinli/manual creative örnekleri listeler; rapor sınırlamalarını gösterir. Sistem 4 özgün konsepte ait mockup board üretir. Kullanıcı `Last Move Rescue` benzeri özgün bir konsepti seçer.

### Demo 2: Production
Workflow Studio otomatik graph açar; Game DNA + selected board -> asset plan -> image generation -> playable code -> sandbox build -> browser QA -> human approval -> export. Her node üzerinde gerçek status ve artifact preview vardır.

### Demo 3: Observatory
İkinci sekmede `Creative Core` çevresinde aktif agentlar ve tool worker'ları ışıklı bağlantılarla görünür. Playable Build adımı hata verir; ekran attempt #1 hata, attempt #2 retry ve maliyetlerini ayrıştırır. İnsan QA seçimine geçer.

### Demo 4: Ledger & Analytics
Kullanıcı `run_id` ile istek metnini (izinli veya redacted), prompt/template sürümünü, input/output tokenını, medya maliyetini, 2 image + 1 playable artifact'i, tekrar denemeleri, reviewer notunu ve run manifest'i görür. `Run Compare` iki modeli/graf sürümünü karşılaştırır.

### Demo 5: Experiments
Aynı konseptin yalnızca CTA değişen iki varyantı offline QA ile karşılaştırılır. Gerçek kampanya datası yoksa sistem CTR tahmini veya 'kazanan' performans açıklaması üretmez; yalnızca offline sonuç sunar.

## S. Mimari karar kayıtları (ADR)

| ADR | Karar | Reddedilen/ertelenen alternatif | Gerekçe |
|---|---|---|---|
| 001 | UI React Flow ile özel | full ComfyUI fork | ürün creative decision + agent UI öncelikli |
| 002 | Temporal workflow + PostgreSQL Ledger | yalnız cron/queue, yalnız Temporal history | pause/resume + kalıcı iş kaydı |
| 003 | Phoenix + OTel | Phoenix+Langfuse+başka gözlemleme aynı anda | düşük operasyonel karmaşa |
| 004 | Provider adapter & LiteLLM | model sağlayıcısına bağımlı çağrılar | routing ve cost policy |
| 005 | Pydantic typed contracts | serbest Markdown agent handoff | deterministik validation |
| 006 | Immutable artifacts + lineage | aynı dosyayı üzerine yazma | reproducibility/audit |
| 007 | Postgres read models | ilk günden ayrı data warehouse | portföy projesinde sadelik |
| 008 | Human approval | otomatik tüm yayınlama | kalite ve içerik kontrolü |
| 009 | Basic playable export | gelişmiş reklam ağı compiler | seçilen scope'a sadakat |
| 010 | Source permission-first | scraping-first | güvenilirlik, erişim kuralları ve sürdürülebilirlik |

## T. Yürütmeye hazır toplam teslim listesi

- [ ] Çalışır iki sekmeli Studio: Workflow ve Observatory.
- [ ] Kaynak ve güven göstergeli trend tarama.
- [ ] En az 3 seçilebilir oyun/creative mockup board.
- [ ] Game DNA editor, versioning, original assets.
- [ ] Image, video composition ve basic playable flow.
- [ ] Typed contract + agent context bundle.
- [ ] Durable run/retry/pause/resume/cancel.
- [ ] Çok katmanlı QA ve human approval.
- [ ] Model registry, versioned price catalogue, budgets.
- [ ] Complete Execution Ledger and event provenance.
- [ ] Dashboard: token/usage/maliyet/retry/agent/asset/QA/run.
- [ ] Artifact lineage, versions, run manifests, rerun vs replay.
- [ ] Real vs simulation badge, strict input provenance.
- [ ] Test suite, license review, threat model, README/demo.
- [ ] Offline experiment engine + optional authorized real outcome import.

## U. Başarı ölçütleri ve CV değeri

Bu proje tamamlandığında GitHub ve CV'de gerçekte ölçülmüş sayılarla şunlar gösterilebilir: `N` run, `M` generated artifacts, provider reported input/output token toplamları, per-asset maliyet, `P` başarılı playable build, retry recovery oranı, end-to-end workflow latency, creative QA human agreement ve failure analysis. **Bu sayılar ölçülmeden CV'de yüzdelik veya ürün performansı iddiası verilmemelidir.**

Örnek açıklama (tamamlanırsa):
> Built an agentic creative intelligence and production studio with a node-based workflow editor, trend-grounded concept generation, multimodal image/video/playable pipelines, durable execution, event-sourced operational auditing, model-cost accounting, and real-time agent observability.

---

### Doğrulanan referans sayfalar (25 Ekim 2026 araştırması)
- https://reactflow.dev/
- https://github.com/temporalio/sdk-python
- https://github.com/Comfy-Org/docs/blob/main/development/comfyui-server/comms_routes.mdx
- https://github.com/remotion-dev/remotion
- https://github.com/phaserjs/phaser
- https://github.com/microsoft/playwright
- https://github.com/Arize-ai/phoenix
- https://github.com/Arize-ai/openinference
- https://github.com/BerriAI/litellm
- https://github.com/pgvector/pgvector
- https://github.com/open-telemetry/semantic-conventions-genai
- https://apps.apple.com/tr/iphone/charts/6014
- https://ads.tiktok.com/resources/help/article/creative-center

**Rapor durumu:** Bu metin kapsamlı ürün ve uygulama planıdır, çalışan sistemin üretildiğine dair iddia değildir. Her geliştirme maddesi implementasyon görevlerine bölünerek ilerlenebilir.
