---
title: Sahne Arkası
---

--8<-- "article_wip.txt"

# Sahne Arkası {: #title }

Relay, kullanıcı ile Discord arasında köprü kuran programlanabilir bir Discord botu. Peki nasıl çalışıyor?

!!! warning "Bu makale teknik bilgi içerebilir."
    Herkesin anlayabilmesi için içeriği basit dille anlatmamıza rağmen, daha basitleştiremeyeceğimiz terimler olabilir. Bunun bilincinde devam edin. 

## Giriş {: #intro }

Öncelikle, Relay'ın nasıl çalıştığını öğrenmek için Discord botlarının nasıl çalıştığını bilmek gerekiyor. Discord botları, o programlama dili için hazırlanmış Discord [kütüphanesinin](https://tr.wikipedia.org/wiki/K%C3%BCt%C3%BCphane_(bilgisayar_bilimi)){ target="_blank" } kullanımı ve kodun sürekli çalışıyor olmasıyla var olur.

Doğal olarak, bu Discord kütüphaneleri, biz geliştiricilere kod içinde Discord öğeleriyle etkileşime geçmek için çeşitli kod parçaları sunar. Örneğin, kod içinde bir metin kanalının hangi sunucuya ait olduğunu, bir üyenin takma adı gibi tüm veriler buradan alınır. 

Diğer botlar, bu verileri kendi içinde kullanır. Eğer birisini sunucunuzdan yasaklamak isterseniz, bot, kullandığı Discord kütüphanesinden üye bilgisini ve sunucu bilgisini alır ardından sunucudan üyeyi kaldırır. Fakat Relay'de bu böyle değildir, Relay bu Discord bilgisini size paslar, siz ardından bu veri ile ne yapacağınıza karar verirsiniz.

## Objeler {: #objects }

Discord kütüphanesi, kanala bir mesaj yazıldığında o mesajın detaylarını çekmek için tüm bilgileri bir "Mesaj" (İngilizce: Message) objesine ekler. Bu sadece mesaj için değil, Discord'da gördüğünüz her öğe için böyledir. Bu bir "Rol", "Üye", "Kullanıcı", "Kanal", "Sunucu", "Mesaj", "Embed" (Discord'un içinde "gömülü mesaj" olarak da geçer) öğesi de olabilir.

Relay, bu öğelerdeki verileri alır ve önceden hazırlanan özel objelere yerleştirir. Bu özel objeler, Discord objelerinin yeniden tasarlanmış halidir, fakat botun kendisi gibi kullanıcının erişmemesi gereken objeler çıkartılır, ardından kullanıcıya bu verileri okuması için tam yetki verilir.

<p class="center-image">
    <img src="../assets/bts_1.png" width="700"><br>
    Her Discord objesi için Relay objesi de vardır, bunlar özünde Discord objelerinin kopyasıdır, fakat insanların bu objelerden dışarı çıkıp Relay'in tam kontrolünün alınmaması için botun kendisi gibi objeler hariç bırakılır. En sonunda bu Relay objeleri, kullanıcıya istediği gibi okuma hakkı tanır.
</p>

Relay objeleri, Discord kütüphanesinin verdiği objeleri kendi objelerine dönüştürecek kadar güçlülerdir, ve direkt olarak JSON biçimine aktarılabilir.

## Eylemler {: #functions }

Elbette Relay ile bir şey yapmak için aynı zamanda eylemlere de ihtiyaç var, bir kanala mesaj göndermek, mesaja tepki eklemek gibi. Peki Relay bunu nasıl yapıyor?

Relay'in içinde, kullanıcıların kullanabileceği [Discord eylemleri](api/discord){ target="_blank" } önceden kodlanmıştır. Yani bir mesaj göndermek istiyorsanız, sadece "Mesaj Gönderme" eyleminin kodunu bilmeniz yeterli. Ve tabii ki o eylemin istediği parametreler.

<p class="center-image">
    <img src="../assets/bts_2.png" width="700"><br>
    Relay'deki eylemler, Relay objelerini herhangi bir değişiklik olmadan destekleyebilir. Eğer mesaj yazılan kanala yeni bir mesaj göndermek istiyorsanız, sadece mesajın kanalına referans vermeniz yeterli.
</p>

Sadece Discord eylemleri değil, [Matematik](https://pyconduit.ysfchn.com/blocks/math){ target="_blank" }, [Metin](https://pyconduit.ysfchn.com/blocks/text){ target="_blank" } gibi genel işlemler için de eylemler bulunur.