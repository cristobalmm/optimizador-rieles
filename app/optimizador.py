import streamlit as st
import pandas as pd
from itertools import combinations_with_replacement
import pulp
import time

# Configuración de la página
st.set_page_config(page_title="Optimizador de Rieles UC", layout="wide")

st.title("🏗️ Optimizador de Corte de Rieles")
st.markdown("""
Esta herramienta calcula la cantidad mínima de barras necesarias para cubrir tu pedido, 
optimizando los cortes para perder la menor cantidad de material posible.\n Para que funcione debes tener todas las medidas en una misma columna en el Excel y la primera celda debe llamrse "Medida (cm)"
""")

# Barra lateral para parámetros
with st.sidebar:
    st.header("Configuración")
    # Cambiado a float y agregado step para decimales
    largo_max = st.number_input("Largo de la barra maestra (cm)", value=580.0, step=0.5, format="%.2f")
    max_piezas = st.number_input("Máximo de piezas por barra", value=4)
    
uploaded_file = st.file_uploader("Sube tu archivo Excel (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        # 1. Leer archivo
        df = pd.read_excel(uploaded_file)
        
        # Intentar encontrar la columna de medidas
        col_medida = None
        for col in df.columns:
            nombre_col = str(col).lower()
            if 'medida' in nombre_col or 'largo' in nombre_col or 'cm' in nombre_col:
                col_medida = col
                break
        
        if col_medida is None:
            col_medida = df.columns[0]
            st.warning(f"No se detectó el nombre de la columna. Usando la primera: '{col_medida}'")

            df[col_medida] = pd.to_numeric(df[col_medida], errors='coerce')
            df = df.dropna(subset=[col_medida]

        # --- CAMBIO PARA DECIMALES ---
        # Asegurar que los datos sean numéricos y redondear para evitar errores de precisión de punto flotante
        df[col_medida] = pd.to_numeric(df[col_medida], errors='coerce').round(2)
        df = df.dropna(subset=[col_medida])
        
        # 2. Procesar Demanda
        demanda = df[col_medida].value_counts().to_dict()
        
        st.subheader("📊 Resumen de Pedido")
        st.write(f"Total de piezas solicitadas: **{sum(demanda.values())}**")
        st.write(f"Medidas únicas detectadas: **{len(demanda)}**")

        if st.button("🚀 Calcular Optimización"):
            with st.spinner("Generando patrones y resolviendo el modelo matemático..."):
                start_time = time.time()
                
                # 3. Generar Patrones Únicos (Flexibles)
                patrones_set = set()
                medidas_disponibles = sorted(demanda.keys())
                
                for r in range(1, max_piezas + 1):
                    for combo in combinations_with_replacement(medidas_disponibles, r):
                        # Usamos un pequeño margen de error (1e-7) para comparaciones de punto flotante
                        if sum(combo) <= (largo_max + 1e-7):
                            valido = True
                            for m in set(combo):
                                if combo.count(m) > demanda[m]:
                                    valido = False
                                    break
                            if valido:
                                patrones_set.add(tuple(sorted(combo)))
                
                patrones_validos = list(patrones_set)
                
                # 4. Definir Problema de Programación Entera
                prob = pulp.LpProblem("Corte_Rieles", pulp.LpMinimize)
                x = pulp.LpVariable.dicts("P", range(len(patrones_validos)), lowBound=0, cat='Integer')

                # Función Objetivo: Minimizar barras totales
                prob += pulp.lpSum([x[i] for i in range(len(patrones_validos))])

                # Restricciones de Demanda
                for medida, cant in demanda.items():
                    prob += pulp.lpSum([x[i] * patrones_validos[i].count(medida) for i in range(len(patrones_validos))]) == cant

                # Resolver
                prob.solve(pulp.PULP_CBC_CMD(msg=0))
                
                end_time = time.time()

            # 5. Mostrar Resultados
            if pulp.LpStatus[prob.status] == 'Optimal':
                st.success(f"✅ ¡Optimización completada en {end_time - start_time:.2f} segundos!")
                
                col1, col2, col3 = st.columns(3)
                total_barras = int(pulp.value(prob.objective))
                
                # Calcular residuo
                residuo_total = 0.0
                resumen_cortes = []
                
                for i in range(len(patrones_validos)):
                    cantidad_barras = int(x[i].varValue)
                    if cantidad_barras > 0:
                        largo_usado = round(sum(patrones_validos[i]), 2)
                        sobrante = round(largo_max - largo_usado, 2)
                        residuo_total += (sobrante * cantidad_barras)
                        resumen_cortes.append({
                            "Cantidad de Barras": cantidad_barras,
                            "Patrón de Corte": " + ".join([str(m) for m in patrones_validos[i]]),
                            "Uso (cm)": largo_usado,
                            "Sobrante c/u (cm)": sobrante
                        })

                with col1:
                    st.metric(f"Barras de {largo_max}cm", total_barras)
                with col2:
                    st.metric("Residuo Total", f"{residuo_total:.2f} cm")
                with col3:
                    eficiencia = (1 - (residuo_total / (total_barras * largo_max))) * 100
                    st.metric("Eficiencia de Material", f"{eficiencia:.2f}%")

                st.subheader("📋 Plan de Corte Detallado")
                resultados_df = pd.DataFrame(resumen_cortes)
                st.table(resultados_df)
                
                # Opción para descargar
                csv = resultados_df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Descargar Plan de Corte (CSV)", csv, "plan_de_corte.csv", "text/csv")
            else:
                st.error("No se pudo encontrar una solución. Revisa si alguna pieza es más larga que la barra maestra.")

    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
else:
    st.info("👋 Por favor, sube un archivo Excel para comenzar.")