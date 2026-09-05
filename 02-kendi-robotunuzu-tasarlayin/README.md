# Modül 2: Kendi Robotunuzu Tasarlayın

## Neden Hazır Bir Modelle (TurtleBot3) Başlayıp Sonra Kendi Modelinize Geçiyoruz?

Hazır modeller (TurtleBot3 gibi) ROS/Gazebo'nun genel işleyişini hızlıca test etmek için harika, ama "kendi projeniz" dediğinizde gerçekten sizin tasarladığınız bir şey olması gerekir. Bu modülde, **SDF (Simulation Description Format)** kullanarak sıfırdan bir robot modeli inşa ediyoruz: kutu gövde, 2 tekerlek, bir denge tekeri (caster), IMU, lidar ve kamera sensörleri.

## SDF Nedir, Kısaca

SDF, Gazebo'nun robot/nesne tanımlamak için kullandığı XML tabanlı bir format. Temel yapı taşları:

- **`<link>`**: Robotun fiziksel bir parçası (gövde, tekerlek gibi) — kütlesi, şekli (collision/visual) var.
- **`<joint>`**: İki link'i birbirine bağlayan eklem (sabit ya da dönebilen).
- **`<sensor>`**: Bir link'e eklenen algılayıcı (kamera, lidar, IMU).
- **`<plugin>`**: Gazebo'nun fiziksel/sensör verisini ROS'a bağlayan köprü kod parçaları.

## Model Yapımız (`model.sdf`)

Bu klasördeki [`model.sdf`](./model.sdf) dosyası şunları içeriyor:

- `base_link` — ana kutu gövde
- `left_wheel` / `right_wheel` — dönebilen tekerlekler
- `caster_wheel` — sürtünmesiz, sabit bir denge küresi (2 tekerlek tek başına robotu dengede tutamaz)
- `imu_link` — ivme/açısal hız sensörü
- `lidar_link` — 360° tarayan lazer sensörü, `/scan` topic'ine yayın yapar
- `camera_link` — `/ika_rover/camera_sensor/image_raw` topic'ine görüntü yayınlayan kamera
- `diff_drive` plugin'i — `/cmd_vel`'i dinleyip tekerlekleri döndüren, Gazebo'nun hazır diferansiyel sürüş eklentisi

## 🐛 Hata #1: Gazebo Insert Menüsünde Model Görünmüyor

Model dosyalarını (`model.config`, `model.sdf`) `~/.gazebo/models/<isim>/` altına koyduğunuzda, bazen Gazebo bunları hemen tanımaz.

**Çözüm:** Gazebo'yu tamamen kapatıp (`ps aux | grep gz` ile arta kalan süreç olmadığından emin olup) temiz bir şekilde yeniden başlatın. Gazebo, model listesini genelde sadece açılışta tarar.

## 🐛 Hata #2: Model Insert İle Eklendiğinde İsim Çakışması (`_0` Eki)

Modeli Gazebo'nun "Insert" menüsünden manuel eklerseniz, Gazebo otomatik olarak ismin sonuna `_0` gibi bir ek koyar (`ika_rover_0`). Bu, sensör isimlerini sabit olarak yapılandırdığımız pluginlerde (örn. IMU adı) eşleşme sorununa yol açar.

**Çözüm:** Modeli Insert ile eklemek yerine, doğrudan bir **world dosyasının içine gömün** — bu şekilde isim sabit kalır:

```bash
{
echo '<?xml version="1.0"?>'
echo '<sdf version="1.6">'
echo '  <world name="default">'
echo '    <include><uri>model://sun</uri></include>'
echo '    <include><uri>model://ground_plane</uri></include>'
sed -n '/<model /,/<\/model>/p' ~/.gazebo/models/ika_rover/model.sdf
echo '  </world>'
echo '</sdf>'
} > ~/ika_rover.world
```

## 🐛 Hata #3: Tekerlekler Dönüyor Ama Robot Düz Gitmiyor (En Önemli Ders!)

Tekerlek modelini doğru yöne çevirmek için `<pose>` içinde 90° döndürdük, ama joint'in dönme eksenini (`<axis><xyz>0 1 0</xyz>`) hangi referans çerçevesinde yorumlayacağını belirtmedik. SDF, bunu varsayılan olarak tekerleğin **kendi (döndürülmüş) çerçevesinde** yorumluyor — bu da tekerleğin, ileri gitmesi gereken eksende değil, **dikey eksende** (bir topaç gibi) dönmesine yol açıyor.

**Çözüm:** Eksenin **modelin ana çerçevesinde** yorumlanmasını belirtin:

```xml
<axis>
  <xyz>0 1 0</xyz>
  <use_parent_model_frame>1</use_parent_model_frame>
  <limit><lower>-1e+16</lower><upper>1e+16</upper></limit>
</axis>
```

Bu satır, `model.sdf` dosyasında zaten düzeltilmiş halde mevcut. **Kendi modelinizi sıfırdan yazarken, döndürülmüş bir link'e joint eklerken bunu unutmayın** — bu proje boyunca karşılaştığımız en sinsi hatalardan biriydi çünkü hata mesajı vermiyor, sadece garip bir fiziksel davranış üretiyor.

## Kurulum ve Test

```bash
mkdir -p ~/.gazebo/models/ika_rover
# model.sdf ve model.config dosyalarını bu klasöre kopyalayın (bu depodan)

# World dosyasını oluşturun (yukarıdaki komutla)

gazebo --verbose ~/ika_rover.world
```

Başka bir terminalde doğrulayın:

```bash
ros2 topic list
# /scan, /cmd_vel, /odom, /ika_rover/camera_sensor/image_raw görmelisiniz
```

Hareket testi:

```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.2}}" -r 5
```

**Önemli:** Bu komut sürekli tekrar eder (`-r 5`). Durdurmak için sadece `Ctrl+C` yapmak **yeterli değildir** — `gazebo_ros_diff_drive` eklentisi son aldığı komutu yeni bir komut gelene kadar uygulamaya devam eder. Robotu gerçekten durdurmak için:

```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0}, angular: {z: 0.0}}" --once
```

## Sırada

[Modül 3: Engelden Kaçma Algoritması](../03-engelden-kacma-algoritmasi) — lidar verisini okuyup robotu otonom şekilde yönetecek ilk ROS 2 node'unuzu yazıyoruz.
