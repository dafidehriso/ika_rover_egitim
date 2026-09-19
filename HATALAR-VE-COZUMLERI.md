# Tüm Hatalar ve Çözümleri — Hızlı Referans

Bu dosya, kurs boyunca karşılaştığımız her hatayı tek bir yerden aranabilir hale getiriyor. Detaylı açıklamalar için ilgili modülün README'sine bakın.

| Hata Belirtisi | Kontrol / Kök Sebep | Çözüm | Modül |
|---|---|---|---|
| `Sorry, passwords do not match` | Linux terminalinde şifre yazarken karakterler görünmez | Yavaşça yazın; gerekirse `wsl -d Ubuntu-22.04 -u root` ile `passwd` sıfırlayın | [01](./01-wsl-ros2-gazebo-kurulum) |
| `.bashrc` içinde `syntax error near unexpected token` | Windows PATH'indeki boşluklu/parantezli klasör adları tırnaksız eklenmiş | PATH eklerken her zaman tırnak kullanın: `export PATH="..."` | [01](./01-wsl-ros2-gazebo-kurulum) |
| `.bashrc` düzenlendi ama komutlar bulunamıyor | `.bashrc` değişiklikleri mevcut shell'e otomatik yansımaz | Terminalde `source ~/.bashrc` çalıştırın ya da yeni terminal açın | [01](./01-wsl-ros2-gazebo-kurulum) |
| `colcon: command not found` | `python3-colcon-common-extensions` kurulu değil | `sudo apt install python3-colcon-common-extensions -y` | [01](./01-wsl-ros2-gazebo-kurulum), [03](./03-engelden-kacma-algoritmasi) |
| Gazebo Insert menüsünde model görünmüyor | Gazebo model listesini sadece açılışta tarıyor | Gazebo'yu tamamen kapatıp temiz yeniden başlatın | [02](./02-kendi-robotunuzu-tasarlayin) |
| `Service /spawn_entity unavailable` | Gazebo'nun ROS factory eklentisi (`libgazebo_ros_factory.so`) başlatılmamış | `gazebo -s libgazebo_ros_init.so -s libgazebo_ros_factory.so` ile başlatın | [02](./02-kendi-robotunuzu-tasarlayin) |
| `Error parsing XML ... Error document empty` | PowerShell `>` ile yazılan `.world`/`.sdf` dosyası UTF-16LE kodlanmış | `file dosya.world` ile kontrol edin; dosyayı UTF-8 formatında kaydedin | [02](./02-kendi-robotunuzu-tasarlayin), [07](./07-cok-kamera-mimarisi-ve-parkur), [11](./11-denge-ve-fizik-duzeltmeleri) |
| Tekerlekler dönüyor ama robot düz gitmiyor | Joint axis, döndürülmüş link'in kendi çerçevesinde yorumlanıyor | `<axis>` içine `<use_parent_model_frame>1</use_parent_model_frame>` ekleyin | [02](./02-kendi-robotunuzu-tasarlayin) |
| `Ctrl+C` sonrası robot durmuyor, tekerlek dönmeye devam ediyor | `diff_drive` eklentisi son komutu süresiz uyguluyor | Node kapanışında (`finally`/`destroy_node`) sıfır hız komutu gönderin | [02](./02-kendi-robotunuzu-tasarlayin), [03](./03-engelden-kacma-algoritmasi) |
| Robot önde engel varken durmuyor, arkada varken duruyor | Lidar -π..+π taramasında `ranges[0:15]` arkaya bakar, ön sektör ortadadır | `angle_min + i * angle_increment` ile normalize açı hesabı yapın | [03](./03-engelden-kacma-algoritmasi) |
| Kamerada hiçbir şey doğru görünmüyor | Gazebo'nun genel sahne görünümüyle robotun gerçek kamerası karıştırılıyor | `cv2.imshow` ile açılan, ızgarasız pencereye bakın | [04](./04-opencv-goruntu-isleme) |
| AprilTag PNG'si sadece birkaç yüz bayt | **Bu bir hata değil** — AprilTag görselleri gerçekten düşük çözünürlüklü (10x10 piksel) | `file` komutuyla geçerli bir PNG olduğunu doğrulayın | [05](./05-apriltag-ile-konum-tespiti) |
| Tag kamerada ince bir çizgi gibi görünüyor | Levhanın geniş yüzey normali ±Y'dir; X yönündeki kameraya ince kenar bakar | Tag'i dikey eksende 90° döndürün (`pose`'daki yaw=1.5708) | [05](./05-apriltag-ile-konum-tespiti) |
| AprilTag 3D mesafe ölçümü %25 hatalı (büyük) çıkıyor | YAML `size`, dış levha değil 8x8 siyah kare boyutu olmalıdır | 0.30 m levha için `size: 0.24` parametresini kullanın | [05](./05-apriltag-ile-konum-tespiti) |
| Tag görüşten çıktığı halde robot hareket etmeye devam ediyor | `lookup_transform(..., Time())` zaman aşımı kontrolü olmadan son kaydı döner | TF zaman damgası yaşını (`now - stamp > 0.5s`) denetleyip robotu durdurun | [05](./05-apriltag-ile-konum-tespiti) |
| `mavproxy.py: command not found` | `~/.local/bin` PATH'e ekli değil | `export PATH="$PATH:$HOME/.local/bin"` ekleyip `source ~/.bashrc` | [06](./06-mavros-ardupilot-entegrasyonu) |
| ArduPilot robot döndükten sonra yanlış yöne gidiyor | Gazebo gövde FLU kullanırken MAVROS varsayılanı LOCAL_NED kullanıyor | MAVROS parametrelerinde `BODY_NED` kullanın veya açık frame dönüşümü yapın | [06](./06-mavros-ardupilot-entegrasyonu) |
| Gazebo/Rockwall dokusu hiç görünmedi / materyal çalışmıyor | Materyal ismi var sanılıp doğrulanmadan kullanılmış, texture eksik/bozuk | `awk`/`grep` ile gazebo.material script'inde texture_unit kontrolü yapın | [07](./07-cok-kamera-mimarisi-ve-parkur) |
| Periyodik doku (CeilingTiled) stereo eşleştirmeyi bozuyor | Tekrarlayan kare desen stereo eşleştirmede çoklu yanlış eşleşmeye yol açıyor | Organik/düzensiz doku (Grass gibi) tercih edin | [07](./07-cok-kamera-mimarisi-ve-parkur), [08](./08-stereo-derinlik-point-cloud) |
| SLAM haritası hep boş kaldı, Message Filter dropping uyarısı | Robotta URDF/robot_state_publisher yok, sensör TF ağacında yok | `static_transform_publisher` ile sensör TF'lerini yayınlayın | [09](./09-2d-slam) |
| TF var ama SLAM haritası hâlâ boş | slam_toolbox varsayılan base_frame: base_footprint arıyor, robotta base_link var | `slam_params.yaml` içinde `base_frame: base_link` tanımlayın | [09](./09-2d-slam) |
| OctoMap point cloud havada/saçılmış görünüyor | Kamera optik kuralı (Z=derinlik) ile ROS gövde kuralı (X=ileri) aynı frame'de karıştırılmış | Sadece rotasyon farkı olan `camera_optical_frame` TF'i ekleyin | [10](./10-3d-haritalama-octomap) |
| OctoMap'te "hayalet duvarlar" ve voxel kaymaları | OctoMap loop-closure'da ani sıçrama yapabilen 'map' frame'ine bağlı | OctoMap'i sürekli/kaymasız 'odom' frame'ine bağlayın | [10](./10-3d-haritalama-octomap) |
| WSL2'de FastDDS / ROS 2 mesajlaşma kilitlenmeleri | FastDDS alt seviye taşıma/multicast sorunları | `export FASTDDS_BUILTIN_TRANSPORTS=UDPv4` ortam değişkenini ekleyin | [10](./10-3d-haritalama-octomap) |
| Rampa robota "görünmez duvar" gibi çarpıyor | Kutu merkezinden döndürülünce giriş ucu zeminden ~30cm yukarıda kaldı | Giriş ucu tam zemin seviyesinde olacak şekilde merkez ve pitch açısını yeniden hesaplayın | [11](./11-denge-ve-fizik-duzeltmeleri) |
| Robot hızlanırken öne yalpalayıp kamera yere bakıyor | Tek arka caster, önde hiç destek noktası yok (cantilever yük) | Öne 2 yeni serbest destek tekeri (front caster) ekleyin (5 nokta temas) | [11](./11-denge-ve-fizik-duzeltmeleri) |

---

## Sistematik Hata Teşhis Rehberi (Belirti → Kontrol → Neden → Çözüm)

### 1. `Message Filter [target: ...] dropping message` Uyarısı
Bu uyarı tek bir nedene bağlı değildir; aşağıdaki 4 kontrolü sırayla yapın:
1. **TF Eksikliği:**
   - *Kontrol:* `ros2 run tf2_tools view_frames` veya `ros2 run tf2_ros tf2_echo odom <sensor_frame>`
   - *Beklenen Çıktı:* TF ağacının `map -> odom -> base_link -> sensor_frame` şeklinde kesintisiz bağlanması.
   - *Çözüm:* Eksik bağlantıyı `static_transform_publisher` ile tamamlayın ([Modül 9](./09-2d-slam)).
2. **Simülasyon Zamanı Uyuşmazlığı (`use_sim_time`):**
   - *Kontrol:* Node veya launch parametrelerinde `use_sim_time` değerini inceleyin.
   - *Beklenen:* Gazebo çalışırken tüm ROS node'ları simülasyon zamanını (`/clock`) kullanmalıdır (`use_sim_time:=true`). Biri sistem saatini, diğeri simülasyon saatini kullanırsa mesajlar zaman aşımından düşer.
3. **QoS (Quality of Service) Uyuşmazlığı:**
   - *Kontrol:* `ros2 topic info /scan --verbose`
   - *Neden:* Gazebo sensör plugin'i `Best Effort` yayınlarken alıcı node `Reliable` bekliyorsa iletişim kurulamaz.
4. **İşlem Başlama Sırası:**
   - *Neden:* TF yayıncısı sensörden 1-2 saniye geç başlarsa ilk paketler düşer; kalıcı launch dosyasında TF yayıncılarını en başta başlatın ([Modül 10](./10-3d-haritalama-octomap)).

---

### 2. Gazebo XML / SDF Dosyalarında `Error document empty` Hatası
- **Belirti:** `[gzserver] Error [parser.cc:403] Error parsing XML ... Error document empty.`
- **Kontrol Komutu:**
  ```bash
  file <dosya_adi>
  ```
- **Beklenen Çıktı:** `XML 1.0 document, Unicode text, UTF-8 text`
- **Hatalı Çıktı:** `XML 1.0 document, Unicode text, UTF-16, little-endian text`
- **Olası Neden:** Windows PowerShell'de `cat ... > dosya.world` yönlendirmesi varsayılan olarak UTF-16LE kodlaması üretir. Gazebo'nun C++ tabanlı XML ayrıştırıcısı (TinyXML) UTF-16 desteklemez ve dosyayı boş görür.
- **Çözüm:** Dosyayı UTF-8 formatında kaydedin veya WSL içinde doğrudan kopyalayın (`cp kaynak hedef`).

---

### 3. Lidar Dizi İndeksi Yanılgısı (Ön Sektör vs Arka Sektör)
- **Belirti:** Robot önünde 30 cm mesafede engel varken durmayıp çarpar; arkasına engel konulduğunda durup döner.
- **Kontrol Komutu:**
  ```bash
  ros2 topic echo /scan --field angle_min
  ros2 topic echo /scan --field angle_max
  ```
- **Beklenen Çıktı:** `angle_min: -3.14159`, `angle_max: 3.14159`.
- **Olası Neden:** Gazebo Lidar sensörü $-\pi$ ile $+\pi$ arasında tarama yapar. Dizi indeksi 0 ve -1 robotun tam arkasını temsil eder. Sabit `ranges[0:15]` seçimi robotun arkasını kontrol eder.
- **Çözüm:** Açıyı dinamik hesaplayın: `angle = angle_min + i * angle_increment`. Yalnızca `abs(angle) <= math.radians(15.0)` şartını sağlayan ışınları değerlendirin ([Modül 3](./03-engelden-kacma-algoritmasi)).

---

### 4. AprilTag Boyutu ve Pose Derinlik Hatası (Quiet Zone Payı)
- **Belirti:** Robot AprilTag'den 1.0 m uzakta durması gerekirken 1.25 m uzakta duruyor (%25 derinlik sapması).
- **Kontrol Komutu:** `cat apriltag_config.yaml | grep size`
- **Olası Neden:** 10x10 piksel tag36h11 dokusunda dıştaki 1'er piksel beyaz kenar payıdır (quiet zone). AprilTag algoritmasının `size` parametresi dış levhanın değil, algılanan 8x8 siyah kare köşelerinin fiziksel genişliğini bekler.
- **Çözüm:** 0.30 m levha için etkin boyutu $(8/10) \times 0.30\text{ m} = 0.24\text{ m}$ olarak ayarlayın ([Modül 5](./05-apriltag-ile-konum-tespiti)).

---

### 5. AprilTag / TF Yaş Kontrolü (Stale Transform)
- **Belirti:** AprilTag kameranın görüş açısından çıktığı halde robot dönmeye veya son komutla gitmeye devam eder.
- **Kontrol Komutu:** `transform.header.stamp` ile `node.get_clock().now()` arasındaki farkı inceleyin.
- **Olası Neden:** `lookup_transform(..., Time())` fonksiyonu zaman aşımı belirtilmediğinde buffer'daki son geçerli dönüşümü döndürür.
- **Çözüm:** Dönüşüm zaman damgası mevcut zamandan 0.5 saniyeden eskiyse tag kayboldu kabul edilip robot durdurulmalıdır ([Modül 5](./05-apriltag-ile-konum-tespiti)).

---

## Genel Kalıp: Terminal Kopyala-Yapıştır Sorunları

Bu depodaki komutların büyük çoğunluğu, uzun/çok satırlı içerik terminale yapıştırılırken satırların birleşmesi ya da kesilmesi sorunuyla en az bir kez karşılaştı. En güvenilir yöntemler, önem sırasına göre:

1. **`printf '%s\n' 'satır1' 'satır2' ... > dosya`** — kısa, tek satırlık içerikler için en güvenli.
2. **`cat > dosya << 'EOF' ... EOF` (heredoc)** — uzun, çok satırlı kod/config dosyaları için.
3. Herhangi bir dosya oluşturduktan sonra her zaman `wc -l dosya` ile satır sayısını ya da `file dosya` ile kodlamasını doğrulayın.
