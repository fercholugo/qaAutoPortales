Feature: Proximos Pasos

Pasos realizados e implementados a HOY:

1. Inclusión y automatización de reportes
- Integración de reportes automáticos con Allure y pytest-html.
- Personalización dinámica del reporte HTML: extracción de scenario, historia de usuario y logs de la Task (incluyendo MAC generada).
- Script externo (personalizar_reporte.py) para limpiar y reordenar secciones del reporte HTML.
- Limpieza automática de resultados previos antes de cada ejecución para evitar acumulación.

2. Refactorización y modularización del framework
- Migración de script procedural a estructura profesional con POO y patrón Screenplay.
- Implementación de utilidades para detección de elementos (utils_detect_form_elements.py), generación de MAC y datos random.
- Refactorización de la Task principal para modularidad, trazabilidad, robustez en interacción de elementos y flujo de los mismos dependiendo de los paneles(inputs, selects, checkboxes, radios, textareas, botones).
  - validacion para que interactue con javascript en caso de que el elemento no sea interactuable de forma directa.
  - implementacion de esperas explicitas para asegurar la presencia y visibilidad de los elementos antes de interactuar con ellos.
  - implementacion para captura de logs en cada paso de la Task para el reporte

3. Validaciones y Questions Screenplay
Creación e implementacion de la question "is_on_google.py" para validar que el flujo termina en la página de Google, 
para condicionar el éxito del test según la URL final. (aqui va la validacion por base de datos)


Pasos a realizar e implementar:
Grabacion en video de la ejecucion y listarlo en el reporte(Ya se esta trabajando en ello)

1. Implementacion de Questions con base de datos(se necesitan credenciales)
2. Analisis e implementacion inicial de portales con flujo de datos correctos especial(con videos, con api)
3. Definir y si es asi analizar implementacion de otros navegadores(firefox, safari)
4. Analisis y definicion otros scenarios(Validacion mensajes cuando hay datos incorrectos, Ej.)
5. Definir y si es asi analizar implementacion de framework como servicio Web.
