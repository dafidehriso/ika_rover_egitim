# Modül 11: Denge ve Fizik Düzeltmeleri

## Durum: KISMEN TAMAMLANDI — rampa düzeltmesi son haliyle DOĞRULANMADI, bunu
dürüstçe böyle belirt, "tamamlandı" deme.

## Sorun 1: Robot Hızlanırken/Dönerken Öne Yalpalıyor, Kamera Aşağı Bakıyor
Kök neden: Orijinal tasarımda tek bir denge küresi (caster_wheel) SADECE
ARKADA (x=-0.2) vardı. Kameralar önde (x=0.3). Önde HİÇ destek noktası
olmadığı için, o bölge havada asılı (cantilever) duruyordu, hızlanınca öne
sarkıyordu.

Değerlendirilen ama TERCİH EDİLMEYEN çözüm: Tam 4 tekerlekli tahrike (4WD/
skid-steer) geçmek — gereksiz karmaşıklık, farklı bir Gazebo plugin'i ve
kinematik hesap gerektirir.

Uygulanan çözüm: Mevcut 2 tahrikli tekerlek + diff_drive mantığı aynı
kalarak, öne 2 yeni destek küresi eklendi (front_caster_left/right, x=0.35,
y=±0.15, kamera bölgesinin altında). Robot artık 5 noktadan temas ediyor
(2 tahrik + 1 arka + 2 ön caster).

## Sorun 2: Rampa Robota "Görünmez Duvar" Gibi Çarpıyordu
Kök neden: Rampa bir kutuyu MERKEZİNDEN pitch açısıyla döndürerek yapılmıştı.
Bir kutuyu merkezinden döndürünce iki ucu ZIT yönlerde yükselir/alçalır —
ilk denemede rampanın robotun GİRDİĞİ ucu zeminden ~30cm YUKARIDA kalıyordu,
yani robot rampaya "tırmanmıyor", ona çarpıyordu.

İlk düzeltme denemesi (pitch işaretini ters çevirmek) sorunu ÇÖZMEDİ, sadece
hangi ucun havada kaldığını değiştirdi.

Matematiksel analiz yapıldı: rampa merkezi ve pitch açısı kullanılarak her iki
ucun gerçek zemin yüksekliği hesaplandı. Sonuç: açı daha ölçülü (~8.6°'den
~3.4°'ye) düşürülüp, merkez pozisyonu giriş ucu TAM ZEMİN SEVİYESİNDE
oturacak şekilde yeniden hesaplandı (pose: 2.5 0 0.03 0 -0.06 0). Ayrıca
tekerlek yarıçapı (10cm) ile rampanın çıkış ucundaki basamak yüksekliği
kıyaslanıp, yeni açının bu basamağı ~12cm'ye indirdiği (yönetilebilir bir
fark) doğrulandı.

DURUM: Bu matematiksel düzeltme world dosyasına uygulandı ve build edildi
ama robotun gerçek sürüşle rampadan pürüzsüz geçtiği HENÜZ GÖRSEL OLARAK
DOĞRULANMADI. Bir sonraki oturumda bu doğrulanmalı.

## Sırada
Modül 12: Otonom Keşif ve Navigasyon (Nav2 + explore_lite) — henüz başlanmadı
