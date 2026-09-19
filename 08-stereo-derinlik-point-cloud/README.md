# Modül 8: Stereo Derinlik ve Point Cloud

## Öğrenme Hedefleri
1. İki monoküler kameradan (stereo çift) derinlik ve disparity (ayrıklık) kavramını anlamak.
2. `camera_info` topic'inden intrinsics ($K$ matrisi) okumak.
3. OpenCV StereoSGBM algoritması ile disparity hesaplayıp `PointCloud2` nokta bulutu üretmek.
4. Dokusuz yüzey problemlerini ve parametre ince ayarlarını uygulamak.

## Modül Dosyaları
- [`stereo_disparity.py`](./stereo_disparity.py): Sol ve sağ kamerayı senkronize alıp PointCloud2 yayınlayan ROS 2 node'u.

---

## Konsept: İki Göz, Bir Derinlik
İnsan gözünün derinlik algısı gibi: aynı nesnenin sol ve sağ kameradaki piksel konumu farkına **disparity ($d$)** denir. Kameralar arası mesafe (**baseline $B$**, bu modelde $0.12\text{ m}$) bilindiğinde derinlik ($Z$) doğrudan hesaplanır:

$$Z = \frac{B \cdot f_x}{d}$$

Noktaların 3B uzay koordinatları ($X, Y, Z$):
$$X = \frac{(u - c_x) \cdot Z}{f_x}, \quad Y = \frac{(v - c_y) \cdot Z}{f_y}$$

### `camera_info` Topic'i ve K Matrisi
Bu değerler elle sabit kodlanmaz; kamera sürücüsünün yayınladığı `camera_info` topic'inden otomatik okunur:
- $f_x, f_y$: Odak uzaklığı ($381.46\text{ px}$)
- $c_x, c_y$: Optik merkez ($320.5, 240.5\text{ px}$)
- Çözünürlük: $640 \times 480$

---

## StereoSGBM ile Disparity ve Nokta Bulutu ([`stereo_disparity.py`](./stereo_disparity.py))

`stereo_disparity.py` node'u:
1. `message_filters.ApproximateTimeSynchronizer` ile sol (`/ika_rover/camera_sensor/image_raw`) ve sağ (`/ika_rover/right_camera_sensor/image_raw`) görüntüleri **5 milisaniyelik zaman toleransıyla (`slop=0.005` sn)** filtreleyerek eşleştirir.
   - *Kavramsal Netlik (Eşzamanlı Çekim vs Kabul Sınırı):* 5 ms'lik tolerans (`slop`), kameraların fiziksel olarak **eşzamanlı çekim garantisi değildir**; yalnızca yazılım katmanında iki mesajın zaman damgaları (`header.stamp`) arasındaki **kabul sınırıdır** ($|t_{\text{sol}} - t_{\text{sağ}}| \le 5\text{ ms}$).
   - *Neden 5 ms?* 30 FPS kamera akışında iki ardışık kare arası süre $\approx 33.3\text{ ms}$'dir. $5\text{ ms}$'lik dar tolerans penceresi, farklı çevrimlerde yakalanmış karelerin yanlışlıkla çift oluşturmasını engellerken, simülasyon render zamanındaki mikrosaniyelik gecikmelere tolerans tanır.
   - *Donanım Düzeyi Eşzamanlılık:* Fiziksel kameralarda gerçek eşzamanlı pozlama (simultaneous exposure) yazılımla değil, donanımsal tetikleme hattı (hardware genlock / sync pini) ve global shutter sensörlerle sağlanır. ROS katmanındaki `ApproximateTimeSynchronizer` ise gelen mesaj havuzundan damgaları bu tolerans sınırında kalanları eşleştirir.
2. `cv2.StereoSGBM` ile disparity haritası üretir (`/ika_rover/stereo/disparity`).
3. Her geçerli pikseli $(X, Y, Z, RGB)$ formatında `sensor_msgs/PointCloud2` mesajına dönüştürür (`/ika_rover/stereo/points`).
4. Noktalar **`camera_optical_frame`** eksenine etiketlenir (bkz. Modül 10 optik eksen kuralı).

---

## 🐛 HATA: İlk Disparity Haritası Tamamen Gürültülüydü
- **Sebep:** Gazebo'daki varsayılan nesneler (kutular, zemin) tek renkli/düz yüzeylerdir. StereoSGBM eşleşme kurabilmek için doku ve kenar varyansı arar. Düz yüzeyde kontrast olmadığı için algoritma rastgele piksel eşleşmesi yapar ve devasa bir gürültü oluşur.
- **Çözüm (Kısmi):**
  1. Modül 7'de zemine organik `Gazebo/Grass` çim dokusu verildi.
  2. SGBM parametreleri optimize edildi:
     - `blockSize`: 7 → 11 (daha geniş pencereli desen karşılaştırma)
     - `uniquenessRatio`: 10 → 15 (en iyi eşleşmenin ikinciden belirgin derecede üstün olması şartı)
     - `speckleWindowSize`: 100 → 150 (küçük gürültü adacıklarını temizleme)
  3. Yerel varyans filtresi (`cv2.boxFilter`) ile kontrastı 8 gri seviyenin altındaki dokusuz bölgeler elendi.

---

## Hazır `camera_vision` Paketine Geçiş veya Bağımsız Çalıştırma

Modül 4'te oluşturduğunuz temel `camera_vision` paketi yerine, bu depoda hazır olarak gelen ve stereo disparity, derinlik filtreleme ile tam haritalama launch'ını içeren paketi kullanabilirsiniz:

```bash
# 1. Öğrencinin Modül 4'teki önceki çalışmalarını korumak için mevcut paketi ROS çalışma alanı DIŞINA benzersiz bir yedek dizinine taşıyın:
# (ÖNEMLİ: Paket ROS workspace içinde bırakılırsa colcon aynı isimde çift paket algılayıp çakışma hatası verir)
cd ~/ika_ws/src
mkdir -p ~/ika_backups
if [ -e "camera_vision" ]; then
    mv camera_vision ~/ika_backups/camera_vision_backup_$(date +%Y%m%d_%H%M%S)
fi

# 2. Depodaki tam teşekküllü paketi çalışma alanına bağlayın (Sembolik Link Tavsiye Edilir):
ln -s ~/ika_rover_egitim/camera_vision ~/ika_ws/src/camera_vision
# (Alternatif kopyalama: cp -r ~/ika_rover_egitim/camera_vision ~/ika_ws/src/)

# 3. Paketi derleyin ve ortamı yükleyin:
cd ~/ika_ws
colcon build --symlink-install --packages-select camera_vision
source install/setup.bash
```

---

## Adım Adım Çalıştırma ve RViz Görselleştirme

1. **Simülasyonu Başlatın:**
   (Modül 7'de güncellenen `parkur.world`, 5 kameralı robotu hazır olarak içerir)
   ```bash
   gazebo --verbose 07-cok-kamera-mimarisi-ve-parkur/parkur.world
   ```
2. **Stereo Disparity Node'unu Çalıştırın:**
   *Paket üzerinden çalıştırma (Tavsiye Edilen):*
   ```bash
   ros2 run camera_vision stereo_disparity --ros-args -p use_sim_time:=true
   ```
   *Veya doğrudan Python script'i olarak çalıştırma:*
   ```bash
   python3 08-stereo-derinlik-point-cloud/stereo_disparity.py --ros-args -p use_sim_time:=true
   ```
3. **RViz2 ile İnceleyin:**
   ```bash
   rviz2
   ```
   - **Fixed Frame:** `camera_optical_frame`
   - **Add -> By topic -> `/ika_rover/stereo/points` (PointCloud2)**
   - **Color Transformer:** `RGB8`
   - **Style:** `Flat Squares`, Size: `0.03`

*Sonuç:* Çimlerin yeşili, ahşap rampanın kahverengisi ve tuğlaların kırmızısıyla gerçek renkli 3B nokta bulutu ekranda belirir.

---

## Mimari Not: Bu Node Neden Kod Tabanında Korundu?
Modül 10'da 3D haritalama için Gazebo'nun native `depth_camera` sensörüne geçilmiştir (simülasyon derinlik kamerası gürültüsüz kesin mesafe verir). Ancak `stereo_disparity.py` silinmemiştir; gerçek dünyada pahalı derinlik sensörleri yerine 2 adet ucuz monoküler kamerayla stereo derinlik üretmenin mantığını ve sınırlarını öğretmek için kasıtlı olarak depoda bırakılmıştır.

## Sırada
[Modül 9: 2D SLAM (slam_toolbox)](../09-2d-slam)
