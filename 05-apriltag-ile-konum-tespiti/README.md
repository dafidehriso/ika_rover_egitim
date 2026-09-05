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
  <pose>1.2 0 0 0 0 1.5708</pose>
</include>
```

### 🐛 Hata: Tag Kameraya Yandan/Kenardan Görünüyor (İnce Bir Çizgi Gibi)

Levhamızı, ince kenarı Y ekseninde, geniş yüzeyleri X ekseninin +/- yönünde olacak şekilde tasarladık. Kamera X ekseni boyunca (ileri) baktığında, döndürülmemiş bir tag'in **kenarını** görür, yüzünü değil.

**Çözüm:** Tag'i, dikey (Z) ekseni etrafında 90° (`1.5708` radyan) döndürün — yukarıdaki `<pose>` satırındaki son değer (`yaw`) bunu yapıyor. Bu değeri world dosyasına baştan koyarsanız, Gazebo'yu her yeniden başlattığınızda elle döndürmeniz gerekmez.

## Adım 4: AprilTag Node'unu Çalıştırın

[`apriltag_config.yaml`](./apriltag_config.yaml) dosyasını `~/apriltag_config.yaml` olarak kopyalayın.

```bash
ros2 run apriltag_ros apriltag_node --ros-args \
  -r image_rect:=/ika_rover/camera_sensor/image_raw \
  -r camera_info:=/ika_rover/camera_sensor/camera_info \
  --params-file ~/apriltag_config.yaml
```

### 🐛 Hata: YAML Girinti (Indentation) Bozuluyor

Terminale çok satırlı YAML içeriği yapıştırırken satırlar birleşip düz bir metin haline gelebiliyor, bu da YAML'ın gerektirdiği hiyerarşiyi bozuyor ve `Cannot have a value before ros__parameters` gibi bir hatayla sonuçlanıyor.

**Çözüm:** `printf` ile satır satır, kaçış karakterleriyle (`\n`) oluşturun:

```bash
printf 'apriltag:\n  ros__parameters:\n    image_transport: raw\n    family: 36h11\n    size: 0.3\n' > ~/apriltag_config.yaml
```

## Adım 5: Tespiti Doğrulayın

```bash
ros2 topic echo /detections
```

Başarılı bir tespit şöyle görünür:

```yaml
detections:
- family: tag36h11
  id: 0
  hamming: 0
  decision_margin: 95.32
  corners: [...]
```

- **`hamming: 0`** — sıfır hata, mükemmel okuma.
- **`decision_margin`** — güven skoru, yüksek olması iyi.

## Adım 6: Gerçek Mesafe/Açıyı Sorgulayın

`apriltag_ros`, otomatik olarak `/tf` üzerinden tag'in tam pozunu yayınlıyor (bunun için `size` parametresi doğru ayarlanmış olmalı):

```bash
ros2 run tf2_ros tf2_echo camera_link tag36h11:0
```

Çıktı:

```
- Translation: [-0.003, -0.126, 1.107]
```

Kamera optik çerçevesinde: **z = ileri mesafe**, **x = sağ/sol ofset**, **y = dikey ofset**. Yani bu örnekte tag, kameradan **1.107 metre** uzakta ve neredeyse tam ortada.

## Adım 7: "Tag'e Git ve 1 Metre Önünde Dur" Davranışı

[`tag_follower.py`](./tag_follower.py) dosyası, `/tf`'ten okuduğu mesafe/ofset bilgisini kullanarak basit bir **oransal (proportional) kontrol** ile robotu tag'e yönlendiriyor:

```bash
cd ~/ika_ws/src
ros2 pkg create --build-type ament_python tag_follower --dependencies rclpy geometry_msgs tf2_ros
# tag_follower.py dosyasını kopyalayın, setup.py'a ekleyin:
# 'tag_follower = tag_follower.tag_follower:main',
cd ~/ika_ws && colcon build --packages-select tag_follower
source install/setup.bash
ros2 run tag_follower tag_follower
```

**Kodun mantığı:** `distance_error` pozitifse (tag hedeften uzaksa) ileri gidiyor, negatifse geri gidiyor. `lateral_offset` robotu tag'i ortalayacak şekilde döndürüyor — hatanın büyüklüğüyle orantılı bir düzeltme (klasik P-controller).

## Bu Modülün Gösterdiği Gerçek Dünya Uygulamaları

- GPS'in çalışmadığı kapalı alanlarda konumlandırma
- Şarj istasyonuna / yükleme noktasına hassas yanaşma
- Hedefe yönelik, hesaplanmış otonom hareket (sadece "engelden kaç" gibi tepkisel değil)

## Sırada

[Modül 6: MAVROS + ArduPilot Entegrasyonu](../06-mavros-ardupilot-entegrasyonu) — bu robotun kararlarını gerçek bir Pixhawk mikrokontrolcü simülasyonuna nasıl ilettiğimizi göreceğiz.
