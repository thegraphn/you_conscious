import unittest

from data_processing.filter_datafeed.filter_data_feed import isArticleVegan


class UnitTest(unittest.TestCase):

    def test_isArticleVegan(self):
        article_test_isArticleVegan_vegan: list = [
            "Sitzt super und ist vielseittig das Bikinitop Hemse von Dedicated. Durch herausnehmbare softe dreieckige Cups kann man je nach Belieben variieren und das Top nicht nur zum Baden sondern auch sonst im Sommer tragen. Durch das breite Band unter der Brust sitzt das Top fest und eignet sich so auch für sportliche Aktivitäten am Wasser. Durch die doppellagige Verarbeitung ist das Top außerdem blickdicht.",
            "https://cdn.loveco-shop.de/media/image/78/59/0c/dedicated-bikini-top-hemse-schwarz-lov14462-1_333x500.jpg",
            "https://track.webgains.com/click.html?wgcampaignid=1332125&wgprogramid=274885&product=1&wglinkid=2860445&productname=Bikini+Top+Hemse+Schwarz&wgtarget=https://loveco-shop.de/p/4518-dedicated-bikini-top-hemse-schwarz/?number=LOV14462&utm_source=webgains&utm_medium=cpo&utm_campaign=productfeed",
            "1604", "Women.Bekleidung.Bademode", "Damen", "Bademode > Badeanzüge > Damen", "39.90", "LOV14462",
            "Bikini Top Hemse Schwarz", "274885", "LOVECO - Fair & Vegan Fashion and Shoes", "2020-03-20 16:24:52",
            "Ja", "Paypal/Kauf auf Rechnung/Sofort Banking/Apple Pay/Kreditkarte/Nachnahme/Barzahlung bei Abholung",
            "https://cdn.loveco-shop.de/media/image/28/fd/9d/dedicated-bikini-top-hemse-schwarz-lov14462-1_1200x1800.jpg",
            "7333125049399", "Schwarz", "Maenner", "XS", "Vegan", "Öko", "Nachhaltig", "Fair Trade", "Bio",
            "Sitzt super und ist vielseittig das Bikinitop Hemse von Dedicated. Durch herausnehmbare softe dreiec",
            "1-2 Tage", "dedicated", "Recyceltes Polyester", "4518", "39.90", "3.90", "Deutschland", "EUR"]
        article_test_isArticleVegan_notVegan: list = ["34489", "13822", "HALLHUBER DE", "24283258309",
                                                      "https://www.awin1.com/pclick.php?p=24283258309&a=540557&m=13822",
                                                      "https://images2.productserve.com/?w=200&h=200&bg=white&trim=5&t=letterbox&url=ssl%3Astatic.hallhuber.com%2Fmedia%2Fcatalog%2Fproduct%2F3%2F0%2F3005689.jpg&feedId=34489&k=0b74547efd1de50a54a2a14535f093fb49b20154",
                                                      "https://images2.productserve.com/?w=70&h=70&bg=white&trim=5&t=letterbox&url=ssl%3Astatic.hallhuber.com%2Fmedia%2Fcatalog%2Fproduct%2F3%2F0%2F3005689.jpg&feedId=34489&k=0b74547efd1de50a54a2a14535f093fb49b20154",
                                                      "0", "0", "HALLHUBER", "1920712381107", "4058422225583",
                                                      "Hallhuber Seidenshirt im Materialmix für Damen in elfenbein",
                                                      "Vorne Seidensatin",
                                                      " Rückseite & Schulterpartie aus Jersey – der hochwertige Materialmix und ein Ausschnitt mit Fältchen machen das weit geschnittene HALLHUBER Seidenshirt aus! Weit geschnittenes SeidenshirtAusschnitt mit Seidenpaspel & FältchenVorderseite aus SeidensatinRückseite aus JerseyFließender Fall",
                                                      "https://www.hallhuber.com/de/seidenshirt-im-materialmix-elfenbein.html?___store=de",
                                                      "https://static.hallhuber.com/media/catalog/product/3/0/3005689.jpg",
                                                      "1 - 3 Werktage", ",", "EUR", "49.99", "5.00", "elfenbein",
                                                      "Damen", "0",
                                                      "Default Category > Bekleidung > Oberteile > T-Shirts"]

        result_vegan = isArticleVegan(article_test_isArticleVegan_vegan)
        result_notVegan = isArticleVegan(article_test_isArticleVegan_notVegan)
        self.assertEqual(result_vegan, result_vegan)
        self.assertEqual(result_notVegan, None)


unit_test = UnitTest()
UnitTest.test_isArticleVegan(unit_test)
