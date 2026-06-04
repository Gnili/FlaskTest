# Flask Aplikacije - Projekt

Tri Flask aplikacije v enem Codespace projektu z uporabo TinyDB baze podatkov.

## Struktura projekta

```
project/
├── app1.py          # Osebni zapiski
├── app2.py          # Socialna platforma
├── app3.py          # Todo aplikacija
├── templates1/      # Templati za app1
├── templates2/      # Templati za app2
├── templates3/      # Templati za app3
├── static1/         # Statični datoteki za app1
├── static2/         # Statični datoteki za app2
├── static3/         # Statični datoteki za app3
└── db/              # Direktorij za TinyDB baze
    ├── notes_db.json
    ├── social_db.json
    └── todo_db.json
```

## Napisan kod vključuje:

### App1 - Osebni zapiski
- **Port**: 5000
- **Funkcionalnosti**:
  - Prijava in registracija (TinyDB)
  - Dodajanje novih zapiskov (AJAX - /api/notes/add)
  - Urejanje zapiskov (PUT /api/notes/{id}/edit)
  - Brisanje zapiskov (DELETE /api/notes/{id}/delete)
  - Sinhrone rute za prikaz (GET /)
  - Session za upravljanje prijave

### App2 - Socialna platforma
- **Port**: 5001
- **Funkcionalnosti**:
  - Registracija in prijava
  - Objavljanje besedila in slik (AJAX - /api/posts/add)
  - Nalaganje slik v static2/uploads
  - Pregled vseh objav drugih uporabnikov
  - Brisanje lastnih objav (DELETE /api/posts/{id}/delete)
  - Periodično osvežanje objav (vsakih 5 sekund)
  - Sinhrone rute za prikaz

### App3 - Todo aplikacija
- **Port**: 5002
- **Funkcionalnosti**:
  - Registracija in prijava
  - Dodajanje nalog s prioritetami (visoka, srednja, nizka)
  - Označevanje nalog kot opravljenih (PUT /api/tasks/{id}/toggle)
  - Urejanje nalog (PUT /api/tasks/{id}/edit)
  - Brisanje nalog (DELETE /api/tasks/{id}/delete)
  - Statistika (skupaj, opravljenih, čakajočih)
  - Barvna kodiranje po prioriteti

## Zahteve - Izpolnjene

✅ Uporaba baze podatkov (TinyDB)
✅ Uporaba session (Flask session)
✅ Sinhrone klice (Flask route - GET, POST)
✅ Asinhrone klice (AJAX - fetch API)
✅ Razumljiva koda z komentarji
✅ Brez CSS - osnoven HTML
✅ Primerna funkcionalnost za vsako aplikacijo

## Kako zagnati aplikacije

1. **Instaliraj odvisnosti**:
```bash
pip install flask tinydb werkzeug
```

2. **Zagon app1 (Osebni zapiski)**:
```bash
python app1.py
```
Odpri: http://localhost:5000

3. **Zagon app2 (Socialna platforma)** (v drugem terminalu):
```bash
python app2.py
```
Odpri: http://localhost:5001

4. **Zagon app3 (Todo aplikacija)** (v tretjem terminalu):
```bash
python app3.py
```
Odpri: http://localhost:5002

## Tehnične zahteve

### Baza podatkov (TinyDB)
- JSON-based baza - enostavna za razvoj
- Vsaka aplikacija ima lastno bazo:
  - `notes_db.json` - Osebni zapiski
  - `social_db.json` - Socialna platforma
  - `todo_db.json` - Todo naloge

### Session
- Flask session za sledenje prijavljenim uporabnikom
- Secret key za varnost

### API kot JSON
- Vse AJAX zahteve pošiljajo/prejemajo JSON
- Naslednji API endpoints:
  - POST /api/notes/add - Dodaj zapis
  - PUT /api/notes/{id}/edit - Uredi zapis
  - DELETE /api/notes/{id}/delete - Izbriši zapis
  - GET /api/posts - Pridobi objave
  - POST /api/posts/add - Dodaj objavo
  - DELETE /api/posts/{id}/delete - Izbriši objavo
  - GET /api/tasks - Pridobi naloge
  - POST /api/tasks/add - Dodaj nalogo
  - PUT /api/tasks/{id}/toggle - Označi kot opravljeno
  - PUT /api/tasks/{id}/edit - Uredi nalogo
  - DELETE /api/tasks/{id}/delete - Izbriši nalogo

## Varnost

- Gesla se hešira z werkzeug.security
- Session spremenljivke za avtentifikacijo
- Preverjanje lastništva podatkov pri posodobitvah/brisanju

## Napotki za razumevanje kode

1. **TinyDB**: V `get_db()` funkcijah se kreira nova konekcija do JSON datoteke
2. **Query**: Uporablja se za iskanje dokumentov v TinyDB
3. **AJAX**: JavaScript fetch API pošilja zahteve na Flask API endpoints
4. **Asinkrona obdelava**: Slike se nalagajo z `FormData` v app2
5. **DOM manipulacija**: Novi elementi se dodajajo direktno v HTML z JavaScript