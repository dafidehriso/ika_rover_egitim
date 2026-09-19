# Modül 10: 3D Haritalama (OctoMap)

## Durum: TAMAMLANDI (kalite ve doğrulama ince ayarı ileride sürebilir)

## Önkoşullar ve Paket Kurulumu
```bash
sudo apt install ros-humble-octomap-server ros-humble-octomap-rviz-plugins ros-humble-slam-toolbox -y
```

## Modül Dosyaları
- [`depth_cloud_filter.py`](./depth_cloud_filter.py): Native derinlik kamerasından gelen bulutu zemin/tavan/mesafe filtrelerinden geçirip alt örnekleyen node.
- [`sensor_tf.launch.py`](./sensor_tf.launch.py): Gövde ve optik çerçeve TF yayınlarını başlatan launch dosyası.
- [`ika_mapping.launch.py`](./ika_mapping.launch.py): Gazebo, SLAM, filtre, OctoMap ve RViz'i tek komutla başlatan birleşik pipeline.
- [`ika_mapping.rviz`](./ika_mapping.rviz): 2B harita, 3B OctoMap ve sensörleri hazır getiren RViz görselleştirme konfigürasyonu.

## Konsept: OctoMap Nedir? (3B Haritalama vs 3B SLAM)
- **2D SLAM (slam_toolbox):** Lidar verisiyle zemine paralel düzlemde bir occupancy grid (doluluk ızgarası) haritası çıkarır. Sadece (X, Y) koordinatlarında duvar/engel olup olmadığını bilir; tavan, rampa, masa üstü gibi yükseklik boyutunu (Z) bilmez.
- **OctoMap (Hacimsel 3B Harita):** Uzayı sekizli ağaç (octree) yapısıyla küçük küplere (voxel - varsayılan 0.10 m) böler. Her küpü "dolu", "boş" veya "bilinmeyen" olarak olasılıksal günceller.
- **⚠️ Önemli Ayrım:** OctoMap tek başına bir **SLAM algoritması DEĞİLDİR**. Kendi robot konumunu kestirmez; robotun o an nerede olduğunu harici bir kaynaktan (odometri veya 2D SLAM) alıp gelen nokta bulutundaki pikselleri 3B uzaya yerleştirir (ray casting).

## EN ÖNEMLİ KAVRAMSAL HATA: "Optik Çerçeve" Sorunu
OctoMap'e ilk bağlandığında, 3D nokta bulutu robotun ÖNÜNDE değil, TAMAMEN HAVADA/ÜSTÜNDE saçılmış görünüyordu.

### Kök Neden: İKİ Farklı, Çakışan Yön Kuralı (REP-103 vs Pinhole)
1. **ROS Gövde Kuralı (REP-103):** X = İleri, Y = Sol, Z = Yukarı.
2. **Kamera Pinhole Matematiği Kuralı:** Z = Derinlik (İleri), X = Sağ, Y = Aşağı.

`stereo_disparity.py` veya derinlik kamerası, noktaları KAMERA matematiğine göre hesaplıyordu (Z ekseni ileri mesafe). Ancak bu noktalar `camera_link` frame'ine etiketleniyordu — ve `camera_link`, TF ağacında gövde kuralına göre (X=ileri) bağlanmıştı!
Sonuç: İleri yöndeki derinlik (Z), TF tarafından "robotun yukarısı" olarak algılandı ve tüm duvarlar gökyüzüne dikildi.

### Çözüm: `camera_optical_frame` Rotasyon Frame'i
Gerçek endüstriyel kamera sürücülerinin (Intel RealSense, ZED vb.) yaptığı gibi, `camera_link`'e ek olarak, **sadece eksen rotasyonu içeren** ikinci bir frame tanımlandı:

```bash
ros2 run tf2_ros static_transform_publisher 0 0 0 -1.5707963267948966 0 -1.5707963267948966 camera_link camera_optical_frame
```

Ve üretilen tüm point cloud mesajlarının `header.frame_id` değeri `camera_optical_frame` olarak güncellendi.
- `base_link` → `camera_link` (Fiziksel montaj konumu: 0.3m ileri, 0.2m yukarı)
- `camera_link` → `camera_optical_frame` (Sadece koordinat ekseni rotasyonu: roll=-90°, yaw=-90°)

> **DERS:** Bir sensörün TF'ini kurarken, **fiziksel montaj konumu** ile **üretilen verinin matematiksel eksen sözleşmesi** İKİ AYRI ŞEYDİR; aynı frame etiketinde karıştırılmamalıdır.

---

## Mimari Değişiklik: Stereo Disparity'den Native Depth Camera'ya Geçiş
Optik çerçeve düzeltmesinden sonra bile stereo nokta bulutu dokusuz yüzeylerde (düz duvar, çim) gürültü içeriyordu (StereoSGBM doku arar).
- **Yeni Node:** `depth_cloud_filter.py`, Gazebo'nun native derinlik sensöründen (`/ika_rover/depth_camera/points`) beslenir.
- **Filtreler:** Zemin seviyesi (min 0.08 m altı filtrelenir), tavan/yükseklik limiti (max 1.65 m), maksimum menzil (8.0 m) ve 0.10 m voxel grid alt örnekleme uygulanarak OctoMap için temiz bir engel bulutu (`/ika_rover/depth/obstacles`) üretilir.
- *Not:* Modül 8'deki `stereo_disparity.py` silinmedi; iki yöntemi karşılaştırmak amacıyla teşhis/öğretici olarak tutulmaktadır.

---

## Kritik TF Kapsamı: OctoMap'i 'odom' Frame'ine Bağlama
İlk denemede OctoMap `map` frame'ine bağlanmıştı.
- **Sorun:** `slam_toolbox`, kapalı döngüde (loop-closure) haritayı optimize ederken `map -> odom` dönüşümünde ani düzeltme sıçramaları yapabilir. OctoMap `map` frame'indeyken bu ani sıçrama anında eklenen voxel'ler eski voxel'lerle üst üste binip haritada "hayalet duvarlar" oluşturdu.
- **Çözüm ve Sınırları:** OctoMap `frame_id: odom` olarak ayarlandı.
  - **Doğru Kapsam:** `odom` frame'i süreklidir (ani sıçrama yapmaz, teğetsel akar), bu nedenle yeni gelen ölçümler o anki gövdeye göre tutarlı birikir.
  - **⚠️ Önemli Teknik Uyarı:** Odom'a bağlamak **global bir loop-closure düzeltmesi DEĞİLDİR**. Tekerlek odometrisi zamanla kayarsa (drift), odom frame'indeki harita da hafifçe deforme olabilir ve geçmişte eklenmiş voxel'ler geriye dönük düzeltilmez. RViz'de Fixed Frame olarak `map` seçildiğinde ise odom haritası bir bütün olarak dönüştürülerek gösterilir.

---

## Odometri Kaynağı: Simülasyon Ground-Truth vs Tekerlek Enkoderi
`model.sdf` içindeki `diff_drive` eklentisinde:
```xml
<odometry_source>1</odometry_source>
```
- **`1` (WORLD - Varsayılan):** Gazebo'nun simülasyon fizik motorundaki kusursuz yer gerçeği pozunu (ground truth) yayınlar. Tekerlek kayması ve patinaj odometriyi bozmaz. Başlangıç SLAM ve haritalama dersleri için idealdir.
- **`0` (ENCODER):** Gerçek hayattaki gibi tekerleklerin dönüş eklemlerinden entegre edilir; sürtünme ve kaymalar drift yaratır.

---

## Hazır `camera_vision` Paketini Çalışma Alanına Aktarma ve Derleme

Modül 4'te oluşturulan temel paket yalnızca basit renk filtreleme içeriyordu. Modül 10'da çalıştıracağımız birleşik pipeline (`ika_mapping.launch.py`), depomuzun kök dizininde yer alan tam teşekküllü [`camera_vision`](../camera_vision) paketinin derlenmiş olmasına ihtiyaç duyar.

Aşağıdaki adımları sırayla uygulayarak depodaki hazır paketi ROS 2 çalışma alanınıza aktarın:

```bash
# 1. ROS 2 çalışma alanınızın kaynak dizinine geçin:
cd ~/ika_ws/src

# 2. Modül 4'teki temel paketi depodaki tam paketle güncelleyin (Sembolik Link Tavsiye Edilir):
rm -rf camera_vision
ln -s ~/ika_rover_egitim/camera_vision ~/ika_ws/src/camera_vision
# (Alternatif kopyalama yöntemi: cp -r ~/ika_rover_egitim/camera_vision ~/ika_ws/src/)

# 3. Bağımlılıkları derleyin:
cd ~/ika_ws
colcon build --symlink-install --packages-select camera_vision

# 4. Ortamı yükleyin (Her yeni terminalde gereklidir):
source install/setup.bash
```

---

## Sistem Kararlılığı ve Birleşik Launch

1. **DDS Kilitlenmeleri (WSL2):** Ubuntu 22.04'te FastDDS çoklu yayın paketlerinin kilitlenmesini önlemek için:
   ```bash
   export FASTDDS_BUILTIN_TRANSPORTS=UDPv4
   ```
2. **Kalıcı TF Launch'ı:** Tüm statik dönüşümler `sensor_tf.launch.py` içine taşındı.
3. **Tek Komutla Tam Haritalama Pipeline'ı:**
   ```bash
   ros2 launch camera_vision ika_mapping.launch.py
   ```
   Bu launch dosyası aşağıdaki tüm bileşenleri tek komutla ayağa kaldırır:
   - Gazebo simülasyonu (`ika_rover.world` dünyası ve 5 kameralı robot)
   - Sensör ve optik çerçeve TF yayınları (`sensor_tf.launch.py`)
   - 2D Lidar SLAM motoru (`slam_toolbox`)
   - Zemin/tavan engel filtresi (`depth_cloud_filter`)
   - 3B Voxel haritalama sunucusu (`octomap_server`)
   - Önceden yapılandırılmış görselleştirme arayüzü (`rviz2`)

---

## Ölçüm ve Doğrulama Durumu
Önceki geliştirme oturumunda SDF referans duvarlarıyla yapılan geometrik karşılaştırmada %99.5 (3D) ve %100 (2D) örtüşme elde edildiği raporlanmıştır.
- **Önemli Şeffaflık Notu:** Bu oranlar geçmiş oturumdaki bir test turundan bildirilmiş olup, bu depoda henüz tekrar çalıştırılabilir otomatik bir kıyaslama script'i ile sunulmamaktadır.
- Hedeflenen Değerlendirme Standardı: Koridor parkurunda 0.10 m voxel çözünürlüğünde, bilinen referans duvar geometrisi ile ölçülen dolu hücreler arasındaki IoU (Intersection over Union) ve hassasiyet/duyarlılık (precision/recall) metrikleri şeklinde belgelenmelidir.

## Sırada
[Modül 11: Denge ve Fizik Düzeltmeleri](../11-denge-ve-fizik-duzeltmeleri)
