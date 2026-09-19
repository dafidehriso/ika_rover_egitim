# Modül 1: WSL2 + ROS 2 + Gazebo Kurulumu

> 🌐 **Dil / Language:** **Türkçe** | [English Version (README_EN.md)](README_EN.md)

## Neden WSL2, Neden Docker Değil?

Gazebo gibi bir 3D simülatör **GUI (grafik arayüzü)** gerektirir. Docker container'ların kendi ekranı olmadığı için GUI göstermek üzere ekstra bir X server (VcXsrv gibi) kurup karmaşık ayarlar yapmanız gerekir.

Windows 11'de bunun çok daha basit bir çözümü var: **WSL2 + WSLg**. WSLg, Windows 11'e gömülü bir özellik olduğu için Linux GUI uygulamaları hiçbir ekstra ayara gerek kalmadan doğrudan Windows masaüstünüzde bir pencere olarak açılır.

## Adım 1: WSL2 + Ubuntu Kurulumu

PowerShell'i **yönetici olarak** açıp:

```powershell
wsl --install -d Ubuntu-22.04
```

**Neden Ubuntu 22.04 (Jammy)?** ROS 2 Humble bu sürümü resmi olarak destekliyor. Farklı bir kombinasyon, ilerde bulunması zor bağımlılık sorunlarına yol açar.

### 🐛 Hata: "Sorry, passwords do not match"

Şifre yazarken **ekranda hiçbir karakter görünmez** (yıldız bile çıkmaz) — bu Linux terminallerinin standart davranışı, güvenlik amaçlı. Görmediğiniz için yazım hatası yapmak kolaylaşıyor.

**Çözüm:** Yavaşça, harfleri tek tek düşünerek yazın. Hâlâ eşleşmiyorsa, Windows PowerShell'den root olarak girip sıfırlayın:

```powershell
wsl -d Ubuntu-22.04 -u root
```

İçeride: `passwd <kullanici_adiniz>`

### 🐛 Hata: `.bashrc` İçinde Syntax Error

PATH değişkenine yeni yollar eklerken şu hatayla karşılaşabilirsiniz:

```
-bash: /home/kullanici/.bashrc: line 123: syntax error near unexpected token `('
```

**Neden oluyor?** WSL, Windows'un PATH değişkenini otomatik olarak Linux'a da aktarır. Bu yollar arasında `Program Files (x86)` gibi **boşluk ve parantez içeren** Windows klasör adları vardır. Bu karakterler tırnaksız yazılınca bash hata verir.

**Çözüm:** PATH'e her ekleme yaparken mutlaka tırnak kullanın:

```bash
export PATH="$PATH:$HOME/ardupilot/Tools/autotest:$HOME/.local/bin"
```

## Adım 2: ROS 2 Humble Kurulumu

```bash
# Locale (dil/karakter seti) ayarı - ROS UTF-8 bekliyor
sudo apt update && sudo apt install locales -y
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8

# Universe repo'sunu etkinleştir
sudo apt install software-properties-common -y
sudo add-apt-repository universe

# ROS 2'nin GPG anahtarını ekle
sudo apt install curl -y
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg

# ROS 2 paket kaynağını tanıt
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# Kurulum
sudo apt update && sudo apt install ros-humble-desktop -y

# Her terminalde otomatik yükle
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### Doğrulama

```bash
printenv ROS_DISTRO   # "humble" yazmalı
```

İki terminalde klasik test:

```bash
# Terminal 1
ros2 run demo_nodes_cpp talker

# Terminal 2
ros2 run demo_nodes_py listener
```

Talker'ın gönderdiği sayılar listener'da görünüyorsa kurulum sağlıklıdır.

## Adım 3: Gazebo Kurulumu

```bash
sudo apt install ros-humble-gazebo-ros-pkgs -y
gazebo
```

WSLg sayesinde pencere ekstra ayar gerekmeden açılmalı.

### 🐛 Hata: `colcon: command not found`

Kod paketlerini derlemek için kullanılan `colcon` aracı desktop kurulumuyla otomatik gelmiyor.

```bash
sudo apt install python3-colcon-common-extensions -y
```

### ⚠️ Simülatör Sürümü ve Gazebo Classic EOL Bilgisi
Bu eğitim serisinde **Gazebo Classic 11.10.2** (`gazebo_ros_pkgs`) kullanılmaktadır.
- Gazebo Classic, resmi olarak Ocak 2025'te kullanım ömrünün sonuna (End-of-Life / EOL) ulaşmıştır.
- Mevcut robotik ekosisteminde (özellikle üniversite ve yarışma projelerinde) Gazebo Classic SDF modelleri yaygın olarak kullanılmaya devam etmektedir. Bu kurs, denenmiş ve çalışan Gazebo Classic 11 mimarisini temel alır.
- Yeni projelere başlarken modern Gazebo'ya (eski adıyla Ignition / Gz Sim) geçiş önerilir; bu geçiş kursun ayrı bir yol haritası olarak değerlendirilebilir.

## Genel Dersler (Bu Modülden)

- **`.bashrc` değişiklikleri otomatik olarak mevcut shell'e uygulanmaz** — dosyadaki değişikliklerin geçerli olması için her seferinde `source ~/.bashrc` çalıştırmanız ya da yeni bir terminal açmanız gerekir.
- Klavye girdisi her zaman **odaktaki pencereye** gider — hangi terminalin komutu aldığını takip edin.
- WSL2'de ilk açılışlar (özellikle Gazebo) beklenenden yavaş olabilir.

## Sırada

[Modül 2: Kendi Robotunuzu Tasarlayın](../02-kendi-robotunuzu-tasarlayin) — TurtleBot3 gibi hazır bir modelle test ettikten sonra, sıfırdan kendi robot modelinizi (SDF formatında) inşa edeceğiz.
