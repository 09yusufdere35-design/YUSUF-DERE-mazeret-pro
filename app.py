from flask import Flask, render_template, request, send_file, make_response
import random
import sqlite3
import datetime
from fpdf import FPDF
import os
import io
import csv
import base64

app = Flask(__name__)

# --- 1. VERİTABANI ---
def init_db():
    conn = sqlite3.connect('mail_gecmisi.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS gecmis 
                 (id INTEGER PRIMARY KEY, tarih TEXT, ders TEXT, hoca TEXT, kategori TEXT, ciddiyet TEXT, icerik TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- 2. ŞABLONLAR ---
SABLONLAR = {
    "tr": {"subject": "{course} - Ödev Teslimi / {student_name}", "salutation_formal": "Sayın {lecturer},", "salutation_informal": "Merhaba {lecturer} Hocam,", "opening_sentence": "{course} dersinin {date} teslim tarihli ödevini ekte tarafınıza sunuyorum.", "closing_formal": "Saygılarımla,\n{student_name}", "closing_informal": "İyi çalışmalar dilerim,\n{student_name}"},
    "en": {"subject": "{course} - Assignment Submission / {student_name}", "salutation_formal": "Dear {lecturer},", "salutation_informal": "Hi Professor {lecturer},", "opening_sentence": "I am submitting the assignment for {course}, which was due on {date}.", "closing_formal": "Sincerely,\n{student_name}", "closing_informal": "Best regards,\n{student_name}"},
    "de": {"subject": "{course} - Hausarbeit Abgabe / {student_name}", "salutation_formal": "Sehr geehrte(r) {lecturer},", "salutation_informal": "Hallo {lecturer},", "opening_sentence": "hiermit reiche ich die Hausarbeit für den Kurs {course} (Frist: {date}) ein.", "closing_formal": "Mit freundlichen Grüßen,\n{student_name}", "closing_informal": "Viele Grüße,\n{student_name}"}
}

# --- 3. LEGO SİSTEMİ (FULL DESTAN MODU) ---
LEGO_PARCALAR = {
    "teknik": {
        "tr": {
            "1": {
                "baslangic": ["Sayın Hocam, ödevimi tam vaktinde sisteme yüklemek adına bilgisayar başına geçmiştim; ancak kullandığım kelime işlemci yazılımı (MS Word/LaTeX), kaynakça yönetim eklentisiyle (Mendeley/Zotero) beklenmedik bir 'runtime' çakışması yaşayarak tüm atıf formatlarını bozdu.", "Dosyamı PDF formatına dönüştürüp son bir kez gözden geçirirken, işletim sistemi güncellemesi sonrası yazı tiplerinde (font rendering) ve sayfa düzenlerinde ciddi kaymalar olduğunu fark ettim.", "Ödev dosyamı üniversitenin bulut sunucusuna yüklemeye çalıştığım esnada, internet servis sağlayıcımın bölgesel altyapı çalışması nedeniyle bağlantım 'Packet Loss' hatası vermeye başladı ve yükleme %99'da kesildi."],
                "gelisme": ["Akademik ciddiyete yakışmayan, formatı bozuk bir dosya göndermek size ve dersinize saygısızlık olacağından, paniğe kapılmadan tüm kaynakçayı ve formatı manuel olarak tek tek düzeltmek ve her satırı yeniden kontrol etmek zorunda kaldım.", "Hatalı dosya gönderme riskini göze almayarak, telefonumun internetini (hotspot) bilgisayara bağlamayı denedim; ancak operatör kaynaklı şebeke sorunu nedeniyle stabil bir bağlantı kurmam ve dosyayı güvenle sunucuya iletmem sandığımdan çok daha uzun sürdü.", "Sistemin güncelleme döngüsünden çıkmasını çaresizce beklerken bir yandan da ödevimin yedeğini tablet üzerinden kontrol etmeye çalıştım, ancak işlemin bitmesi ve bilgisayarın tekrar açılması maalesef teslim saatini bir miktar aşmama neden oldu."],
                "sonuc": ["Yaşanan bu talihsiz teknik aksaklık planladığım teslim saatini biraz geciktirdi, ancak titizlikle düzelttiğim çalışmamı eksiksiz bir şekilde ekte tarafınıza sunuyorum.", "Emeğimin basit bir teknik hata yüzünden heba olmasını istemediğim için gösterdiğim bu hassasiyeti ve yaşanan kısa süreli gecikmeyi anlayışla karşılayacağınızı ümit ediyorum.", "Gecikme için en içten özürlerimi sunar, teknik sorunlara rağmen tamamlamayı başardığım ödev dosyamı kabul buyurmanızı rica ederim."]
            },
            "3": {
                "baslangic": ["Dün gece projemin en kritik derleme (compile) aşamasına geldiğimde, işlemcimin aşırı yük altında ısınması sonucu anakartın termal koruma sensörleri devreye girdi ve bilgisayar kendini aniden kapatarak 'BIOS Post' ekranında takılı kaldı.", "Kullandığım simülasyon ve analiz yazılımının lisans sunucularında yaşanan global bir 'Authentication Timeout' erişim kesintisi nedeniyle, projemin nihai çıktılarını (export) almam ve raporuma eklemem teknik olarak imkansız hale geldi.", "Bölgemizdeki trafo merkezinde meydana gelen ani bir arıza nedeniyle tüm mahallede elektrikler kesildi; laptopumun bataryası da projenin getirdiği yüksek işlemci yükü nedeniyle hızla tükendiği için çalışmamın son %10'luk kısmı yarıda kaldı."],
                "gelisme": ["Bilgisayarın soğumasını bekledikten sonra, olası veri kayıplarını önlemek adına disk imajını alıp çalışmamı başka bir bilgisayara aktarmam ve ortam kurulumlarını (environment setup) sıfırdan yapmam sabahın ilk ışıklarına kadar sürdü.", "Elektriklerin gelmesini beklerken vakit kaybetmemek adına, bilgisayarımı ve notlarımı alıp açık bulabildiğim nöbetçi bir kafeye gidip, gürültülü ve zor bir ortamda, neredeyse bitmiş olan bataryamla çalışmamı toparlamaya gayret ettim.", "Lisans sorunu çözülemeyince, teknik destek forumlarında saatlerce araştırma yaparak 'open-source' alternatif bir araç buldum ve verilerimi bu araca göre yeniden düzenleyerek çıktılarımı manuel olarak oluşturmak zorunda kaldım."],
                "sonuc": ["Bu kaotik ve stresli sürecin sonunda, geç de olsa ödevimi kurtarmanın ve size sunabilmenin haklı gururunu yaşıyorum; bu teknik karmaşa için özür dilerim.", "Karşılaştığım bu beklenmedik teknik engeller teslim süremi aksatsa da, sorumluluğumu yerine getirmek adına pes etmedim ve dosyamı ekte iletiyorum.", "Teknik altyapıdan kaynaklanan bu mücbir sebepten ötürü yaşanan gecikmeyi, gösterdiğim çabayı da göz önünde bulundurarak anlayışla karşılamanızı dilerim."]
            },
            "5": {
                "baslangic": ["Maalesef dün gece bilgisayarımı açtığımda siyah ekranda 'Boot Device Not Found' hatasıyla karşılaştım; BIOS üzerinden yaptığım kontrollerde, NVMe M.2 SSD diskimin donanımsal bir arıza nedeniyle sistem tarafından hiç görülmediğini dehşetle fark ettim.", "Bilgisayarıma bulaşan ve son günlerde yayılan agresif bir fidye yazılımı (ransomware) saldırısı sonucunda, masaüstümdeki tüm akademik çalışmalarım şifrelendi ve fidye talep notuyla karşılaştım.", "Çalışma masamda talihsiz bir kaza sonucu laptopumun klavyesine dökülen sıvı, anakart üzerinde anında kısa devreye yol açtı ve cihazımdan dumanlar yükselerek sistem tamamen kapandı, anakart yandı."],
                "gelisme": ["Bu felaket karşısında pes etmek yerine, diski söküp harici bir aparatla başka bir bilgisayara bağladım ve Linux tabanlı özel 'forensic' kurtarma araçları kullanarak, 'bad sector' oluşmuş diskten verilerimi 'bit-by-bit' kopyalamak için tüm gece uykusuz kalarak mücadele ettim.", "Siber güvenlik uzmanı bir arkadaşımdan aldığım teknik destekle, bilgisayarı güvenli ağ modunda başlatıp 'decryption' (şifre çözme) araçlarını çalıştırdık ve iki gün süren uykusuz bir maratonun ardından dosyaların büyük kısmını kurtarmayı başardık.", "Servisin 'anakart değişimi şart, 1 hafta sürer' demesine aldırmadan, diskimi söküp bir internet kafeye giderek, oradaki kısıtlı ve hijyenik olmayan şartlarda, gürültü içinde konsantre olmaya çalışarak ödevimi sıfırdan derledim."],
                "sonuc": ["Verdiğim bu 'hayatta kalma mücadelesi' (survival) tadındaki süreç sonunda, dosyalarımı kurtarıp size sunabilmiş olmaktan dolayı büyük bir rahatlama yaşıyorum; gecikmemi lütfen maruz görün.", "Neredeyse tüm akademik arşivimi ve bu derse ait emeklerimi kaybediyordum ama inatla uğraşarak ödevimi kurtardım; bu mücbir sebepten ötürü affınızı diliyorum.", "Yaşadığım bu büyük stres, maddi hasar ve teknik felaket nedeniyle oluşan gecikmeyi, insani bir durum ve olağanüstü hal olarak değerlendireceğinizi umuyor, çalışmamı saygılarımla sunuyorum."]
            }
        },
        "en": {
            "1": {
                "baslangic": ["Dear Professor, I was sitting at my computer, ready to upload my assignment exactly on time; however, my word processing software unexpectedly conflicted with my citation manager plug-in, corrupting the formatting of the entire document at the last second.", "While converting my file to PDF for a final review, I noticed significant layout shifts and font rendering errors caused by a recent background operating system update, which made the document look unprofessional.", "As I attempted to upload my assignment to the university cloud server, my internet connection became extremely unstable due to sudden ISP infrastructure maintenance in my area, causing repeated upload failures."],
                "gelisme": ["Since sending a poorly formatted document would be disrespectful to your course and academic standards, I had to manually correct every single citation and layout issue line by line, which took significantly longer than anticipated.", "Not wanting to risk sending a corrupted file, I tried tethering my mobile data to my computer, but establishing a stable connection took considerable time due to poor network coverage in my building.", "I had to wait for the system update loop to finish while simultaneously checking my backup files on my tablet to ensure data integrity, refusing to submit an incomplete work."],
                "sonuc": ["This technical glitch caused a slight delay, but I am pleased to submit my fully corrected and complete assignment attached here.", "I hope you understand that I wanted to ensure the quality of my work rather than submitting a corrupted file on time; apologies for the inconvenience.", "I sincerely apologize for the delay and ask you to accept my assignment, which I managed to complete despite these unforeseen technical issues."]
            },
            "3": {
                "baslangic": ["Last night, during the critical compilation phase of my project, my CPU overheated due to high load, triggering the thermal protection sensors which caused the computer to shut down abruptly and refuse to restart for a long time.", "Due to a global outage in the license servers of the specialized simulation software I use for this project, it became technically impossible to export the final results and include them in my report.", "A sudden transformer explosion in our neighborhood caused a massive power outage; my laptop battery drained quickly under the heavy workload, halting my progress right before the conclusion."],
                "gelisme": ["After waiting for the computer to cool down, I spent the entire night creating a disk image to prevent data loss and transferring my work to another machine, reinstalling all necessary environments from scratch.", "Instead of waiting for the power to return, I took my laptop to a late-night cafe and tried to finalize my work in a noisy and difficult environment with the remaining battery life.", "Since the license issue couldn't be resolved, I researched technical forums, found an open-source alternative tool, and manually re-processed my data to generate the required outputs."],
                "sonuc": ["At the end of this chaotic process, I am proud to have salvaged my assignment and submit it to you, albeit late. I apologize for the delay caused by these technical hurdles.", "Although these unexpected technical obstacles disrupted my submission timeline, I did not give up on fulfilling my responsibility.", "I hope you can understand this delay caused by force majeure technical infrastructure issues beyond my control."]
            },
            "5": {
                "baslangic": ["Unfortunately, when I turned on my computer last night, I encountered a critical 'Boot Device Not Found' error; my NVMe SSD was physically damaged and not recognized by the BIOS, putting all my data at risk.", "Due to an aggressive ransomware attack on my computer, all my academic files and the desktop environment were encrypted, and I was locked out of my own system.", "Accidentally spilling liquid on my laptop keyboard caused an immediate short circuit on the motherboard, and my device completely stopped working amidst smoke and sparks."],
                "gelisme": ["I removed the drive, connected it to another computer via an external forensic dock, and stayed up all night using Linux-based recovery tools to salvage my data bit-by-bit from the corrupted sectors.", "With the help of a cybersecurity specialist friend, we ran advanced decryption tools for two days in a sleepless marathon and managed to recover most of the files just now.", "I removed my hard drive and went to an internet cafe, where I tried to compile my assignment from scratch under very limited and unhygienic conditions, using older backups."],
                "sonuc": ["After this survival-like struggle, I am relieved to have recovered my files and submit them to you; please excuse my lateness due to this hardware disaster.", "I almost lost my entire academic archive, but I persisted and saved the assignment; I ask for your forgiveness for this force majeure situation.", "Despite this disaster scenario which was completely out of my control, I completed and submitted my work out of respect for your course."]
            }
        },
        "de": {
            "1": {
                "baslangic": ["Sehr geehrte(r) Professor(in), ich war bereit, meine Hausarbeit pünktlich hochzuladen, jedoch verursachte mein Textverarbeitungsprogramm einen kritischen Konflikt mit dem Zitationsmanager, wodurch die gesamte Formatierung in der letzten Minute zerstört wurde.", "Als ich meine Datei zur letzten Überprüfung in ein PDF umwandelte, bemerkte ich erhebliche Layout-Verschiebungen und Schriftartfehler, die durch ein kürzliches Hintergrund-Systemupdate verursacht wurden.", "Während ich versuchte, meine Hausarbeit auf den Universitätsserver hochzuladen, brach meine Internetverbindung aufgrund unangekündigter Wartungsarbeiten des Anbieters ständig ab."],
                "gelisme": ["Da es respektlos wäre, ein schlecht formatiertes Dokument einzureichen, musste ich jede einzelne Zitation und das Layout manuell korrigieren, was deutlich länger dauerte als erwartet.", "Um das Risiko einer fehlerhaften Datei zu vermeiden, versuchte ich, mein Handy als Hotspot zu nutzen, aber eine stabile Verbindung herzustellen, nahm viel Zeit in Anspruch.", "Ich musste warten, bis das Systemupdate abgeschlossen war, und überprüfte gleichzeitig meine Sicherungskopien auf dem Tablet, um die Datenintegrität sicherzustellen."],
                "sonuc": ["Diese technische Störung verursachte eine leichte Verzögerung, aber ich freue mich, Ihnen meine vollständig korrigierte Arbeit im Anhang senden zu können.", "Ich hoffe auf Ihr Verständnis, dass ich die Qualität meiner Arbeit sicherstellen wollte, anstatt eine fehlerhafte Datei pünktlich abzugeben.", "Ich entschuldige mich aufrichtig für die Verspätung und bitte Sie, meine Arbeit trotz dieser technischen Probleme anzunehmen."]
            },
            "3": {
                "baslangic": ["Gestern Nacht, während der kritischen Kompilierungsphase meines Projekts, überhitzte meine CPU aufgrund hoher Last, woraufhin sich der Computer abschaltete und lange Zeit nicht mehr starten ließ.", "Aufgrund eines weltweiten Ausfalls der Lizenzserver der von mir verwendeten Simulationssoftware war es technisch unmöglich, die Endergebnisse meines Projekts zu exportieren und in den Bericht aufzunehmen.", "Ein Transformatorausfall in unserer Nachbarschaft verursachte einen massiven Stromausfall; der Akku meines Laptops war aufgrund der hohen Arbeitslast schnell leer, was meinen Fortschritt stoppte."],
                "gelisme": ["Nachdem ich gewartet hatte, bis der Computer abgekühlt war, verbrachte ich die ganze Nacht damit, ein Disk-Image zu erstellen, um Datenverlust zu vermeiden, und meine Arbeit auf einen anderen Rechner zu übertragen.", "Anstatt auf den Strom zu warten, ging ich in ein Nachtcafé und versuchte, meine Arbeit in einer lauten und schwierigen Umgebung mit dem verbleibenden Akku fertigzustellen.", "Da das Lizenzproblem nicht gelöst werden konnte, suchte ich in technischen Foren nach einer Open-Source-Alternative und bearbeitete meine Daten manuell neu."],
                "sonuc": ["Am Ende dieses chaotischen Prozesses bin ich stolz darauf, meine Arbeit gerettet zu haben und sie Ihnen, wenn auch verspätet, vorlegen zu können.", "Obwohl diese unerwarteten technischen Hindernisse meinen Zeitplan durcheinanderbrachten, habe ich meine Verantwortung nicht aufgegeben.", "Ich hoffe, Sie haben Verständnis für diese Verzögerung, die durch technische Infrastrukturprobleme (höhere Gewalt) verursacht wurde."]
            },
            "5": {
                "baslangic": ["Leider erhielt ich gestern Nacht beim Einschalten meines Computers die kritische Fehlermeldung 'Boot Device Not Found'; meine NVMe SSD war physisch beschädigt und wurde vom BIOS nicht erkannt.", "Aufgrund eines aggressiven Ransomware-Angriffs auf meinen Computer wurden alle meine akademischen Dateien verschlüsselt, und ich wurde aus meinem eigenen System ausgesperrt.", "Ein versehentlich verschüttetes Getränk auf meiner Laptop-Tastatur verursachte einen sofortigen Kurzschluss auf dem Mainboard, und mein Gerät stellte unter Rauchentwicklung den Dienst ein."],
                "gelisme": ["Ich baute die Festplatte aus, schloss sie über ein externes forensisches Dock an einen anderen Computer an und verbrachte die ganze Nacht damit, Linux-basierte Wiederherstellungstools zu nutzen, um meine Daten zu retten.", "Mit der Hilfe eines befreundeten IT-Sicherheitsexperten ließen wir zwei Tage lang Entschlüsselungstools laufen und schafften es gerade noch, den Großteil der Dateien wiederherzustellen.", "Ich nahm meine Festplatte mit in ein Internetcafé, wo ich versuchte, meine Hausarbeit unter sehr eingeschränkten und unhygienischen Bedingungen von Grund auf neu zusammenzustellen."],
                "sonuc": ["Nach diesem überlebenswichtigen Kampf bin ich erleichtert, meine Dateien wiederhergestellt zu haben und sie Ihnen zu senden; bitte entschuldigen Sie die Verspätung aufgrund dieses Hardware-Desasters.", "Ich hätte fast mein gesamtes akademisches Archiv verloren, aber ich habe nicht aufgegeben und die Arbeit gerettet; ich bitte um Verzeihung für diese höhere Gewalt.", "Trotz dieses Katastrophenszenarios, das außerhalb meiner Kontrolle lag, habe ich meine Arbeit aus Respekt vor Ihrem Kurs fertiggestellt und eingereicht."]
            }
        }
    },
    "saglik": {
        "tr": {
            "1": {
                "baslangic": ["Mevsim geçişlerinin getirdiği ani hava değişimleri nedeniyle, son birkaç gündür şiddetli bir üst solunum yolu enfeksiyonu ve buna bağlı 39 dereceye varan yüksek ateşle mücadele etmekteyim.", "Dün gece tükettiğim bir gıdadan kaynaklandığını düşündüğüm akut mide rahatsızlığı ve şiddetli bulantı, beni çalışma masamdan defalarca kalkmak zorunda bıraktı ve performansımı sıfıra indirdi.", "Yoğun bilgisayar kullanımı ve uykusuzluk neticesinde gözlerimde oluşan aşırı hassasiyet ve konjonktivit başlangıcı, ekrana uzun süre bakmamı imkansız hale getirdiği için sık sık ara vermek zorunda kaldım."],
                "gelisme": ["Doktorumun önerdiği ilaçları alıp bir süre dinlendikten sonra, kendimi biraz toparlar toparlamaz, sorumluluğumu yerine getirmek adına hemen bilgisayar başına geçtim ve kalan gücümle çalışmamı sürdürdüm.", "Hastalığın verdiği halsizlik ve ilaçların yarattığı uyku haline rağmen, teslim tarihini kaçırmamak için büyük bir irade göstererek, yavaş da olsa ödevimi tamamlamak için elimden gelen gayreti gösterdim.", "Rapor alıp süreci uzatmak yerine, akademik takvime sadık kalmak adına, sağlığımı biraz zorlayarak da olsa çalışmamı nihayete erdirmeyi tercih ettim."],
                "sonuc": ["Sağlık durumumdan kaynaklanan bu fizyolojik engeller nedeniyle oluşan ufak gecikmeyi anlayışla karşılayacağınızı umuyor, ödevimi ekte sunuyorum.", "Tam kapasitemle istediğim hızı gösteremesem de ödevimi tamamlamış olmanın huzuruyla dosyamı iletiyorum, gecikme için özür dilerim.", "İyileşme sürecim devam etse de, dersinize olan saygımdan ötürü çalışmamı tamamladım; iyi çalışmalar dilerim."]
            },
            "3": {
                "baslangic": ["Kronikleşen migren rahatsızlığım, sınav döneminin stresiyle birleşince dün gece auralı ve şiddetli bir atak şeklinde nüksetti; ışığa ve sese karşı aşırı hassasiyetim nedeniyle 24 saattir karanlık odada kalmam gerekti.", "Aniden yükselen ateş ve kontrol altına alınamayan titreme nöbetleri nedeniyle dün geceyi hastanenin acil servisinde, serum takılı halde ve müşahede altında geçirmek zorunda kaldım.", "Dişime yapılan acil cerrahi müdahale sonrasında gelişen beklenmedik komplikasyonlar ve dayanılmaz ağrı, mental olarak odaklanmamı tamamen engellediği için çalışmam aksadı."],
                "gelisme": ["Doktorun 'kesin yatak istirahati' vermesine rağmen, atağım hafifler hafiflemez, henüz tam iyileşmeden ödevimi bitirmek için masaya oturdum ve büyük bir baş ağrısıyla mücadele ederek yazdım.", "Hastaneden taburcu edilir edilmez, eve dönüp dinlenmek yerine akademik sorumluluğumu önceliklendirerek, kolumdaki bantla bilgisayar başına geçtim ve çalışmamı tamamladım.", "Güçlü ağrı kesicilerin etkisiyle ayakta durmaya çalışarak, zor da olsa projemi tamamladım; çünkü bu ödevi zamanında vermemek benim için bir seçenek değildi."],
                "sonuc": ["Bu ciddi ve acılı sağlık sorunu nedeniyle oluşan mecburi gecikmeyi, içinde bulunduğum zor durumu göz önüne alarak maruz görmenizi dilerim.", "Sağlığım elverdiği ölçüde en kısa sürede teslimatı yapıyorum, raporum da mevcuttur, anlayışınız için teşekkürler.", "Elimde olmayan bu sağlık problemlerine ve fiziksel acıya rağmen ödevimi tamamlamanın verdiği sorumluluk bilinciyle dosyamı iletiyorum."]
            },
            "5": {
                "baslangic": ["Maalesef karın bölgesindeki şiddetli ağrı şikayetiyle gittiğim hastanede, akut apandisit teşhisi konularak acilen ameliyata alındım; anestezi ve cerrahi süreç planlarımı tamamen devre dışı bıraktı.", "Birinci derece bir yakınımın ani gelişen kalp krizi şüphesiyle yoğun bakıma kaldırılması sonucu, tüm aile olarak günlerdir hastane koridorlarında endişeli bir bekleyiş içindeyiz.", "Geçirdiğim talihsiz bir trafik kazası sonucu vücudumda oluşan yumuşak doku zedelenmeleri ve sağ kolumdaki travma nedeniyle, bilgisayar kullanmam ve klavye ile yazı yazmam fiziksel olarak imkansızdı."],
                "gelisme": ["Henüz dikişlerim tazeyken ve hastane sürecim devam ederken, bir arkadaşımın yardımıyla laptopumu hastaneye getirterek, hasta yatağımda yarı oturur vaziyette ödevimi tamamladım.", "Bu büyük psikolojik yıkım ve fiziksel yorgunluğun arasında, zihnimi toplayabildiğim ilk fırsatta, hastane kantininde köşeye çekilerek görevimi yerine getirmeye çalıştım.", "Polis tutanakları, röntgen çekimleri ve tıbbi işlemler biter bitmez, tek elimi kullanarak güçlükle ve büyük bir acıyla da olsa çalışmamı son haline getirdim."],
                "sonuc": ["Hayatımın en zor ve acılı günlerinden birini geçirmeme rağmen, dersinize olan saygımdan dolayı ödevimi size sunuyorum; epikriz raporum ektedir.", "Bu olağanüstü mücbir sebep ve sağlık krizi karşısında göstereceğiniz anlayış ve tolerans için şimdiden minnettarım.", "Böylesine bir felaketin ve acının gölgesinde bile akademik sorumluluğumu aksatmamak için insanüstü bir çaba harcadım, saygılarımla."]
            }
        },
        "en": {
            "1": {"baslangic": ["Due to sudden weather changes, I have been fighting a severe upper respiratory infection and high fever for the past few days.", "Acute stomach issues and nausea, which I suspect were caused by food poisoning, forced me to leave my desk repeatedly.", "Extreme sensitivity in my eyes due to prolonged computer usage made it impossible for me to look at the screen for extended periods."], "gelisme": ["After taking my medication and resting, I went straight back to my computer to fulfill my responsibility as soon as I felt slightly better.", "Despite the fatigue caused by the illness, I showed great willpower to complete my assignment so as not to miss the deadline.", "Instead of getting a medical report and extending the process, I preferred to push my health limits to stick to the academic calendar."], "sonuc": ["I hope you can understand this slight delay caused by physiological obstacles related to my health.", "Although I couldn't work at full capacity, I am submitting my file with the peace of mind of having completed the assignment.", "Even though my recovery process is ongoing, I completed my work out of respect for your course."]},
            "3": {"baslangic": ["My chronic migraine condition triggered a severe attack due to stress; I had to stay in a dark room for 24 hours due to light sensitivity.", "Due to a sudden high fever and uncontrollable shivering, I had to spend last night in the emergency room on an IV drip.", "Unexpected complications and unbearable pain following a surgical dental procedure completely prevented me from focusing."], "gelisme": ["Although the doctor prescribed rest, I sat down at my desk to finish my assignment as soon as the attack subsided, even before fully recovering.", "As soon as I was discharged from the hospital, instead of going home to rest, I went to my computer with the band on my arm and finished my work.", "I tried to stay upright under the influence of strong painkillers and completed my project, albeit with difficulty, because not submitting was not an option."], "sonuc": ["I ask you to excuse this mandatory delay caused by this serious and painful health issue, considering my difficult situation.", "I am submitting the assignment as soon as my health allows; my medical report is available if needed.", "Despite these health problems and physical pain beyond my control, I am sending my file with the consciousness of having completed my task."]},
            "5": {"baslangic": ["Unfortunately, I was diagnosed with acute appendicitis and taken into emergency surgery; the anesthesia and surgical process completely disrupted my plans.", "Due to a close family member being rushed to intensive care with a suspected heart attack, my entire family has been in the hospital corridors for days.", "Because of soft tissue injuries and trauma to my right arm resulting from a traffic accident, using a keyboard was physically impossible for me."], "gelisme": ["While my stitches were still fresh and my hospital stay continued, I had my laptop brought to the hospital and completed my assignment in my hospital bed.", "Amidst this great psychological destruction, I tried to fulfill my duty in the hospital cafeteria at the first opportunity I could gather my thoughts.", "As soon as the medical procedures were over, I finalized my work, albeit with great difficulty and pain, using only one hand."], "sonuc": ["Despite having one of the most difficult days of my life, I am submitting my assignment out of respect for your course; my report is attached.", "I am grateful in advance for your understanding regarding this extraordinary force majeure and health crisis.", "Even in the shadow of such a disaster, I made a superhuman effort not to neglect my academic responsibility."]}
        },
        "de": {
            "1": {"baslangic": ["Aufgrund der plötzlichen Wetterumschwünge kämpfe ich seit einigen Tagen mit einer schweren Infektion und hohem Fieber.", "Akute Magenbeschwerden und Übelkeit, die vermutlich durch eine Lebensmittelvergiftung verursacht wurden, zwangen mich gestern Nacht immer wieder dazu, meine Arbeit zu unterbrechen.", "Eine extreme Empfindlichkeit meiner Augen durch übermäßige Computernutzung machte es mir unmöglich, längere Zeit auf den Bildschirm zu schauen."], "gelisme": ["Nachdem ich meine Medikamente eingenommen und mich ausgeruht hatte, setzte ich mich sofort wieder an den Computer, um meine Verantwortung zu erfüllen, sobald ich mich etwas besser fühlte.", "Trotz der krankheitsbedingten Erschöpfung zeigte ich großen Willen, meine Hausarbeit fertigzustellen, um die Frist nicht zu verpassen.", "Anstatt ein ärztliches Attest zu holen und den Prozess zu verlängern, zog ich es vor, meine Gesundheit zu belasten, um den akademischen Kalender einzuhalten."], "sonuc": ["Ich hoffe, Sie haben Verständnis für diese leichte Verzögerung, die durch physiologische Hindernisse aufgrund meines Gesundheitszustands verursacht wurde.", "Obwohl ich nicht mit voller Kapazität arbeiten konnte, sende ich Ihnen meine Datei mit der Gewissheit, die Aufgabe erledigt zu haben.", "Auch wenn mein Genesungsprozess noch andauert, habe ich meine Arbeit aus Respekt vor Ihrem Kurs fertiggestellt."]},
            "3": {"baslangic": ["Meine chronische Migräne löste stressbedingt einen schweren Anfall aus; aufgrund der Lichtempfindlichkeit musste ich 24 Stunden in einem dunklen Raum verbringen.", "Wegen plötzlichem hohem Fieber und unkontrollierbarem Schüttelfrost musste ich die letzte Nacht in der Notaufnahme am Tropf verbringen.", "Unerwartete Komplikationen und unerträgliche Schmerzen nach einem chirurgischen Zahneingriff hinderten mich völlig daran, mich zu konzentrieren."], "gelisme": ["Obwohl der Arzt Ruhe verordnete, setzte ich mich an den Schreibtisch, um meine Arbeit zu beenden, sobald der Anfall nachließ, noch bevor ich vollständig genesen war.", "Sobald ich aus dem Krankenhaus entlassen wurde, setzte ich mich mit dem Verband am Arm an den Computer und beendete meine Arbeit, anstatt mich auszuruhen.", "Ich versuchte, unter dem Einfluss starker Schmerzmittel aufrecht zu bleiben, und beendete mein Projekt, wenn auch mit Schwierigkeiten, da eine Nichtabgabe keine Option war."], "sonuc": ["Ich bitte Sie, diese zwingende Verzögerung aufgrund dieses ernsten und schmerzhaften Gesundheitsproblems unter Berücksichtigung meiner schwierigen Situation zu entschuldigen.", "Ich reiche die Arbeit so schnell ein, wie es meine Gesundheit zulässt; mein ärztliches Attest liegt vor.", "Trotz dieser gesundheitlichen Probleme und körperlichen Schmerzen, die außerhalb meiner Kontrolle lagen, sende ich meine Datei im Bewusstsein, meine Aufgabe erfüllt zu haben."]},
            "5": {"baslangic": ["Leider wurde bei mir eine akute Blinddarmentzündung diagnostiziert und ich musste sofort operiert werden; die Anästhesie und der chirurgische Eingriff haben meine Pläne völlig durchkreuzt.", "Da ein enges Familienmitglied mit Verdacht auf Herzinfarkt auf die Intensivstation eingeliefert wurde, befindet sich meine ganze Familie seit Tagen in den Krankenhausfluren.", "Aufgrund von Weichteilverletzungen und einem Trauma am rechten Arm infolge eines Verkehrsunfalls war es mir physisch unmöglich, eine Tastatur zu benutzen."], "gelisme": ["Während meine Fäden noch frisch waren und mein Krankenhausaufenthalt andauerte, ließ ich mir meinen Laptop ins Krankenhaus bringen und beendete meine Arbeit im Krankenbett.", "Inmitten dieser großen psychischen Belastung versuchte ich, meine Pflicht in der Krankenhauskantine bei der ersten Gelegenheit zu erfüllen.", "Sobald die medizinischen Prozeduren abgeschlossen waren, stellte ich meine Arbeit fertig, wenn auch unter großen Schwierigkeiten und Schmerzen, indem ich nur eine Hand benutzte."], "sonuc": ["Obwohl ich einen der schwersten Tage meines Lebens hatte, reiche ich meine Arbeit aus Respekt vor Ihrem Kurs ein; mein Bericht liegt bei.", "Ich bin Ihnen im Voraus dankbar für Ihr Verständnis angesichts dieser außergewöhnlichen höheren Gewalt und Gesundheitskrise.", "Selbst im Schatten einer solchen Katastrophe habe ich übermenschliche Anstrengungen unternommen, um meine akademische Verantwortung nicht zu vernachlässigen."]}
        }
    },
    "aile": {
        "tr": {
            "1": {"baslangic": ["Şehir dışından habersiz gelen kalabalık bir misafir grubu nedeniyle evdeki çalışma ortamım tamamen kayboldu ve odaklanabileceğim sessiz bir alan bulmam imkansızlaştı.", "Kardeşimin okul projesinde yaşadığı büyük bir krizi çözmek adına, ebeveynlerimin de ricasıyla tüm gecemi ona yardım etmeye ayırmak zorunda kaldım.", "Evimizde yapılan beklenmedik bir tadilat ve oluşan gürültü nedeniyle, gün boyu bilgisayarımı açıp verimli bir şekilde çalışabileceğim bir ortam oluşmadı."], "gelisme": ["Misafirler uyuduktan sonra gece geç saatlerde sessizliği yakalayabildim ve uykusuz kalma pahasına sabaha kadar çalışarak ödevimi tamamladım.", "Kendi ödevimi, onun teslim süresi daha erken olduğu için ikinci plana atmak zorunda kaldım ve ancak sabah saatlerinde kendi projeme odaklanabildim.", "Evin tozu ve gürültüsü dindikten sonra, çalışma odamı temizleyip düzenledim ve kaybolan zamanı telafi etmek için aralıksız çalıştım."], "sonuc": ["Ailevi sorumluluklarımdan kaynaklanan bu planlama hatası ve gecikme için özür diler, çalışmamı ekte sunarım.", "Elimde olmayan bu ev içi yoğunluk nedeniyle oluşan gecikmeyi anlayışla karşılayacağınızı umuyorum.", "Çalışma ortamımdaki bu geçici aksaklığa rağmen ödevimi tamamlamayı başardım, saygılarımla."]},
            "3": {"baslangic": ["Ailevi çok özel ve acil bir meseleden dolayı, hazırlıksız bir şekilde memlekete gitmem gerekti; yolculuk süresince ve vardığım yerde internet erişimim maalesef yoktu.", "Evimizin su tesisatında meydana gelen büyük bir patlama sonucu tüm daireyi su bastı; bilgisayarımı ve notlarımı son anda kurtararak gün boyu tahliye işlemleriyle uğraştık.", "Aile büyüklerimden birinin ani rahatsızlığı ve bakım ihtiyacı doğması sebebiyle, tüm günümü hastane ve ev arasında mekik dokuyarak geçirmek zorunda kaldım."], "gelisme": ["Yanımda laptopum olmasına rağmen, bulunduğum köy/kasaba şartlarında stabil bir bağlantı bulabilmek için ilçe merkezine gitmem ve ödevimi oradan göndermem gerekti.", "Bu kaotik ortamda, ıslanan eşyaların arasında kendime kuru bir köşe bularak, yaşadığım strese rağmen ödevimi tamamlamaya çalıştım.", "Refakatçi olarak kaldığım süre boyunca, hastane sandalyesinde ve kısıtlı imkanlarla çalışmamı sürdürmeye gayret ettim ancak şartlar beni çok zorladı."], "sonuc": ["Bu beklenmedik ailevi kriz ve seyahat nedeniyle yaşanan gecikmeyi maruz görmenizi dilerim.", "Yaşadığımız bu maddi hasar ve manevi yorgunluk içinde bile dersimi ihmal etmemeye çalıştım, anlayışınız için teşekkürler.", "İnsani bir durumdan kaynaklanan bu gecikmeyi telafi etmek adına çalışmamı en iyi şekilde hazırlayıp sunuyorum."]},
            "5": {"baslangic": ["Maalesef ailemizden çok sevdiğimiz bir büyüğümüzü ani bir şekilde kaybettik; cenaze işlemleri ve taziye süreci nedeniyle apar topar şehir dışına çıkmak zorunda kaldım.", "Ailemizin karıştığı ciddi bir adli vaka/kaza nedeniyle günlerdir karakol ve adliye koridorlarında, büyük bir hukuki ve psikolojik savaş vermekteyiz.", "Yaşadığımız bölgedeki doğal afet uyarısı ve evimizin hasar görmesi nedeniyle, yetkililerin talimatıyla evimizi tahliye edip geçici barınma alanına geçmek zorunda kaldık."], "gelisme": ["Bu derin acı ve yas sürecinde, akademik sorumluluklarımı düşünmek çok zor olsa da, cenaze defnedildikten sonra ilk fırsatta bilgisayar başına geçip ödevimi tamamladım.", "Psikolojik olarak çökmüş durumda olmama rağmen, geleceğimi etkileyecek bu dersi bırakmamak adına, uykusuz ve bitkin bir halde bu çalışmayı hazırladım.", "Güvenli bir alana geçip, internet ve elektrik bulabildiğim ilk anda, yaşadığımız travmaya rağmen hayata tutunmak adına ödevimi yapmaya çalıştım."], "sonuc": ["İçinde bulunduğum bu yas ve matem sürecinde yaşanan gecikmeyi, insani değerler çerçevesinde anlayışla karşılayacağınızı umuyorum.", "Hayatımın en zor dönemlerinden birini yaşarken gösterdiğim bu akademik çabayı takdir edeceğinize inanıyor, çalışmamı sunuyorum.", "Böylesine bir yıkımın ortasında bile sorumluluğumu yerine getirdim, gecikme için en derin özürlerimi sunarım."]}
        },
        "en": {
            "1": {"baslangic": ["Due to a large group of unexpected guests arriving from out of town, my working environment at home completely disappeared.", "To resolve a major crisis with my sibling's school project, I had to dedicate my entire night to helping them at my parents' request.", "Due to unexpected renovations and noise in our house, I couldn't find a suitable environment to open my computer and work efficiently all day."], "gelisme": ["I was only able to find silence late at night after the guests went to sleep, and I worked until morning at the cost of losing sleep to complete my assignment.", "I had to prioritize their project since their deadline was earlier, and I could only focus on my own project in the early morning hours.", "After the dust and noise settled, I cleaned my study room and worked non-stop to make up for the lost time."], "sonuc": ["I apologize for this planning error and delay caused by my family responsibilities and submit my work attached.", "I hope you understand the delay caused by this household busyness which was out of my control.", "Despite this temporary disruption in my work environment, I managed to complete my assignment."]},
            "3": {"baslangic": ["Due to a very private and urgent family matter, I had to travel to my hometown unprepared; I had no internet access during the journey.", "A major burst in our water pipes flooded our entire apartment; I barely saved my computer and dealt with evacuation procedures all day.", "Due to the sudden illness of an elderly family member requiring care, I had to spend my entire day shuttling between the hospital and home."], "gelisme": ["Although I had my laptop, I had to travel to the town center to find a stable connection given the conditions in the village I was in.", "In this chaotic environment, I found a dry corner among wet belongings and tried to complete my assignment despite the stress.", "During the time I stayed as a companion, I tried to continue my work on a hospital chair with limited resources."], "sonuc": ["I ask you to excuse the delay caused by this unexpected family crisis and travel.", "Even amidst this material damage and emotional fatigue, I tried not to neglect my course.", "I am submitting my work to make up for this delay caused by a humanitarian situation."]},
            "5": {"baslangic": ["Unfortunately, we suddenly lost a beloved family elder; I had to leave the city in a rush for the funeral procedures.", "Due to a serious legal case involving our family, we have been fighting a major legal battle in police stations and courthouses for days.", "Due to a natural disaster warning in our area and damage to our house, we were forced to evacuate our home by order of the authorities."], "gelisme": ["Although it was very hard to think about academic responsibilities during this deep pain and mourning, I sat at the computer at the first opportunity after the funeral.", "Despite being psychologically devastated, I prepared this work sleepless and exhausted so as not to fail this course which affects my future.", "The moment I reached a safe area and found internet and electricity, I tried to do my assignment to hold on to life despite the trauma we experienced."], "sonuc": ["I hope you will understand the delay experienced during this process of mourning and grief within the framework of human values.", "I believe you will appreciate this academic effort I showed while going through one of the most difficult periods of my life.", "I fulfilled my responsibility even in the middle of such destruction; I apologize for the delay."]}
        },
        "de": {
            "1": {"baslangic": ["Aufgrund einer großen Gruppe unerwarteter Gäste von außerhalb verschwand meine Arbeitsumgebung zu Hause vollständig.", "Um eine große Krise im Schulprojekt meines Geschwisters zu lösen, musste ich auf Bitte meiner Eltern die ganze Nacht damit verbringen, ihm zu helfen.", "Aufgrund unerwarteter Renovierungsarbeiten und Lärm in unserem Haus konnte ich den ganzen Tag keine geeignete Umgebung finden, um effizient zu arbeiten."], "gelisme": ["Erst spät in der Nacht, als die Gäste schliefen, fand ich Ruhe und arbeitete bis zum Morgen durch, um meine Hausarbeit fertigzustellen.", "Ich musste sein Projekt priorisieren, da seine Frist früher war, und konnte mich erst in den frühen Morgenstunden auf mein eigenes Projekt konzentrieren.", "Nachdem sich Staub und Lärm gelegt hatten, reinigte ich mein Arbeitszimmer und arbeitete pausenlos, um die verlorene Zeit aufzuholen."], "sonuc": ["Ich entschuldige mich für diesen Planungsfehler und die Verzögerung aufgrund meiner familiären Pflichten und reiche meine Arbeit im Anhang ein.", "Ich hoffe, Sie haben Verständnis für die Verzögerung durch diese häusliche Hektik, die außerhalb meiner Kontrolle lag.", "Trotz dieser vorübergehenden Störung meiner Arbeitsumgebung habe ich es geschafft, meine Hausarbeit fertigzustellen."]},
            "3": {"baslangic": ["Aufgrund einer sehr privaten und dringenden Familienangelegenheit musste ich unvorbereitet in meine Heimatstadt reisen; während der Fahrt hatte ich kein Internet.", "Ein großer Rohrbruch in unserer Wasserleitung überflutete unsere gesamte Wohnung; ich rettete meinen Computer in letzter Sekunde.", "Wegen der plötzlichen Erkrankung eines älteren Familienmitglieds, das Pflege benötigte, verbrachte ich den ganzen Tag damit, zwischen Krankenhaus und Zuhause zu pendeln."], "gelisme": ["Obwohl ich meinen Laptop dabei hatte, musste ich ins Stadtzentrum fahren, um unter den Bedingungen im Dorf eine stabile Verbindung zu finden.", "In dieser chaotischen Umgebung fand ich eine trockene Ecke zwischen nassen Gegenständen und versuchte, meine Arbeit trotz des Stresses zu beenden.", "Während ich als Begleitperson blieb, versuchte ich, meine Arbeit auf einem Krankenhausstuhl mit begrenzten Mitteln fortzusetzen."], "sonuc": ["Ich bitte Sie, die Verzögerung aufgrund dieser unerwarteten Familienkrise und Reise zu entschuldigen.", "Selbst inmitten dieses materiellen Schadens und der emotionalen Erschöpfung habe ich versucht, meinen Kurs nicht zu vernachlässigen.", "Ich reiche meine Arbeit ein, um diese durch eine humanitäre Situation verursachte Verzögerung auszugleichen."]},
            "5": {"baslangic": ["Leider haben wir plötzlich ein geliebtes Familienmitglied verloren; ich musste für die Beerdigung überstürzt die Stadt verlassen.", "Aufgrund eines ernsten Rechtsfalls, in den unsere Familie verwickelt ist, kämpfen wir seit Tagen in Polizeiwachen und Gerichten.", "Aufgrund einer Naturkatastrophenwarnung in unserem Gebiet und Schäden an unserem Haus mussten wir unser Zuhause auf Anordnung der Behörden evakuieren."], "gelisme": ["Obwohl es sehr schwer war, in dieser tiefen Trauer an akademische Pflichten zu denken, setzte ich mich bei der ersten Gelegenheit nach der Beerdigung an den Computer.", "Obwohl ich psychisch am Boden zerstört war, bereitete ich diese Arbeit schlaflos und erschöpft vor, um diesen für meine Zukunft wichtigen Kurs nicht zu gefährden.", "Sobald ich einen sicheren Bereich erreichte und Internet sowie Strom fand, versuchte ich, meine Hausarbeit zu erledigen, um trotz des Traumas am Alltag festzuhalten."], "sonuc": ["Ich hoffe, Sie haben im Rahmen menschlicher Werte Verständnis für die Verzögerung während dieser Zeit der Trauer.", "Ich glaube, Sie werden diese akademische Anstrengung zu schätzen wissen, die ich in einer der schwierigsten Phasen meines Lebens gezeigt habe.", "Selbst inmitten einer solchen Zerstörung habe ich meine Verantwortung erfüllt; ich entschuldige mich für die Verspätung."]}
        }
    },
    "ulasim": {
        "tr": {
            "1": {"baslangic": ["Şehir trafiğindeki beklenmedik kilitlenme ve toplu taşımadaki arıza nedeniyle, eve planladığımdan çok geç vardım.", "Kullandığım otobüs hattındaki sefer iptali nedeniyle durakta uzun süre beklemek zorunda kaldım.", "Özel aracımla eve dönerken lastiğimin patlaması bana çok değerli saatler kaybettirdi."], "gelisme": ["Eve adım atar atmaz, yorgunluğuma bakmadan bilgisayar başına geçip çalışmaya başladım.", "Kaybettiğim zamanı telafi etmek için çok hızlı çalışarak ödevimi tamamladım ancak saati kaçırdım.", "Yol yardımını bekleyip vakit kaybetmek yerine sorunu kendim çözüp eve ulaştım ve projemi bitirdim."], "sonuc": ["Trafik kaynaklı bu elde olmayan gecikme için özür diler, tamamladığım çalışmamı ekte sunarım.", "Planlanmayan bu aksaklık nedeniyle oluşan kısa süreli gecikmeyi anlayışla karşılayacağınızı umuyorum.", "Yetiştirmek için çok çabaladım, gecikmeli de olsa ödevimi kabul buyurmanızı rica ederim."]},
            "3": {"baslangic": ["Şehirlerarası yolculuk yaptığım otobüs motor arızası yaptı ve saatlerce dağ başında mahsur kaldık.", "Şahsi aracımla seyir halindeyken aracım hararet yaptı ve yolda kaldım; çekici gelmesi geceyi buldu.", "Havalimanındaki sistemsel arızalar nedeniyle seferim rötara girdi ve bekleme salonunda internet yoktu."], "gelisme": ["Yeni otobüs gelene kadar soğukta bekledik; internete eriştiğim ilk saniyede dosyamı yüklemeye çalıştım.", "Serviste tamiri beklerken, telefondan zor şartlarda ödevimi tamamlamaya gayret ettim.", "Yolculuk boyunca yaşadığım stres ve yorgunluğa rağmen, varır varmaz uyumayıp ödevimi bitirdim."], "sonuc": ["Yolda mahsur kalmamdan kaynaklanan bu mücbir sebep dolayısıyla yaşanan gecikmeyi maruz görmenizi dilerim.", "Elimde olmayan ulaşım engellerine rağmen sorumluluğumu yerine getirdim, dosyam ektedir.", "Seyahat sırasındaki bu talihsizlikler planlarımı bozsa da ödevimi tamamladım."]},
            "5": {"baslangic": ["Maalesef eve dönerken zincirleme bir trafik kazasına karıştım; aracımda ağır maddi hasar oluştu.", "Bulunduğum toplu taşıma aracının karıştığı bir kaza nedeniyle olay yerine ambulans ve polis geldi.", "Yoğun fırtına nedeniyle bindiğim araç yolda mahsur kaldı ve ekiplerin bizi kurtarmasını bekledik."], "gelisme": ["Hastanede yapılan kontroller ve polis tutanakları bittikten sonra, şoka rağmen eve gelip bu ödevi gönderiyorum.", "Kaza yerindeki kargaşada laptopumun zarar görüp görmediğini bile kontrol edememiştim; neyse ki çalışıyor.", "Hayat güvenliğimizin tehlikede olduğu o anlarda bile aklımda dersim vardı; kurtarıldıktan sonra ilk işim bu oldu."], "sonuc": ["Büyük bir hayati tehlike atlattığım bu kazadan sonra, gecikmeli de olsa ödevimi göndermemi takdir edeceğinizi umuyorum.", "Canımızı zor kurtardığımız bu felaketin gölgesinde, akademik sorumluluğumu unutmadım; raporlarım ektedir.", "Yaşadığım travmaya rağmen ödevimi tamamladım, bu olağanüstü durumu anlayışla karşılayacağınızı biliyorum."]}
        },
        "en": {
            "1": {"baslangic": ["Due to an unexpected gridlock in city traffic and a breakdown in public transport, I arrived home much later than planned.", "Because of a cancellation on my bus route, I had to wait at the stop for a long time, disrupting my schedule.", "A flat tire while driving home in my private car cost me very valuable hours."], "gelisme": ["As soon as I stepped into the house, regardless of my fatigue, I sat at the computer and started working.", "I worked very fast to make up for the lost time and completed my assignment, but I missed the deadline slightly.", "Instead of wasting time waiting for roadside assistance, I fixed the issue myself, got home, and finished my project."], "sonuc": ["I apologize for this unavoidable delay caused by traffic and submit my completed work attached.", "I hope you understand the short delay caused by this unplanned disruption.", "I tried very hard to make it on time; I ask you to accept my assignment despite the delay."]},
            "3": {"baslangic": ["The intercity bus I was traveling on had an engine failure, and we were stranded in a remote area for hours.", "My car overheated while driving, and I was stranded; it took until midnight for the tow truck to arrive.", "Due to system failures at the airport, my flight was delayed, and there was no internet access in the waiting lounge."], "gelisme": ["We waited in the cold until the new bus arrived; I tried to upload my file the first second I got internet access.", "While waiting for repairs at the service station, I tried to complete my assignment on my phone under difficult conditions.", "Despite the stress and fatigue of the journey, I didn't sleep as soon as I arrived but finished my assignment instead."], "sonuc": ["I ask you to excuse the delay caused by this force majeure of being stranded on the road.", "Despite transportation obstacles out of my control, I fulfilled my responsibility; my file is attached.", "Although these misfortunes during travel disrupted my plans, I completed my assignment."]},
            "5": {"baslangic": ["Unfortunately, I was involved in a chain traffic accident while returning home; my car suffered heavy material damage.", "Due to an accident involving the public transport vehicle I was in, ambulances and police arrived at the scene.", "Due to a severe storm, the vehicle I was in got stuck on the road, and we had to wait for rescue teams."], "gelisme": ["After hospital checks and police reports were done, despite the shock, I came home to send this assignment.", "In the chaos at the accident scene, I couldn't even check if my laptop was damaged; thankfully, it works.", "Even in those moments when our safety was at risk, I had my course in mind; this was the first thing I did after being rescued."], "sonuc": ["I hope you appreciate me sending my assignment, albeit late, after surviving a life-threatening accident.", "In the shadow of this disaster where we barely saved our lives, I did not forget my academic responsibility; my reports are attached.", "I completed my assignment despite the trauma I experienced; I know you will understand this extraordinary situation."]}
        },
        "de": {
            "1": {"baslangic": ["Aufgrund eines unerwarteten Staus im Stadtverkehr und einer Störung im öffentlichen Nahverkehr kam ich viel später als geplant nach Hause.", "Wegen eines Ausfalls auf meiner Buslinie musste ich lange an der Haltestelle warten, was meinen Zeitplan durcheinanderbrachte.", "Ein platter Reifen auf dem Heimweg mit meinem Privatwagen kostete mich sehr wertvolle Stunden."], "gelisme": ["Sobald ich das Haus betrat, setzte ich mich ungeachtet meiner Müdigkeit an den Computer und begann zu arbeiten.", "Ich arbeitete sehr schnell, um die verlorene Zeit aufzuholen, und beendete meine Hausarbeit, verpasste aber die Frist knapp.", "Anstatt Zeit mit Warten auf den Pannenhilfe zu verschwenden, löste ich das Problem selbst, kam nach Hause und beendete mein Projekt."], "sonuc": ["Ich entschuldige mich für diese unvermeidbare verkehrsbedingte Verzögerung und reiche meine fertige Arbeit im Anhang ein.", "Ich hoffe, Sie haben Verständnis für die kurze Verzögerung aufgrund dieser ungeplanten Störung.", "Ich habe mich sehr bemüht, es rechtzeitig zu schaffen; ich bitte Sie, meine Arbeit trotz der Verspätung anzunehmen."]},
            "3": {"baslangic": ["Der Überlandbus, mit dem ich reiste, hatte einen Motorschaden, und wir saßen stundenlang in einer abgelegenen Gegend fest.", "Mein Auto überhitzte während der Fahrt und ich blieb liegen; es dauerte bis Mitternacht, bis der Abschleppwagen kam.", "Aufgrund von Systemausfällen am Flughafen hatte mein Flug Verspätung, und es gab kein Internet in der Wartehalle."], "gelisme": ["Wir warteten in der Kälte, bis der neue Bus kam; ich versuchte, meine Datei in der ersten Sekunde hochzuladen, als ich Internet hatte.", "Während ich in der Werkstatt auf die Reparatur wartete, versuchte ich, meine Hausarbeit unter schwierigen Bedingungen auf meinem Handy fertigzustellen.", "Trotz des Stresses und der Müdigkeit der Reise schlief ich nicht, sobald ich ankam, sondern beendete meine Hausarbeit."], "sonuc": ["Ich bitte Sie, die Verzögerung aufgrund dieser höheren Gewalt (Festsitzen auf der Straße) zu entschuldigen.", "Trotz Transporthindernissen, die außerhalb meiner Kontrolle lagen, habe ich meine Verantwortung erfüllt; meine Datei liegt bei.", "Obwohl dieses Pech während der Reise meine Pläne durchkreuzte, habe ich meine Hausarbeit beendet."]},
            "5": {"baslangic": ["Leider wurde ich auf dem Heimweg in einen Kettenauffahrunfall verwickelt; mein Auto erlitt einen schweren Sachschaden.", "Aufgrund eines Unfalls mit dem öffentlichen Verkehrsmittel, in dem ich mich befand, kamen Krankenwagen und Polizei zum Unfallort.", "Aufgrund eines schweren Sturms blieb das Fahrzeug, in dem ich mich befand, auf der Straße stecken, und wir mussten auf Rettungsteams warten."], "gelisme": ["Nachdem die Krankenhausuntersuchungen und Polizeiberichte abgeschlossen waren, kam ich trotz des Schocks nach Hause, um diese Arbeit zu senden.", "Im Chaos am Unfallort konnte ich nicht einmal überprüfen, ob mein Laptop beschädigt war; zum Glück funktioniert er.", "Selbst in jenen Momenten, als unsere Sicherheit gefährdet war, dachte ich an meinen Kurs; dies war das Erste, was ich tat, nachdem ich gerettet wurde."], "sonuc": ["Ich hoffe, Sie schätzen es, dass ich meine Hausarbeit, wenn auch verspätet, sende, nachdem ich einen lebensbedrohlichen Unfall überlebt habe.", "Im Schatten dieser Katastrophe, bei der wir unser Leben kaum retten konnten, habe ich meine akademische Verantwortung nicht vergessen; meine Berichte liegen bei.", "Ich habe meine Arbeit trotz des Traumas beendet; ich weiß, dass Sie für diese außergewöhnliche Situation Verständnis haben werden."]}
        }
    }
}

def bahane_uret(kategori, dil, ciddiyet):
    try:
        havuz = LEGO_PARCALAR.get(kategori, LEGO_PARCALAR["teknik"])
        dil_havuzu = havuz.get(dil, havuz["tr"])
        seviye_havuzu = dil_havuzu.get(str(ciddiyet), dil_havuzu["1"])
        return f"{random.choice(seviye_havuzu['baslangic'])} {random.choice(seviye_havuzu['gelisme'])} {random.choice(seviye_havuzu['sonuc'])}"
    except:
        return "Teknik hata."

def calculate_reliability_score(ciddiyet, kategori, kelime_sayisi):
    base_score = min(kelime_sayisi * 1.5, 60)
    severity_bonus = int(ciddiyet) * 4
    random_factor = random.randint(-5, 10)
    return min(max(int(base_score + severity_bonus + random_factor + 20), 40), 99)

# --- 4. PDF (İMZA DESTEKLİ) ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'MAZERET DILEKCESI', 0, 1, 'C')
        self.ln(10)

def create_pdf(icerik, ogrenci_ad, ders, imza_path=None):
    pdf = PDF()
    pdf.add_page()
    tr_map = str.maketrans("ğĞıİşŞçÇöÖüÜ", "gGiIsScCoOuU")
    icerik_clean = icerik.translate(tr_map)
    ders_clean = ders.translate(tr_map)
    ad_clean = ogrenci_ad.translate(tr_map)
    
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Tarih: {datetime.date.today()}", 0, 1, 'R')
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"ILGILI MAKAMINA ({ders_clean})", 0, 1, 'L')
    pdf.ln(10)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 8, icerik_clean)
    pdf.ln(20)
    
    pdf.set_x(120)
    
    if imza_path and os.path.exists(imza_path):
        pdf.image(imza_path, x=130, y=pdf.get_y(), w=40)
        pdf.ln(25)
    else:
        pdf.ln(5)
        
    pdf.set_x(120)
    pdf.multi_cell(0, 5, f"{ad_clean}", 0, 'C')
    
    pdf.output("mazeret_dilekcesi.pdf")

# --- 5. ROTALAR ---
@app.route('/', methods=['GET', 'POST'])
def index():
    mail_metni = ""
    skor = 0
    skor_renk = "warning"
    
    conn = sqlite3.connect('mail_gecmisi.db')
    c = conn.cursor()
    
    if request.method == 'POST':
        ogrenci_ad = request.form.get('ogrenciAd') or "[Ogrenci]"
        ders = request.form.get('ders')
        hoca = request.form.get('hoca')
        tarih = request.form.get('tarih')
        dil = request.form.get('dil')
        tarz = request.form.get('tarz')
        kategori = request.form.get('kategori')
        ciddiyet = request.form.get('ciddiyet')
        imza_data = request.form.get('imzaVerisi')

        sablon = SABLONLAR.get(dil, SABLONLAR["tr"])
        konu = sablon["subject"].format(course=ders, student_name=ogrenci_ad)
        
        if tarz == "formal":
            hitap = sablon["salutation_formal"].format(lecturer=hoca)
            kapanis = sablon["closing_formal"].format(student_name=ogrenci_ad)
        else:
            hitap = sablon["salutation_informal"].format(lecturer=hoca)
            kapanis = sablon["closing_informal"].format(student_name=ogrenci_ad)
            
        giris = sablon["opening_sentence"].format(course=ders, date=tarih)
        bahane = bahane_uret(kategori, dil, ciddiyet)
        govde = f"{hitap}\n\n{giris}\n\n{bahane}\n\n{kapanis}"

        mail_metni = {"konu": konu, "icerik": govde}
        
        skor = calculate_reliability_score(ciddiyet, kategori, len(bahane.split()))
        if skor > 85: skor_renk = "success"
        elif skor > 60: skor_renk = "primary"
        else: skor_renk = "danger"

        imza_dosya_adi = None
        if imza_data and len(imza_data) > 100:
            try:
                header, encoded = imza_data.split(",", 1)
                data = base64.b64decode(encoded)
                imza_dosya_adi = "gecici_imza.png"
                with open(imza_dosya_adi, "wb") as f:
                    f.write(data)
            except:
                pass

        bugun = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        c.execute("INSERT INTO gecmis (tarih, ders, hoca, kategori, ciddiyet, icerik) VALUES (?, ?, ?, ?, ?, ?)",
                  (bugun, ders, hoca, kategori, ciddiyet, govde))
        conn.commit()
        
        create_pdf(govde, ogrenci_ad, ders, imza_dosya_adi)

    c.execute("SELECT kategori, count(*) FROM gecmis GROUP BY kategori")
    kategori_stats = dict(c.fetchall())
    c.execute("SELECT ders, count(*) FROM gecmis GROUP BY ders ORDER BY count(*) DESC LIMIT 5")
    ders_stats = dict(c.fetchall())
    c.execute("SELECT * FROM gecmis ORDER BY id DESC")
    gecmis = c.fetchall()
    conn.close()

    return render_template('index.html', mail=mail_metni, gecmis=gecmis, 
                           kategori_stats=kategori_stats, ders_stats=ders_stats,
                           skor=skor, skor_renk=skor_renk)

@app.route('/indir-pdf')
def indir_pdf():
    try:
        return send_file('mazeret_dilekcesi.pdf', as_attachment=True)
    except:
        return "Dosya yok."

@app.route('/indir-excel')
def indir_excel():
    conn = sqlite3.connect('mail_gecmisi.db')
    c = conn.cursor()
    c.execute("SELECT tarih, ders, hoca, kategori, ciddiyet, icerik FROM gecmis")
    rows = c.fetchall()
    conn.close()
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['Tarih', 'Ders', 'Hoca', 'Kategori', 'Ciddiyet', 'Mazeret Icerigi'])
    cw.writerows(rows)
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=mazeret_raporu.csv"
    output.headers["Content-type"] = "text/csv"
    return output

if __name__ == '__main__':
    app.run(debug=True)