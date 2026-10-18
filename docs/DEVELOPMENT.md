# Ohjelmistokehityksen toimintamalli

Tämä ohje koskee OpenMontagen koodin, testien, käyttöliittymän, riippuvuuksien ja kehitystyökalujen muutoksia. `AGENT_GUIDE.md`:n videotuotannon luovat hyväksynnät ja enintään kahden kierroksen sisältöarvio eivät korvaa PR-katselmointia. Videon tuotanto ja ohjelmiston kehitys ovat eri työnkulkuja.

Ohjeversio: 18.10.2026. Kehitysmallin lähtöversion tunniste on `a67e7283b860a91be9b90deaf59c2b4c320d5bc1`. Tämä on julkiseen harrasterepoon sovitettu yleinen kehitysmalli; se ei sisällä sisäisiä tuotekohtaisia ohjeita tai tunnuksia. Seuraavassa sessiossa lue tuore `origin/main` ja kirjaa tehtävään käytetty ohjeversio. Tarkista myös varsinaisen ohjepohjan mahdollinen muutos sieltä, missä siihen on pääsy.

## Tehtävästä toimitukseksi

1. Tee työstä GitHub-issue: ongelma, rajaus, hyväksymiskriteerit, omistaja ja ei-tavoitteet. Prioriteetti kirjataan selvästi. Paperclip-kortti linkittää issueen; se kertoo suorituksen ja ajojen tilan.
2. Tarkista avoimet PR:t ja keskeneräiset työt ennen aloitusta. Yhteiseen muutosalueeseen osuminen tarvitsee omistajien päätöksen. Älä resetoi toisen työpuuta tai ota toisen tehtävää hiljaa.
3. Tee pieni muutos omassa lyhyessä haarassa ja eristetyssä työpuussa. Tavallinen vaatimus osoitetaan oikealla RED → GREEN -testillä. Uusi oikeus-, varaus-, toisto- tai fail-closed-vartio tarvitsee myös merkityksellisen mutaationäytön: rikottu vartio tekee testistä punaisen, palautettu vihreän.
4. Päivitä samaan PR:ään tarvittavat ohjeet. Kirjoita pilotin uudet repo-ohjeet, commitit, issuet ja PR-kuvaukset suomeksi. Koodi, tunnisteet ja lokit ovat englanniksi. Tuotteen nykyistä englanninkielistä sisältöä ei käännetä tämän vuoksi.
5. PR kertoo muutoksen, riskin, ajetut tarkistukset ja niiden todelliset tulokset sekä ei-soveltuvat tarkistukset perusteluineen. Lisää `Closes #N`. Pelkkä vanhan testimäärän kopiointi ei ole näyttöä.
6. Riippumaton katselmointi ja nyky-headin vaadittu CI ovat mergeportteja. Niitä voi odottaa rinnakkain. Hyväksyttyyn rajaukseen kuuluva työ etenee vihreiden porttien jälkeen ilman toistuvaa ihmisen etenemiskuittausta.
7. Tarkista mergen jälkeen main ja tehtävän sulkeutuminen sekä emotehtävän seuraava sovittu teko. Viimeinen auditointikommentti ei saa jättää valmista Paperclip-tehtävää uudelleen avoimeksi. Kokonaisuutta ei suljeta yhden PR:n perusteella.

Tässä pilotissa erillistä GitHub Project -boardia ei ole perustettu. Tilasovitus on yksi näkyvä Paperclip-työjono: Todo → In Progress → Done, linkitettynä GitHubin avoimeen/suljettuun kehitysissueen. Toinen samanniminen tilakenttä ei tuo toista totuutta. Uusi board tai erilainen sovitus kirjataan erikseen. Tuotekohtainen wiki, tenant/RLS/DB-matriisi ja framework-kohtaiset komennot eivät sovellu tähän muutokseen sellaisinaan.

## Testit riskin mukaan

`git diff --name-only --no-renames -z BASE...HEAD | python -B scripts/quality_gate.py classify` lukee tiedostonimet datana. BASE ja HEAD ovat varmennettuja commit-tunnisteita. Älä sijoita issue-otsikkoa, kommenttia tai tiedostonimeä suoritettavaksi komentotekstiksi.

| Muutos | Vaadittu CI |
| --- | --- |
| Tavallinen dokumentaatio | Portin testit |
| Kehitysohjeet | Portin testit ja CLI-smoke |
| Workflow tai portin koodi | Kaikki määritellyt jobit; myös ajettavat CI-pinnat todennetaan |
| Demo-CLI ja sen fixturet | Portin testit ja 15 nykyistä CLI-testiä |
| Paikallisen käyttöliittymäprototyypin HTML/testit tai UI-testiriippuvuudet | Portin testit ja DOM-testit |
| Python-runtime, työkalut, skeemat ja pipeline-sopimukset | Portin testit ja runtime-sopimus-/työkalutestit |
| Remotion-koodi ja sen build-riippuvuudet | Portin testit ja TypeScript-tarkistus |
| Tuntematon polku tai epäonnistunut luokittelu | Eteneminen estyy; luokitus täydennetään katselmoituna |

Sekamuutos vaatii kaikkien osien tarkistukset. `quality-gate` tarkistaa lopputulokset myös muiden jobien epäonnistuessa. Vaadittu `skipped`, `cancelled`, puuttuva tai tuntematon tulos ei ole vihreä. Luokittelijan valitsematta jättämä job saa olla `skipped`. Paikallinen fokuskoe ei korvaa valittua PR-CI:tä. CI todennetaan samalle täydelle headille, josta katselmointi on annettu. Tyhjä commit ei ole CI:n uusintamekanismi.

Paikalliset nopeat tarkistukset:

```sh
python3 -B -m unittest tests.test_quality_gate tests.test_render_demo -v
npm ci --ignore-scripts --no-audit --no-fund --prefix tests/ui
NODE_PATH="$PWD/tests/ui/node_modules" node --test docs/pilot/sau-4/prototype.test.cjs
```

jsdom ja sen aliriippuvuudet lukitaan `tests/ui/package-lock.json`:iin. DOM-testi ei ole selaimen asettelu-, näppäimistö- tai saavutettavuusauditointi. Linux-CI ei yksin osoita Windows-yhteensopivuutta tai renderöinnin onnistumista. Pythonin olemassa olevia `requirements*.txt`-riippuvuuksia ei vielä ole hash-lukittu: runtime-asennuksen versiot voivat vaihtua. Luokittelu ja tulosten validointi ovat deterministisiä; tämä ei tee koko riippuvuusasennuksesta toistettavaa. Riippuvuuksien lukitus ja seuranta kuuluvat ylläpitovaiheeseen. Varsinainen renderöinti ja `tests/qa` voivat tarvita erillisen laite-/mediaympäristön; niitä ei ajeta jokaisen ohjemuutoksen vuoksi.

## Riippumaton katselmointi

Toteuttajan omat tarkistukset eivät korvaa toisen mallin ensimmäistä arviota. Codex-työn katselmoija on Claude CLI erillisessä työpuussa. Jokainen arviointikutsu antaa nimenomaisesti `--model opus`, myös `--resume`-jatkokutsu. Ensimmäinen sessio saa vaatimukset, ohjeet, diffin, lähteet ja testinäytön; sille ei siirretä toteuttajan keskusteluhistoriaa tai tämän omia ennakolta valittuja löydöksiä.

Saman PR:n korjauskierrokset jatkavat samaa katselmoijasessiota. Tekninen pakollinen sessionvaihto dokumentoidaan ja avoimet löydökset siirretään. Katselmoijaa ei vaihdeta helpomman hyväksynnän saamiseksi. Tekninen erimielisyys käsitellään näytöllä ja tarvittaessa rajatulla erillisellä Opus-arviolla; alkuperäinen katselmoija antaa PR:n lopputuloksen.

Tallenna CLI:n alkuperäinen vastaus muuttamattomana PR-kommentiksi. Lisää suorittajan CLI-/mallitieto ja session tunniste erilliseen toimitusmerkintään; älä muuta itse tulosta. Ensimmäinen rivi on täsmälleen:

```text
Katselmoitu head: <täysi 40 merkin SHA>
```

Viimeinen ei-tyhjä rivi on paljas `READY YES` tai `READY NO`. Löydökset luokitellaan Critical / Important / Minor, yksilöidään pysyvästi ja niille kerrotaan näyttö sekä sulkemisehto. READY YES edellyttää, ettei avoimia Critical- tai Important-löydöksiä ole. READY NO johtaa korjaukseen ja saman session uuteen arvioon ilman kovaa kierrosrajaa. Raportoi korjatut, avoimet ja jatkoon siirretyt havainnot sekä lopputulos.

Uusi commit tai rebase vanhentaa edellisen headin katselmoinnin ja CI-näytön. Lainaus, otsikko tai toteuttajan oma READY YES ei ole hyväksyntä. Kapea vähäriskinen poikkeus voi soveltua vain suoraan tarkistettavaan, paikalliseen ja palautettavaan muutokseen, joka ei muuta käyttäytymistä, tietoa, oikeuksia, lupausta tai yhteistä sopimusta eikä jätä epävarmuutta. Sitä ei käytetä arkkitehtuuriin, riippuvuuksiin, integraatioihin, tietoturvaan, AI-ajoihin, CI:hin tai mergeporttiin. Organisaatiopilotissa riippumaton katselmointi säilyy oletuksena; poikkeusta ei kirjata ulkopuoliseksi READY YES -tulokseksi.

## Luottamusraja

CI käyttää GitHubin ajokoneita, read-only-sisältöoikeutta, tarkkoihin virallisiin committeihin lukittuja actioneita ja checkoutia ilman pysyviä Git-tunnuksia. PR-testit eivät saa henkilökohtaisia kirjautumisia, Board-tunnusta, pilvitunnusta tai julkaisusalaisuutta. `pull_request_target` ei aja PR-koodia. Tämä työnkulku ei tee julkaisuja tai hyväksy PR:iä.

PR voi muuttaa omaa workflow-tiedostoaan. Siksi sen vihreä tulos, itse ilmoitettu testimäärä tai keksitty katselmoijakenttä ei yksin ole mergevaltuus. Luotettu toimituksen ohjain hakee itse GitHubin nykyisen headin, diffin, ajot ja lopputulokset sekä katselmoijan alkuperäisen CLI-tuloksen ja tunnetun session. Mallikenttä tulee toteutuneen CLI-tuloksen ratkaistusta `modelUsage`-mallitunnisteesta, ei pyydetystä `opus`-aliaksesta. Se käyttää PR:n ulkopuolelta lukittua porttiversiota. `quality_gate.verify` tarkistaa näiden tietojen yhteensopivuuden; se ei autentikoi mielivaltaisen JSON-tiedoston lähettäjää. Oikean alkuperän varmistaminen ja tunnusten eristys kuuluvat ohjaimelle.

Main oli tätä muutosta valmisteltaessa suojaamaton. Tämä PR ei muuta repo-oikeuksia, haarasuojausta tai admin-ohituksia. Pilotin luotettu toimituspolku ei mergetä porttien vastaisesti, mutta se ei estä repositoryn ylläpitäjää tekemästä suoraa muutosta muulla välineellä. Rajaus kirjataan organisaatiokokeen näyttöön.

## Käyttöliittymä ja ihmisen päätökset

Esittely käyttää samaa toimivaa toteutusta kuin toimitus. Agentti hoitaa riskin mukaiset laatutarkistukset, työpöytä-/mobiilikokeen, näppäimistön ja soveltuvat kieli-/teemavariaatiot. Ihminen voi hyväksyä uuden tuoteratkaisun yhdellä selkeällä viestillä; teknistä QA-lomaketta ei siirretä hänelle. Kirjaa esittelyversio, hyväksyjä, päivä, tehtävä ja päätöksen lähde sekä agentin tarkistusnäyttö erikseen.

Aiemmin hyväksyttyä muuttumatonta ratkaisua ei hyväksytetä uudelleen teknisen pilkkomisen tai PR:n vuoksi. Muuttunut käyttäjälupaus tarvitsee uuden tuotepäätöksen. Epäselvä oikeus, uusi henkilö tai laskutus, tuotantovaikutus ja toisen työn omistus nostetaan oikealle päätöksentekijälle. Sisäisiä aineistoja, oikeita salaisuuksia tai tuotantodataa ei sisällytetä julkiseen issueen, testiin tai katselmointipakettiin.
