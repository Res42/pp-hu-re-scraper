# Mi ez?

Portfolio Performance kompatibilis adatokat előállító script a magyar ingatlanokhoz.

Az adatsorok a https://github.com/Res42/pp-hu-re-data repositoryban találhatók.

## Adatforrások

A projekt fő adatforrása a [KSH Ingatlanadattár](https://www.ksh.hu/s/ingatlanadattar/adattar), ami (akár) utca és épület típus szintre bontott adatokat tartalmaz. A hátránya, hogy évente 1 adatpontot ad ki, illetve hogy ~1-2 éves lemaradásban van az aktuális naphoz.

Ezen hátrányok kiküszöbölésére különböző interpolációkat és/vagy extrapolációkat tartalmazó adatsorok között lehet választani.

## Választható adatsorok

| Adatsor                                                                     |    Interpolált?    |    Extrapolált?    | Időbeli felbontás                             | Adat jellege                                                                                                                                                                                           | Grafikon megjelenése a PP-ben                                                   |
| --------------------------------------------------------------------------- | :----------------: | :----------------: | --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------- |
| [ksh](https://github.com/Res42/pp-hu-re-data/tree/master/ksh)               |         ❌         |         ❌         | **Évente 1 adat** <br> _(minden év dec. 31.)_ | Csak a KSH átlagárak. ~1-2 éves lemaradás az aktuális naptól.                                                                                                                                          | ![Lépcsőzetes, év végén ugrásszerűen változó vonal.](docs/images/chart-ksh.png) |
| [ksh-linear](https://github.com/Res42/pp-hu-re-data/tree/master/ksh-linear) | ✅ <br> _lineáris_ |         ❌         | **Napi 1 adat**                               | Ugyanaz, mint a `ksh`, de interpolált.                                                                                                                                                                 | ![Folyamatosan ívelő egyenes.](docs/images/chart-ksh-linear.png)                |
| `ksh-mnb-linear`                                                            | ✅ <br> _lineáris_ | ✅ <br> _lineáris_ | **Napi 1 adat**                               | A KSH-s adatok kiegészítése az MNB lakásárindexszel. ~¼-½ éves lemaradás az aktuális naptól. <br> **Fontos:** az utolsó KSH-s adatponttól kezdve extrapolálva vannak az adatok az utolsó MNB-s pontig. | TODO:                                                                           |

## Hogyan importáljam be a Portfolio Performanceba?

1. Válaszd ki a neked tetsző adatsort és felbontást.
   1. Rakd össze az adatsor URLjét: `https://cdn.jsdelivr.net/gh/Res42/pp-hu-re-data@master/<adatsor>/<...felbontás...>/<tipus>.json`.  
      Például egy kész URL így néz ki: `https://cdn.jsdelivr.net/gh/Res42/pp-hu-re-data@master/ksh-linear/budapest/budapest-11-kerulet/budafoki-ut/tobbl.json`
2. Hozz létre egy új eszközt a PP-ben:
   1. `(+)` gomb (bal oldali panel tetején)
   2. `New instrument` gomb
   3. `Empty instrument` gomb (a felugró ablak alján)
      1. `Name` mezőben adj meg egy nevet, az ingatlan címe például egy jó név.
      2. `Currency` mezőben add meg a HUF értéket (ha még nem lenne automatikusan kitöltve).
      3. `Historical Quotes` fül
         1. `Provider` legördülő menüben válaszd ki a `JSON` lehetőséget
         2. `Feed URL` mezőbe írd be a kiválasztott adatforrás linkjét az `1.1.` lépésből.
         3. `Path to Date` mezőbe írd be: `$[*].date`
         4. `Path to Close` mezőbe írd be: `$[*].price`
      4. `Ok` gomb
3. **‼️ Vegyél az eszközből annyi részvényt, ahány négyzetméteres az ingatlan. ‼️** A vásárlási dátumnak és végösszegnek az ingatlan vásárlási adatait add meg.
4. Készen vagy.

## Köszönetnyilvánítás

@havasd-nek, akinek a https://github.com/havasd/pp-scraper és https://github.com/havasd/pp-data projektje ezt a projektet ihlette.
