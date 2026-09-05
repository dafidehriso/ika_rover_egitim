# Modül 6: MAVROS + ArduPilot Entegrasyonu

## Neden Bu Modül?

Gerçek bir Pixhawk tabanlı İKA'da mimari şöyle çalışır:

- **Pixhawk** (ArduPilot çalıştıran mikrokontrolcü) — tekerlekleri döndüren motor kontrolcüsü, düşük seviye.
- **Companion computer** (bir Raspberry Pi/Jetson gibi, ROS çalıştıran bilgisayar) — lidar/kamera'yı okuyup "şu yöne git" kararını veren beyin, yüksek seviye.

Bu ikisi **MAVLink** protokolü üzerinden konuşur. Bu modülde, Pixhawk'ı gerçek donanım olmadan **SITL (Software-In-The-Loop)** ile simüle edip, ROS tarafımızın (Modül 3'teki `avoider.py`) ona nasıl komut gönderdiğini kuruyoruz.

## Dürüst Bir Not: Neden Gazebo'yu ArduPilot'a Doğrudan Bağlamadık

İlk denemede, ArduPilot'un Gazebo'daki robotu **doğrudan** sürmesini sağlayan bir köprü eklentisi (`ardupilot_gazebo`) kullanmayı denedik. Bu, Gazebo Classic (bizim kullandığımız, artık EOL olmuş sürüm) için yazılmış eski bir fork'ta, özel (TurtleBot3/iris olmayan) modellerde **bilinen, çözülmemiş bir hata** (`imu_sensor scoped name not found`) ile karşılaştık — hatta kütüphanenin kaynak kodunda geliştiricilerin bıraktığı `// TODO: this fails for multi-nested models` yorumunu bile bulduk.

Bu yaklaşımdan vazgeçip, daha pragmatik bir mimariye geçtik: **Gazebo (görsel/fiziksel simülasyon) ve ArduPilot SITL (Pixhawk simülasyonu) ayrı çalışıyor**, ama aynı ROS node'u ikisine de **aynı kararı** gönderiyor. Bu, "companion computer → MAVLink → Pixhawk" komut akışını gerçek anlamda kanıtlıyor — sadece fizik motoru ortak değil (ki gerçek donanımda zaten Gazebo diye bir şey olmayacak, bu detay önemsizleşiyor).

## Adım 1: ArduPilot Rover SITL Kurulumu

**Neden ArduPilot, PX4 değil?** Kara araçları (rover/UGV) için ArduPilot'un Rover firmware'i çok daha olgun, daha geniş dokümantasyona sahip.

```bash
cd ~
git clone https://github.com/ArduPilot/ardupilot.git
cd ardupilot
git submodule update --init --recursive
Tools/environment_install/install-prereqs-ubuntu.sh -y
```

```bash
cd ~/ardupilot
sim_vehicle.py -v Rover --console --map
```

### 🐛 Hata: `sim_vehicle.py: command not found`

Kurulum script'i PATH'e ekleme yapıyor ama bu değişikliğin etkili olması için terminali yenilemeniz gerekiyor: `source ~/.bashrc` ya da yeni bir terminal.

### 🐛 Hata: `mavproxy.py: command not found`

```bash
pip3 install MAVProxy
which mavproxy.py   # bir dosya yolu dönmeli
```

Boş dönerse `~/.local/bin` PATH'e eklenmemiş demektir:

```bash
echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.bashrc
source ~/.bashrc
```

İlk derleme ~1373 dosyayı derliyor, birkaç dakika sürebilir.

## Adım 2: MAVROS Kurulumu ve Bağlantı

```bash
sudo apt install ros-humble-mavros ros-humble-mavros-extras -y
sudo bash /opt/ros/humble/lib/mavros/install_geographiclib_datasets.sh
```

SITL çalışırken:

```bash
ros2 launch mavros apm.launch fcu_url:=tcp://127.0.0.1:5762@
```

Doğrulama:

```bash
ros2 topic echo /mavros/state
```

`connected: true` görmek, MAVROS'un SITL'den **heartbeat mesajını düzenli aldığının** kanıtı.

## Adım 3: Aracı Arm Edip Hareket Ettirme

```bash
# Modu GUIDED yap (dışarıdan komut almaya hazır hale getir)
ros2 service call /mavros/set_mode mavros_msgs/srv/SetMode "{custom_mode: 'GUIDED'}"

# Arm et (motorları aktif hale getir)
ros2 service call /mavros/cmd/arming mavros_msgs/srv/CommandBool "{value: true}"

# Hareket komutu gönder
ros2 topic pub /mavros/setpoint_velocity/cmd_vel_unstamped geometry_msgs/msg/Twist "{linear: {x: 1.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}" -r 10
```

MAVProxy'nin harita penceresinde aracın konumunun değiştiğini görmelisiniz.

## Modül 3'teki Kodu Bu Modülle Birleştirme

[Modül 3](../03-engelden-kacma-algoritmasi)'teki `avoider.py` zaten hem `/cmd_vel` (Gazebo) hem `/mavros/setpoint_velocity/cmd_vel_unstamped` (ArduPilot) topic'lerine yayın yapıyor. Bu modüldeki adımları tamamladıktan sonra `avoider.py`'ı çalıştırırsanız, robotun engelden kaçma kararının **aynı anda hem Gazebo'da hem MAVProxy haritasında** yansıdığını göreceksiniz.

## Genel Ders

Bu modül, projenin en çok "gerçek mühendislik kararı" gerektiren kısmıydı: bir teknolojinin (eski Gazebo Classic + ArduPilot köprüsü) beklendiği gibi çalışmadığını fark edip, daha pragmatik bir alternatife geçmek. Her teknik sorunun "doğru" çözümü, en son/en parlak yöntem değil, **elinizdeki zaman ve hedefe göre en uygun** çözüm olabilir.

## Kursun Sonu — Elinizde Ne Var

Bu 6 modülü tamamladıysanız, kendi tasarladığınız bir robotta: lidar tabanlı engelden kaçma, kamera tabanlı renk tespiti, AprilTag ile hassas navigasyon ve Pixhawk simülasyonuna komut gönderen tam bir otonom sistem kurmuş oldunuz — hepsi sıfırdan, Windows üzerinde.
