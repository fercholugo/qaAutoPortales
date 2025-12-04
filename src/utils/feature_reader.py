import re

def get_scenario_info(feature_file_path, scenario_name=None):
    """
    Extrae el scenario por nombre (id) desde el archivo .feature. Si no se encuentra, devuelve el primero como fallback.
    """
    try:
        with open(feature_file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        if scenario_name:
            # Buscar Scenario Outline por nombre
            pattern_outline = rf'Scenario Outline:.*{re.escape(scenario_name)}.*?(?=Scenario Outline:|Scenario:|Feature:|\Z)'
            match_outline = re.search(pattern_outline, content, re.DOTALL | re.IGNORECASE)
            if match_outline:
                return match_outline.group(0).strip()
            # Buscar Scenario por nombre
            pattern_scenario = rf'Scenario:.*{re.escape(scenario_name)}.*?(?=Scenario Outline:|Scenario:|Feature:|\Z)'
            match_scenario = re.search(pattern_scenario, content, re.DOTALL | re.IGNORECASE)
            if match_scenario:
                return match_scenario.group(0).strip()
        # Si no se encuentra, devolver el primero
        pattern_first_outline = r'Scenario Outline:.*?(?=Scenario Outline:|Scenario:|Feature:|\Z)'
        match_first_outline = re.search(pattern_first_outline, content, re.DOTALL | re.IGNORECASE)
        if match_first_outline:
            return match_first_outline.group(0).strip()
        pattern_first_scenario = r'Scenario:.*?(?=Scenario Outline:|Scenario:|Feature:|\Z)'
        match_first_scenario = re.search(pattern_first_scenario, content, re.DOTALL | re.IGNORECASE)
        if match_first_scenario:
            return match_first_scenario.group(0).strip()
        return "No se encontró ningún Scenario en el feature."
    except Exception as e:
        return f"Error leyendo feature file: {str(e)}"

def get_feature_title(feature_file_path):
    try:
        with open(feature_file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if line.strip().startswith('Feature:'):
                    return line.strip()
        return "Feature: No title found"
    except:
        return "Feature: Error reading file"

def get_scenario_by_keyword(feature_file_path, keyword=None):
    """
    Busca el scenario cuyo título contenga la palabra clave (keyword). Si no encuentra, devuelve el primero.
    """
    try:
        with open(feature_file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Buscar todos los Scenario Outline y Scenario
        pattern = r'(Scenario Outline:.*?(?=Scenario Outline:|Scenario:|Feature:|\Z))|(Scenario:.*?(?=Scenario Outline:|Scenario:|Feature:|\Z))'
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        scenarios = [m[0] if m[0] else m[1] for m in matches]

        if keyword:
            for scenario in scenarios:
                # Buscar coincidencia parcial en el título del scenario
                title_match = re.search(r'(Scenario Outline:|Scenario:)(.*)', scenario)
                if title_match and keyword.lower() in title_match.group(2).lower():
                    return scenario.strip()
        # Si no encuentra, devolver el primero
        if scenarios:
            return scenarios[0].strip()
        return "No se encontró ningún Scenario en el feature."
    except Exception as e:
        return f"Error leyendo feature file: {str(e)}"

def get_task_execution_logs():
    """
    Devuelve los logs de ejecución de la Task principal, incluyendo la MAC generada.
    """
    try:
        from src.tasks.task_fill_portal_form import TaskFillPortalForm
        info = TaskFillPortalForm.get_execution_info()
        logs = info.get('logs', [])
        return logs
    except Exception as e:
        return [f"Error obteniendo logs de la Task: {str(e)}"]