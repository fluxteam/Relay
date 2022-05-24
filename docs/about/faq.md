---
title: SSS
---

--8<-- "article_wip.txt"

# SSS {: #title }

Relay ile ilgili merak ettiğiniz tüm sorularınızın cevabını burada bulabilirsiniz! Eğer aradığınız sorun burada yoksa istediğiniz zaman [:fontawesome-brands-discord: FluxTeam Discord](https://ysfchn.com/flux) sunucusuna katılarak yardım alabilirsiniz.

---

## Genel {: #general }

### Relay nedir? {: #what-is-relay }

Relay, sunucunuzda istediğiniz herhangi bir komutu yapabilen, programlanabilir bir bottur. Yani botun ne yapmasını istediğinizi siz seçersiniz. İsterseniz, diğer Relay kullanıcılarının yayınladığı özellikleri tek tıkla kurabilirsiniz veya yaratıcılığınızı göstermek için kendi komutlarınızı ve işlemlerinizi oluşturabilirsiniz.

### Relay ile neler yapabilirim? {: #what-can-i-do }

İstediğiniz çoğu şeyi! Sunucunuzda her küçük işi yapan farklı botlar var ise hepsini Relay'e yaptırabilirsiniz. Bu sayede bot kalabalığından kurtulabilirsiniz. Fakat bazı nedenlerden ötürü (aşağıdaki sorunun cevabında belirtilmiştir) Relay ile her şeyi yapmak mümkün değildir. 

### Neden Relay'de her şeyi yapmak mümkün değil? {: #why-limitations }

Relay'in tıpkı diğer kullanıcılar ve botlar gibi Discord'un [Hizmet ve Kullanım Şartları](https://dis.gd/tos){ target="_blank" }'na uygun bir şekilde davranması gerekiyor. İnsanların Relay'i kullanarak hem botun sistemine hem de kendi sunucularındaki kullanıcılara zarar verecek her türlü olanağı yok etmek zorundayız. Relay'in herhangi bir şekilde "kötü" sayılabilecek bir amaçla kullanılmasına izin vermek istemiyoruz.

Zaman ilerledikçe Relay'deki kısıtlamalar Discord'un politikaları ve sahip olduğumuz teknik kapasiteye göre artabilir veya azalabilir. Relay ile neler yapamayacağınızı güncel olarak "Kısıtlamalar" sayfasından görebilirsiniz. Kısıtlamalar değiştikçe olabildiğinde hızlı şekilde güncellemeye çalışacağız.

### Relay hangi teknolojiler ("kütüphaneler") ile yapıldı? {: #which-libraries }

Relay'in kullandığı kütüphanelerin bir listesini [Açık Kaynak Kütüphaneleri](libraries) sayfasında bulabilirsiniz.

### Relay hakkında bir soru, sorun veya öneri sunmak istiyorum, nereden yapabilirim? {: #questions }

[:fontawesome-brands-discord: FluxTeam Discord](https://ysfchn.com/flux) sunucusuna katılarak Relay hakkında soru, soru veya öneri belirtebilirsiniz ve aynı zamanda güncellemelerden haberdar olabilirsiniz.

---

## Kullanıcı Deneyimi {: #user-experience }

### Relay'in ön eki ("prefix") nedir? {: #prefix }

Relay'in tüm komutları eğik çizgi komutları ("slash commands") üzerinden sunulmaktadır. Bu yüzden Relay'in bir ön eki yok. Komutların bir listesini görmek için eğik çizgi komut kullanma yetkinizin olduğu herhangi bir kanalda mesaj kutusuna `/` (eğik çizgi karakteri) yazın ve Relay'i seçin.

### Sunucumda Relay'in dilini nasıl değiştirebilirim? {: #language }

`/server language` komutu ile Relay'in dilini değiştirebilirsiniz. Botu sunucuya ilk eklediğinizde ayarlandığı ilk dil, İngilizce veya sunucunuzda Topluluk özellikleri açık ise Topluluk ayarlarındaki sunucu dilidir.

### Sunucular aracılığı ile Relay'den bir sürü mesaj alıyorum, nasıl önleyebilirim? {: #too-many-dm }

İnsanları rahatsız etmeye olanak sağlamamak adına sunucuya katıldığınızda Relay'in herhangi bir kişiye özelden mesaj atmasını yasakladık. Fakat sunucudaki başka bir etkinlikten (mesaj gönderme, tepki verme gibi) dolayı mesaj alıyorsanız ve bu mesajları kapatmak istiyorsanız herhangi bir sunucuda veya özel mesajlarda `/me dnd True` komutunu çalıştırarak Rahatsız Etme modunu açabilirsiniz. Eğer mesajları tekrar açmak istiyorsanız `/me dnd False` yazabilirsiniz.

!!! warning "Rahatsız Etme modu tüm bildirimleri kapatmaz"
    Unutmayın ki Rahatsız Etme modunu açtığınızda tüm bildirimler olmasa da yine de **önemli bildirimleri** alırsınız. Örneğin bir sunucuya "Merhaba" yazdığınızda Relay'in size durduk yere mesaj atması "önemli" bir sebep değildir o yüzden bu mesaj size ulaşmaz, fakat destek talebi açmak için bir mesaja tepki verdiğinizde zaten talebiniz olduğu için Relay'in size mesaj ile uyarı vermesi "önemli" bir bildirimdir.

### Eğik çizgi komutlarını neden göremiyorum? {: #missing-commands }

Lütfen kanalda "Eğik Çizgi Komutları Kullan" iznine sahip olduğunuzdan emin olun. Eğer izne sahip iseniz, <kbd>Kullanıcı Ayarları</kbd> > <kbd>Metin ve Resimler</kbd> > "Eğik çizgi komutu kullan" ayarının açık olduğundan emin olun.

---

## Relay Web {: #web }

### Yanlış kişi ile giriş yaptım, nasıl hesap değiştirebilirim? {: #switch-accounts }

Sayfanın sağ üstündeki "Sen değil misin?" bağlantısına tıkladıktan sonra gelen Discord yetkilendirme penceresinde de yine aynı seçeneği seçerek hesap değiştirebilirsiniz.
