# Software FJ — Sistema de Gestión de Clientes, Servicios y Reservas

Sistema orientado a objetos en Python (sin bases de datos) para gestionar
clientes, servicios (salas de reuniones, alquiler de equipos, asesorías
especializadas) y reservas, con manejo robusto de excepciones y registro
de eventos/errores en logs.

## Requisitos

- Python 3.10+
- Sin dependencias externas (solo librería estándar)

## Ejecución

```bash
python3 main.py
```

Esto ejecuta una simulación de 15 operaciones (registros válidos e
inválidos de clientes, creación correcta e incorrecta de servicios, y
reservas exitosas y fallidas), imprime un resumen final en consola y
genera el archivo `logs/eventos.log` con el detalle de cada evento/error.

## Estructura del proyecto

```
softwarefj/
├── excepciones.py   # Jerarquía de excepciones personalizadas
├── entidad.py        # Clase abstracta EntidadSistema (ABC)
├── cliente.py         # Clase Cliente (encapsulación + validaciones)
├── servicio.py         # Clase abstracta Servicio + SalaReunion,
│                        # AlquilerEquipo, AsesoriaEspecializada
├── reserva.py          # Clase Reserva (ciclo de vida y cálculo de costo)
├── sistema.py           # Fachada SistemaSoftwareFJ (listas en memoria)
├── logger.py             # Configuración de logging a archivo
├── main.py                # Simulación de 15 operaciones
└── logs/
    └── eventos.log         # Se genera al ejecutar main.py
```

## Arquitectura orientada a objetos

- **Abstracción**: `EntidadSistema` y `Servicio` son clases abstractas
  (`ABC` + `@abstractmethod`) que definen contratos comunes.
- **Herencia**: `Cliente` y `Servicio` heredan de `EntidadSistema`;
  `SalaReunion`, `AlquilerEquipo` y `AsesoriaEspecializada` heredan de
  `Servicio`.
- **Polimorfismo**: cada servicio sobrescribe `calcular_costo_base()`,
  `validar_parametros()` y `descripcion()` con su propia lógica.
- **Encapsulación**: todos los atributos son privados y se acceden vía
  propiedades (`@property`) con validación en cada setter.
- **Sobrecarga de métodos (simulada)**: `Servicio.calcular_costo()`
  acepta distintas combinaciones de argumentos (cantidad, impuesto,
  descuento) usando `*args`/`**kwargs`.
- **Manejo de excepciones**: jerarquía propia (`SoftwareFJError` y
  subclases), bloques `try/except`, `try/except/else`, `try/except/finally`
  y encadenamiento de excepciones (`raise ... from exc`) en
  `Reserva.procesar()`.

## Logs

Cada operación (exitosa o fallida) queda registrada en
`logs/eventos.log` con nivel `INFO`, `WARNING`, `ERROR` o `DEBUG`,
según corresponda, sin detener nunca la ejecución del programa.
