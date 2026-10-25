# CreativeForge Intelligence Studio v3.0 — Frontend Studio (`apps/web`)

Bu uygulama, **CreativeForge Intelligence Studio v3.0** platformunun **Agent 6 (Frontend Studio, Canvas, Observatory & Dashboards)** sorumluluk alanıdır.

Next.js 14+ (App Router), TypeScript, Tailwind CSS, `@xyflow/react` (React Flow), Lucide Icons ve Zustand kullanılarak sıfırdan inşa edilmiş, tam işlevsel, üretim standartlarında bir arayüzdür.

---

## 🚀 Hızlı Başlangıç

```bash
# apps/web dizinine gidin
cd apps/web

# Bağımlılıkları yükleyin (zaten kurulduysa atlayabilirsiniz)
npm install

# Geliştirme sunucusunu başlatın
npm run dev

# Veya production build alıp çalıştırın
npm run build
npm run start
```

Tarayıcınızda `http://localhost:3000` adresini açarak platformu deneyimleyebilirsiniz.

---

## 🧭 Sayfa ve Rota Haritası

| Rota | Modül | Açıklama |
|---|---|---|
| `/` veya `/app` | **Studio Overview** | Proje KPI'ları, aktif run durumu, hızlı başlatma kartları ve son append-only event akışı. |
| `/projects/:p/studio?tab=workflow` | **Workflow Studio (Sekme 1)** | React Flow tabanlı ComfyUI tarzı görsel DAG editörü. 28 node tipi paleti, parametre/model inspector'ı, tip uyumlu portlar, cycle tespiti, dry-run ve alt drawer. |
| `/projects/:p/studio?tab=agents&run=run_88` | **Agent Observatory (Sekme 2)** | Canlı SSE telemetrisi ve zaman yolculuğu (time-travel replay). 5 ajan kümesi (Insight, Strategy, Production, QA, Control), merkez Orchestration Core, dinamik sinyal animasyonu, Siber Neon ve Operasyon modları. |
| `/projects/:p/concepts` | **Concept Gallery** | 3-8 adet gerekçelendirilmiş mockup kartı, reklam hook ilk kareleri, duygusal yay (emotional arc), kanıt kaynakları, 6-faktörlü sezgisel skorlama ve "Select & Build Workflow" aksiyonu. |
| `/projects/:p/game-dna` | **Game DNA & Consistency** | 8x8 match-3 mekanik spec'i, renk paleti tokenları, karakter/sprite kütüphanesi, anti-hallucination ("Do Not Generate") kuralları ve dondurulabilir versiyon geçmişi (`v2.1 - FROZEN`). |
| `/projects/:p/ledger` | **Execution Ledger Explorer** | Append-only olay tablosu, SHA-256 bütünlük kontrolü, şifrelenmiş JSON envelope inceleyicisi, PII redaksiyon göstergeleri, JSONL ve CSV dışa aktarımı. |
| `/projects/:p/analytics` | **Analytics & Cost Dashboard** | PostgreSQL rollup KPI'ları (Success Rate, Retry Rate, Cost/Asset, Token Ingestion, Latency P50/P95). Provider/model maliyet şelalesi, 7 Gate QA geçiş oranları, bilinmeyen maliyetler için açık "unknown" rozeti. |
| `/projects/:p/quality` | **Quality Center** | 7 Kademeli Quality Gates (Schema, Technical, GameTruth, Visual, Similarity, LLMJudge, HumanReview). İnsan onay kuyruğu (gerekçeli Approve/Reject). |
| `/projects/:p/artifacts` | **Artifact Library** | Görsel keyframe'ler, 9:16 dikey MP4 video oynatıcı, interaktif Phaser Match-3 HTML5 playable sandbox demosu ve manifest JSON'ları. |
| `/projects/:p/experiments` | **A/B Testing Matrix** | Tek değişkenli varyant türetimi, sentetik offline QA ile gerçek kampanya ayrımı, sıfıra bölme güvenli CPI, CTR, IPM hesaplamaları. |
| `/settings/models` | **LiteLLM Model Registry** | Sağlayıcılar, modeller, birim fiyatlar, önbellek indirimleri ve dinamik fallback rotaları. |
| `/settings/security` | **Security & Governance** | RBAC, PII redaksiyon seviyeleri ve SHA-256 zincir doğrulaması. |
| `/api/v1/runs/:r/events/stream` | **Mock & Live SSE Stream** | `Last-Event-ID` ve `since_seq` destekli, gerçek zamanlı EventEnvelope yayınlayan standart SSE API uç noktası. |

---

## 🎯 Agent 6 Kabul Kriterleri Doğrulama Durumu

1. **React Flow DAG:** 28 node tipi eklenebilir, sürüklenebilir, tip uyumlu handle'lar ile bağlanabilir, cycle ve geçersiz edge uyarısı verir. ✅
2. **Agent Observatory:** Canlı SSE bağlantısı dinler; gelen eventlere göre ajan durumlarını (`idle → queued → running → completed / failed`) günceller; sadece gerçek olay geldiğinde sinyal parçacığı animasyonu üretir. Replay modu zaman çizgisinde adım adım geriye/ileriye sarar. ✅
3. **Lossless SSE Reconnect:** `since_seq` ve `Last-Event-ID` ile bağlantı koptuğunda kaçırılan olayları sırayla yeniden çeker. ✅
4. **Çift Tema Desteği:** "Siber Neon Modu" (sunum & görsel derinlik) ile "Sade Operasyon Modu" (operasyonel netlik) arasında anında geçiş yapılır; Reduced-Motion erişilebilirlik düğmesi mevcuttur. ✅
5. **Simülasyon / Demo Bildirimi:** Demo akışı çalışırken ekranda kalıcı `[SIMULATION DEMO STREAM: run_88]` rozeti gösterilir; sahte thinking iddiaları yapılmaz. ✅
6. **Bilinmeyen Maliyet Prensibi:** Fiyatı henüz bilinmeyen veya unpriced olan çağrılar asla $0 gösterilmez, açıkça `unknown` olarak etiketlenir. ✅
7. **TypeScript & Build:** `npm run build` hatasız şekilde (exit code 0) tamamlanır; hiçbir tip veya lint hatası yoktur. ✅
