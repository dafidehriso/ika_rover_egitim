# Modül 10: 3D Haritalama (OctoMap)

## Durum: TAMAMLANDI (kalite ince ayarı ileride sürebilir)

## Konsept: OctoMap Nedir?
2D SLAM haritası sadece "burada duvar var mı" (x,y) bilir, yükseklik yok.
OctoMap, uzayı küçük küplere (voxel) bölüp her birini "dolu/boş/bilinmiyor"
olarak işaretleyerek GERÇEK 3D hacimsel harita çıkarır. Kendi konum kestirmez —
SLAM'dan (Modül 9) gelen konumu kullanıp sadece hacmi doldurur.

## EN ÖNEMLİ KAVRAMSAL HATA: "Optik Çerçeve" Sorunu
OctoMap'e ilk bağlandığında, 3D nokta bulutu robotun ÖNÜNDE değil, TAMAMEN
HAVADA/ÜSTÜNDE saçılmış görünüyordu.

Kök neden: İKİ farklı, çakışan yön kuralı var:
- ROS'un gövde kuralı (REP-103): X=ileri, Y=sol, Z=yukarı
- Kamera matematiğinin (pinhole) kuralı: Z=derinlik(ileri), X=sağ, Y=aşağı

stereo_disparity.py, noktaları KAMERA kuralına göre hesaplıyordu (Z=derinlik)
ama bu noktalar camera_link frame'ine etiketleniyordu — ve camera_link, TF'e
GÖVDE kuralına göre (X=ileri) tanıtılmıştı. Sonuç: "derinlik" (ileri mesafe),
yanlışlıkla "yukarı" (Z, gövde kuralında) olarak yorumlanıyordu.

Çözüm: Gerçek kamera sürücülerinin (RealSense, vb.) yaptığı gibi, camera_link'e
EK olarak, SADECE ROTASYON farkı olan ikinci bir frame tanımlandı:
```bash
ros2 run tf2_ros static_transform_publisher 0 0 0 -1.5707963267948966 0 -1.5707963267948966 camera_link camera_optical_frame
```
Ve point cloud'un frame_id'si camera_link yerine camera_optical_frame yapıldı.
Bu, TF zincirini base_link → camera_link (fiziksel konum) → camera_optical_frame
(sadece rotasyon, kamera matematiğine çevirir) şeklinde ikiye ayırıyor.

DERS: Bir sensörün TF'ini kurarken, "fiziksel montaj konumu" ile "verinin
matematiksel olarak hangi eksen kuralında üretildiği" İKİ AYRI ŞEYDİR, aynı
frame'de karıştırılmamalı.

## Mimari Değişiklik: Stereo'dan Native Depth Camera'ya Geçiş
Optik çerçeve düzeltmesinden sonra bile point cloud hâlâ gürültülüydü (çim
dokusu + StereoSGBM sınırlamaları + robot dönerken biriken hatalı noktalar).
Karar: OctoMap'i beslemek için artık stereo_disparity.py DEĞİL, Gazebo'nun
native `depth_camera` sensöründen türetilen, zemin/yükseklik filtreli
`/ika_rover/depth/obstacles` point cloud'u (yeni bir node: depth_cloud_filter.py)
kullanılıyor. Stereo node'u SİLİNMEDİ — tanı/gözlem ve "iki yöntemi karşılaştırma"
amaçlı, kurs için bilinçli olarak korundu (bkz Modül 8).

## Kritik TF/Drift Kararı: OctoMap'i 'map' Değil 'odom' Frame'ine Bağlama
İlk denemede OctoMap 'map' frame'ine bağlıydı. Sorun: slam_toolbox loop-closure
sırasında map→odom dönüşümünde ani "sıçramalar" yapabilir (harita optimize
olurken robotun tahmini konumu küçük düzeltmeler alır). OctoMap 'map' frame'inde
olduğunda, bu sıçramalar eski (zaten yerleştirilmiş) 3D voxel'lerin haritada
KAYIP, "hayalet duvarlar" şeklinde kalmasına yol açıyordu. Çözüm: OctoMap
'odom' frame'ine bağlandı — bu frame sürekli/kaymasız (drift daha yavaş ve
sürekli, ani sıçrama yok), voxel tutarlılığı korunuyor.

## Sistem Kararlılığı İyileştirmeleri
- WSL2/Ubuntu 22.04'te yaşanan DDS (ROS 2'nin alt seviye mesajlaşma protokolü)
  kilitlenmeleri, her terminalde `export FASTDDS_BUILTIN_TRANSPORTS=UDPv4`
  ortam değişkeniyle çözüldü.
- Tüm elle açılan static_transform_publisher komutları, kalıcı bir launch
  dosyasına (sensor_tf.launch.py) taşındı — artık her oturumda elle
  yazılmıyor.
- Tek bir launch dosyası (ika_mapping.launch.py), tüm ekosistemi (Gazebo,
  slam_toolbox, TF'ler, depth filtreleme, OctoMap, RViz2) tek komutla
  başlatıyor:
```bash
  ros2 launch camera_vision ika_mapping.launch.py
```

## Doğrulama Sonucu
SDF'teki referans geometriyle karşılaştırıldığında: %99.5 (3D) ve %100 (2D)
geometrik örtüşme ölçüldü — Modül 9 ve 10'un teknik olarak başarıyla
tamamlandığının kanıtı.

## Sırada
Modül 11: Denge ve Fizik Düzeltmeleri, sonra Modül 12: Otonom Keşif (Nav2)
