# Modül 3: Engelden Kaçma Algoritması

## Konsept: ROS 2 Node Nedir?

Bir **node**, ROS 2'de tek bir işi yapan bağımsız bir programdır. Node'lar birbirleriyle **topic**'ler üzerinden konuşur: biri bir topic'e veri **yayınlar (publish)**, biri o topic'i **dinler (subscribe)**. Bu modülde yazacağımız node:

- `/scan` topic'ini **dinliyor** (lidar verisi alıyor)
- `/cmd_vel` topic'ine **yayın yapıyor** (hareket komutu gönderiyor)

Yani "önümde engel var mı?" diye lidar'ı kontrol edip, karar verip, hareket komutunu gönderen bir otonom karar döngüsü.

## Kod: [`avoider.py`](./avoider.py)

**Mantık özetle:** Robotun tam önündeki (±15 derece) lidar okumalarına dinamik açı hesabı ile bakar. Ön sektördeki en yakın engel mesafesi `safe_distance` (varsayılan 0.5 m) eşiğinden azsa robot durup sola döner; yol açıksa düz ilerler.

### ⚠️ KRİTİK HATA VE TARİHSEL GELİŞİM: Lidar Dizi İndeksi Yanılgısı
İlk sürümde ön sektörü seçmek için şu kod kullanılmıştı:
```python
# HATALI İLK SÜRÜM:
front_ranges = msg.ranges[0:15] + msg.ranges[-15:]
```
- **Kök Neden:** SDF modelinde lidar taraması `min_angle = -3.14159` (-π) ile `max_angle = +3.14159` (+π) arasındadır. Lidar dizisinin 0. indeksi -π (robotun TAM ARKASI), son indeksi ise +π (yine robotun TAM ARKASI) anlamına gelir! Tam ön yön (0 radyan) ise dizinin tam ortasındadır (360 örnekte indeks 180). Dolayısıyla ilk kod, robotun önüne değil **arkasına** bakıyordu!
- **Düzeltilmiş Yaklaşım:** Sabit dizi indeksi varsayımı (360 vs 720 ışın farkında da bozulur) tamamen kaldırıldı. Her ışının gerçek açısı `angle_min + i * angle_increment` formülüyle hesaplanıp `[-π, +π]` aralığına normalize edildi. Sadece `abs(beam_angle) <= math.radians(15.0)` şartını sağlayan ışınlar ön sektör olarak filtrelendi.

### Açısal Yön (REP-103) Kuralı
ROS standardında (REP-103) Z ekseni yukarı bakar. Sağ el kuralına göre **pozitif `angular.z` saat yönünün tersi, yani SOLA dönüştür**. Kodda `angular.z = +0.5` verildiğinde robot sola döner.

### Sensör Veri Politikası (NaN, Aralık Dışı ve +Inf)
1. **`+Inf` (Dönüşsüz Işın):** Lidar ışını menzil içinde hiçbir engele çarpmadan sonsuza/açık alana gitmiştir. Bu bir engel **değildir**; yolun açık olduğunu gösterir.
2. **`NaN` / Boş Veri:** Sensör okuma hatası veya donanımsal kör noktadır. Geçersiz sayılır.
3. **Güvenlik İlkesi:** Ön sektörde hiç geçerli ışın okunamıyorsa robot körlemesine gitmez, güvenlik için hemen durur (`publish_stop()`).

### Watchdog Zaman Aşımı ve Kapanış Güvenliği
- **Watchdog:** Lidar node'u çökerse veya veri akışı kesilirse, robotun son hız komutuyla sonsuza kadar gitmesini engellemek için `scan_timeout_sec` (0.5 sn) süresince veri gelmediğinde robot otomatik durdurulur.
- **Güvenli Kapanış:** Node `Ctrl+C` ile kapatılırken `finally` bloğu ve `destroy_node()` içinde açıkça sıfır hız (`linear.x=0, angular.z=0`) gönderilir.
- *Mimari Not:* Ani process ölümünde (SIGKILL, güç kesintisi) Gazebo'nun son komutta kalmaması için alt seviye diferansiyel sürücüde de zaman aşımı katmanı bulunmalıdır.

### ⚠️ Komut Sahipliği (Command Multiplexing) Uyarısı
Aynı anda birden fazla node (örneğin hem `teleop_twist_keyboard` hem `avoider` hem de Modül 5'teki `tag_follower`) doğrudan `/cmd_vel` topic'ine komut yayınlarsa tekerlekler titrer ve hareket kararsızlaşır.
- `avoider` çalışırken teleop klavye aracını kapatın.
- İleri seviye sistemlerde `twist_mux` paketiyle komut önceliği yönetilir.

---

## ROS 2 Paketi Oluşturma

```bash
mkdir -p ~/ika_ws/src && cd ~/ika_ws/src
ros2 pkg create --build-type ament_python obstacle_avoidance --dependencies rclpy sensor_msgs geometry_msgs
```

`avoider.py` dosyasını `~/ika_ws/src/obstacle_avoidance/obstacle_avoidance/avoider.py` konumuna koyun.

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
- Bir klasörü doğrudan çalıştırmaya çalışıp `Is a directory` hatası alırsanız: klasöre `cd` ile girip içine bir dosya oluşturmanız gerekir (`nano dosya.py` gibi), klasörün kendisini çalıştıramazsınız.

## Derleme ve Çalıştırma

```bash
cd ~/ika_ws
colcon build --packages-select obstacle_avoidance
source install/setup.bash
ros2 run obstacle_avoidance avoider
```

Gazebo'da robotunuzun kendi kendine ilerleyip engellere yaklaştığında sola dönmesi ve engelsiz alanda düz devam etmesi gerekir.

## Neden Hem Gazebo Hem MAVROS'a Yayın Yapıyoruz?

Kodda iki ayrı publisher var: biri Gazebo'daki robotu (`/cmd_vel`), diğeri MAVROS üzerinden ArduPilot'u (`/mavros/setpoint_velocity/cmd_vel_unstamped`) hedefliyor. Bunun sebebi [Modül 6](../06-mavros-ardupilot-entegrasyonu)'da anlatılıyor — kısaca, gerçek bir Pixhawk tabanlı araçta "companion computer" (bu node) kararları verir, Pixhawk motorları çalıştırır; bu ikili yayın, o mimarinin komut akışını simülasyonda da kanıtlıyor. Modül 6'yı henüz yapmadıysanız, MAVROS satırları sorunsuz çalışır, sadece hiçbir yere ulaşmaz (dinleyen olmadığı için).

## Sırada

[Modül 4: OpenCV ile Görüntü İşleme](../04-opencv-goruntu-isleme) — kamera sensörünü ekleyip, renk tabanlı nesne tespiti yapacağız.
