# Modül 9: 2D SLAM (slam_toolbox)

## Durum: TAMAMLANDI

## Konsept: SLAM'ın Tavuk-Yumurta Problemi
SLAM = Simultaneous Localization And Mapping. Doğru harita için konum, doğru
konum için harita gerekir — bu döngüsel bağımlılık, ardışık lidar taramalarını
karşılaştırıp (scan matching) + tekerlek odometrisini birleştirerek çözülür.
"Loop closure": robot daha önce gördüğü bir yere dönünce, geçmiş haritayla
karşılaştırıp biriken küçük hataları toplu düzeltir — bu yüzden Modül 7'de
parkuru KAPALI DÖNGÜ yaptık.

## HATA 1: Harita hep boş kaldı, RViz "Message Filter dropping message" verdi
Kök neden: Robotta URDF/robot_state_publisher YOK (robot doğrudan SDF'te
tanımlı). Bu yüzden lidar_link hiç TF ağacında değildi — /scan verisi geliyordu
ama "bu veri robotun neresinde toplandı" bilgisi yoktu.
Çözüm: Elle statik TF yayınlandı:
```bash
ros2 run tf2_ros static_transform_publisher 0.2 0 0.3 0 0 0 base_link lidar_link
```
(0.2, 0, 0.3 = lidar_link'in model.sdf'teki gerçek pose'u)

## HATA 2: TF düzeldi ama harita HÂLÂ boştu
Kök neden: slam_toolbox varsayılan olarak `base_frame: base_footprint` arıyor
ama robotta böyle bir frame yok, `base_link` var.
Çözüm: `~/slam_params.yaml` oluşturulup base_frame: base_link olarak
slam_params_file parametresiyle launch edildi:
```bash
ros2 launch slam_toolbox online_async_launch.py slam_params_file:=slam_params.yaml
```

## Sonuç
Robot tüm döngüyü (4 koridor kolu) gezdikten sonra, RViz'de TAM KAPALI
DÖRTGEN şeklinde, temiz bir occupancy grid harita elde edildi. Pose graph
(SLAM'ın iç iskelet görselleştirmesi) başlangıç ve bitiş noktalarında
birbirine bağlanmış görünüyor — loop closure'ın çalıştığının kanıtı.

## Sırada
Modül 10: 3D Haritalama (OctoMap)
