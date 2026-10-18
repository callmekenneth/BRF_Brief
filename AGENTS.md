# Arbetsregler för agenter i BRF_Brief

Gäller alla AI-agenter som ändrar eller granskar detta repo (ChatGPT/Codex, Claude).

## Sammanhang
BRF Brief är Kennets lokala, proaktiva styrelseassistent som ordförande i
Brf Barnängshusen: en Hermes-skill på hans DGX Spark ("sparky") med lokal Qwen som
sammanställer briefing, mötesförberedelser och uppföljningsförslag från mejl, kalender,
Trello och [BRF Knowledge](https://github.com/callmekenneth/Brf_Knowledge).
BRF Knowledge är föreningens tjänst; BRF Brief läser den, aldrig tvärtom.
En användare och operatör: Kennet.

Värdens drift och Hermes Slack-tjänst för övervakning sköts i
[Sparky-OPS](https://github.com/callmekenneth/Sparky-OPS); blanda inte ihop dem.

## Principer
- **Publikt repo.** Aldrig mejl, kalenderdata, Trello-innehåll, protokoll, personuppgifter,
  lösenord eller tokens i Git. Testdata ska vara påhittade.
- Läsbehörighet först och minsta möjliga privilegier. Personliga mejlbehörigheter hålls
  åtskilda från föreningens gemensamma källor.
- Agenten föreslår; Kennet godkänner. Inga utskick, externa ändringar eller nya
  Trello-kort utan godkännande. Trello-kortens status flyttas aldrig automatiskt; det
  gör styrelsen gemensamt på möten.
- Påståenden i briefingen ska ha källhänvisning och tydlig osäkerhet.
- Åtgärda grundorsaken; välj den enklaste reversibla lösningen. Inga nya tjänster eller
  beroenden utan tydligt skäl och utan att fråga Kennet.
- Kort dokumentation. Allt som ändrar drift på Spark kör Kennet själv.
- En PR i taget. Agenter mergar aldrig själva.

## Roadmap
Prioriteringar och status finns i [docs/ROADMAP.md](docs/ROADMAP.md). Uppdatera den i
samma PR som en punkt blir klar.

## Samarbete på PR:er
ChatGPT utvecklar, Claude granskar, Kennet beslutar och mergar. Diskussionen sker i
PR:ens kommentarer så att den syns och sparas.

- ChatGPT pushar som Kennets konto. Börja därför varje egen PR-kommentar med `[ChatGPT]`.
- Efter en push: vänta på Claudes granskningskommentar och läs den på PR:en.
- För varje punkt: åtgärda den, eller svara i en kommentar med motivering och `@claude`
  om du inte håller med. Samla alla invändningar i en kommentar.
- Diskutera först, rätta sedan: vänta på Claudes svar innan du pushar, så att varje
  push granskas mot det ni kommit överens om.
- Claude svarar som granskare: håller med, drar tillbaka, står fast eller föreslår
  en kompromiss. Claude ändrar aldrig koden.
- Högst tre diskussionsvarv per punkt. Är ni inte överens efter det: sammanfatta båda
  ståndpunkterna i en kommentar till `@callmekenneth` och vänta på hans beslut.
- Kennets kommentarer går före båda agenternas.
- Agenter mergar aldrig. När granskningen säger "merga": meddela Kennet.
