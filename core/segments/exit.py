import promptvar


def main(segment):
    text_inside = ""
    skip = False

    exit_code = promptvar.variables.get("exitcode", 0)

    properties = segment.get("properties", {})
    display_exit_code = properties.get("display_exit_code", True)
    always_enabled = properties.get("always_enabled", False)
    error_color = properties.get("error_color", "red")
    success_icon = properties.get("success_icon", "✔")
    error_icon = properties.get("error_icon", "✖")
    
    if exit_code == 0:
        text_inside = success_icon
        if not always_enabled: skip = True
    else:
        if error_color:
            text_inside = f'<style fg="{error_color}">{error_icon}'
        
            if display_exit_code:
                text_inside += " " + str(exit_code) + "</style>"
                
        else:
            text_inside = error_icon
            
            if display_exit_code:
                text_inside += " " + str(exit_code)

    return text_inside, skip