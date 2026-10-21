# Reparación de caracteres especiales perdidos por el export de SAP

## Qué pasó

El export de SAP (`data.csv`, `report1790238371853.csv`, `report_italy.csv`) está
codificado en **ISO-8859-1 (Latin-1)**. Ese juego de caracteres no incluye las
letras que usan los nombres locales (š, ž, ć, č, ł, ř, ı, ş, ğ, ș, ț...) ni la
apóstrofo tipográfica ni los guiones largos, así que el export escribió un `?`
en su lugar. El importador no pierde nada: decodifica `utf-8-sig` y, si falla,
`cp1252`, y guarda el fichero tal cual.

Comprobado sobre los ficheros: los bytes de `Bal?kesir` son `3f 61 6c` — el `?`
está en el fichero, no aparece al decodificar. **La información ya no existe en
el origen**, por lo que no se puede reimportar: hay que reconstruirla.

## Alcance

| Tabla | Afectados | Total |
|---|---|---|
| `customers.account_name` | 77 | 2483 |
| `customer_sites.physical_city` / `physical_street` | 7 | 479 |
| `equipment` (nombre, material, tipo) | 0 | 45507 |
| `offer_items` | 0 | 65 |

## Decisión

No se toca el importador: no es un bug suyo, el fichero llega así. Se restituyen
los caracteres con un **mapeo revisado a mano**, que es dato y no código:

- `backend/data/special_character_fixes.json` — valor actual, valor corregido y
  nota de por qué se corrigió cada fila.
- `backend/scripts/repair_special_characters.py` — aplica el mapeo.

El script:

1. comprueba que la base de datos sigue teniendo exactamente el valor "actual"
   de cada fila (si no, se detiene y no escribe nada);
2. comprueba que el valor corregido tiene el mismo número de caracteres y
   sustituye exactamente el mismo número de `?`;
3. escribe todo en una sola transacción;
4. verifica al terminar que no queda ningún `?` en nombres ni ubicaciones.

```bash
cd backend
python scripts/repair_special_characters.py           # simulación
python scripts/repair_special_characters.py --apply   # escritura
```

## Reconstrucciones confirmadas

En 16 de las 84 filas el carácter no se podía confirmar con los datos del export
(estaban marcados con `"confirmed": false` en el JSON). El usuario los ha
contrastado con SAP y los da por buenos, así que quedan aplicados en la base de
datos y marcados como `confirmed` en el mapeo. Se dejan aquí las
reconstrucciones, que son el punto que conviene volver a revisar si algún día
se reimporta el catálogo:

| Cliente | Actual | Corregido | Duda que había |
|---|---|---|---|
| 0001052466 | `Dr?be?á?ský závod Klatovy a. s.` | `Drábežáňský závod Klatovy a. s.` | la palabra no aparecía completa en ningún sitio |
| 0001052473 | `Ettat Et Ürünleri ?n?. G?da San. ve` | `Ettat Et Ürünleri Önü. Gıda San. ve` | abreviatura de 3 letras (`?n?`) |
| 0001057365 | `... RENT A CAR ?UNA TRADE` | `... RENT A CAR ĐUNA TRADE` | la inicial perdida |
| 0001054047 | `A/S ?Cesvaines Piens?` | `A/S “Cesvaines Piens”` | comillas tipográficas supuestas |
| 0001056419 | `AGRA?S FOOD FACTORY SRL` | `AGRAȘS FOOD FACTORY SRL` | la `S` final, quizá doble `S` en SAP |
| 0001059250 | `DRU?TVO ... ?SU?ARA STANI?I?` | `DRUŠTVO ... ŠSUŠARA STANIŠIĆ` | el primer token (`?SU?ARA`) no cuadra con `ŠUŠARA` |
| 0001059729 | `Öz???k Süt Ürünleri` | `Öztürk Süt Ürünleri` | reconstrucción por patrón |
| 0001050611 / 0001057742 / 0001054360 | separador `?` | `–` (guion largo) | el tipo de guion no se puede saber |

El resto sí se pudo confirmar con el propio export: el mismo fichero trae la
dirección del cliente con la letra correcta (`Gavrilovi?ev trg`, `Nik?i?
Stra?evina bb`, `Velké Mezi?í?í`, `Krom??í?`, `P?íbram`, `Bohu?ovice n./O.`,
`Runovi?i`, `Suboti?te-Pe?inci`, `SAVA BURI?A 2`…).

## Cómo evitarlo

Pedir a SAP el export en **UTF-8**. Con UTF-8 el importador ya lee los
caracteres correctos (el `utf-8-sig` es el primer intento) y no habría nada
que reparar.

## Nota

El orden alfabético del selector de clientes de la pantalla de New Offer
(inventario de esta sesión) usaba una clave que pliega acentos; con los `?`
restaurados la lista queda ordenada de verdad: `Žahoviž` aparece con las Z y
los nombres con apóstrofo (`O'Brien`, `Farmer's`) con su letra.
