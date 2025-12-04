#!/usr/bin/env bash
FEATURE_ALIAS=${1:-portal_normal}
SCENARIO=${2:-}

case "$FEATURE_ALIAS" in
  portal_normal)
    STEPS_FILE="tests/test_steps_portal_cautivo_normal_flujo_principal.py"
    FEATURE_FILE="features/portal_cautivo_normal_flujo_principal.feature"    
    ;;
  portal_api)
    STEPS_FILE="tests/test_steps_portal_cautivo_normal_flujo_principal.py"
    FEATURE_FILE="features/portal_cautivo_api_flujo_principal.feature"
    ;;
  *)
    echo "Alias de feature no reconocido: $FEATURE_ALIAS"
    exit 1
    ;;
esac

# Exporta alias y keywords para que steps/fixtures puedan usarlos
export FEATURE_ALIAS
export SCENARIO_KEYWORD="$SCENARIO"

pytest "$STEPS_FILE" -v -s ${SCENARIO:+-k "$SCENARIO"} --html=reporte_html/reporte.html --self-contained-html
python3 reporte_html/personalizar_reporte.py "$FEATURE_FILE"
open reporte_html/reporte.html



