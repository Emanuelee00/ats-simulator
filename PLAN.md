# ATS Simulator — Piano tecnico e legale

## 1. Cosa abbiamo scoperto ispezionando OpenCATS

Repo analizzata: `github.com/opencats/OpenCATS` (clonata temporaneamente solo per studio, poi rimossa).

### Correzione sulla licenza
OpenCATS è sotto **Mozilla Public License 2.0** (codice attuale) + **CATS Public License 1.1a** (porzioni originali 2007, anch'essa una MPL modificata) — **non CPAL** come avevo detto in precedenza, quella era un'informazione sbagliata/obsoleta.

Implicazione pratica: la MPL 2.0 è un copyleft "debole" **a livello di singolo file**, e soprattutto **non ha la clausola "network use"** che hanno AGPL/CPAL. Questo significa:
- Se modifichi un file MPL e lo distribuisci, devi rilasciare il sorgente *di quel file* sotto MPL.
- Ma usarlo per erogare un servizio via rete (il tuo SaaS) **non è di per sé un atto che obbliga alla pubblicazione del codice**, a differenza di AGPL/CPAL.
- Resta comunque vero il principio generale: **non copiare la loro espressione di codice** (struttura, commenti, nomi, organizzazione specifica) in un prodotto proprietario — le tecniche generiche (regex per email/telefono, euristiche di segmentazione) restano libere da usare perché non sono opera protetta in sé.

### Scoperta architetturale più importante
Il parsing "pesante" di un CV (estrazione di skills, education, experience) **OpenCATS non lo fa in casa**: `lib/ParseUtility.php` è un semplice client **SOAP** che manda il documento a un **servizio esterno di parsing** (via `wsdl/parse.wsdl`) e si aspetta indietro un oggetto già strutturato (firstName, lastName, email, skills, education, experience...).

Il codice PHP proprio di OpenCATS (`lib/AddressParser.php`, 880 righe) fa **solo** parsing leggero di blocco indirizzo/contatti (nome, telefono, email, città) da testo già estratto — non tocca skill/esperienza.

**Conseguenza per noi**: anche un ATS open source maturo ha scelto di **non reinventare il parsing profondo del CV**, ma di appoggiarsi a un motore esterno specializzato. Questo convalida direttamente la strategia di usare RChilli/Sovren invece di provare a replicare tutto da zero per la parte più difficile (skills/experience), e ci lascia solo la parte "facile" (contatti/sezioni) da scrivere in autonomia.

---

## 2. Confronto RChilli vs Textkernel/Sovren

| | **RChilli** | **Textkernel / Sovren** |
|---|---|---|
| Fondata | 2010 | Sovren storico, acquisita da Textkernel |
| Modello pricing | A consumo ("pay for what you use"), da **~$75** in su, nessun impegno obbligatorio | Piano **Professional** da **$99/mese** (500–25.000 crediti/mese); piano **Accelerator** $200 per 5.000 documenti |
| Free trial | Sì, versione free + trial disponibili | Sì, **500 crediti** gratuiti via demo UI o API |
| Clienti tipici | Enterprise, ATS/CRM, job board, staffing, integrazioni Oracle HCM / PeopleSoft / Salesforce AppExchange | Enterprise HR tech, molti ATS commerciali lo usano come motore sotto il cofano |
| Lingue/feature | Parsing multilingua, normalizzazione dati | Parsing in **29 lingue**, job parsing in 9 lingue, auto-detect layout a colonne, normalizzazione skill/job title, OCR per immagini, geocoding (add-on) |
| Rating pubblico | 4.4/5 (Capterra) | — |

Fonti:
- [RChilli Resume Parser Web API — Capterra](https://www.capterra.ca/software/105548/rchilli-resume-parser-web-api)
- [Textkernel Parser Pricing](https://www.textkernel.com/products-solutions/parser/pricing/)
- [Resume Parser Software Pricing — Capterra](https://www.capterra.com/p/33114/Resume-Parser/)

**Considerazione**: Textkernel/Sovren ha feature più "enterprise-grade" (auto-detect colonne, OCR, 29 lingue) ed è il motore effettivamente usato da molti ATS commerciali reali — più rappresentativo come test di fedeltà. RChilli è più economico all'ingresso e flessibile a consumo, buono per iniziare senza impegno mensile fisso.

**Scelta consigliata per la fase di validazione**: aprire il trial gratuito di **entrambi** (costo zero), far passare lo stesso set di 10-15 CV reali attraverso tutti e due, confrontare l'output JSON strutturato → capire quale si allinea meglio ai casi reali del tuo pubblico target prima di scegliere un fornitore a pagamento definitivo.

---

## 3. Architettura consigliata

```
CV generato dal tuo tool
        │
        ├──> [Parser proprietario, scritto da zero] ──> score veloce, gratis, nessun limite
        │     (contatti, sezioni, keyword — ispirato a tecniche generiche, NON al codice OpenCATS)
        │
        ├──> [OpenCATS self-hosted] ──> validazione black-box periodica, gratis
        │     (usato solo come "oracolo" esterno: carichi il CV, leggi cosa estrae dal form,
        │      MAI copiarne il codice dentro il tuo prodotto)
        │
        └──> [RChilli / Sovren API] ──> validazione enterprise-grade
              (trial gratuito per sviluppo, a pagamento in produzione — usata con parsimonia,
               es. solo su richiesta esplicita dell'utente o a campione periodico)
```

### Perché questa combinazione
- **Costo zero per i check di routine** (parser proprietario + OpenCATS self-hosted).
- **Nessun rischio di licenza**: non deriviamo codice da OpenCATS, lo usiamo solo come servizio esterno indipendente; il parser proprietario è scritto da zero.
- **Fedeltà enterprise quando serve**: RChilli/Sovren sono i motori reali dietro molti ATS commerciali, quindi un test lì è il miglior proxy per "questo CV passerà Workday/Greenhouse".

---

## 4. Roadmap pratica

1. **Settimana 1**: scrivere il parser proprietario minimo (estrazione testo da PDF/DOCX con librerie generiche tipo `pdfplumber`/`python-docx`, regex per contatti, segmentazione sezioni per heading comuni).
2. **Settimana 1-2**: self-host OpenCATS via Docker in locale, script Playwright per upload-and-scrape automatico.
3. **Settimana 2**: registrare trial RChilli e Textkernel/Sovren, confrontare output su un set di CV di test.
4. **Settimana 3**: costruire lo score "ATS readability" che combina i 3 segnali (parser proprietario + OpenCATS + API enterprise a campione).
5. **Dopo validazione con utenti reali**: decidere se e quale fornitore enterprise (RChilli o Sovren) passare a piano a pagamento in produzione.

---

## 5. Nota operativa

La repo `opencats/OpenCATS` è stata clonata **temporaneamente** in questa sessione solo per ispezione strutturale (letta, mai modificata, nessun file copiato nel nostro codice). Va rimossa dal filesystem locale dopo questa analisi, come da richiesta.
