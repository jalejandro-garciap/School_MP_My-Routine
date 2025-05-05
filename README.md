# Mi Rutina

Es un sistema que incentiva la actividad física y combate la contaminación recompensando a los usuarios con pasajes de transporte público por completar rutinas de ejercicio. Utiliza visión por computadora (detección facial y corporal) para validar los ejercicios y una plataforma web para la gestión de usuarios e historial. Busca mejorar la salud y la sostenibilidad urbana.

## Objetivos Principales

* Mejorar la salud de los usuarios.

* Promover la actividad física.

* Reducir el uso de transporte privado.

## Problemática

Combate el sedentarismo y la contaminación causada por el uso excesivo de vehículos personales.

## Beneficios Clave

Mejora la salud, reduce el tráfico y la contaminación, fomenta hábitos activos y es accesible.

## Metodología y Tecnología

Desarrollado con metodología ágil (Scrum y Kanban) y un enfoque MVC. Tecnologías clave incluyen:

* **Visión por Computadora:** CNN, Haar Cascades, MediaPipe para detección y validación de ejercicios.

* **Backend:** Spring Boot (Java).

* **Frontend:** Angular (Typescript).

* **Base de Datos:** PostgreSQL.

* **Despliegue:** Railway.

* **Seguridad:** JWT para autenticación.

## Requerimientos Funcionales

Incluye registro/inicio de sesión, creación y seguimiento de rutinas, generación de pasajes, integración con transporte público, paneles de usuario/admin, historial, notificaciones, recompensas, seguridad y escalabilidad.

## Resultados y Conclusiones

El proyecto validó su atractivo logrando registros de usuarios y demostrando la comprensión de su objetivo. Es una solución viable con potencial para mejorar la calidad de vida y reducir la contaminación.

## Video Explicativo

[![Alt text](https://img.youtube.com/vi/dOGhXYsRVz0/0.jpg)](https://www.youtube.com/watch?v=dOGhXYsRVz0)

## Ejecución del Código Python (Flask)

El código Python proporcionado (`main.py`) parece ser la lógica central que se ejecuta en la estación física, interactuando con la cámara y el lector RFID.

**Requisitos:**

* Python 3.x

* Flask (aunque el código principal no muestra la estructura típica de una app Flask web, asume que los controladores interactúan con algún framework web como Flask).

* OpenCV (`cv2`)

* Bibliotecas para detección facial/corporal (MediaPipe, etc. - asumidas por los controladores).

* Bibliotecas para RFID (asumidas por el controlador RFID).

* Módulos locales del proyecto (`controllers`, `database`, `utils`).

**Instrucciones de Ejecución:**

1. Asegúrate de tener Python instalado.

2. Instala las dependencias necesarias (ej: `pip install Flask opencv-python mediapipe`). Puede que necesites instalar otras bibliotecas dependiendo de la implementación exacta de los controladores de RFID y sonido.

3. Asegúrate de que la cámara y el lector RFID estén conectados y sean accesibles por el sistema.

4. Configura la base de datos PostgreSQL y asegúrate de que las operaciones en `database_operations.py` estén correctamente configuradas para conectarse a ella.

5. Ejecuta el script principal desde la terminal:

python main.py
6. La aplicación debería iniciar la captura de video y esperar la interacción con la tarjeta RFID. Presiona 'q' para salir.

**Nota:** Este código es una parte del sistema completo. La integración con el backend (Spring Boot) y frontend (Angular) para la gestión de usuarios, historial y la recarga de saldo se realiza a través de las operaciones de base de datos y, presumiblemente, APIs a las que acceden los controladores.

## Diagrama de Flujo del Proceso Principal

```mermaid
graph TD;
    A[Inicio] --> B[Inicializar Controladores];
    B --> C[Obtener información de la Estación];
    C --> D[Inicializar Cámara y Temporizador];
    D --> E[Iniciar lectura de RFID en segundo plano];
    E --> F[Bucle Principal];
    F --> G[Capturar Fotograma];
    G --> H{¿Fotograma es válido?};
    H -->|Sí| I{¿Tarjeta RFID escaneada?};
    I -->|No| J["Mostrar PRESENTA TU TARJETA"];
    J --> K[Reiniciar Temporizador];
    K --> F;
    I -->|Sí| L{¿Rostro capturado?};
    L -->|No| M[Intentar detectar Rostro];
    M --> N["Mostrar ANALISIS FACIAL"];
    N --> O{¿Rostro detectado?};
    O -->|Sí| P{¿Han pasado 3 segundos?};
    P -->|No| Q["Mostrar contador de segundos"];
    Q --> R[Añadir rostro a la lista];
    R --> F;
    P -->|Sí| S[Establecer Rostro capturado a Verdadero];
    S --> T[Reiniciar Temporizador];
    T --> U[Continuar al siguiente paso];
    O -->|No| V["Mostrar MIRA A LA CAMARA"];
    V --> W[Reiniciar Temporizador];
    W --> F;
    L -->|Sí| X{¿Cuerpo capturado?};
    X -->|No| Y[Intentar detectar Cuerpo];
    Y --> Z["Mostrar ANALISIS CORPORAL"];
    Z --> AA{¿Cuerpo detectado?};
    AA -->|Sí| AB{¿Han pasado 3 segundos?};
    AB -->|No| AC["Mostrar contador de segundos"];
    AC --> AD[Añadir cuerpo a la lista];
    AD --> F;
    AB -->|Sí| AE[Establecer Cuerpo capturado a Verdadero];
    AE --> AF[Reiniciar Temporizador];
    AF --> AG[Continuar al siguiente paso];
    AA -->|No| AH["Mostrar ALEJATE DE LA CAMARA"];
    AH --> AI[Reiniciar Temporizador];
    AI --> F;
    X -->|Sí| AJ{¿Ejercicio seleccionado?};
    AJ -->|No| AK[Intentar detectar Brazo levantado];
    AK --> AL["Mostrar ESCOGE LEVANTANDO TU BRAZO"];
    AL --> AM{¿Brazo detectado?};
    AM -->|Sí| AN{¿Han pasado 3 segundos?};
    AN -->|No| AO["Mostrar contador de segundos"];
    AO --> AP[Añadir brazo a la lista];
    AP --> F;
    AN -->|Sí| AQ[Establecer Ejercicio seleccionado a Verdadero];
    AQ --> AR[Reiniciar Temporizador];
    AR --> AS[Continuar al siguiente paso];
    AM -->|No| AT["Mostrar MUESTRA TU BRAZO"];
    AT --> AU[Reiniciar Temporizador];
    AU --> F;
    AJ -->|Sí| AV{¿Ejercicio iniciado?};
    AV -->|No| AW{¿Análisis corporal iniciado?};
    AW -->|No| AX[Realizar análisis corporal];
    AX --> F;
    AW -->|Sí| AY{¿Análisis corporal finalizado?};
    AY -->|Sí| AZ[Analizar opción de ejercicio];
    AZ --> BA[Asignar ejercicio basado en análisis];
    BA --> BB[Establecer Ejercicio iniciado a Verdadero];
    BB --> BC[Reiniciar Temporizador];
    BC --> BD[Imprimir resultados];
    BD --> BE[Continuar al siguiente paso];
    AV -->|Sí| BF{¿Ejercicio terminado?};
    BF -->|No| BG{¿Han pasado 60 segundos?};
    BG -->|No| BH{¿Quedan 5 segundos?};
    BH -->|Sí| BI[Reproducir sonido de cuenta regresiva];
    BI --> BJ["Mostrar tiempo restante"];
    BJ --> BK[Ejecutar lógica de validación];
    BK --> F;
    BG -->|Sí| BL[Establecer Ejercicio terminado a Verdadero];
    BL --> BM[Continuar al siguiente paso];
    BF -->|Sí| BN{¿Mostrar resultado?};
    BN -->|No| BO[Determinar si el desafío fue completado];
    BO --> BP[Reproducir sonido de ganador o perdedor];
    BP --> BQ[Insertar registro en la base de datos];
    BQ --> BR[Reiniciar Temporizador];
    BR --> BS[Recargar saldo];
    BS --> BT[Establecer Mostrar resultado a Verdadero];
    BT --> BU[Continuar al siguiente paso];
    BN -->|Sí| BV{¿Han pasado 10 segundos?};
    BV -->|No| BW["Mostrar resultados"];
    BW --> F;
    BV -->|Sí| BX[Reinicializar controladores];
    BX --> BY[Reiniciar Temporizador];
    BY --> F;
    H -->|No| BZ[Continuar al siguiente ciclo];
    BZ --> CA{¿Tecla 'q' presionada?};
    CA -->|Sí| CB[Salir del Bucle Principal];
    CA -->|No| F;
    CB --> CC[Liberar Cámara];
    CC --> CD[Cerrar Ventanas];
    CD --> CE[Fin];
```

