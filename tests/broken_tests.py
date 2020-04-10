def test_isArticleVegan(self):
    """
    Test the function isArticleVegan
    :return:
    """
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
                                                  "https://www.hallhuber.com/de/seidenshirt-im-materialmix"
                                                  "-elfenbein.html?___store=de",
                                                  "https://static.hallhuber.com/media/catalog/product/3/0/3005689.jpg",
                                                  "1 - 3 Werktage", ",", "EUR", "49.99", "5.00", "elfenbein",
                                                  "Damen", "0",
                                                  "Default Category > Bekleidung > Oberteile > T-Shirts"]

    filter = Filter()
    result_vegan = filter.isArticleVegan(article_test_isArticleVegan_vegan)
    result_notVegan = filter.isArticleVegan(article_test_isArticleVegan_notVegan)
    self.assertEqual(result_vegan, result_vegan)
    self.assertEqual(result_notVegan, None)


def test_addFeaturesArticle(self):
    ft_add = featuresAdder()
    article_test_addFeaturesArticle = ["", "", "", "", "", "", "", "", "", "", "119.99", "14962", "", "", "", "heine",
                                       "", "", "", "made in Green", "", "(organic cotton)", "", "",
                                       "Frauen > Bekleidung > Kleider > Cocktailkleider", "33943", "",
                                       "https://www.aboutyou.de/p/heine/spitzenkleid-982110", "", "", "", "",
                                       "https://images2.productserve.com/?w=70&h=70&bg=white&trim=5&t=letterbox&url=cdn.aboutyou.de%2Ffile%2F74355bf5b3030d258d223c2d9ad18dda%3Fwidth%3D2000%26height%3D2000&feedId=33943&k=8f499005e4a9318831d4eb1c95c516d9e74eda3c",
                                       "48,46,44,34,36,40,38", "", "", "", "",
                                       "Farben pro Pack: Eine Farbe pro Pack; Material: Weiteres Material; Ausschnitt: Rundhals-Ausschnitt; Trägerart: Weitere Trägerart; Design: Taillierter Schnitt, Verdeckter Reißverschluss, Materialmix; Muster: Unifarben; Ärmellänge: Dreiviertelarm; Länge: Knielang; Passform: Normale Passform; Elastizität: Nicht elastisch",
                                       "female", "",
                                       "http://cdn.aboutyou.de/file/308da6b536648614669aea5a1d108ee1?width=2000&height=2000",
                                       "", "",
                                       "http://cdn.aboutyou.de/file/125fdc19ee33c19fab1d131bfeb088af?width=2000&height=2000",
                                       "", "", "", "", "", "EUR", "", "7000",
                                       "6953123660092,6953123622373,6953123622366,6953123622311,6953123622328,6953123622342,6953123622335",
                                       "Spitzenkleid", "", "", "",
                                       "http://cdn.aboutyou.de/file/74355bf5b3030d258d223c2d9ad18dda?width=2000&height=2000",
                                       "0", "23787", "", "", "",
                                       "http://cdn.aboutyou.de/file/4a28a6346966bee4ddbf3ebeba52aa17?width=2000&height=2000",
                                       "", "", "", "", "", "24128724961",
                                       "http://cdn.aboutyou.de/file/f5a001dd1e4af8fb51a78d73cea6b7cc?width=2000&height=2000",
                                       "ABOUT YOU DE", "",
                                       "https://www.awin1.com/pclick.php?p=24128724961&a=540557&m=14962", "", "0.00",
                                       "", "", "",
                                       "Obermaterial:Polyamid=54%,Viskose=46%,Spitze:Polyester=100%,Futter:Polyester=100%",
                                       "schwarz", "", "982110",
                                       "http://cdn.aboutyou.de/file/e3840a03008da27db87cf9a61b428c64?width=2000&height=2000",
                                       "", "", "", "", "", ""]
    result_article_test_addFeaturesArticle = ft_add.addFeaturesArticle(article_test_addFeaturesArticle)
    golden_resul_tarticle_test_addFeaturesArticle = ["Bio-Baumwolle", "", "", "", "MADE IN GREEN by OEKO-TEX", "", "",
                                                     "", "", "", "119.99", "14962", "", "", "", "heine", "", "", "",
                                                     "made in Green", "", "(organic cotton)", "", "",
                                                     "Frauen > Bekleidung > Kleider > Cocktailkleider", "33943", "",
                                                     "https://www.aboutyou.de/p/heine/spitzenkleid-982110", "", "", "",
                                                     "",
                                                     "https://images2.productserve.com/?w=70&h=70&bg=white&trim=5&t=letterbox&url=cdn.aboutyou.de%2Ffile%2F74355bf5b3030d258d223c2d9ad18dda%3Fwidth%3D2000%26height%3D2000&feedId=33943&k=8f499005e4a9318831d4eb1c95c516d9e74eda3c",
                                                     "48,46,44,34,36,40,38", "", "", "", "",
                                                     "Farben pro Pack: Eine Farbe pro Pack; Material: Weiteres Material; Ausschnitt: Rundhals-Ausschnitt; Trägerart: Weitere Trägerart; Design: Taillierter Schnitt, Verdeckter Reißverschluss, Materialmix; Muster: Unifarben; Ärmellänge: Dreiviertelarm; Länge: Knielang; Passform: Normale Passform; Elastizität: Nicht elastisch",
                                                     "female", "",
                                                     "http://cdn.aboutyou.de/file/308da6b536648614669aea5a1d108ee1?width=2000&height=2000",
                                                     "", "",
                                                     "http://cdn.aboutyou.de/file/125fdc19ee33c19fab1d131bfeb088af?width=2000&height=2000",
                                                     "", "", "", "", "", "EUR", "", "7000",
                                                     "6953123660092,6953123622373,6953123622366,6953123622311,6953123622328,6953123622342,6953123622335",
                                                     "Spitzenkleid", "", "", "",
                                                     "http://cdn.aboutyou.de/file/74355bf5b3030d258d223c2d9ad18dda?width=2000&height=2000",
                                                     "0", "23787", "", "", "",
                                                     "http://cdn.aboutyou.de/file/4a28a6346966bee4ddbf3ebeba52aa17?width=2000&height=2000",
                                                     "", "", "", "", "", "24128724961",
                                                     "http://cdn.aboutyou.de/file/f5a001dd1e4af8fb51a78d73cea6b7cc?width=2000&height=2000",
                                                     "ABOUT YOU DE", "",
                                                     "https://www.awin1.com/pclick.php?p=24128724961&a=540557&m=14962",
                                                     "", "0.00", "", "", "",
                                                     "Obermaterial:Polyamid=54%,Viskose=46%,Spitze:Polyester=100%,Futter:Polyester=100%",
                                                     "schwarz", "", "982110",
                                                     "http://cdn.aboutyou.de/file/e3840a03008da27db87cf9a61b428c64?width=2000&height=2000",
                                                     "", "", "", "", "", ""]
    self.assertEqual(result_article_test_addFeaturesArticle, golden_resul_tarticle_test_addFeaturesArticle)
