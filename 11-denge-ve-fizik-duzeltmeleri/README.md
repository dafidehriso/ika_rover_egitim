# Modül 11: Denge ve Fizik Düzeltmeleri

## Durum: KISMEN TAMAMLANDI
Ön caster denge düzeltmesi tamamlandı ve test edildi. Rampa matematiksel geometrisi hesaplanarak world dosyasına işlendi; ancak robotun gerçek sürüşle rampadan pürüzsüz geçişi henüz görsel/fiziksel olarak doğrulanmamıştır (bir sonraki oturumda doğrulanacaktır).

---

## Sorun 1: Robot Hızlanırken/Dönerken Öne Yalpalıyor, Kamera Aşağı Bakıyor

### Kök Neden
Orijinal robot tasarımında ([Modül 2](../02-kendi-robotunuzu-tasarlayin)) tek bir denge küresi (`caster_wheel`) **sadece arkada** ($x = -0.2\text{ m}$) bulunuyordu.
Kameralar ve lidar ise gövdenin en ön ucunda ($x = +0.3\text{ m}$) yer alıyor. Ön bölgede hiçbir zemin destek noktası olmadığı için bu bölge bir konsol kiriş (cantilever) gibi havada asılı kalıyordu. Robot ivmelendiğinde veya dönerken oluşan tork etkisiyle şasi öne doğru eğiliyor, kameralar yere bakıyor ve haritalama geometrisi bozuluyordu.

### Değerlendirilen Alternatifler
- **4WD / Skid-Steer Tahrike Geçmek:** Reddedildi. 4 tekerleğin bağımsız tahriki farklı bir kinematik hesap, farklı bir Gazebo eklentisi ve dönüşlerde yüksek zemin sürtünmesi (skid slip) getirir; diferansiyel sürüşün basitliğini bozar.

### Uygulanan Çözüm: 5 Noktadan Zemin Teması
Diferansiyel sürüş mimarisi (2 tahrikli tekerlek) korunarak, ön kamera bölgesinin altına sağ ve sol olmak üzere 2 yeni serbest denge küresi eklendi:
- `front_caster_left`: pose `(0.35, 0.15, 0.05)`
- `front_caster_right`: pose `(0.35, -0.15, 0.05)`

Robot artık **5 noktadan** zeminle temas eder: 2 ana tahrik tekeri + 1 arka caster + 2 ön caster. Hızlanma ve dönüşlerdeki yalpalanma tamamen engellenmiştir.

---

## Sorun 2: Rampa Robota "Görünmez Duvar" Gibi Çarpıyordu

### Kök Neden: Gazebo Kutu Döndürme Geometrisi
Gazebo'da `<box>` geometrileri **kendi ağırlık merkezlerinden (origin)** döndürülür.
Bir rampayı merkezinden pitch açısıyla döndürdüğünüzde, geometrinin iki ucu zıt yönlerde yükselir ve alçalır.
- İlk denemede rampa kutusunun robotun girdiği ucu zeminden yaklaşık **30 cm yukarıda** havada kalmıştı. Robot rampaya tırmanamıyor, kutunun dikey yan yüzeyine bir duvara çarpar gibi çarpıp duruyordu.
- Pitch açısının işaretini ters çevirmek sorunu çözmedi; yalnızca hangi ucun havada kaldığını tersine çevirdi.

### Matematiksel Analiz ve Geometrik Çözüm
Rampa üst yüzey uç noktalarının yükseklik formülü ([`rampa_hesapla.py`](./rampa_hesapla.py)):

$$z_{\text{giriş\_üst}} = z_{\text{merkez}} - \frac{L}{2} \sin(-\theta) + \frac{t}{2} \cos(\theta)$$
$$z_{\text{çıkış\_üst}} = z_{\text{merkez}} + \frac{L}{2} \sin(-\theta) + \frac{t}{2} \cos(\theta)$$

Parametreler:
- Uzunluk: $L = 2.0\text{ m}$, Kalınlık: $t = 0.06\text{ m}$
- Eğim açısı: $\theta = -0.06\text{ rad} \approx -3.44^\circ$
- Merkez konumu: $x = 2.5\text{ m}$, $z = 0.03\text{ m}$

Hesaplanan Değerler:
- **Giriş ucu üst yüzeyi:** $z \approx 0.00\text{ cm}$ (Giriş ucu tam zemin seviyesine oturtuldu, basamak sıfırlandı).
- **Çıkış ucu üst yüzeyi:** $z \approx 11.99\text{ cm}$.

```bash
# Matematiksel doğrulamayı çalıştırmak için:
python3 11-denge-ve-fizik-duzeltmeleri/rampa_hesapla.py
```

### ⚠️ Doğrulama Sınırları ve Açık Kalan Test
Giriş ucunun zeminle sıfır kotunda buluşması matematiksel olarak doğrulanmıştır. Ancak 12 cm'lik çıkış kotunun aşılabilirliği; yalnızca tekerlek yarıçapı ($10\text{ cm}$) ile kıyaslanamaz:
- Aracın alt açıklığı (ground clearance)
- Caster tekerleklerin rampa kırılma kenarındaki teması
- Motor torku ve aracın ters yönde iniş/çıkış davranışları

Bu nedenle, bu matematiksel rampa modeli [`ika_rover.world`](./ika_rover.world) dosyasına işlenmiş olsa da, **fiziksel sürüş pürüzsüzlüğü henüz görsel olarak doğrulanmamıştır**. Bu test bir sonraki oturumda yapılacaktır.

---

## Modül Dosyaları
- [`model.sdf`](./model.sdf): 5 temas noktalı nihai rover modeli.
- [`ika_rover.world`](./ika_rover.world): Kapalı koridor + rampa + renkli kutulu tam parkur.
- [`rampa_hesapla.py`](./rampa_hesapla.py): Rampa uç yüksekliklerini hesaplayan doğrulama scripti.

## Sırada
Modül 12: Otonom Keşif ve Navigasyon (Nav2 + explore_lite)
