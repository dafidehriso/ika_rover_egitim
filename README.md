# İKA Kursu: Sıfırdan Windows'ta ROS 2 + Gazebo ile Otonom İnsansız Kara Aracı Simülasyonu

Bu depo, **Windows 11 + WSL2** üzerinde, hiç Linux/ROS deneyimi olmayan birinin bile takip edip **kendi otonom robot simülasyonunu** kurabileceği, adım adım, hatasıyla-çözümüyle anlatılmış tam bir eğitim serisidir.

Gerçek bir öğrenme sürecinin (deneme-yanılma, hata alma, hatayı anlama, çözme) birebir kaydı olduğu için, "her şey ilk seferde mükemmel çalıştı" diyen kurslardan farklı: **karşılaşacağınız gerçek hataları ve bunları nasıl teşhis edip çözdüğümüzü** de görüyorsunuz.

## Kimin İçin?

- ROS 2 / Gazebo'ya hiç dokunmamış ama robotik projesi (okul, staj, kişisel) yapması gereken biri
- Windows kullanıp Linux'a geçmek istemeyen biri (WSL2 tam olarak bunu çözüyor)
- Sadece komutları kopyalamak değil, **neden** o komutu çalıştırdığını anlamak isteyen biri

## Kurs Yapısı

Her klasör bağımsız bir "ders" — sırayla takip edin, her biri bir öncekinin üzerine inşa ediyor.

| # | Modül | Ne Öğreniyorsunuz |
|---|-------|-------------------|
| [01](./01-wsl-ros2-gazebo-kurulum) | WSL2 + ROS 2 + Gazebo Kurulumu | Windows'ta Linux robotik ortamı kurma, `.bashrc`/PATH hataları, GUI (WSLg) sorunları |
| [02](./02-kendi-robotunuzu-tasarlayin) | Kendi Robotunuzu Tasarlayın | SDF formatında sıfırdan robot modeli (gövde, tekerlek, sensörler), fizik/joint hataları |
| [03](./03-engelden-kacma-algoritmasi) | Engelden Kaçma Algoritması | Lidar verisi okuma, ROS 2 node yazma, otonom karar verme |
| [04](./04-opencv-goruntu-isleme) | OpenCV ile Görüntü İşleme | Kamera sensörü, `cv_bridge`, HSV renk uzayı, kontur tespiti |
| [05](./05-apriltag-ile-konum-tespiti) | AprilTag ile Konum Tespiti | Görsel işaretlerden 3D pose çıkarma, `tf2`, hedefe yönelik otonom hareket |
| [06](./06-mavros-ardupilot-entegrasyonu) | MAVROS + ArduPilot Entegrasyonu | Pixhawk simülasyonu (SITL), companion computer ↔ flight controller mimarisi |
| [07](./07-cok-kamera-mimarisi-ve-parkur) | Çoklu Kamera Mimarisi ve Gerçekçi Parkur | 5 kameralı SDF tasarımı, doku/materyal doğrulama, kapalı döngü koridor, WASD kontrolü |
| [08](./08-stereo-derinlik-point-cloud) | Stereo Derinlik ve Point Cloud | Disparity haritası, camera_info intrinsics, PointCloud2, RViz görselleştirme |
| [09](./09-2d-slam) | 2D SLAM (slam_toolbox) | TF ağacı kurma, base_frame konfigürasyonu, loop closure, occupancy grid |
| [10](./10-3d-haritalama-octomap) | 3D Haritalama (OctoMap) | Optik çerçeve kavramı, native depth camera, odom vs map frame, launch dosyası birleştirme |
| [11](./11-denge-ve-fizik-duzeltmeleri) | Denge ve Fizik Düzeltmeleri | Caster yerleşimi, rampa geometrisi matematiği (kısmen doğrulanmış) |

## Genel Mimari

Kursun sonunda elinizde şu parçalar olacak:

```
Gazebo (fizik + sensör simülasyonu)
   ├── Lidar → engelden kaçma node'u → /cmd_vel
   ├── Kamera → OpenCV renk tespiti
   ├── Kamera → AprilTag tespiti → tf pose → tag_follower node'u → /cmd_vel
   ├── 5 Kamera (ön stereo çift + sağ/sol/arka mono) → çoklu görüş
   ├── Ön Stereo Çift → stereo_disparity node → point cloud (tanı amaçlı, korunuyor)
   ├── Native Depth Camera → depth_cloud_filter node → filtrelenmiş point cloud → OctoMap (odom frame)
   ├── Lidar → slam_toolbox → 2D occupancy grid harita (map frame, loop closure)
   └── /cmd_vel ──┬──> Gazebo diff_drive (görsel/fiziksel hareket)
                  └──> MAVROS → ArduPilot SITL (Pixhawk simülasyonu, komut akışı kanıtı)
```

## Neden Bu Sırayla?

Her modül bir öncekinin **çalışan** bir temelini gerektiriyor — örneğin AprilTag modülü, kameranın zaten doğru yayın yaptığı bir robota ihtiyaç duyuyor. Sırayı atlarsanız, o modüldeki hata-çözüm anlatıları sizin durumunuza uymayabilir.

## Hızlı Hata Referansı

Belirli bir hatayla mı karşılaştınız? [`HATALAR-VE-COZUMLERI.md`](./HATALAR-VE-COZUMLERI.md) dosyasında, kurs boyunca karşılaştığımız her hatanın tek satırlık bir özeti ve çözümü var — hangi modülde detaylandırıldığına dair linklerle birlikte.

## Genel Öğrenilen Dersler (Tüm Modüllerde Tekrar Eden)

Bu depoyu takip ederken sürekli karşınıza çıkacak birkaç kalıp var, önceden bilmekte fayda var:

1. **Terminal kopyala-yapıştır sorunları**: Uzun, çok satırlı içerik (kod, config dosyası) terminale yapıştırılırken satırlar birleşebiliyor/kayabiliyor. Bu depodaki her komut, bu sorunu en aza indirecek şekilde (`heredoc` veya `printf` ile) yazıldı — yine de sorun yaşarsanız, komutu daha küçük parçalara bölün.
2. **`.bashrc`/PATH değişiklikleri anlık etkili olmaz**: Yeni bir ortam değişkeni eklediğinizde, ya `source ~/.bashrc` çalıştırın ya da yeni bir terminal açın.
3. **WSL2'de ilk açılışlar yavaş olabilir**: Gazebo veya büyük derlemeler beklediğinizden uzun sürebilir, hemen hata sanmayın.
4. **Bir şey "çalışmıyor" dediğinizde önce doğrulayın**: `ros2 topic list`, `ros2 topic echo`, `ros2 node list` gibi komutlarla neyin gerçekten çalışıp çalışmadığını görmeden tahmin yürütmeyin.

## Lisans / Kullanım

Bu içerik özgürce kullanılabilir, çatallanabilir (fork), değiştirilebilir. Bir üniversite/staj projesinde kullanıyorsanız, kaynak göstermeniz nazik bir davranış olur ama zorunlu değil.
