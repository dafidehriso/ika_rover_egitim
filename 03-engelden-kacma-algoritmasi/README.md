# Modül 3: Engelden Kaçma Algoritması

## Konsept: ROS 2 Node Nedir?

Bir **node**, ROS 2'de tek bir işi yapan bağımsız bir programdır. Node'lar birbirleriyle **topic**'ler üzerinden konuşur: biri bir topic'e veri **yayınlar (publish)**, biri o topic'i **dinler (subscribe)**. Bu modülde yazacağımız node:

- `/scan` topic'ini **dinliyor** (lidar verisi alıyor)
- `/cmd_vel` topic'ine **yayın yapıyor** (hareket komutu gönderiyor)

Yani "engel var mı?" diye lidar'ı kontrol edip, karar verip, hareket komutunu gönderen basit bir karar döngüsü.

## Kod: [`avoider.py`](./avoider.py)

**Mantık özetle:** Robotun tam önündeki (±15 derece) lidar okumalarına bakıyor. En yakın mesafe 0.5 metreden azsa robot durup sağa dönüyor; değilse düz ilerliyor.

## ROS 2 Paketi Oluşturma

```bash
mkdir -p ~/ika_ws/src && cd ~/ika_ws/src
ros2 pkg create --build-type ament_python obstacle_avoidance --dependencies rclpy sensor_msgs geometry_msgs
```

`avoider.py` dosyasını bu depodan kopyalayıp `~/ika_ws/src/obstacle_avoidance/obstacle_avoidance/avoider.py` konumuna koyun.

`setup.py` içindeki `entry_points`'e ekleyin:

```python
entry_points={
    'console_scripts': [
        'avoider = obstacle_avoidance.avoider:main',
    ],
},
```

## 🐛 Hata: `colcon: command not found` / Klasörü Komut Gibi Çalıştırma

- `colcon` eksikse: `sudo apt install python3-colcon-common-extensions -y`
- Bir klasörü doğrudan çalıştırmaya çalışıp `Is a directory` hatası alırsanız: klasöre `cd` ile girip içine bir dosya oluşturmanız gerekiyor (`nano dosya.py` gibi), klasörün kendisini çalıştıramazsınız.

## Derleme ve Çalıştırma

```bash
cd ~/ika_ws
colcon build --packages-select obstacle_avoidance
source install/setup.bash
ros2 run obstacle_avoidance avoider
```

Gazebo'da robotunuzun kendi kendine ilerleyip engellere yaklaştığında dönmesi gerekiyor.

## Neden Hem Gazebo Hem MAVROS'a Yayın Yapıyoruz?

Kodda iki ayrı publisher var: biri Gazebo'daki robotu (`/cmd_vel`), diğeri MAVROS üzerinden ArduPilot'u (`/mavros/setpoint_velocity/cmd_vel_unstamped`) hedefliyor. Bunun sebebi [Modül 6](../06-mavros-ardupilot-entegrasyonu)'da anlatılıyor — kısaca, gerçek bir Pixhawk tabanlı araçta "companion computer" (bu node) kararları verir, Pixhawk motorları çalıştırır; bu ikili yayın, o mimarinin komut akışını simülasyonda da kanıtlıyor. Modül 6'yı henüz yapmadıysanız, MAVROS satırları sorunsuz çalışır, sadece hiçbir yere ulaşmaz (dinleyen olmadığı için).

## Sırada

[Modül 4: OpenCV ile Görüntü İşleme](../04-opencv-goruntu-isleme) — kamera sensörünü ekleyip, renk tabanlı nesne tespiti yapacağız.
