# Fases del análisis

Mini-JFC desarrolla cada análisis en 5 fases. Las fases las coordina el Orchestrator; las fases no son agentes.

## 1. Strategy
Entender el objetivo físico, crear el plan del análisis y determinar qué información necesita el sistema (literatura, documentación y datasets).

## 2. Exploration
Buscar datasets, explorar los archivos ROOT/Parquet, identificar las variables disponibles y comprobar que los datos sirven para el objetivo.

## 3. Processing
Ejecutar el análisis: aplicar selecciones, producir histogramas y calcular los resultados.

## 4. Validation
Revisar código, física y resultados, y detectar problemas. Si algo falla, se vuelve a fases anteriores (bucle Validation -> fases anteriores).

## 5. Documentation
Documentar la metodología y los resultados, registrar la literatura usada y generar el informe final.
