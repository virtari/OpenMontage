# A-prototyypin kokeilu

Ari valitsi listan ja tietopaneelin yhdistelmän 16.10.2026. `prototype.html` on yksi paikallinen HTML-tiedosto: avaa se itse selaimessa. Erillistä palvelinta tai asennusta ei tarvita. Valinnat katoavat sivun uudelleenlatauksessa. `options.html` ja `options-overview.png` säilyvät aiempien luonnosten vertailuaineistona.

## Mitä voi kokeilla

- valita minkä tahansa kolmesta demosta
- hakea nimen tai sisältötyypin perusteella
- nähdä tyhjän hakutuloksen ja palauttaa listan
- nähdä, että esikatseluvideota ei ole prototyypissä
- simuloida valitun demon tarkistuksen ja tarkastella esimerkkipolkuja sekä vastaavaa CLI-komentoa.

Prototyyppi ei lue demotiedostoja, suorita komentoja, kirjoita tiedostoja, käytä tallennustilaa tai tee verkkokutsuja. Näytetty tulos on aina merkitty simuloiduksi. Aidon renderöinnin onnistumista ei luvata. Tekstisisältö päivitetään `textContent`-ominaisuudella, eikä käyttäjän hakua tulkita HTML:nä.

## Automaattiset tarkistukset

Testit käyttävät Node.js:n test runneria ja **pilotissa jo asennetun** Paperclipin jsdom-kirjastoa. Prototyypillä ei ole ajonaikaisia riippuvuuksia, eikä OpenMontagen riippuvuustiedostoja ole muutettu.

Aja repon juuresta olemassa olevalla jsdom-asennuksella:

```sh
NODE_PATH=/polku/olemassa-olevaan/node_modules node --test docs/pilot/sau-4/prototype.test.cjs
```

Paikallisessa pilotissa moduulihakemisto on `paperclip-local-pilot/runtime/node_modules`. Testit tarkistavat valinnat, haun, tyhjän tilan, palautuksen, tuloksen nollauksen, simulaation, verkko- ja tallennusoperaatioiden puuttumisen, kontrollien nimet, tilailmoituksen, sisällön suojauskäytännön hashit ja määritetyn tekstiväripaletin kontrastit.

jsdom ei piirrä sivua eikä varmista selaimen CSP-toteutusta, näppäimistön oletustoimintoja, mobiiliasettelua tai ruudunlukijan käyttäytymistä. Näitä testejä ei kutsuta selain- tai saavutettavuusauditoinniksi.

Jos muokkaat upotettua tyyliä tai skriptiä, päivitä sen SHA-256-hash `Content-Security-Policy`-metatietoon. Testit hylkäävät vanhentuneen hashin. Verkkolähteet ja `unsafe-inline` eivät kuulu sallittuun käytäntöön.

## Ihmisen käyttöskenaario ja visuaalinen hyväksyntä

1. Etsi **FocusFlow Pitch**, valitse se ja kerro itsellesi, mitä demo esittelee.
2. Paina **Simuloi tarkistus**. Varmista, että tuloksessa on juuri valitsemasi demo ja että ymmärrät tuloksen olevan simuloitu.
3. Vaihda **World in Numbers** -demoon. Aiemman tuloksen tulee kadota.
4. Hae sanaa, jota ei löydy. Tyhjennä haku tyhjän tilan painikkeella.
5. Kokeile samaa näppäimillä Tab, Shift+Tab, Enter ja välilyönti. Kohdistuksen pitää erottua, eikä toiminto saa vaatia hiirtä.
6. Tarkista 1280 ja 360 pikselin leveydet. Tekstien, painikkeiden ja polkujen pitää mahtua ilman vaakavieritystä.

Kirjaa onnistuminen tai epäselvyys Paperclipin SAU-4:ään tai Codex-keskusteluun. Tämä on oikea ihmisen koe: avustajan oma arvio ei korvaa sitä. Visuaalinen hyväksyntä ja täsmällisen commitin G4-mergepäätös kirjataan erikseen.

## Avoin selainvarmennus

Pilotin selainautomaatio esti aiemmin paikallisen `file:`-protokollan avaamisen. Rajoitusta ei kierretä toisella selainpinnalla tai esikatselupalvelimella. Siksi automaattiset DOM- ja lähdetarkistukset sekä riippumaton katselmointi erotetaan todellisesta selainkokeesta ja kuvakaappauksista. Puuttuvaa 360/1280-kuvakaappausnäyttöä tai näppäimistövarmennusta ei merkitä tehdyksi.

Palautus: peru vain suunnittelu- ja prototyyppitiedostojen commitit. Muiden tiedostojen tai käyttäjän videoiden poistaminen ei kuulu palautukseen.
