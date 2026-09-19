# Modül 6: MAVROS + ArduPilot Entegrasyonu

## Neden Bu Modül?

Gerçek bir Pixhawk tabanlı İKA'da (İnsansız Kara Aracı) mimari iki ana katmandan oluşur:

- **Pixhawk (Uçuş/Araç Kontrolcüsü):** ArduPilot (Rover) firmware'i çalıştırır. Tekerlek motor sürücüleri, PWM çıkışları, dahili IMU ve düşük seviye PID hız kontrolünü yönetir.
- **Companion Computer (Görev Bilgisayarı):** Raspberry Pi veya NVIDIA Jetson gibi, ROS 2 çalıştıran üst seviye bilgisayardır. Lidar ve kameraları işler, haritalama yapar ve "şu yöne git" komutunu üretir.

Bu iki sistem birbirleriyle seri port üzerinden **MAVLink** protokolüyle konuşur; ROS 2 dünyası ile MAVLink arasındaki köprüyü ise **MAVROS** paketi kurar. Bu modülde, Pixhawk'ı fiziksel donanım olmadan **SITL (Software-In-The-Loop)** simülasyonuyla çalıştırıp, ROS 2 tarafındaki node'umuzun MAVLink üzerinden ArduPilot'a nasıl komut ilettiğini deneyimliyoruz.

---

## ⚠️ Kritik Mimari ve Koordinat Çerçevesi Analizi

### 1. Deneyin Kapsamı: "MAVLink Komut İletimi Gösterimi"
Bu modülde kurulan yapı, **MAVLink komut iletimi gösterimidir**. Ortak bir fizik simülasyonu veya kapalı döngü (closed-loop) donanım simülasyonu değildir:
- Gazebo ve ArduPilot SITL **ayrı iki süreç** olarak çalışır.
- `avoider.py` node'u, Gazebo'daki lidar verisine bakarak karar üretir ve bu komutu hem Gazebo diff_drive eklentisine hem de MAVROS topic'ine gönderir.
- Pixhawk simülasyonu Gazebo'daki engelleri doğrudan hissetmez; companion computer'dan gelen hız vektörünü MAVLink üzerinden alıp kendi iç durumunda uygular.

### 2. Koordinat ve Frame Farkı (Gövde FLU vs Yerel NED/ENU)
- **Gazebo `/cmd_vel`:** Doğrudan robotun gövde çerçevesinde (`base_link` - FLU: Forward, Left, Up) yorumlanır. `linear.x = 1.0` daima robotun burnunun baktığı yönde ileri git demektir.
- **MAVROS `/mavros/setpoint_velocity/cmd_vel_unstamped`:**
  - MAVROS `apm_config.yaml` dosyasında `setpoint_velocity.mav_frame` varsayılan olarak **`LOCAL_NED`** (North-East-Down) kullanır. ROS tarafındaki hızları yerel harita koordinatlarına (ENU) göre yorumlar.
  - Eğer robot 90° dönmüşse (örneğin Doğuya bakıyorsa), gövdeye göre "ileri" ($X_{\text{body}}$) komutu ile haritaya göre "Kuzey" ($X_{\text{local}}$) komutu farklı yönleri ifade eder!
  - **Doğru Yapılandırma:** Robotun baktığı yönde ilerlemesi için komutların **Gövde Çerçevesinde (BODY_NED / BODY_OFFSET_NED)** gönderilmesi veya MAVROS konfigürasyonunda `mav_frame: BODY_NED` seçilmesi gerekir.

---

## Adım 1: ArduPilot Rover SITL Kurulumu

Kara araçları (UGV) için ArduPilot'un Rover yazılımı olgun bir diferansiyel sürüş desteğine sahiptir.

```bash
cd ~
git clone https://github.com/ArduPilot/ardupilot.git
cd ardupilot
git submodule update --init --recursive
Tools/environment_install/install-prereqs-ubuntu.sh -y
```

SITL'i başlatın:

```bash
cd ~/ardupilot
sim_vehicle.py -v Rover --console --map
```

### 🐛 Hata Teşhisi: `sim_vehicle.py` veya `mavproxy.py` Bulunamadı
- Kurulum script'i PATH'e ekleme yapar ancak mevcut shell hemen görmez: `source ~/.bashrc` çalıştırın.
- `mavproxy.py: command not found` durumunda:
  ```bash
  pip3 install MAVProxy
  echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.bashrc
  source ~/.bashrc
  ```

---

## Adım 2: MAVROS Kurulumu ve Bağlantı

```bash
sudo apt install ros-humble-mavros ros-humble-mavros-extras -y
sudo bash /opt/ros/humble/lib/mavros/install_geographiclib_datasets.sh
```

SITL çalışırken MAVROS'u APM yapılandırmasıyla başlatın:

```bash
ros2 launch mavros apm.launch fcu_url:=tcp://127.0.0.1:5762@
```

Bağlantıyı doğrulayın:

```bash
ros2 topic echo /mavros/state
```

- **`connected: true`** — MAVROS, SITL'den MAVLink heartbeat paketlerini başarıyla alıyor.

---

## Adım 3: Aracı GUIDED Moduna Alma, Arm Etme ve Sürüş

ArduPilot güvenlik mekanizmaları gereği, dışarıdan gelen hız komutlarını yalnızca araç **GUIDED** modundayken ve **ARM** edilmişken kabul eder:

```bash
# 1. Modu GUIDED yap
ros2 service call /mavros/set_mode mavros_msgs/srv/SetMode "{custom_mode: 'GUIDED'}"

# 2. Motorları ARM et (güvenlik kilidini aç)
ros2 service call /mavros/cmd/arming mavros_msgs/srv/CommandBool "{value: true}"

# 3. Hız komutu gönder (10 Hz düzenli akış)
ros2 topic pub /mavros/setpoint_velocity/cmd_vel_unstamped geometry_msgs/msg/Twist "{linear: {x: 1.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}" -r 10
```

MAVProxy konsolunda ve harita penceresinde aracın konumunun ve yer hızının değiştiği gözlemlenmelidir.

---

## Modül 3'teki Engelden Kaçma Node'u ile Birlikte Çalışma

[`03-engelden-kacma-algoritmasi/avoider.py`](../03-engelden-kacma-algoritmasi/avoider.py) dosyasında hem Gazebo (`/cmd_vel`) hem de MAVROS (`/mavros/setpoint_velocity/cmd_vel_unstamped`) publisher'ları mevcuttur.
Bu sayede Gazebo'da robot bir engelle karşılaşıp dönüş kararı aldığında, companion computer bu manevra niyetini eşzamanlı olarak Pixhawk kontrolcüsüne de aktarır.

---

## Aşama Değerlendirmesi ve İleri Modüllere Geçiş

Bu 6 modülü tamamladıysanız; temel simülasyon kurulumu, SDF robot tasarımı, lidar ile engelden kaçma, OpenCV görüntü işleme, AprilTag ile bağıl konumlandırma ve MAVLink köprüsünü başarıyla tamamlamış oldunuz.

Bundan sonraki modüllerde robotun algı ve navigasyon kabiliyetleri bir üst seviyeye taşınacaktır:
- **Modül 7:** Çoklu kamera mimarisi ve döngü kapanmalı (loop-closure) test parkuru
- **Modül 8:** Stereo disparity derinlik hesabı ve nokta bulutu
- **Modül 9:** 2D SLAM (`slam_toolbox`) ve kapalı döngü haritalama
- **Modül 10:** 3D Hacimsel Haritalama (OctoMap) ve Optik TF ayrımı
- **Modül 11:** Çok temaslı fizik dengelemesi ve rampa geometrisi

## Sırada
[Modül 7: Çoklu Kamera Mimarisi ve Gerçekçi Test Parkuru](../07-cok-kamera-mimarisi-ve-parkur)
