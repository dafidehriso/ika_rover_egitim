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

## Genel Kalıp: Terminal Kopyala-Yapıştır Sorunları

Bu depodaki komutların büyük çoğunluğu, uzun/çok satırlı içerik terminale yapıştırılırken satırların birleşmesi ya da kesilmesi sorunuyla en az bir kez karşılaştı. En güvenilir yöntemler, önem sırasına göre:

1. **`printf '%s\n' 'satır1' 'satır2' ... > dosya`** — kısa, tek satırlık içerikler için en güvenli.
2. **`cat > dosya << 'EOF' ... EOF` (heredoc)** — uzun, çok satırlı kod/config dosyaları için, ama yapıştırma sırasında terminal satırları birleştirebiliyor; sorun yaşarsanız komutu küçük parçalara bölün.
3. **`nano`** — en son çare, çünkü kopyala-yapıştırda özel karakterlerde (`<`, `>`) sorun çıkarabiliyor.

Herhangi bir dosya oluşturduktan sonra **her zaman** `wc -l dosya` ile satır sayısını ya da `cat dosya` ile içeriği doğrulayın — sessizce yarım kalmış bir dosya, ileride anlaşılması çok daha zor hatalara yol açar.
