# Problema II
### Cerința [în original](https://github.com/Dragos-Florin-Pojoga/Proiect_PS/blob/main/tema_de_proiect.pdf) (paginile 2-3)

# Vizualizator interactiv de grafice generate de R

![](./assets/example_4_points.png)

# Funcționalități
* Suport complet pentru mediul R
* Randarea de grafice în timp real
    * mai multe linii pe același grafic
    * scalare dinamică a graficului
    * legendă de culori
    * 6 culori predefinite și multe altele generate aleator pentru fiecare linii din grafic
* funcții definite în R
    * INPUT:
        * slider(min, max, [step], [default])
            * NOTĂ: această funcție nu poate primi variabile ca intrări. Doar numere de tip int/float.
    * OUTPUT:
        * plot_line(xs, ys, [name])
        * plot_func(func, xs, [name])
* editor de cod
* glisoare dinamice bazate pe codul R
* fereastră de output și erori
* carusel cu exemple

# Dependențe:
* python3
    * PyQt6
* R

# Descriere

Problema se poate împărți în trei subprobleme:
1) să construim o aplicație [Shiny](https://shiny.posit.co/r/getstarted/shiny-basics/lesson1/)

Shiny este o librărie pentru R ce creează aplicații web interactive. Această librărie practic "compilează" codul de R pentru interfață în html, css și js iar codul pentru generarea graficelor este rulat la nevoie pentru a produce imagini ce sunt inserate înapoi în pagină. Acest proces este extrem de complex, ceea ce se reflectă în dimensiunea proiectului: ~115000 de linii de cod scrise de 88 de persoane pe decursul a 13 ani (proiectul a început în 2012)

Pentru a crea o aplicație cu o parte din funcționalitatea acestei librării, am ales să folosesc python și cât mai puține librării externe, în final având doar una singura: [PyQt6](https://pypi.org/project/PyQt6/) o librărie cross-platform ce permite crearea de interfețe grafice modulare

<placeholder>


2) să reprezentăm grafic funcțiile de repartiție a unor variabile aleatoare

<placeholder>

3) să afișăm anumite funcții cu parametri particularizabili de către utilizator și să calculăm și media și varianța pentru variabila aleatoare corespunzătoare

<placeholder>



# Galerie

![](./assets/reddit.png)

![](./assets/example_4_points.png)

![](./assets/example_4_lines.png)