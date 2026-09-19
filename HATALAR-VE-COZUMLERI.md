# Tüm Hatalar ve Çözümleri — Hızlı Referans

Bu dosya, kurs boyunca karşılaştığımız her hatayı tek bir yerden aranabilir hale getiriyor. Detaylı açıklamalar için ilgili modülün README'sine bakın.

| Hata Belirtisi | Kök Sebep | Çözüm | Modül |
|---|---|---|---|
| `Sorry, passwords do not match` | Linux terminalinde şifre yazarken karakterler görünmez | Yavaşça yazın; gerekirse `wsl -d Ubuntu-22.04 -u root` ile `passwd` sıfırlayın | [01](./01-wsl-ros2-gazebo-kurulum) |
| `.bashrc` içinde `syntax error near unexpected token` | Windows PATH'indeki boşluklu/parantezli klasör adları tırnaksız eklenmiş | PATH eklerken her zaman tırnak kullanın: `export PATH="..."` | [01](./01-wsl-ros2-gazebo-kurulum) |
| `colcon: command not found` | `python3-colcon-common-extensions` kurulu değil | `sudo apt install python3-colcon-common-extensions -y` | [01](./01-wsl-ros2-gazebo-kurulum), [03](./03-engelden-kacma-algoritmasi) |
| Gazebo Insert menüsünde model görünmüyor | Gazebo model listesini sadece açılışta tarıyor | Gazebo'yu tamamen kapatıp temiz yeniden başlatın | [02](./02-kendi-robotunuzu-tasarlayin) |
| `Service /spawn_entity unavailable` | WSL2'de Gazebo'nun ROS factory servisi geç başlıyor | `wsl --shutdown` ile temiz sıfırlama, tekrar deneyin | [02](./02-kendi-robotunuzu-tasarlayin) |
| Model `_0` eki alıyor, sensör bulunamıyor | Insert menüsünden manuel ekleme isim çakışması yaratıyor | Modeli world dosyasının içine gömün, `<include>` kullanmayın | [02](./02-kendi-robotunuzu-tasarlayin) |
| Tekerlekler dönüyor ama robot düz gitmiyor | Joint axis, döndürülmüş link'in kendi çerçevesinde yorumlanıyor | `<axis>` içine `<use_parent_model_frame>1</use_parent_model_frame>` ekleyin | [02](./02-kendi-robotunuzu-tasarlayin) |
| `Ctrl+C` sonrası robot durmuyor, tekerlek dönmeye devam ediyor | `diff_drive` eklentisi son komutu süresiz uyguluyor | Açıkça sıfır hız komutu gönderin: `--once` ile `linear.x: 0.0` | [02](./02-kendi-robotunuzu-tasarlayin) |
| Kamerada hiçbir şey doğru görünmüyor | Gazebo'nun genel sahne görünümüyle robotun gerçek kamerası karıştırılıyor | `cv2.imshow` ile açılan, ızgarasız pencereye bakın | [04](./04-opencv-goruntu-isleme) |
| AprilTag PNG'si sadece birkaç yüz bayt | **Bu bir hata değil** — AprilTag görselleri gerçekten düşük çözünürlüklü (10x10 piksel) | `file` komutuyla geçerli bir PNG olduğunu doğrulayın | [05](./05-apriltag-ile-konum-tespiti) |
| Tag kamerada ince bir çizgi gibi görünüyor | Levhanın geniş yüzü kameraya değil, yana bakıyor | Tag'i dikey eksende 90° döndürün (`pose`'daki yaw değeri) | [05](./05-apriltag-ile-konum-tespiti) |
| `Cannot have a value before ros__parameters` | YAML dosyasının girintisi (indentation) yapıştırırken bozulmuş | `printf` ile satır satır, `\n` kaçış karakterleriyle oluşturun | [05](./05-apriltag-ile-konum-tespiti) |
| `/detections` sürekli boş dönüyor | Tag kameranın görüş alanında değil, ya da yanlış açıda | `camera_viewer` penceresinden gerçek kamera görüntüsünü kontrol edin | [05](./05-apriltag-ile-konum-tespiti) |
| `mavproxy.py: command not found` | `~/.local/bin` PATH'e ekli değil | `export PATH="$PATH:$HOME/.local/bin"` ekleyip `source ~/.bashrc` | [06](./06-mavros-ardupilot-entegrasyonu) |
| ArduPilot-Gazebo köprü eklentisinde IMU bulunamıyor hatası | Eski/bakımsız bir kütüphanenin (`ardupilot_gazebo` Classic fork) bilinen, çözülmemiş sınırlaması | Bu yaklaşımdan vazgeçip Gazebo+ArduPilot'u ayrı çalıştırıp aynı komutu ikisine de gönderin | [06](./06-mavros-ardupilot-entegrasyonu) |
| Gazebo/Rockwall dokusu hiç görünmedi / materyal çalışmıyor | Materyal ismi var sanılıp doğrulanmadan kullanılmış, texture eksik/bozuk | `awk`/`grep` ile gazebo.material script'inde texture_unit kontrolü yapın | [07](./07-cok-kamera-mimarisi-ve-parkur) |
| Periyodik doku (CeilingTiled) stereo eşleştirmeyi bozuyor | Tekrarlayan kare desen stereo eşleştirmede çoklu yanlış eşleşmeye yol açıyor | Organik/düzensiz doku (Grass gibi) tercih edin | [07](./07-cok-kamera-mimarisi-ve-parkur), [08](./08-stereo-derinlik-point-cloud) |
| SLAM haritası hep boş kaldı, Message Filter dropping uyarısı | Robotta URDF/robot_state_publisher yok, sensör TF ağacında yok | `static_transform_publisher` ile sensör TF'lerini yayınlayın | [09](./09-2d-slam) |
| TF var ama SLAM haritası hâlâ boş | slam_toolbox varsayılan base_frame: base_footprint arıyor, robotta base_link var | `slam_params.yaml` içinde `base_frame: base_link` tanımlayın | [09](./09-2d-slam) |
| OctoMap point cloud havada/saçılmış görünüyor | Kamera optik kuralı (Z=derinlik) ile ROS gövde kuralı (X=ileri) aynı frame'de karıştırılmış | Sadece rotasyon farkı olan `camera_optical_frame` TF'i ekleyin | [10](./10-3d-haritalama-octomap) |
| OctoMap'te "hayalet duvarlar" ve voxel kaymaları | OctoMap loop-closure'da ani sıçrama yapabilen 'map' frame'ine bağlı | OctoMap'i sürekli/kaymasız 'odom' frame'ine bağlayın | [10](./10-3d-haritalama-octomap) |
| WSL2'de FastDDS / ROS 2 mesajlaşma kilitlenmeleri | FastDDS alt seviye taşıma/multicast sorunları | `export FASTDDS_BUILTIN_TRANSPORTS=UDPv4` ortam değişkenini ekleyin | [10](./10-3d-haritalama-octomap) |
| Rampa robota "görünmez duvar" gibi çarpıyor | Kutu merkezinden döndürülünce giriş ucu zeminden ~30cm yukarıda kaldı | Giriş ucu tam zemin seviyesinde olacak şekilde merkez ve pitch açısını yeniden hesaplayın | [11](./11-denge-ve-fizik-duzeltmeleri) |
| Robot hızlanırken öne yalpalayıp kamera yere bakıyor | Tek arka caster, önde hiç destek noktası yok (cantilever yük) | Öne 2 yeni serbest destek tekeri (front caster) ekleyin (5 nokta temas) | [11](./11-denge-ve-fizik-duzeltmeleri) |

## Genel Kalıp: Terminal Kopyala-Yapıştır Sorunları

Bu depodaki komutların büyük çoğunluğu, uzun/çok satırlı içerik terminale yapıştırılırken satırların birleşmesi ya da kesilmesi sorunuyla en az bir kez karşılaştı. En güvenilir yöntemler, önem sırasına göre:

1. **`printf '%s\n' 'satır1' 'satır2' ... > dosya`** — kısa, tek satırlık içerikler için en güvenli.
2. **`cat > dosya << 'EOF' ... EOF` (heredoc)** — uzun, çok satırlı kod/config dosyaları için, ama yapıştırma sırasında terminal satırları birleştirebiliyor; sorun yaşarsanız komutu küçük parçalara bölün.
3. **`nano`** — en son çare, çünkü kopyala-yapıştırda özel karakterlerde (`<`, `>`) sorun çıkarabiliyor.

Herhangi bir dosya oluşturduktan sonra **her zaman** `wc -l dosya` ile satır sayısını ya da `cat dosya` ile içeriği doğrulayın — sessizce yarım kalmış bir dosya, ileride anlaşılması çok daha zor hatalara yol açar.

## Modül 7-11 Hataları

### Materyal/doku isimleri doğrulanmadan kullanılınca sessizce çalışmıyor
Belirti: Gazebo/Rockwall gibi bir materyal isminin hiçbir görsel etkisi olmadı.
Çözüm: `awk`/`grep` ile gazebo.material script dosyasında texture_unit
tanımının gerçekten var olduğunu önce doğrula. (Modül 7)

### Periyodik/tekrarlayan doku stereo eşleştirmeyi bozar
Belirti: CeilingTiled gibi kare desenli zemin, disparity haritasında bloklu/
anlamsız sonuç verdi. Çözüm: organik/düzensiz doku (Grass) kullan. (Modül 7-8)

### SLAM haritası hep boş kaldı — TF eksikliği
Belirti: RViz "Message Filter dropping message" uyarısı verdi, /map topic'i
hiç dolmadı. Kök neden: robotta robot_state_publisher/URDF yok, sensör
frame'leri TF ağacında hiç yoktu. Çözüm: static_transform_publisher ile elle
(sonra launch dosyasına taşınarak) her sensör için TF yayınlandı. (Modül 9)

### SLAM base_frame uyuşmazlığı
Belirti: TF düzeldi ama harita hâlâ boştu. Kök neden: slam_toolbox varsayılan
base_frame=base_footprint arıyordu, robotta base_link var. Çözüm:
slam_params.yaml içinde base_frame:base_link tanımlanıp slam_params_file
parametresiyle launch edildi. (Modül 9)

### OctoMap point cloud'u havada/saçılmış gösterdi — "optik çerçeve" hatası
Belirti: 3D nokta bulutu robotun önünde değil, tamamen üstünde/havada
saçılmış görünüyordu. Kök neden: kamera matematiği kuralı (Z=derinlik) ile
ROS gövde kuralı (X=ileri) aynı frame'de (camera_link) karıştırılmıştı.
Çözüm: camera_link'e ek, sadece rotasyon farkı olan camera_optical_frame
eklendi, point cloud bu yeni frame'e etiketlendi. (Modül 10 — EN ÖNEMLİ DERS)

### OctoMap'te "hayalet duvarlar" — yanlış TF frame'ine bağlama
Belirti: SLAM loop-closure sonrası eski 3D voxel'ler haritada yanlış/kayıp
yerlerde kalıyordu. Kök neden: OctoMap 'map' frame'ine bağlıydı, ama bu frame
loop-closure sırasında ani sıçramalar yapabiliyor. Çözüm: OctoMap 'odom'
frame'ine bağlandı (daha sürekli/kaymasız). (Modül 10)

### WSL2'de DDS (ROS 2 mesajlaşma) kilitlenmeleri
Çözüm: Her terminalde `export FASTDDS_BUILTIN_TRANSPORTS=UDPv4` ortam
değişkeni ayarlandı. (Modül 10)

### Rampa robota "görünmez duvar" gibi çarpıyordu
Belirti: Robot rampaya yaklaşınca ilerlemeyi durduruyordu. Kök neden: kutu
şeklindeki rampa merkezinden döndürülünce, girilen ucu zeminden ~30cm
yukarıda kalıyordu. İlk düzeltme (pitch işaretini ters çevirmek) sorunu
çözmedi, sadece hangi ucun havada olduğunu değiştirdi. Çözüm: pitch açısı ve
merkez pozisyonu matematiksel olarak yeniden hesaplandı (giriş ucu tam
zemin seviyesinde oturacak şekilde). DURUM: son haliyle gerçek sürüşle
DOĞRULANMADI. (Modül 11)

### Robot hızlanırken öne yalpalayıp kamera aşağı bakıyordu
Kök neden: tek arka caster, önde hiç destek noktası yok. Çözüm: tam 4WD'ye
geçmek yerine, öne 2 yeni caster eklendi (5 nokta temas). (Modül 11)

