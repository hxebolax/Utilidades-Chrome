# Utilidades ChromePequeño complemento al cual se le irán agregando mejoras para el navegador Chrome.Este complemento solo funciona en versiones de NVDA 2019.3 en adelante.Ahora aguanta todas sus funciones en las 3 variantes, Final, Beta y Canary.## Órdenes de teclado del complemento:Todas las órdenes de teclado del complemento pueden modificarse en el diálogo de NVDA Gestos de entrada.Una vez en dicho diálogo estarán en la categoría Utilidades Chrome.Hay que decir que para que dicha categoría aparezca tiene que ser llamado el diálogo Gestos de entrada con el navegador Chrome abierto y enfocado.* Shift+F4: Activa y desactiva la navegación cíclica.* NVDA+F6: Abre el diálogo de lista de pestañas.* F7: Nos mostrara el historial de las paginas visitadas hacia atrás.* F8: Nos mostrara el historial de las paginas visitadas hacia adelante.* F9: Activara y desactivara el modo lectura.* Shift+F9: Inicia la lectura continua en modo lectura.### Navegación cíclicaAhora podremos tener la navegación cíclica en Chrome, muy conocida en otros lectores de pantalla.La navegación cíclica hace que el lector de pantalla vaya a la parte superior de la página o viceversa cuando no hay más elementos del tipo adecuado según la letra de navegación rápida que estés utilizando. Por ejemplo, si pulsas la h para navegar por encabezados y ya no hay más encabezados disponibles, NVDA saltará al principio de la página y te situará de nuevo en el primero.Podremos activar o desactivar la navegación cíclica con Shift+F4.Una vez activada navega por la web utilizando teclas de navegación de una sola letra.¡Atención!Si me parare a explicar que ya existe un complemento alojado en la web oficial de la comunidad de NVDA en español  que es el siguiente:<https://nvda.es/2019/01/25/screen-rapping-navegacion-ciclica/>o desde el repositorio del autor en GitHub:<https://github.com/hamadatrichine/nvda-screen-rapping>Bien dicho complemento esta desactualizado y tendríamos que andar cambiando el manifiesto para que funcione usando los indicadores de compatibilidad con versiones recientes de NVDA , y el autor   me parece que ya no sigue con su desarrollo hace 2 años.Por lo tanto si quiero lanzar la advertencia que si vamos a usar dicha función en Chrome solamente es recomendable si tuviésemos instalado el complemento Screen Rapping deshabilitarlo o desinstalarlo si no fuésemos a usarlo en otra parte y usar la función que ya viene en mi complemento.Si fuésemos a usar la navegación cíclica en otros documentos o navegadores pues entonces recomiendo usar el complemento Screen Rapping y olvidarnos de la función que viene en mi complemento.Esto ya va a gusto de todos pero bueno Screen Rapping al ser un complemento que no se actualiza y que es poco conocido me pareció correcto incorporar su función en el complemento Utilidades Chrome con el visto bueno  de Hamada Trichine para usar su código.Y finalmente en el caso de que tuviéramos otro complemento que realice la misma  función por favor les recomiendo usar su complemento y olvidarnos de la función que viene en mi complemento.### Control de pestañasEn el navegador Chrome podemos cambiar de áreas con F6 pudiendo llegar al área de las pestañas y recorrerlas con flechas al igual que encima de la pestaña que deseamos si pulsamos la tecla aplicaciones nos desplegara un menú con distintas opciones que podremos realizar en la pestaña.También podemos cambiar rápidamente entre pestañas con la combinación CTRL+1 al 9, pero la cosa se complica cuando tenemos más pestañas.Bien ahora el complemento tendrá una combinación que nos desplegara un diálogo con todas las pestañas que tengamos abiertas ordenadas en orden conforme fueron abiertas.Para abrir dicho diálogo tendremos que pulsar NVDA+F6.En dicho diálogo tiene dos áreas una con la lista de las pestañas y otra con botones, podemos movernos entre las distintas áreas tabulando o con las teclas rápidas.En la lista si pulsamos la tecla Intro nos llevara a la pestaña que tengamos seleccionada en dicho momento.Tenemos 4 botones que son:* Clic en botón Izquierdo, el cual nos dejara en la pestaña que tengamos seleccionada en la lista.* Clic en botón Derecho, el cual nos desplegara las opciones para la pestaña que tengamos seleccionada en la lista.* Nueva pestaña, este botón nos abrirá una nueva pestaña donde podremos empezar desde cero, nos dejara el foco en la barra de direcciones para que busquemos o introduzcamos la dirección que deseemos.* Cerrar, este botón nos cerrara el diálogo y nos dejara en la pagina desde donde fue llamado el diálogo.Hay que decir que la ventana diálogo de pestañas puede cerrarse a través del botón correspondiente, pulsando la tecla ESC o perdiendo el foco.Esto ultimo significa que con la ventana abierta de diálogo de pestañas si regresamos al navegador, automáticamente se cerrara el diálogo de lista de pestañas.Esto asegura que cuando llamemos al diálogo de nuevo reciba la información correcta de cada momento que a sido llamado.### Historial rápido de páginas visitadasSe a incluido el poder acceder rápidamente al historial de las paginas que hemos visitado ya sea adelante o atrás.Para acceder a dicho historial usaremos F7 y F8.Voy a poner un ejemplo para su mejor entendimiento.Si abrimos el navegador y por defecto no tenemos ninguna página abierta, nos dirigiremos a www.google.com.Una vez cargada la página ahora pulsamos CTRL+L y ponemos www.nvda.es, ahora si pulsamos F7 veremos que se despliega un menú con la página de Google en el historial. Si elegimos dicha página de Google nos cargara dicha página.Ahora si pulsamos F8 veremos que tenemos en el historial hacia adelante la pagina de NVDA en Español.Bien estos historiales tanto atrás como adelante son para la pestaña que tenga el foco en cada momento, actualizando el historial para cada pestaña.Esto es útil cuando navegamos por muchas paginas en la misma sesión y en la misma pestaña.Advertencia, el historial se borra cuando cerramos Chrome.### Mejora en modo lecturaChrome por sí solo no trae este modo como si otros navegadores.Si deseamos tener dicha función tendremos que activarla manualmente antes de poder usarla.Para activar dicha función nos posicionamos en la barra de dirección y escribimos lo siguiente:chrome://flagsPulsamos intro y en la pantalla que nos deja en el campo de búsqueda Search flags escribimos lo siguiente:reader modeCuando lo escribamos escucharemos que hay un resultado por lo que tabularemos hasta oír lo siguiente:-#enable-reader-modePues tabulamos una vez más y caeremos en un cuadro combinado teniendo que elegir la opción Enable.Ahora volvemos a tabular hasta el botón Relaunch, lo pulsamos y la próxima vez que el navegador reinicie ya tendremos activado el modo lectura.Bien cuando entremos en una página que permita el modo lectura, cuidado no todas lo permiten. Podremos activar dicho modo para quitar todo lo que molesta de la página, es decir, sólo se mostrará el contenido de una página sin apariencia o anuncios publicitarios, conservando sólo el texto y las imágenes para mayor comodidad de lectura, esto podemos hacerlo de dos maneras:1º Desde el menú de Chrome subiendo o bajando por el hasta que oigamos Activar/Desactivar modo de lectura y entraremos en modo lectura, si en el menú no aparece dicha opción es que la página en la que nos encontramos no lo permite.2º Podemos una vez que estamos en la página pulsar F6 y dos tabulaciones para caer en un botón que dice Activar/Desactivar modo de lectura, si lo pulsamos entraremos en dicho modo. Si dicho botón no aparece es que la página en la que estamos no lo permite.Pues bien aunque parezca poco si somos mucho de usar dicho modo de lectura, echaba de menos un atajo rápido para poder activar o desactivar dicho modo o que me avise si la página no lo permite.Pues bien ahora con el complemento si pulsamos F9 activaremos el modo lectura.Bien si la página en la que nos encontramos no permite dicho modo se nos avisara con un mensaje.Si la página lo permite entrara en modo lectura avisando que entra en dicho modo con un mensaje.Si pulsamos F9 ya estando dentro del modo lectura saldrá de él y nos avisara también de que está saliendo de dicho modo.### Lectura continua en modo lecturaSi pulsamos Shift+F9 cuando el modo lectura este activado NVDA empezara a leer la pagina desde donde este posicionado el cursor.Si pulsamos Ctrl pararemos la lectura.### Panel de opcionesA partir de la versión 0.7 del complemento tendremos una nueva área en Preferencias / Opciones y buscar Utilidades Chrome.En este apartado de opciones iré agregando opciones que pueda considerar interesantes para el navegador.Para poder visualizar esta categoría tendremos que llamar a las opciones de NVDA desde el navegador Chrome, de lo contrario no será visible.De momento tenemos la siguiente opción:* Abrir las ventanas de Chrome maximizadasSi activamos esta casilla todas las ventanas de Chrome se abrirán maximizadas por defecto.## Traductores y colaboradores:* Francés: Rémy Ruiz* Portugués: Ângelo Miguel Abrantes* Árabe: Wafiq Taher# Registro de cambios.## Versión 0.8.* Cambios internos para adaptarse a la nueva API en NVDA 2021.1 y mantener la compatibilidad con versiones anteriores* Soporte de Google Chrome 91## Versión 0.7.* Agregada la posibilidad de abrir Chrome siempre maximizado.## Versión 0.6.* Versión inicial.