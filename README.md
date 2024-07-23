# AV_CVE
# CVE Arama ve Klonlama Aracı

Bu README dosyasını `README.md` adıyla proje dizininize ekleyin. Projenizi GitHub'a eklemek için aşağıdaki adımları izleyebilirsiniz:

Bu proje, GitHub API'sini kullanarak yeni CVE'leri aramak ve klonlamak için geliştirilmiş bir araçtır. Araç, CVE açıklamalarını Türkçeye çevirmek için `googletrans` modülünü kullanır ve zengin terminal çıktıları için `rich` modülünü kullanır.

## Gereksinimler

- Python 3.x
- `requests` modülü
- `rich` modülü
- `tzlocal` modülü
- `googletrans` modülü

## Kurulum

Gerekli Python modüllerini yüklemek için aşağıdaki adımları izleyin:

1. Python kurulu değilse [Python](https://www.python.org/downloads/) sitesinden Python'u indirip kurun.
2. Proje dizinine gidin ve aşağıdaki komutu çalıştırarak gerekli modülleri yükleyin:

   ```bash
   pip install requests rich tzlocal googletrans==4.0.0-rc1

   settings.json dosyasına GitHub tokeninizi ekleyin veya program çalışırken tokeni girin.
   github tokeni aşağıdaki gibi oluşturabilirsiniz:
1) ![image](https://github.com/user-attachments/assets/5474e9b7-31fb-4df7-8a1e-745ba8962622) <br>
2) ![image](https://github.com/user-attachments/assets/f762c2d8-b825-4cde-8164-dafc32c63b71) <br>
3) ![image](https://github.com/user-attachments/assets/f5f08b2d-89f3-4026-85ad-18502f88ea1d) <br>
4) ![image](https://github.com/user-attachments/assets/1963b6cc-9e6d-4ecf-93cb-68afc69255d9) <br>
5) ![image](https://github.com/user-attachments/assets/e6399366-23d7-43a2-8619-8118e0af6b4e) <br>
6) ![image](https://github.com/user-attachments/assets/a7cd1608-8597-4265-9f05-309f5805c6e1)




Terminal veya komut satırından proje dizinine gidin ve aşağıdaki komutu çalıştırın:


python avcve.py
Program çalıştırıldıktan sonra menüdeki seçenekleri kullanarak belirli bir CVE'yi veya anahtar kelimeyi arayabilir, yeni CVE'leri arayabilir veya belirli bir tarihte oluşturulan CVE'leri arayabilirsiniz.

Menü Seçenekleri
Belirli bir CVE veya anahtar kelime arama: CVE ID'sini veya anahtar kelimeyi girerek ilgili depoları arayın.
Yeni CVE'leri arama: Son aramadan beri oluşturulan yeni CVE'leri arayın.
Belirli bir tarihte oluşturulan CVE'leri arama: Belirli bir tarihte oluşturulan CVE'leri arayın.
Yardım: Mevcut komutlar hakkında bilgi alın.
Çıkış: Programdan çıkın.

Örnek Kullanım
Belirli bir CVE ID'sini veya anahtar kelimeyi aramak için: "1" seçeneğini seçin ve CVE ID'sini veya anahtar kelimeyi girin.
Yeni CVE'leri aramak için: "2" seçeneğini seçin.
Belirli bir tarihte oluşturulan CVE'leri aramak için: "3" seçeneğini seçin ve tarihi girin.
Programdan çıkmak için: "5" seçeneğini seçin.
Katkıda Bulunma
Katkıda bulunmak için lütfen bir issue oluşturun veya bir pull request gönderin.
