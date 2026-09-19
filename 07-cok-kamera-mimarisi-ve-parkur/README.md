# Modül 7: Çoklu Kamera Mimarisi ve Gerçekçi Test Parkuru

## Durum: TAMAMLANDI

## Konsept: Bir Kamera Nasıl "Var Olur"?
Gazebo'da bir kamera 4 parçadan oluşur:
1. `<joint>` — kameranın base_link'e sabit bağlantısı (type="fixed")
2. `<link>` — fiziksel konum (pose: x y z roll pitch yaw)
3. `<sensor type="camera">` — görüş açısı, çözünürlük, güncelleme hızı
4. `<plugin libgazebo_ros_camera.so>` — Gazebo görüntüsünü ROS topic'lerine köprüler

ROS yön kuralı (REP-103): X=ileri, Y=sol, Z=yukarı. yaw=-1.5708 sağa, yaw=1.5708 sola,
yaw=3.14159 geriye baktırır.

## Yapılan: 5 Kameralı Mimari
Önceki robotta (Modül 2) sadece 1 kamera vardı. Şimdi 5'e çıkarıldı:
- `camera_link` (0.3, 0, 0.2) — ön-sol, ana kamera
- `right_camera_link` (0.3, -0.12, 0.2) — ön-sağ, sol kameradan 12cm mesafede
  STEREO ÇİFT oluşturuyor (baseline=0.12m, Modül 8'de kullanılacak)
- `side_right_camera_link` (0, -0.25, 0.2, yaw=-1.5708) — sağa bakan mono
- `side_left_camera_link` (0, 0.25, 0.2, yaw=1.5708) — sola bakan mono
- `rear_camera_link` (-0.3, 0, 0.2, yaw=3.14159) — geriye bakan mono

Tüm 5 kameranın topic'leri `ros2 topic list | grep camera` ile doğrulandı, her biri
image_raw + camera_info + compressed/theora varyantlarıyla yayında.

## Gerçekçi Test Parkuru
Düz zemin + birkaç kutu yerine, kapalı DÖNGÜ şeklinde bir koridor inşa edildi
(4 duvar kolu: leg1-leg2-leg3-leg4, biri diğerine 90° dönerek birleşiyor, bir tarafı
giriş için açık bırakıldı). Amaç: ileride SLAM'ın "loop closure" (döngü kapanması)
özelliğini gerçek anlamda test edebilmek — açık bir düzlükte bu mümkün değil.

Materyaller: `Gazebo/Grass` (zemin), `Gazebo/Bricks`, `Gazebo/PaintedWall`,
`Gazebo/Wood`, `Gazebo/WoodFloor` (rampa).

### HATA: Gazebo/Rockwall dokusu hiç görünmedi
Sebep: materyal ismi var sanılıp doğrulanmadan kullanılmıştı ama arkasındaki
texture dosyası bu Gazebo kurulumunda eksik/bozuktu.
Çözüm: Bir materyali kullanmadan önce, gerçekten `gazebo.material` script
dosyasında `texture_unit` ile tanımlı olduğunu doğrula:
```bash
awk '/^material Gazebo\// {name=$0} /texture (wood|bricks|grass)\.(jpg|png)/ {print name, "->", $0}' /usr/share/gazebo-11/media/materials/scripts/gazebo.material
```

### HATA: Periyodik doku (CeilingTiled) stereo eşleştirmeyi bozdu
Tekrarlayan/kare desenli dokular, ileride stereo kamerada (Modül 8) çoklu yanlış
eşleşmeye yol açıyor çünkü desen kendini tekrarlıyor. Organik/düzensiz doku
(Grass gibi) tercih edilmeli.

## WASD Klavye Kontrolü
`ros-humble-teleop-twist-keyboard` paketiyle robot artık `ros2 topic pub` yerine
gerçek zamanlı klavye ile sürülebiliyor:
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

## Sırada
Modül 8: Stereo Derinlik ve Point Cloud
