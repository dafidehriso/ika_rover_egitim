# Modül 4: OpenCV ile Görüntü İşleme

## OpenCV Nedir, Kısaca

Görüntü işleme için kullanılan bir kütüphane. Python'da bir görüntü, temelde bir **sayı dizisi (numpy array)** — her piksel, renk değerlerinden (kırmızı, yeşil, mavi) oluşan sayılar. OpenCV, bu sayı dizileri üzerinde filtreleme, kenar bulma, renk tespiti gibi işlemler yapmanızı sağlıyor.

## Neden Renkli Bir Dünyaya İhtiyacımız Var

Gri bir dünyada renk tabanlı tespit egzersizleri anlamsız kalır. Bu modülde test için `ika_rover.world`'e kırmızı/yeşil/mavi sabit kutular ekliyoruz (bkz. [Modül 2](../02-kendi-robotunuzu-tasarlayin)'deki world dosyasına ek olarak):

```xml
<model name="red_box">
  <static>true</static>
  <pose>2 1 0.25 0 0 0</pose>
  <link name="link">
    <collision name="collision">
      <geometry><box><size>0.5 0.5 0.5</size></box></geometry>
    </collision>
    <visual name="visual">
      <geometry><box><size>0.5 0.5 0.5</size></box></geometry>
      <material>
        <ambient>1 0 0 1</ambient>
        <diffuse>1 0 0 1</diffuse>
      </material>
    </visual>
  </link>
</model>
```
(Yeşil için `0 1 0 1`, mavi için `0 0 1 1` renk değerleri, farklı `pose` konumlarıyla.)

## Kurulum

```bash
sudo apt install ros-humble-cv-bridge python3-opencv -y
cd ~/ika_ws/src
ros2 pkg create --build-type ament_python camera_vision --dependencies rclpy sensor_msgs cv_bridge
```

`cv_bridge`, ROS'un görüntü mesaj formatını (`sensor_msgs/Image`) OpenCV'nin anladığı formata (numpy array) çevirir — ikisi arasındaki köprü budur.

`camera_viewer.py` dosyasını `~/ika_ws/src/camera_vision/camera_vision/` içine koyup `setup.py`'a ekleyin:

```python
'camera_viewer = camera_vision.camera_viewer:main',
```

## Kodun Mantığı, Adım Adım

1. **HSV dönüşümü**: Görüntüler genelde BGR (mavi-yeşil-kırmızı) formatında gelir, ama renk tespiti için **HSV** (Hue-Saturation-Value) formatına çevirmek çok daha kolaydır — "kırmızılık" tek bir sayı aralığıyla ifade edilebilir, ışık değişse bile.
2. **`inRange`**: Belirli bir renk aralığındaki pikselleri beyaz, diğerlerini siyah yapan bir "maske" oluşturur.
3. **`findContours`**: Maskedeki şeklin dış hattını (konturunu) bulur.
4. **`boundingRect`**: O konturu saran en küçük dikdörtgeni hesaplar, ekranda çiziyoruz.

## Çalıştırma

```bash
cd ~/ika_ws && colcon build --packages-select camera_vision
source install/setup.bash
ros2 run camera_vision camera_viewer
```

İki pencere açılmalı: normal görüntü (kırmızı kutunun etrafında yeşil çerçeve) ve maske (kırmızı kutu beyaz, geri kalan her şey siyah).

## 🐛 Hata: Yanlış Pencereye Bakıyorsunuz

Gazebo'nun kendi 3D sahne görünümü (ızgara çizgileri, eksen okları olan) ile robotun **gerçek kamerasının gördüğü** (`cv2.imshow` ile açılan, "ika_rover kamerasi" başlıklı, düz fotoğraf gibi) pencere **farklı şeylerdir**. Kamera testlerinde her zaman ikincisine bakın — birincisi sizin kendi "tanrı gözü" bakış açınız, robotun gördüğü değil.

## Sırada

[Modül 5: AprilTag ile Konum Tespiti](../05-apriltag-ile-konum-tespiti) — kameradan bir görsel işaretin tam 3D konumunu hesaplamayı öğreneceğiz.
