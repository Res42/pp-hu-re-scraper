# Mi ez?

Portfolio Performance kompatibilis adatokat előállító script a magyar ingatlanokhoz.

Az adatsorok a https://github.com/Res42/pp-hu-re-data repositoryban találhatók.

## Felelősség **NEM** vállalás

A projekt licenszéből is érezhető, de hangsúlyozom itt is, hogy:

A projektnek **NEM** célja bármilyen üzleti/befektetési/egyéb tanácsadás, kizárólag információs és vizualizációs célt szolgál. Semmilyen felelősséget nem vállalok az adatok helyességéért és az ezekre alapozott döntésekért.

## Szerzői jogok

A projekt által feldolgozott és közzétett nyers adatok tulajdonosai:

- Adatforrás: [KSH Ingatlanadattár](https://www.ksh.hu/s/ingatlanadattar/adattar)  
  Tulajdonos: [Központi Statisztikai Hivatal](https://www.ksh.hu/)  
  Copyright: [KSH - Copyright](https://www.ksh.hu/copyright)  
  Licenc: [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/deed.hu)

- Adatforrás: [MNB-lakásárindex](https://statisztika.mnb.hu/publikacios-temak/arak_-arfolyamok/lakasarak/tajekoztato---mnb-lakasarindex)  
  Tulajdonos: [Magyar Nemzeti Bank](https://www.mnb.hu/)  
  Jogi nyilatkozat: [MNB - Jogi nyilatkozat](https://www.mnb.hu/a-jegybank/informaciok-a-jegybankrol/gyakorlati-tudnivalok/jogi-nyilatkozat)  
  Licenc: _nincs explicit licenc_

_A projektben szereplő számítások, interpolációk és extrapolációk saját módszertan alapján készültek, azokért a KSH és az MNB felelősséget nem vállal._

## Adatforrások

A projekt fő adatforrása a [KSH Ingatlanadattár](https://www.ksh.hu/s/ingatlanadattar/adattar), ami (akár) utca és épület típus szintre bontott adatokat tartalmaz. A hátránya, hogy évente 1 adatpontot ad ki, illetve hogy ~1-2 éves lemaradásban van az aktuális naphoz.

Ezen hátrányok kiküszöbölésére különböző interpolációkat és/vagy extrapolációkat tartalmazó adatsorok között lehet választani, amik kiegészítő adatforrásokra támaszkodnak.

### Kiegészítő adatforrások

Az [MNB-lakásárindex](https://statisztika.mnb.hu/publikacios-temak/arak_-arfolyamok/lakasarak/tajekoztato---mnb-lakasarindex) negyedévente frissül és régionális szintre bontott adatokat tartalmaz. Az aktuális naphoz képest ~¼-½ éves lemaradásban van.

## Választható adatsorok

| Adatsor                                                                             | Forrás(ok)                                                                                                                                                                                          |                              Interpolált?                               |                                           Extrapolált?                                           | Időbeli felbontás                             | Adat jellege                                                                                      | Grafikon megjelenése a PP-ben                                                                                                                                                                         |
| ----------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------: | :----------------------------------------------------------------------------------------------: | --------------------------------------------- | ------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ksh](https://github.com/Res42/pp-hu-re-data/tree/master/ksh)                       | [KSH Ingatlanadattár](https://www.ksh.hu/s/ingatlanadattar/adattar)                                                                                                                                 |                                   ❌                                    |                                                ❌                                                | **Évente 1 adat** <br> _(minden év dec. 31.)_ | Csak a KSH átlagárak. ~1-2 éves lemaradás az aktuális naptól.                                     | ![Egy grafikon, aminek az X tengelye az évek, az Y tengely pedig árak. A rajzolt vonal lépcsőzetes, év végén ugrásszerűen növekvő.](docs/images/chart-ksh.png)                                        |
| [ksh-linear](https://github.com/Res42/pp-hu-re-data/tree/master/ksh-linear)         | [KSH Ingatlanadattár](https://www.ksh.hu/s/ingatlanadattar/adattar)                                                                                                                                 |                           ✅ <br> _lineáris_                            |                                                ❌                                                | **Napi 1 adat**                               | Ugyanaz, mint a `ksh`, de interpolált.                                                            | ![Egy grafikon, aminek az X tengelye az évek, az Y tengely pedig árak. A rajzolt vonal folyamatosan ívelő egyenes.](docs/images/chart-ksh-linear.png)                                                 |
| [ksh-mnb-linear](https://github.com/Res42/pp-hu-re-data/tree/master/ksh-mnb-linear) | [KSH Ingatlanadattár](https://www.ksh.hu/s/ingatlanadattar/adattar) <br> [MNB-lakásárindex](https://statisztika.mnb.hu/publikacios-temak/arak_-arfolyamok/lakasarak/tajekoztato---mnb-lakasarindex) | ✅ <br> _lineáris_ <br> <br> A negyedéves pontok az MNB-től származnak. | ✅ <br> _lineáris_ <br> <br> A frissebb MNB-s adatokkal extrapoláljuk az eredeti KSH-s adatokat. | **Napi 1 adat**                               | A KSH-s adatok kiegészítése az MNB lakásárindexszel. <br> ~¼-½ éves lemaradás az aktuális naptól. | ![Egy grafikon, aminek az X tengelye az évek, az Y tengely pedig árak. A rajzolt vonal folyamatosan ívelő egyenes. Az egyenes egy évvel tovább tart, mint a többi.](docs/images/chart-mnb-linear.png) |

## Konkrétan melyik fájl kell nekem?

Négy fajta `JSON` fájl közül lehet választani:

- `cshaz.json`: KSH **családi ház** oszlop
- `panel.json`: KSH **lakótelepi panel** oszlop
- `tobbl.json`: KSH **többlakásos társasház** oszlop
- `total.json`: KSH **lakások összesen** oszlop

Nincs mindig mindegyik fájl (mint ahogy a KSH táblázatban sem), ilyenkor a `total.json`t vagy egy hierarchiával magasabb `JSON`t tudsz használni. Vagy amit akarsz, például egy környékbeli utca adatait, amiben hasonló ingatlanok vannak, mint a tied.

Így válassz fájlt:

1. Nyisd meg az [adatokat tartalmazó projektet](https://github.com/Res42/pp-hu-re-data).
2. Válaszd ki, hogy melyik [adatsort](#választható-adatsorok) szeretnéd használni és nyisd meg azt a mappát.
3. Válassz egy megyét / Budapestet.
   - Ha ilyen felbontású adat kell, akkor válaszd itt ki a mappa alján található `JSON` fájlok közül a megfelelőt.
4. Válassz egy települést / kerületet.
   - Ha ilyen felbontású adat kell, akkor válaszd itt ki a mappa alján található `JSON` fájlok közül a megfelelőt.
5. Válassz egy közterületet.
   - Válaszd ki az egyik `JSON` fájlt.

## Hogyan importáljam be a Portfolio Performanceba?

1. Ha megvan a [kiválasztott fájl](#konkrétan-melyik-fájl-kell-nekem) az előző részből, akkor:
   1. Rakd össze az adatsor URLjét: `https://cdn.jsdelivr.net/gh/Res42/pp-hu-re-data@master/<adatsor>/<...felbontás...>/<tipus>.json`.  
      Például egy kész URL így néz ki: `https://cdn.jsdelivr.net/gh/Res42/pp-hu-re-data@master/ksh-linear/budapest/budapest-11-kerulet/budafoki-ut/tobbl.json`
2. Hozz létre egy új eszközt a PP-ben:
   1. `(+)` gomb (bal oldali panel tetején)
   2. `New instrument` gomb
   3. `Empty instrument` gomb (a felugró ablak alján)
      1. `Name` mezőben adj meg egy nevet, az ingatlan címe például egy jó név.
      2. `Currency` mezőben add meg a `HUF` értéket (ha még nem lenne automatikusan kitöltve).
      3. `Calendar` mezőt állítsd `(None)`-ra.
      4. `Historical Quotes` fül
         1. `Provider` legördülő menüben válaszd ki a `JSON` lehetőséget
         2. `Feed URL` mezőbe írd be a kiválasztott adatforrás linkjét az `1.1.` lépésből.
         3. `Path to Date` mezőbe írd be: `$[*].date`
         4. `Path to Close` mezőbe írd be: `$[*].price`
      5. `Ok` gomb
3. **‼️ Vegyél az eszközből annyi részvényt, ahány négyzetméteres az ingatlan. ‼️** A vásárlási dátumnak és végösszegnek az ingatlan vásárlási adatait add meg.
4. Készen vagy.

## Köszönetnyilvánítás

@havasd-nek, akinek a https://github.com/havasd/pp-scraper és https://github.com/havasd/pp-data projektje ezt a projektet ihlette.
