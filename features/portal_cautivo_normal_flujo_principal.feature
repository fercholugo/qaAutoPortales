Feature: Flujo principal portal cautivo normal(datos correctos)
  Como usuario de un portal cautivo
  Quiero poder ingresar los datos solicitados en el flujo del portal
  Para poder acceder al servicio de internet

  Scenario: Flujo principal datos correctos portal cautivo normal (unico)
    Given que el usuario "Fernando" accede al portal cautivo en "chrome" con la url "https://app.datawifi.co/easyfi/web/app.php/portal?called=764x3806&mac="
    When ingresa todos los datos obligatorios y validos en el formulario
    Then el flujo es finalizado y validado correctamente

  Scenario Outline: Flujo principal datos correctos portales cautivos normales (varios)
    Given que el usuario "<nombre_actor>" accede al portal cautivo en "<navegador>" con la url "<url>"
    When ingresa todos los datos obligatorios y validos en el formulario
    Then el flujo es finalizado y validado correctamente

    Examples:
      | nombre_actor | navegador | url                                                                         |
      | Fernando     | chrome    | https://app.datawifi.co/easyfi/web/app.php/portal?called=f89e2875a8aa&mac=  |
      | Maria        | chrome    | https://app.datawifi.co/easyfi/web/app.php/portal?called=764x3806&mac=      |
      | Juan         | chrome    | https://app.datawifi.co/easyfi/web/app.php/portal?called=764x3460&mac=      |

