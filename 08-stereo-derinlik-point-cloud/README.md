# Modül 8: Stereo Derinlik ve Point Cloud

## Durum: TAMAMLANDI (parametre ince ayarı ileride sürebilir)

## Konsept: İki Göz, Bir Derinlik
İnsan gözü gibi: aynı nesnenin iki kameradaki piksel konumu farkı (disparity),
bilinen kamera-arası mesafeyle (baseline) birleşince gerçek mesafeye (derinlik)
çevrilebilir:

Derinlik(Z) = (Baseline × Odak_Uzaklığı) / Disparity

`camera_info` topic'i, K matrisini (fx, fy, cx, cy) taşır — bunlar koddan
OKUNUR, elle sabit kodlanmaz. Gerçek doğrulanmış değerler: fx=fy=381.46,
cx=320.5, cy=240.5 (640x480 çözünürlükte).

Her piksel, disparity'den 3D noktaya çevrilir:
Z = baseline*fx/disparity
X = (u-cx)*Z/fx
Y = (v-cy)*Z/fy

## StereoSGBM ile Disparity Hesabı
OpenCV'nin StereoSGBM algoritması kullanıldı. `camera_vision` paketine
`stereo_disparity.py` node'u eklendi: sol+sağ görüntüyü `message_filters.
ApproximateTimeSynchronizer` ile senkronize alıp, disparity hesaplayıp,
sensor_msgs_py.point_cloud2 ile PointCloud2 yayınlıyor (/ika_rover/stereo/points).

## HATA: İlk disparity haritası tamamen gürültülüydü
Sebep: Sahne (kutular, zemin) çoğunlukla DÜZ/TEK RENKLİ yüzeylerden oluşuyordu.
StereoSGBM eşleşme kurmak için doku/kenar arar, düz yüzeyde hiç "iz" yoktur.
Çözüm (kısmi): Zemine Gazebo/Grass dokusu verilince (Modül 7) durum iyileşti.
Ayrıca parametre ince ayarı yapıldı: blockSize 7→11, uniquenessRatio 10→15,
speckleWindowSize 100→150 (gürültüyü azaltmak için).

## RViz'de Görselleştirme
Fixed Frame=camera_link (sonra camera_optical_frame, bkz Modül 10), Color
Transform=RGB8, Style=Flat Squares. Sonuç: gerçek renklerde (yeşil zemin,
turuncu ahşap, beyaz duvar) tanınabilir 3D nokta bulutu.

## Not: Bu Node Hâlâ Kod Tabanında Duruyor (Tanı Amaçlı)
İleride (Modül 10) 3D haritalama için Gazebo'nun native derinlik kamerasına
geçildi çünkü daha temiz/güvenilir veri veriyor. Ama stereo_disparity.py
SİLİNMEDİ — "iki yöntemi karşılaştırma" için kasıtlı olarak bırakıldı, kurs
açısından öğretici bir örnek.

## Sırada
Modül 9: 2D SLAM (slam_toolbox)
