import random


class RandomGeneratorData:
    """Generador de datos ramdom"""

    @staticmethod
    def generate_random_mac():
        """Genera una dirección MAC aleatoria con prefijo 02:00:00"""
        return "020000%02x%02x%02x" % (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
    )

    @staticmethod
    def generate_random_phone():
        """Genera un número de teléfono aleatorio"""
        return f"3{random.randint(10, 99)}{random.randint(1000000, 9999999)}"
    
