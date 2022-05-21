## This script represents the core for the data digitalization of a local basketball team.

Local folder are organized like this:

.

|-- 1963

|-------allenatore

|-------assistenti

|-------attivitaGiovanile

|-------fotoSquadra

|-------galleria

|-------giocatori

|-------management

|-------rassegnaStampa

|-------statistica

|-------viceAllenatori

|--1964

...



### Steps that update_db.py follows 
We start to read from a spreadsheet which contains the roster and some statistic for a basketball team,

we then proceed to create a new row on the year table,

now that we have in input all the data for a team: players, coaches, league of the championship, year and so on; we can upload a new team.