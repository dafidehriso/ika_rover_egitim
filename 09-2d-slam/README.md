# Modül 9: 2D SLAM (slam_toolbox)

> 🌐 **Dil / Language:** **Türkçe** | [English Version (README_EN.md)](README_EN.md)

## Öğrenme Hedefleri
1. Eşzamanlı Konumlandırma ve Haritalama (SLAM) kavramını ve döngü kapanması (loop closure) mekanizmasını anlamak.
2. SDF tabanlı robotlarda TF yayın eksikliğini teşhis edip `static_transform_publisher` ile çözmek.
3. `slam_toolbox` yapılandırmasını (`base_frame: base_link`, `use_sim_time: true`) hazırlamak.
4. Koridor parkurunu dolaşarak RViz üzerinde 2B doluluk ızgarası (occupancy grid) ve pose graph oluşturmak.

## Modül Dosyaları
- [`slam_params.yaml`](./slam_params.yaml): `slam_toolbox` için taban frame ve aralık parametreleri.

---

## Konsept: SLAM'ın Tavuk-Yumurta Problemi
**SLAM = Simultaneous Localization And Mapping**
- Doğru bir harita çıkarabilmek için robotun uzaydaki kesin konumunu bilmek gerekir.
- Robotun konumunu bilebilmek için ise elinizde bir haritanın bulunması gerekir.

Bu döngüsel bağımlılık (tavuk-yumurta problemi); ardışık lidar taramalarını üst üste oturtarak (scan matching) ve tekerlek odometrisiyle birleştirilerek çözülür.

### Döngü Kapanması (Loop Closure) Neden Önemli?
Tekerlek odometrisi zamanla drift (kayma) yapar; lidar taramalarında da ufak hatalar birikir. Robot daha önce geçtiği bir yere tekrar geldiğinde (kapalı döngü), hafızasındaki eski haritayla yeni taramayı eşleştirir ve biriken tüm kaymaları tek seferde geriye dönük optimize ederek düzeltir. Bu yüzden Modül 7'de parkuru **KAPALI DÖNGÜ** koridor olarak inşa ettik.

---

## 🐛 HATA 1: Harita Hep Boş Kaldı — "Message Filter dropping message" Uyarısı
- **Belirti:** RViz'de `/map` topic'i seçildiğinde hiçbir şey görünmüyor; konsolda `Message Filter [target: odom] dropping message: frame 'lidar_link' does not exist` uyarısı akıyor.
- **Kök Neden:** Robotta URDF ve `robot_state_publisher` kullanılmadı (robot doğrudan Gazebo SDF formatında tanımlandı). Bu yüzden `lidar_link` TF ağacında hiç yoktu; `/scan` verisi geliyordu ama ROS bu verinin robotun neresinde ölçüldüğünü bilmiyordu.
- **Çözüm:** Modelin SDF dosyasındaki gerçek pose değerine göre (`0.2, 0, 0.3`) statik TF yayınlandı:
  ```bash
  ros2 run tf2_ros static_transform_publisher 0.2 0 0.3 0 0 0 base_link lidar_link
  ```

---

## 🐛 HATA 2: TF Düzeldi Ama Harita HÂLÂ Boştu (base_frame Uyuşmazlığı)
- **Belirti:** TF hatası kesildi ancak harita yine güncellenmedi.
- **Kök Neden:** `slam_toolbox` varsayılan olarak `base_frame: base_footprint` arar. Ancak bizim robotumuzda `base_footprint` link'i yoktur; ana gövde `base_link`'tir.
- **Çözüm:** [`slam_params.yaml`](./slam_params.yaml) dosyası oluşturulup `base_frame: base_link` ve simülasyon zamanı için `use_sim_time: true` tanımlandı.

```yaml
slam_toolbox:
  ros__parameters:
    odom_frame: odom
    map_frame: map
    base_frame: base_link
    scan_topic: /scan
    use_sim_time: true
    min_laser_range: 0.12
    max_laser_range: 10.0
```

---

## Adım Adım Laboratuvar Akışı

### 1. Paketi Kurun:
```bash
sudo apt install ros-humble-slam-toolbox -y
```

### 2. Terminal 1: Parkuru Başlatın
```bash
gazebo --verbose 07-cok-kamera-mimarisi-ve-parkur/parkur.world
```

### 3. Terminal 2: Lidar Statik TF'ini Yayınlayın
```bash
ros2 run tf2_ros static_transform_publisher 0.2 0 0.3 0 0 0 base_link lidar_link
```

### 4. Terminal 3: SLAM Toolbox'ı Parametre Dosyasıyla Başlatın
```bash
ros2 launch slam_toolbox online_async_launch.py slam_params_file:=09-2d-slam/slam_params.yaml use_sim_time:=true
```

### 5. Terminal 4: RViz ile Haritayı İzleyin
```bash
rviz2
```
- **Fixed Frame:** `map`
- **Add -> By topic -> `/map` (Map)**
- **Add -> By topic -> `/scan` (LaserScan)**

### 6. Terminal 5: Robotu Sürün ve Döngüyü Kapatın
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```
Robotla 4 koridor kolunu sırayla turlayın. Başlangıç noktasına geri döndüğünüzde, RViz'de döngünün pürüzsüzce kapandığını ve temiz bir dörtgen harita elde edildiğini gözlemleyin.

## Sırada
[Modül 10: 3D Haritalama (OctoMap)](../10-3d-haritalama-octomap)
