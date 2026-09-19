# Modül 7: Çoklu Kamera Mimarisi ve Gerçekçi Test Parkuru

## Öğrenme Hedefleri
1. Tek kameralı robot modelini 5 kameralı çevre görüş mimarisine (stereo çift + yan/arka mono kameralar) genişletmek.
2. SLAM'de döngü kapanması (loop closure) testi yapabilecek kapalı koridor parkurunu Gazebo materyalleriyle inşa etmek.
3. Gazebo materyal ve dokularını kullanmadan önce sistemde doğrulamayı öğrenmek.
4. `teleop_twist_keyboard` ile robotu klavyeden manuel sürmek.

## Modül Dosyaları
- [`model.sdf`](./model.sdf): 5 kameralı İKA Rover SDF modeli.
- [`model.config`](./model.config): Model metaveri dosyası.
- [`parkur.world`](./parkur.world): 4 kollu kapalı koridor parkuru.

---

## Konsept: Bir Kamera Nasıl "Var Olur"?
Gazebo'da bir kamera 4 parçadan oluşur:
1. `<joint>` — kameranın `base_link`'e sabit bağlantısı (`type="fixed"`)
2. `<link>` — fiziksel montaj konumu (`pose: x y z roll pitch yaw`)
3. `<sensor type="camera">` — görüş açısı (FOV), çözünürlük, güncelleme frekansı
4. `<plugin libgazebo_ros_camera.so>` — Gazebo optik motorunu ROS topic'lerine bağlayan köprü

**ROS Yön Kuralı (REP-103):**
- $X$ = İleri, $Y$ = Sol, $Z$ = Yukarı
- $yaw = -1.5708\text{ rad} (-90^\circ)$ sağa bakar
- $yaw = +1.5708\text{ rad} (+90^\circ)$ sola bakar
- $yaw = 3.14159\text{ rad} (180^\circ)$ geriye bakar

---

## 5 Kameralı Çevre Görüş Mimarisi
[Modül 2](../02-kendi-robotunuzu-tasarlayin)'deki tek kameralı model 5 kameraya çıkarıldı ([`model.sdf`](./model.sdf)):
- `camera_link` (0.3, 0, 0.2): Ön-sol ana kamera
- `right_camera_link` (0.3, -0.12, 0.2): Ön-sağ kamera (Sol kameradan 12 cm sağda, **STEREO ÇİFT** oluşturur, baseline=0.12m; Modül 8'de kullanılacak)
- `side_right_camera_link` (0, -0.25, 0.2, yaw=-1.5708): Sağa bakan mono
- `side_left_camera_link` (0, 0.25, 0.2, yaw=1.5708): Sola bakan mono
- `rear_camera_link` (-0.3, 0, 0.2, yaw=3.14159): Geriye bakan mono

Tüm kameralar `/ika_rover/...` namespace'i altında yayın yapar.

---

## Gerçekçi Test Parkuru ([`parkur.world`](./parkur.world))
Düz zemin yerine, kapalı DÖNGÜ şeklinde 4 duvar kolu (leg1-leg2-leg3-leg4, 90° dönerek birleşen dörtgen koridor) inşa edildi.
- **Amaç:** İleride SLAM'ın "loop closure" (döngü kapanması) özelliğini test edebilmek — açık bir düzlükte döngü kapanması test edilemez.
- **Kullanılan Materyaller:** `Gazebo/Grass` (zemin), `Gazebo/Bricks`, `Gazebo/PaintedWall`, `Gazebo/Wood`.

### 🐛 HATA: `Gazebo/Rockwall` Dokusu Görünmedi
- **Sebep:** Materyal ismi var sanılıp doğrulanmadan kullanılmıştı; ancak arkasındaki texture dosyası Gazebo kurulumunda eksikti.
- **Çözüm:** Bir materyali kullanmadan önce `gazebo.material` dosyasında `texture_unit` tanımının gerçekten var olduğunu doğrulayın:
  ```bash
  awk '/^material Gazebo\// {name=$0} /texture (wood|bricks|grass)\.(jpg|png)/ {print name, "->", $0}' /usr/share/gazebo-11/media/materials/scripts/gazebo.material
  ```

### 🐛 HATA: Periyodik Doku (CeilingTiled) Stereo Eşleştirmeyi Bozdu
Tekrarlayan kare/fayans desenli dokular, Modül 8'deki stereo eşleştirmede (StereoSGBM) desen kendini tekrarladığı için çoklu yanlış eşleşmeye ve gürültüye yol açar. Zeminde organik ve düzensiz doku (`Gazebo/Grass`) tercih edilmelidir.

---

## Klavye ile Manuel Sürüş (`teleop_twist_keyboard`)
Robotu `ros2 topic pub` yerine gerçek zamanlı klavye ile sürmek için `teleop_twist_keyboard` paketi kullanılır:

```bash
sudo apt install ros-humble-teleop-twist-keyboard -y
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

### ⌨️ Tuş Haritası (Standart teleop tuşları):
- **Hareket:**
  - `i` : İleri
  - `,` : Geri
  - `j` : Sola dön (yerinde)
  - `l` : Sağa dön (yerinde)
  - `u` / `o` : İleri sol / İleri sağ kavis
  - `m` / `.` : Geri sol / Geri sağ kavis
  - `k` veya `Boşluk` : Acil durdurma
- **Hız Ayarları:**
  - `w` / `x` : Doğrusal hızı %10 artır / azalt
  - `e` / `c` : Açısal hızı %10 artır / azalt

*(Not: Bu araç klasik WASD düzeni değil, yukarıdaki numerik/harf tuş haritasını kullanır).*

---

## Adım Adım Çalıştırma ve Doğrulama

1. **Parkuru Başlatın:**
   ```bash
   gazebo --verbose 07-cok-kamera-mimarisi-ve-parkur/parkur.world
   ```
2. **Kamera Topic'lerini Doğrulayın:**
   ```bash
   ros2 topic list | grep camera
   ```
   *Beklenen çıktı:* 5 kameranın her biri için `image_raw`, `camera_info` topic'lerinin listelenmesi.
3. **Teleop ile Sürün:**
   Ayrı bir terminalde `teleop_twist_keyboard` çalıştırıp robotu koridorda gezdirin.

## Sırada
[Modül 8: Stereo Derinlik ve Point Cloud](../08-stereo-derinlik-point-cloud)
