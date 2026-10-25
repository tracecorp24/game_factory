# HTML5 Playable Mini-Game Engine & QA Sandbox

Bu modül (`services/worker-playable/`), CreativeForge v3.0 platformunda reklam ağlarına hazır ve tarayıcıda çalışan interaktif mini oyunlar (Playable Ads) üretir ve otomatik olarak test eder.

## Temel Bileşenler

1. **`PlayableCodeGenerator` (`generator.py`)**:
   - `packages/media-presets/playable-templates/match3/` şablonunu okur.
   - `PlayableSpec` (renkler, hamle sayısı, hedef puan, metinler, CTA bağlantısı) ile oyun kodunu derler.
   - Tekil self-contained `index.html` ve App Store / Google Play uyumlu `manifest.json` içeren ZIP paketi üretir.

2. **`SandboxBuildRunner` (`sandbox.py`)**:
   - İzole, tek kullanımlık (disposable) geçici dizinde güvenli derleme yapar.
   - Harici ağ erişimini kısıtlar, kaynak/bellek sınırlarını ve 5MB dosya boyutu sınırını denetler.
   - Çıktıyı `sha256` doğrulamasıyla storage sistemine kaydeder.

3. **`PlaywrightRunner` (`qa_runner.py`)**:
   - Mobil viewport (iPhone 14 / Pixel 7: 390x844) üzerinde Chromium başlatır.
   - Oyunun yüklenmesini, Canvas elementinin çizilmesini ve JavaScript konsol hatalarını izler.
   - Simüle edilmiş dokunma ve sürükleme (touch/swipe) hareketleri ile oyun mekaniklerini test eder.
   - CTA butonuna tıklar ve kanıt olarak mobil ekran görüntüsü (`screenshot.png`) alır.
