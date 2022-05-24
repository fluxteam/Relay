---
title: Paketler
---

--8<-- "article_wip.txt"

# Paketler {: #title }

Relay'e yeni içerik eklemeyi istediğiniz için çok teşekkürler! Relay Packages, kullanıcıların içerikleri ile yürütüldüğü için daha fazla paket oluşturmanız, insanların daha fazla pakete ulaşmasına ve paket çeşitliliğin artmasına yardımcı oluyor.

## Paket içeriği {: #package-content }

Relay Paketleri, Relay Actions ile aynı olay akışlarını kullanır. Fakat Relay Paketleri sadece olay akışları içermez, aynı zamanda kullanıcının göreceği bir ismi, adı, yapımcısı bulunur.

<p class="center-image">
    <img src="../../assets/packages_features.png" width="700"><br>
    Paketler, Relay Actions'dan daha fazla özelliğe sahiptir. Hem geliştirici için hem de kullanıcı için daha avantajlıdır.
</p>

| Konu | Relay Paketleri | Relay Actions |
|:-----|:----------------|:--------------|
| Kullanım | Herhangi birisi (bu siz de olabilir başka biri de) oluşturur, diğerleri de sunucularına kurarlar (kendi paketinizi kendi sunucunuza da kurabilirsiniz). | Tamamen kendiniz oluşturursunuz. |
| Görünürlük | Paketler tüm dünya ile paylaşılır, açık kaynak kodludur. Başka insanlar görebilir ve katkıda bulunabilir. | Sadece siz ve sunucunuza özeldir, kimse göremez veya düzenleyemez. |
| Dağıtım | Depoya eklenen paketler Relay üzerinden sunucuya yüklenebilir. Bir güncelleme yayınlamak istiyorsanız, depoya yeni sürümünüzü eklemeniz yeterlidir. | Sadece sunucuya özel olduğu için başka birisiyle direkt olarak paylaşılamaz. |
| Kurulum | Paketlere parametreler eklenebilir, bu sayede kullanıcı paketi kurarken paket ayarlarını belirteceği bir sayfa ile karşılaşır. | Mümkün değil çünkü Relay Actions olay akışları sadece sunucuya özeldir. |
| İnceleme | Oluşturulan tüm içerik FluxTeam tarafından kontrol edilir. | Hiçbir şey inceleme altına tutulmaz. |
| Kısıtlamalar | Relay Paketleri, FluxTeam tarafından incelendiği için botla daha fazla işlem yapabilirler. | Spam ve saldırıları önlemek adına bazı şeyleri yapamazsınız. |
| İçerik | İsim, yapımcı, olay akışları, Python dosyaları ve paket simgelerine sahip olabilir. | Sadece olay akışları dosyalarına sahip olabilir. |
| Özel kod çalıştırma | Paketlerin içine Python dosyası eklenerek özel kod çalıştırılabilir. | Çalıştıramazlar. |

## Giriş {: #intro }

Paket oluşturmaya başlamak için tek sahip olmanız gereken bir metin editörüdür. Bu kendi editörünüz veya sisteminizde bulunan varsayılan editör olabilir.

Relay Paketleri [TOML :octicons-link-external-16:](https://toml.io){ target="_blank" } ve [JSON :octicons-link-external-16:](https://www.json.org/json-tr.html){ target="_blank" } dosyalarından oluştuğu için bu dosyaların hangi yazım kurallarına sahip olduğunu bilmeniz gerekir. Bu sayfadaki adımlar, sizin halihazırda TOML ve JSON'u bildiğinizi düşünerek hazırlanmıştır.

### Paket kimliği {: #package-id }

Her paketin belirli bir kimliği vardır. Bu kimlik, şu ana kadar paylaşılmış olan tüm paketler içinde eşşiz olmalıdır. Bu sayede insanlar, sizin paketinizi bulmak isterlerse sadece kimliği ile bulabilir. Ne de olsa paketlerin gözüken adları başka birinin paketiyle aynı olabilir. Ama paket kimlikleri asla. Paketin kimliği için bazı kurallar bulunur:

* Sadece küçük harfler (a-z) içerir.
* Türkçe veya başka bir dile özel karakter(ler) içeremez (sadece İngilizce alfabesindeki küçük harfler).
* Harf dışında rakam (0-9) veya tire (-) de içerebilir fakat yine de sadece harf ile başlayabilir.
* 3 karakter veya 3 karakterden uzun olmalıdır.

|  Örnek  |  Kabul edilir mi?  |
|:--------|:-------------------|
| `ticket` | :octicons-check-16: |
| `ReactionRoles` | :octicons-x-16: (büyük harflere izin verilmiyor) |
| `my package` | :octicons-x-16: (boşluklara izin verilmiyor) |
| `et` | :octicons-x-16: (en az 3 karakter ve üstü olmalı) |
| `1iki` | :octicons-x-16: (sayı ile başlayamaz) |
| `stopwatch` | :octicons-check-16: |

### Dizin hiyerarşisi {: #directory-tree }

Paketin içinde birden fazla dosya olacağı için ilk başta klasör oluşturarak başlayabilirsiniz. Klasörün adını paketinizin kimliği ile aynı tutmalısınız.

Klasörünüzün adını `my-package` olarak varsayarsak, klasörünüzün yapısı bununla aynı veya benzer yapıda olmalıdır. Her dosyanın ne işe yaradığını öğrenmek için aşağıdaki başlıkları okumaya devam edebilirsiniz.

``` { .toml .annotate }
📁 my-package # (1)
├──📁 1.0
│  ├──📄 workflow_1.json
│  └──📄 version.toml
├──📁 1.1
│  ├──📄 workflow_1.json
│  └──📄 version.toml
├──📄 pack_icon.png
└──📄 metadata.toml
```

1.  Klasörün adını `my-package` yapmayın, bu sadece bir örnek. Siz onu kendi paketinizin adı ile değiştirin. 

[:octicons-download-16: &nbsp; Örnek paket dosyalarını indir](https://relay-packages.pages.dev/extras/example-pack.zip){ .md-button target="_blank" .secondary-button }

## Metaveri {: #metadata }

| Dosya adı | Zorunlu | Notlar | Dosya şeması |
|:----------|:-------:|:-------------|--------------|
| <samp>metadata.toml</samp> | :octicons-check-16: |  | my-package<br>└── **metadata.toml** |

Metaveri dosyası, paketin ana detaylarını içeren bir dosyadır. Bu dosya geçerli bir [TOML :octicons-link-external-16:](https://toml.io){ target="_blank" } dosyası ve tam ismi her zaman `metadata.toml` olmalıdır. (küçük/büyük harf duyarlıdır, yani `Metadata.toml` veya `METADATA.toml` gibi adlandırmalar kabul edilmez.)

Her paketin bir metaveri dosyası bulunmak **zorundadır**. Bu metaveri dosyası, paketinizin adını ve diğer detayları belirtmenize yarar. Bu dosya, klasörünüzün hemen içinde olmalıdır. Yani herhangi bir alt bir klasörde olmamalıdır.

Örnek bir metaveri dosyası bu şekilde gözükür:

``` { .toml title="metadata.toml" .annotate }
[pack]
name = "Ticket Channels" # (1)
title = "Allows server members to get help privately." # (2)
description = """\
    Allows server members to create channels that only can be seen by moderators \ 
    and user who opened the ticket, so they can get help privately from moderators.\
    """ # (3)
icon = "pack_icon.png" # (4)

[pack.versions] # (5)
"2.0" = 3
"1.1" = 2
"1.0" = 1

[pack.translations] # (6)
    [pack.translations.tr]
    description = """\
        Sunucu üyelerinin, yalnızca moderatörler ve talebi açan kullanıcı \
        tarafından görülebilecek kanallar oluşturmasına olanak tanır, böylece moderatörlerden \
        özel olarak yardım alabilirler.\
        """
    title = "Sunucunu üyelerinizin özel olarak yardım almalarını sağlayın."
    name = "Destek Kanalları"

[pack.author] # (7)
username = "flux"
```

1.  Bu paketin ekranda gözükecek olan adı.
2.  Paketin ne işe yaradığına dair kısa bir açıklama/başlık. Genelde tek bir cümleden oluşur.
3.  Paketin ne işe yaradığına dair daha uzun bir açıklama. Eğer başlığın yeterince açıklayıcı olduğunu düşünüyorsanız bunu eklemenize gerek yok.
4.  [Paket ikonu](#pack-icon)nun dosya adı ve uzantısı. 
5.  Versiyon adları ve sayıları burada belirtilir. Versiyonlar, paketi yükseltirken veya kurarken kullanılır.<br><br>Soldaki değerler (anahtarlar) version adlarını belirtirken, sağdaki değerler ise versiyon sayısını belirtir. Versiyon sayıları her versiyon için özel olmalı ve her yeni sürümde artmalıdır. (En eski versiyon en küçük sayıya sahip olmalı, en yeni versiyon da en büyük sayıya sahip olmalı.) Her versiyon adının kendi klasörü vardır.<br><br>Anahtarların ve değerlerin sırası fark etmez, fakat yine de yukarıdan aşağıya doğru en yeni versiyondan en eskisinde doğru yazmanız şiddetle tavsiye edilir.
6.  Bu paketin `name` (isim), `title` (başlık) ve `description` (açıklama) çevirilerini belirtir. Bu sayede kullanıcılar, paketin ayrıntılarını kendi dillerinde okuyabilirler. Dil kodu geçerli bir [ISO 639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes){ target="_blank" } kodu olmalıdır. Eğer bir dil kodu eklerseniz, her dil kodu için en azından `name` ve `title` alanlarını eklemek zorundasınız fakat `description` isteğe bağlıdır.
7.  Sadece `username` adında bir değere sahip olabilir. Bu değerde ise paket yapımcısının kullanıcı adını belirtmeniz gerekir. Yapımcının kullanıcı adı daha önceden Relay paketleri deposuna kayıtlı olmalıdır!


### Seçenekler {: #metadata-options }

|          Anahtar         |   Zorunlu   |   Tip   |   Açıklama   |
|:-------------------------|:-----------:|:-------:|:-------------|
| <samp>name</samp>          |     :octicons-check-16:       | `string` | Bu paketin ekranda gözükecek olan adı. |
| <samp>title</samp>         |     :octicons-check-16:       | `string` | Paketin ne işe yaradığına dair kısa bir açıklama/başlık. Bu genelde tek bir cümleden oluşur. |
| <samp>description</samp>   |             | `string` | Paketin ne işe yaradığına dair daha uzun bir açıklama. Eğer başlığın yeterince açıklayıcı olduğunu düşünüyorsanız bunu eklemenize gerek yok. |
| <samp>icon</samp>           |               | `string` | Paketin ikonunun dosya adı ve uzantısı. Eğer pakete özel bir ikon eklemek istiyorsanız, ikonu bu `metadata.toml` dosyasının olduğu klasörün içine koyabilir ve bu `icon` değerini dosya adını ve uzantısını yazabilirsiniz. İkonu başka bir klasörünün içine eklemeyin ve ikonun adına eğik çizgi koymayın. Sadece dosya adını ve uzantısını girin. Örnek: `paket_ikonu.png`.<br><br>Eğer paketin kendi ikonu olmazsa, o zaman Relay'in varsayılan paket simgesi kullanılır. |
| <samp>versions</samp>       |      :octicons-check-16:      | `section` | Versiyon adları ve sayıları burada belirtilir. Versiyonlar, paketi yükseltirken veya kurarken kullanılır.<br><br>Soldaki değerler (anahtarlar) version adlarını belirtirken, sağdaki değerler ise versiyon sayısını belirtir. Versiyon sayıları her versiyon için özel olmalı ve her yeni sürümde artmalıdır. (En eski versiyon en küçük sayıya sahip olmalı, en yeni versiyon da en büyük sayıya sahip olmalı.) Her versiyon adının kendi klasörü vardır.<br><br>Anahtarların ve değerlerin sırası fark etmez, fakat yine de yukarıdan aşağıya doğru en yeni versiyondan en eskisinde doğru yazmanız şiddetle tavsiye edilir. |
| <samp>translations</samp>       |              | `section` | Bu paketin `name` (isim), `title` (başlık) ve `description` (açıklama) çevirilerini belirtir. Bu sayede kullanıcılar, paketin ayrıntılarını kendi dillerinde okuyabilirler. Dil kodu geçerli bir [ISO 639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes){ target="_blank" } kodu olmalıdır. Eğer bir dil kodu eklerseniz, her dil kodu için en azından `name` ve `title` alanlarını eklemek zorundasınız fakat `description` isteğe bağlıdır. |
| <samp>author</samp>         |     :octicons-check-16:       | `section` | Sadece `username` adında bir değere sahip olabilir. Bu değerde ise paket yapımcısının kullanıcı adını belirtmeniz gerekir. Yapımcının kullanıcı adı daha önceden Relay paketleri deposuna kayıtlı olmalıdır! |

## Paket İkonu {: #pack-icon }

| Dosya adı | Zorunlu | Notlar | Dosya şeması |
|:----------|:-------:|:-------------|--------------|
| <samp>pack_icon.png</samp> |  | • Dosya boyutu 512 KB'a eşit veya küçük olmalı.<br>• Görüntü boyutu 512×512 piksel'e eşit veya daha küçük olmalı. | my-package<br>└── **pack_icon.png** |

Paketinize bir ikon eklemek isterseniz, paketinizin ana klasörüne paket ikonunu ekleyebilirsiniz. İkonun kendisi hakkında herhangi bir zorunluluk yok, fakat dosya boyutunun 512 KB'a eşit veya küçük, ve aynı zamanda görüntü boyutunun 512×512 piksel'e eşit veya daha küçük olduğundan emin olun.

Unutmayın ki paket dosyaları, Relay'e aktarılmadan önce veri tasarrufu ve gecikmeyi azaltmak için sıkıştırılacağı için ikonunuzun kalitesi gözle görülecek derecede düşebilir.

<div class="guide-container no-wrap" markdown="1">
<img src="https://relay-packages.pages.dev/default_pack_icon.jpg" class="guide-image" width="100" style="width: 100px;"><div class="guide-text" markdown="1">

Eğer paket ikonu belirtmezseniz, varsayılan paket ikonu (soldaki resim) gözükecektir. Eğer zaten varsayılan paket ikonunu kullanmak istiyorsanız, bu ikonu indirip paket klasörünüze eklemeyin.

</div></div>

## Sürümler {: #versions }

Paketler kullanıcılara sürümler halinde sunulur. Her sürüm belirli bir değişikliğe sahiptir, ve paketin yapımcısı yeni özellikler eklemek istediğinde veya hataları düzelttiğinde yeni sürüm olarak kullanıcılara sunabilir.

Eski sürümleri kullanmanın pek amacı olmadığından dolayı, kullanıcılar yeni bir paket kurmak istediklerinde, Relay bu paketlerin en son sürümünü kurar. Paketin yapımcısı yeni sürüm çıkarırsa, yeni sürüme yükseltme ve şu anki sürümde kalma seçenekleriniz olur.

!!! warning "Paketin yapımcısı, eğer isterse yeni sürüm çıkartmadan önceki sürümü de düzenleyebilir."
    Bunun sebebi, eğer pakette bir güvenlik açığı çıktıysa ve/veya bu açık Relay'i de kötü etkiliyorsa paketin yapımcısına bunu düzeltme hakkı tanımak içindir. 
    
    Ama merak etmeyin, eğer paketin yapımcısı sizinle bulunduğunuz aynı sürümü düzenlerse, sizin kurduğunuz paketin içeriği zaten kopyalanmış olduğu için onun yaptığı paket kod değişiklikleri (siz istemediğiniz süre) sizi etkilemeyecek. Eğer Relay, sizin bulunduğunuz sürümle paketin o sürümle arasında bir uyuşmazlık tespit ederse Relay size bunu bildirir ve
    tek tuşla onarma imkanınız olur. 
    
    Relay, bir paketin herhangi bir sürümünde kritik açık varsa ve kullanıcılardan biri o sürümü kullanırsa otomatik olarak kullanıcının kurduğu paketi, yeni haliyle değiştirme hakkını saklı tutar.

Her paketin en az 1 sürümü olmak zorundadır. Yeni sürüm oluşturmak için paketinizin ana klasörüne sürüm adını belirten bir klasör oluşturun.

```
📁 my-package
├──📁 1.0
├──📄 pack_icon.png
└──📄 metadata.toml
```

Sürüm adları:

* En az 1 karakter içermelidir.
* Sadece rakam (0-9), nokta (.), tire (-), küçük harfler (a-z) içerebilir.
* Türkçe veya başka bir dile özel karakter(ler) içeremez (sadece İngilizce alfabesindeki küçük harfler).
* Sayı veya harf ile başlayabilir ama nokta veya tire ile başlayamaz.

Sürüm adları için bazı örnekler aşağıdaki gibidir, illa belirli bir kurala göre sürümlendirmek zorunda değilsiniz fakat bunu yapmanız tavsiye edilir.

```
1.0
2.5.2
5.0beta
beta-5.0
a2.1
```

## Olay Akışı {: #workflow }

| Dosya adı | Zorunlu | Notlar | Dosya şeması |
|:----------|:-------:|:-------------|--------------|
| <samp>workflow_(sayı).json</samp><br><small>Örnekler:<br><samp>workflow_1.json</samp><br><samp>workflow_2.json</samp> | :octicons-check-16: | • Her sürüm için en az 1 olay akışı dosyası olmalı. | my-package<br>└── 1.0 (sürüm klasörü)<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└── **workflow_1.json** |

Olay akış dosyaları, yapılacak eylemlerin bir listesini içeren [JSON :octicons-link-external-16:](https://www.json.org/json-tr.html){ target="_blank" } dosyasıdır. Bu dosyanın formatı aşağıdaki gibidir:

``` { .py title="workflow_1.json" .annotate }
{
    "steps": [ # (1)
        {
            "action": "TEXT.JOIN", # (2)
            "parameters": {
                "text1": "Hello", # (3)
                "text2": "World!"
            }
        }
    ]
}
```

1.  Gerçekleştirilecek her adım, yeni bir obje olarak eklenir. Bu adımlar sırasıyla en baştan en aşağıya doğru çalışır.
2.  Yapılacak eylemin kodu. Relay'deki tüm eylemlerin bir listesini, bu dökümantasyonun "Actions API" başlığı altındaki kategorilerden görebilirsiniz.
3.  Bu eylemin aldığı parametreler. (anahtar ve değer şeklinde)

Olay akış dosyası formatının tamamını içeren bir JSON şeması da ayrıca mevcut.

<!-- TODO: Broken link. -->
[:octicons-link-external-16: &nbsp; JSON şemasını görüntüle](/misc/actions_schema_tr.json){ .md-button target="_blank" .secondary-button }