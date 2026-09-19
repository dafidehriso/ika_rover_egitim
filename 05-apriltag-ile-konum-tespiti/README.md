# Modül 5: AprilTag ile Konum Tespiti

## AprilTag Nedir?

Kare şeklinde, özel matematiksel bit desenli bir görsel işaret (QR koda benzer ama daha basit). Kameranın bu işareti görüp, işaretin **fiziksel boyutunu zaten bildiği için**, görüntüde ne kadar büyük/eğik göründüğüne bakarak **kameraya göre tam 3 boyutlu konumunu ve açısını** geometrik olarak hesaplayabilmesini sağlıyor.

Bu, GPS'in çalışmadığı iç mekanlarda ya da hassas konumlandırma (örneğin şarj istasyonuna tam olarak doğru mesafede yanaşma) gerektiren görevlerde kullanılan gerçek bir teknik.

## Adım 1: Paketi Kurun

```bash
sudo apt install ros-humble-apriltag-ros -y
```

## Adım 2: Gerçek Bir AprilTag Görseli Edinin

**Önemli:** Rastgele bir siyah-beyaz kare işe yaramaz — tam olarak matematiksel bir bit deseni gerekiyor.

```bash
mkdir -p ~/.gazebo/models/apriltag_0/materials/textures
wget https://raw.githubusercontent.com/AprilRobotics/apriltag-imgs/master/tag36h11/tag36_11_00000.png -O ~/.gazebo/models/apriltag_0/materials/textures/tag0.png
```

Doğrulayın: `file ~/.gazebo/models/apriltag_0/materials/textures/tag0.png` → `PNG image data, 10 x 10` yazmalı. **10x10 piksel, gerçek bir AprilTag için normaldir** — düşük çözünürlük hatayı değil, tag'in doğasını gösterir.

## Adım 3: Gazebo Modelini Oluşturun

Bu klasördeki dosyaları kopyalayın:
- [`apriltag_0.model.config`](./apriltag_0.model.config) → `~/.gazebo/models/apriltag_0/model.config` olarak
- [`apriltag_model.sdf`](./apriltag_model.sdf) → `~/.gazebo/models/apriltag_0/model.sdf` olarak
- [`apriltag.material`](./apriltag.material) → `~/.gazebo/models/apriltag_0/materials/scripts/apriltag.material` olarak

`filtering none` ayarı material dosyasında kritik — dokunun bulanıklaştırılmadan (net, köşeli) uygulanmasını sağlıyor, bu olmadan AprilTag algılama çalışmaz.

Modeli world dosyanıza ekleyin:

```xml
<include>
  <uri>model://apriltag_0</uri>
  <name>apriltag_0</name>
  <pose>1.2 0 0.15 0 0 1.5708</pose>
</include>
```

### 🐛 Geometri Düzeltmesi: Levha Normali ve Yönlenme
Modelde levha kutu ölçüsü `<size>0.3 0.01 0.3</size>` olarak tanımlıdır (X=0.3, Y=0.01 kalınlık, Z=0.3).
- **Yüzey Normali:** İnce kenar Y ekseni boyunca olduğundan, geniş levha yüzeylerinin normal vektörü **±Y yönündedir** (eski notlardaki ±X ifadesi geometriyle çelişiyordu).
- **Kamera Açısı:** Kamera robotun X ekseni boyunca (ileri) baktığı için, döndürülmemiş (`yaw=0`) bir levhanın sadece 1 cm'lik ince yan kenarını görür!
- **Çözüm:** Levha dikey eksende (Z) 90° (`1.5708` radyan) döndürülür (`yaw=1.5708`). Böylece geniş yüzey normali robotun kamerasına bakar.

### ⚠️ Kritik Fiziksel Boyut: `size: 0.24` Gerçeği
[`apriltag_config.yaml`](./apriltag_config.yaml) dosyasındaki `size` parametresi:
- AprilTag kütüphanesinde `size`, dış levhanın veya beyaz kenar boşluğunun (quiet zone) genişliği **değildir**; algılanan siyah kare sınırının (dış köşelerin) fiziksel ölçüsüdür.
- 10x10 piksel tag36h11 dokusunda 1 piksellik beyaz kenar payı düşüldüğünde 8x8'lik siyah kare kalır:
  $$\text{Etkin Boyut} = \frac{8}{10} \times 0.30\text{ m} = 0.24\text{ m}$$
- Eğer YAML'da `size: 0.3` yazılırsa, hesaplanan 3D pose mesafesi yaklaşık %25 daha büyük (hatalı) çıkar! Doğru yapılandırma `size: 0.24` olmalıdır.

## Adım 4: AprilTag Node'unu Çalıştırın

[`apriltag_config.yaml`](./apriltag_config.yaml) dosyasını `~/apriltag_config.yaml` olarak kopyalayın:

```bash
printf 'apriltag:\n  ros__parameters:\n    image_transport: raw\n    family: 36h11\n    size: 0.24\n' > ~/apriltag_config.yaml
```

Node'u başlatın:

```bash
ros2 run apriltag_ros apriltag_node --ros-args \
  -r image_rect:=/ika_rover/camera_sensor/image_raw \
  -r camera_info:=/ika_rover/camera_sensor/camera_info \
  --params-file ~/apriltag_config.yaml
```

## Adım 5: Tespiti Doğrulayın

```bash
ros2 topic echo /detections
```

Başarılı bir tespit:
- **`hamming: 0`** — sıfır bit hatası.
- **`decision_margin`** — yüksek güven skoru.

## Adım 6: TF Çerçeve Sözleşmesi (Optik vs Gövde Frame)

`apriltag_ros`, tag pozunu kamera optik çerçevesine göre yayınlar:

```bash
ros2 run tf2_ros tf2_echo camera_optical_frame tag36h11:0
```

- **`camera_optical_frame` sorgusunda (Pinhole Kamera Kuralı):**
  - **Z = İleri mesafe (derinlik)**
  - **X = Sağ / Sol ofset** (pozitif = sağ, negatif = sol)
  - **Y = Dikey ofset** (pozitif = aşağı)
- **`base_link` sorgusunda (Robot Gövde Kuralı REP-103):**
  - **X = İleri mesafe**
  - **Y = Sol / Sağ ofset** (pozitif = sol, negatif = sağ)
  - **Z = Yükseklik**

*Ders:* TF sorgusunda hangi referans çerçevesini kullanıyorsanız, hız komutunu o çerçevenin eksen kuralına göre türetmelisiniz (Modül 10'daki optik çerçeve rotasyonuyla uyumluluk).

## Adım 7: Otonom Takip Davranışı ([`tag_follower.py`](./tag_follower.py))

[`tag_follower.py`](./tag_follower.py), `/tf` üzerinden tag pozunu okuyarak robotu hedefin 1.0 m önünde duracak şekilde sürer:

### ⚠️ Önemli Güvenlik ve Tazelik Düzeltmeleri:
1. **Zaman Aşımı (Freshness Watchdog):** `lookup_transform(..., Time())` buffer'daki son kaydı döndürür. Tag kameranın görüşünden çıksa bile son kayıt orada kalır! `tag_follower.py`, TF zaman damgasını (`transform.header.stamp`) denetler; veri 0.5 saniyeden eskiyse tag kayboldu kabul edilip robot durdurulur (`stop_robot()`).
2. **Kamera Montaj Ofseti:** Kamera `base_link` merkezinden 0.3 m önde (x=0.3) ve 0.2 m yukarıdadır. `target_frame: camera_optical_frame` seçildiğinde hedef mesafe kameraya göre; `target_frame: base_link` seçildiğinde robotun gövde merkezine göre hesaplanır.
3. **Güvenli Kapanış:** Node kapatılırken robotun son hızda asılı kalmaması için `stop_robot()` çağrılır.
4. **Tek Kontrolcü Kuralı:** `tag_follower` çalışırken teleop veya avoider node'ları kapatılmalıdır.

```bash
cd ~/ika_ws/src
ros2 pkg create --build-type ament_python tag_follower --dependencies rclpy geometry_msgs tf2_ros
# tag_follower.py dosyasını tag_follower/tag_follower/ içine kopyalayın
cd ~/ika_ws && colcon build --packages-select tag_follower
source install/setup.bash
ros2 run tag_follower tag_follower
```

## Sırada

[Modül 6: MAVROS + ArduPilot Entegrasyonu](../06-mavros-ardupilot-entegrasyonu) — bu robotun kararlarını Pixhawk simülasyonuna nasıl ilettiğimizi göreceğiz.
