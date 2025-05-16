import re


def get_string_as_number(value):
    # Fonction équivalente à noExponents (supprime la notation exponentielle)
    def no_exponents(num):
        if isinstance(num, (int, float)):
            s = "{:.10f}".format(num).rstrip('0').rstrip('.') if '.' in "{:.10f}".format(num) else str(num)
            return s
        return str(num)

    try:
        # Essai de conversion directe en nombre
        exponent = no_exponents(float(value))
        if not exponent.lower().startswith('nan'):  # Vérifie si ce n'est pas NaN
            return float(exponent) if '.' in exponent else int(exponent)
    except (ValueError, TypeError):
        pass

    # Traitement des chaînes
    value_str = str(value).replace(',', '.')
    retour = '0'

    try:
        # Extraction des chiffres et points
        matches = re.findall(r'[\d\.]+', value_str)
        if matches:
            num_str = ''.join(matches)
            # Gestion des points multiples
            dots_count = num_str.count('.')
            while dots_count > 1:
                num_str = num_str.replace('.', '', 1)
                dots_count -= 1
            retour = num_str if num_str else '0'
    except Exception as e:
        print(f"Error processing {value}: {e}")

    # Conversion finale en nombre
    try:
        return float(retour) if '.' in retour else int(retour)
    except (ValueError, TypeError):
        return 0

def is_number(value):
    """Vérifie si une valeur peut être convertie en nombre"""
    try:
        float(value)
        return True
    except ValueError:
        return False

# def get_string_as_number(text):
#     """Convertit un texte en nombre"""
#     try:
#         return float(text.replace(" ", ""))
#     except ValueError:
#         return text