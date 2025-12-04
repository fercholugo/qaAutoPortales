Feature: Flujo principal portal cautivo api(datos correctos)
  Como usuario de un portal cautivo configurado con api
  Quiero poder ingresar los datos solicitados en el flujo del portal
  Para poder acceder al servicio de internet

  Scenario: Flujo principal datos correctos portal cautivo con api (unico)
    Given que el usuario "Fernando" accede al portal cautivo en "chrome" con la url "https://app.datawifi.co/easyfi/web/app.php/portal?called=98254a993fe4&mac="
    When ingresa todos los datos obligatorios y validos en el formulario
    Then el flujo es finalizado y validado correctamente

  Scenario Outline: Flujo principal datos correctos portales cautivos con api (varios)
    Given que el usuario "<nombre_actor>" accede al portal cautivo en "<navegador>" con la url "<url>"
    When ingresa todos los datos obligatorios y validos en el formulario
    Then el flujo es finalizado y validado correctamente

    Examples:
      | nombre_actor | navegador | url                                                                          |
      | Fernando     | chrome    | https://app.datawifi.co/easyfi/web/app.php/portal?called=98254a993fe4&mac=   |
      | Miller       | chrome    | https://app.datawifi.co/easyfi/web/app.php/portal?called=2303x11897&mac=     |
    

