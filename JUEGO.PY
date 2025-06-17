import random

def juego_adivinanza():
    """
    Simula un juego simple de adivinanza de números.
    """
    print("¡Bienvenido al juego de adivinanza de números!")
    print("Estoy pensando en un número entre 1 y 20.")

    # Genera un número aleatorio entre 1 y 20 (ambos incluidos)
    numero_secreto = random.randint(1, 20)
    intentos = 0

    while True:
        try:
            adivinanza = int(input("¿Cuál es tu adivinanza? "))
            intentos += 1

            if adivinanza < numero_secreto:
                print("¡Demasiado bajo! Intenta de nuevo.")
            elif adivinanza > numero_secreto:
                print("¡Demasiado alto! Intenta de nuevo.")
            else:
                print(f"¡Felicidades! Adivinaste el número {numero_secreto} en {intentos} intentos.")
                break # Sale del bucle cuando se adivina correctamente
        except ValueError:
            print("Entrada inválida. Por favor, ingresa un número.")

# Llama a la función para iniciar el juego
if __name__ == "__main__":
    juego_adivinanza()
