#!/usr/bin/env python3
"""
Rampa Geometrisi ve Basamak Yüksekliği Doğrulama Scripti (Modül 11)

Kök Neden Analizi:
Gazebo'da kutu (<box>) geometrileri merkez noktalarından (origin) pitch açısıyla döndürülür.
Kutu merkezinden döndüğünde iki uç zıt yönlerde yükselir/alçalır.

Formül:
L: Rampa uzunluğu (metre)
t: Rampa plaka kalınlığı (metre)
pitch: Eğim açısı (radyan, negatif eğim ileriye doğru yükselir)
x_center, z_center: Rampanın merkez pose koordinatları

Üst yüzey uç noktalarının yükseklikleri (Z):
z_giris = z_center - (L/2) * sin(-pitch) + (t/2) * cos(pitch)
z_cikis = z_center + (L/2) * sin(-pitch) + (t/2) * cos(pitch)
"""

import math
import sys

# Windows konsolunda UTF-8 çıktı desteği
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def rampa_analiz(L=2.0, t=0.06, pitch=-0.06, z_center=0.03, r_teker=0.10):
    print("=" * 60)
    print("IKA ROVER - RAMPA GEOMETRISI VE FIZIK ANALIZI")
    print("=" * 60)
    print(f"Rampa Boyutları   : Uzunluk={L:.2f}m, Kalınlık={t:.3f}m")
    print(f"Merkez Pose Z     : {z_center:.3f}m")
    print(f"Pitch Açısı       : {pitch:.4f} rad ({math.degrees(pitch):.2f}°)")
    print(f"Tekerlek Yarıçapı : {r_teker:.2f}m (Çap: {2*r_teker:.2f}m)")
    print("-" * 60)

    # Eğim bileşeni:
    # pitch < 0 ise x pozitif yönünde yükselir
    sin_pitch = math.sin(-pitch)
    cos_pitch = math.cos(pitch)

    # Üst yüzey merkez yüksekliği
    z_ust_merkez = z_center + (t / 2.0) * cos_pitch

    # Giriş ucu (x = center - L/2) ve Çıkış ucu (x = center + L/2)
    z_giris_ust = z_center - (L / 2.0) * sin_pitch + (t / 2.0) * cos_pitch
    z_cikis_ust = z_center + (L / 2.0) * sin_pitch + (t / 2.0) * cos_pitch

    # Zemin seviyesine (z=0) olan fark
    basamak_giris = z_giris_ust
    basamak_cikis = z_cikis_ust

    print(f"Giriş Ucu Üst Yüksekliği : {z_giris_ust*100:.2f} cm (Hedef: ~0 cm zemin pürüzsüzlüğü)")
    print(f"Çıkış Ucu Üst Yüksekliği : {z_cikis_ust*100:.2f} cm")
    print(f"Çıkıştaki Toplam Yükseklik Farkı: {basamak_cikis*100:.2f} cm")
    print("-" * 60)

    # Değerlendirme
    if abs(z_giris_ust) < 0.01:
        print("[BAŞARILI] Giriş ucu zeminle tam temas halinde (< 1 cm fark). Robot rampaya çarpmaz.")
    else:
        print(f"[UYARI] Giriş ucu zeminden {z_giris_ust*100:.1f} cm yukarıda! Robot 'görünmez duvar' gibi çarpabilir.")

    if basamak_cikis <= r_teker * 1.5:
        print(f"[BİLGİ] Çıkış yüksekliği ({basamak_cikis*100:.1f} cm), tekerlek yarıçapına ({r_teker*100:.1f} cm) yakın.")
        print("        ÖNEMLİ NOT: Çıkışın aşılabilir olması; yerden açıklık (clearance), caster teması,")
        print("        motor torku ve sürüş yönü gibi fiziksel faktörlere de bağlıdır.")
        print("        Bu nedenle matematiksel doğrulama tamamlanmış olsa bile gerçek sürüş görsel olarak")
        print("        doğrulanmalıdır (DURUM: KISMEN TAMAMLANDI).")
    else:
        print(f"[UYARI] Çıkış basamağı çok yüksek ({basamak_cikis*100:.1f} cm)! Robot askıda kalabilir.")

    print("=" * 60)

if __name__ == '__main__':
    rampa_analiz()
