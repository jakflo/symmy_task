Synchronizace mezi daty z erp a externí API

## Popis systému
Aplikace se skládá z webového endpointu a Celery workeru
po zavolání /sync na webovém endpointu se načte erp_data.json jako simulace erp dat a tyto data jsou odeslána na Celery worker
- worker surová data pomocí modulu product_validate zvaliduje a upraví.
    - validace:
        - title musí mít 3-100 znaků
        - price_vat_excl musí být kladné číslo
        - položky uvnitř stocks musí být int nebo "N/A" řetězec
    - úprava dat:
        - price jako price_vat_excl +21%
        - stocks jako součet prvků uvnitř původního stocks ("N/A" řetězec nahrazen 0)
        - color vzato z attributes, není-li, tak color = "N/A"
        - vypočítán hash
- worker pomocí modulu product_compare vyhledá rozdíly mezi erp daty a místní DB:
    - k úpravě dat pouřije product_validate. Pokud validace selže, tak vypíše chybu a danou položku přeskočí
    - pokud existuje více položek se stejným ID, bere se to poslední a předchozí je ignorováno
    - porovná, zda data existují v DB, popř. na základě hash, zda nebyly změněna
    - připraví data k odeslání na API, změněná data jsou připravena na PATCH, tj. obsahuje pouze změněná pole daných položek
    - a instance modelů pro uložení změn do DB
- worker pomocí modulu product_send_changes vezme změny nalezené v product_compare a 
    - pošle je na API (dle nastavení v env) - POST, popř. PATCH
    - pokud API vrátí 429, zkusí to znova - nyní za 2 sekundy
    - pokud API vrátí jinou chybu, nebo se vyčerpá počet pokusů po 429 chybě (nyní 10), proces se přeruší
    - pokud API vrátí 200, popř. 201, uloží se připravené změny do DB
    - pokud API vrátí, že se neuložily všechny položky, pokusí se je poslat znova, nanejvýš 10x

## Instalace
- Vytvořte a spusťte docker kontejner pomocí
    docker compose up
- Vytvořte DB pomocí příkazů 
    python manage.py makemigrations integrator
    python manage.py migrate
spuštěných v podkontejneru web-1

- testy můžete spustit pomocí příkazu
    ./manage.py test
spuštěných v podkontejneru web-1
