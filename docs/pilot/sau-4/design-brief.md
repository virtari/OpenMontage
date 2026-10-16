# SAU-4: demojen selaamisen suunnittelukoe

16.10.2026 · vaihe: suunnan valinta · ei toteutushyväksyntää prototyypille

## Käyttäjän tavoite ja onnistuminen

Uusi OpenMontagen käyttäjä haluaa valita kolmesta mukana tulevasta demosta sopivan, ymmärtää mitä se esittelee ja tietää turvallisen seuraavan askeleen. Pilotti testaa suunnittelijan, katselmoijan ja ihmisen päätöksentekoa. Se ei päätä uuden varsinaisen sovelluksen rakentamisesta.

Lähtötiedot tulevat repon `render_demo.py`:stä: `code-to-screen` esittelee kehittäjän työnkulkua, vertailuja ja KPI-kortteja, `focusflow-pitch` pitch-esitystä Remotion-komponenteilla ja `world-in-numbers` otsikoita, tilastolukuja ja kaavioita. Demoja on kolme. Esikatseluvideoita ei tässä kokeessa generoida.

Oletus: käyttäjä voi tutkia konseptia ilman CLI-osaamista. Halutessaan hän näkee, mikä paikallinen dry-run-komento vastaa seuraavaa askelta. Toiminnon simulointi erotetaan aina oikeasta suorittamisesta.

## Vaihtoehdot

**A — lista ja tietopaneeli (suositus).** Kolme demoa näkyy vasemmalla; valitun demon sisältö ja seuraava askel oikealla. Käyttäjä voi verrata vaihtoehtoja palaamatta erilliselle sivulle. Mobiilissa lista ja tiedot pinotaan. Vahvuus: vähän valintoja, pysyvä konteksti ja yksiselitteinen eteneminen. Heikkous: kuvallinen selailu jää vaatimattomammaksi.

**B — visuaaliset kortit.** Kolme yhtä vahvaa korttia esittelee sisältötyypit. Demon valinnan jälkeen avataan sen tiedot omana näkymänään, jossa on paluu luetteloon. Mobiilissa kortit pinotaan. Vahvuus: visuaaliset erot auttavat sisällön tutkimista. Heikkous: tietojen vertailu vaatii enemmän siirtymistä; abstrakti kuvitus ei saa näyttää lupaukselta valmiista videosta.

Kummassakin käytetään samoja demoja, samaa käyttäjäpolkua ja samoja turvallisuusrajoja. Muotoilu on suomenkielinen paikallista suunnittelukoetta varten, ei tuotteen lopullinen kielipäätös.

## Tämän vaiheen toimitus

`options.html` näyttää kaksi staattista visuaalista luonnosta ja niiden perustelut. Siinä ei ole JavaScriptiä, oikeita demopainikkeita, palvelukutsuja, etäfontteja tai ulkoisia resursseja. Kuviot ovat CSS-kuvitusta; ne eivät ole renderöityjä demovideoita. Sivun sisäiset vertailulinkit toimivat, mutta kuvituksen toimintoelementit eivät käynnistä mitään.

Arilta tarvitaan **A:n tai B:n valinta**, tai konkreettinen muutos toiseen niistä. Suositus on A: kolme demoa mahtuu yksinkertaiseen työpöytään, ja valitun sisällön sekä seuraavan askeleen suhde näkyy heti.

## Valinnan jälkeen

Codex toteuttaa vain valitun klikattavan paikallisen prototyypin. Pääpolku: selaa demoja → valitse demo → tarkista tiedot → simuloi turvallinen esikatselutarkistus → näe simuloitu tulos. Ei oikeaa renderöintiä tai komentojen suorittamista. Tyhjä lista ja puuttuva esikatselu näytetään ymmärrettävästi.

Tarkistukset: 360/1280 pikselin leveydet, näppäimistö, näkyvä kohdistus, kontrollien nimet, tekstikontrastit ja tilojen selkeys. Tallenna kuvakaappaukset. Claude CLI katselmoi omassa työpuussaan; visuaaliset havainnot todennetaan selaimessa. Ari kokeilee yhtä skenaariota ja antaa visuaalisen hyväksynnän. Mahdollinen merge tarvitsee täsmällisen headin G4-päätöksen. Tässä vaiheessa näitä ei vielä merkitä tehdyiksi.

GitHub: https://github.com/virtari/OpenMontage/issues/7 · Paperclip: SAU-4. Paikallinen päätös- ja testiloki: `paperclip-local-pilot/evidence/SAU-4.json`.

## Esitysaineisto ja varmennuksen rajat

`options-overview.png` on samoista vaihtoehdoista tehty staattinen havainnekuva, ei HTML-sivun kuvakaappaus. Kuva tarkastettiin visuaalisesti; tekstit ja molemmat asettelut näkyvät kokonaan. HTML:n rakenne, ankkurit, demojen nimet sekä skriptien ja ulkoisten resurssien puuttuminen tarkistettiin. Paikallisen HTML-tiedoston avaaminen selainautomaatiolla estettiin protokollasäännöllä. Sääntöä ei kierretty; HTML avattiin Codexin tiedostopaneeliin ja vertailua varten tuotettiin paikallinen kuva. HTML:n selainasettelua tai prototyypin saavutettavuutta ei ole vielä varmennettu.
