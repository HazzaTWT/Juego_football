from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os

app = Flask(__name__, template_folder='Templates')
app.secret_key = "una_clave_muy_secreta_123"

ARCHIVO_EQUIPOS = "equipos.json"

# Crear el archivo equipos.json si no existe
if not os.path.exists(ARCHIVO_EQUIPOS):
    with open(ARCHIVO_EQUIPOS, "w") as f:
        json.dump({}, f)

# Cargar jugadores info
with open("jugadores_info.json", "r") as f:
    jugadores_info = json.load(f)

# Formaciones con posiciones en cancha - INCLUYENDO 4-2-1-3
formaciones = {
    '4-3-3': [
        {'nombre': 'Portero', 'top': 550, 'left': 50},
        {'nombre': 'LD', 'top': 450, 'left': 92},
        {'nombre': 'DFC1', 'top': 450, 'left': 65},
        {'nombre': 'DFC2', 'top': 450, 'left': 35},
        {'nombre': 'LI', 'top': 450, 'left': 8},
        {'nombre': 'MC1', 'top': 280, 'left': 20},
        {'nombre': 'MCD', 'top': 322, 'left': 50},
        {'nombre': 'MC3', 'top': 280, 'left': 80},
        {'nombre': 'ED', 'top': 115, 'left': 92},
        {'nombre': 'DC', 'top': 80, 'left': 50},
        {'nombre': 'EI', 'top': 115, 'left': 8},
    ],
    '4-4-2': [
        {'nombre': 'Portero', 'top': 550, 'left': 50},
        {'nombre': 'LD', 'top': 450, 'left': 92},
        {'nombre': 'DFC1', 'top': 450, 'left': 60},
        {'nombre': 'DFC2', 'top': 450, 'left': 40},
        {'nombre': 'LI', 'top': 450, 'left': 8},
        {'nombre': 'MC1', 'top': 280, 'left': 8},
        {'nombre': 'MC2', 'top': 280, 'left': 30},
        {'nombre': 'MC3', 'top': 280, 'left': 70},
        {'nombre': 'MC4', 'top': 280, 'left': 92},
        {'nombre': 'DC1', 'top': 80, 'left': 40},
        {'nombre': 'DC2', 'top': 80, 'left': 60},
    ],
    '4-2-1-3': [
        {'nombre': 'Portero', 'top': 550, 'left': 50},
        {'nombre': 'LD', 'top': 450, 'left': 92},
        {'nombre': 'DFC1', 'top': 450, 'left': 65},
        {'nombre': 'DFC2', 'top': 450, 'left': 35},
        {'nombre': 'LI', 'top': 450, 'left': 8},
        {'nombre': 'MCD1', 'top': 350, 'left': 30},
        {'nombre': 'MCD2', 'top': 350, 'left': 70},
        {'nombre': 'MCA', 'top': 250, 'left': 50},
        {'nombre': 'ED', 'top': 120, 'left': 85},
        {'nombre': 'DC', 'top': 80, 'left': 50},
        {'nombre': 'EI', 'top': 120, 'left': 15},
    ]
}

# SISTEMA DE COMPATIBILIDAD CORREGIDO - Delanteros pueden jugar como extremos
compatibilidad_posiciones = {
    'Portero': ['Portero'],
    'Defensa': ['LD', 'DFC1', 'DFC2', 'LI'],
    'Centrocampista': ['MC1', 'MC2', 'MC3', 'MC4', 'MCD', 'MCD1', 'MCD2', 'MCA'],
    'Extremo': ['ED', 'EI'],
    'Delantero': ['DC', 'DC1', 'DC2', 'ED', 'EI']  # DELANTEROS SÍ PUEDEN JUGAR COMO EXTREMOS
}

# Mapeo de posiciones específicas a roles generales
posicion_a_rol = {
    'Portero': 'Portero',
    'LD': 'Defensa', 'DFC1': 'Defensa', 'DFC2': 'Defensa', 'LI': 'Defensa',
    'MC1': 'Centrocampista', 'MC2': 'Centrocampista', 'MC3': 'Centrocampista', 
    'MC4': 'Centrocampista', 'MCD': 'Centrocampista', 'MCD1': 'Centrocampista', 
    'MCD2': 'Centrocampista', 'MCA': 'Centrocampista',
    'ED': 'Extremo', 'EI': 'Extremo',
    'DC': 'Delantero', 'DC1': 'Delantero', 'DC2': 'Delantero'
}

# Función auxiliar para verificar compatibilidad de posiciones (simplificada)
def es_posicion_compatible(rol_jugador, rol_posicion):
    """Verifica si un jugador puede jugar en una posición específica"""
    # Ya no necesitamos compatibilidades flexibles porque está todo en el diccionario principal
    return False

# Filtro personalizado para formatear números
@app.template_filter('format_number')
def format_number_filter(value):
    try:
        return "{:,}".format(int(value))
    except (ValueError, TypeError):
        return value

# --- Rutas ---
@app.route("/")
def inicio():
    return render_template("index.html")

@app.route("/crear_equipo", methods=["GET", "POST"])
def crear_equipo():
    if request.method == "POST":
        nombre = request.form["nombre"].strip()
        if not nombre:
            return "El nombre del equipo no puede estar vacío 😅"

        with open(ARCHIVO_EQUIPOS, "r") as f:
            equipos = json.load(f)

        if nombre in equipos:
            return "Ya existe un equipo con ese nombre ⚠️"

        equipos[nombre] = {
            "jugadores": [],
            "dinero": 200_000_000,
            "formacion": "4-3-3"
        }

        with open(ARCHIVO_EQUIPOS, "w") as f:
            json.dump(equipos, f, indent=4)

        session["equipo"] = nombre
        return redirect(url_for("ver_equipo", nombre=nombre))

    return render_template("crear_equipo.html")

@app.route("/equipo/<nombre>", methods=["GET"])
def ver_equipo(nombre):
    with open(ARCHIVO_EQUIPOS, "r") as f:
        equipos = json.load(f)

    equipo = equipos.get(nombre)
    if not equipo:
        return "Equipo no encontrado 😢"

    # Validar formación
    formacion_actual = equipo.get('formacion', '4-3-3')
    if formacion_actual not in formaciones:
        formacion_actual = '4-3-3'  # Fallback a 4-3-3 si la formación no existe
        equipo['formacion'] = formacion_actual
        with open(ARCHIVO_EQUIPOS, "w") as f:
            json.dump(equipos, f, indent=4)

    posiciones = formaciones[formacion_actual]

    # Preparar 11 titular y suplentes - CORREGIDO
    titulares = []
    suplentes = []
    
    # Primero, asegurarnos de que todos los jugadores tengan posicion_actual
    for jugador in equipo["jugadores"]:
        if "posicion_actual" not in jugador:
            jugador["posicion_actual"] = None
    
    # Buscar jugadores para cada posición
    for posicion in posiciones:
        jugador_en_posicion = None
        for jugador in equipo["jugadores"]:
            if jugador.get("posicion_actual") == posicion["nombre"]:
                jugador_en_posicion = jugador
                break
        
        if jugador_en_posicion:
            titulares.append({
                **jugador_en_posicion,
                "top": posicion["top"],
                "left": posicion["left"],
                "posicion_actual": posicion["nombre"]
            })
        else:
            # Agregar posición vacía
            titulares.append({
                "nombre": posicion["nombre"],
                "top": posicion["top"],
                "left": posicion["left"],
                "posicion_actual": posicion["nombre"],
                "vacio": True
            })
    
    # Los suplentes son los jugadores sin posición asignada
    for jugador in equipo["jugadores"]:
        if jugador.get("posicion_actual") is None:
            suplentes.append(jugador)

    return render_template(
        "ver_equipo.html",
        nombre=nombre,
        equipo=equipo,
        titulares=titulares,
        suplentes=suplentes,
        formaciones=formaciones.keys(),
        posiciones_formacion=posiciones
    )

@app.route("/guardar_formacion/<nombre>", methods=["POST"])
def guardar_formacion(nombre):
    nueva_formacion = request.form.get("formacion")
    if not nueva_formacion or nueva_formacion not in formaciones:
        return "Formación inválida 😅"

    with open(ARCHIVO_EQUIPOS, "r") as f:
        equipos = json.load(f)

    if nombre not in equipos:
        return "Equipo no encontrado 😢"

    equipos[nombre]['formacion'] = nueva_formacion

    # Reiniciar posiciones actuales al cambiar de formación
    for j in equipos[nombre]["jugadores"]:
        j["posicion_actual"] = None

    with open(ARCHIVO_EQUIPOS, "w") as f:
        json.dump(equipos, f, indent=4)

    return redirect(url_for("ver_equipo", nombre=nombre))

@app.route("/mercado")
def mercado():
    if "equipo" not in session:
        return redirect(url_for("inicio"))

    nombre_equipo = session["equipo"]

    with open(ARCHIVO_EQUIPOS, "r") as f:
        equipos = json.load(f)

    dinero = equipos[nombre_equipo]["dinero"]

    # CORREGIDO: Usar las mismas claves que en jugadores_info.json
    ligas = {
        "Premier League": jugadores_info["Premier League"],
        "La Liga": jugadores_info["La Liga"],
        "Serie A": jugadores_info["Serie A"],
        "Ligue 1": jugadores_info["Ligue 1"],
        "Bundesliga": jugadores_info["Bundesliga"]
    }

    return render_template("mercado.html", ligas=ligas, dinero=dinero)

@app.route("/fichar_ajax/<liga>/<jugador>")
def fichar_ajax(liga, jugador):
    if "equipo" not in session:
        return jsonify({"error": "No tienes un equipo creado."})

    nombre_equipo = session["equipo"]

    with open(ARCHIVO_EQUIPOS, "r") as f:
        equipos = json.load(f)

    equipo = equipos.get(nombre_equipo)
    if not equipo:
        return jsonify({"error": "Equipo no encontrado."})

    # Buscar el jugador en la liga correcta
    if liga not in jugadores_info:
        return jsonify({"error": "Liga no encontrada."})

    jugador_info = None
    for j in jugadores_info[liga]:
        if j["nombre"] == jugador:
            jugador_info = j
            break

    if not jugador_info:
        return jsonify({"error": "Jugador no encontrado."})

    if equipo["dinero"] < jugador_info["valor"]:
        return jsonify({"error": "No tienes suficiente dinero para fichar a este jugador 😅"})

    # Restar el dinero
    equipo["dinero"] -= jugador_info["valor"]

    # Crear una copia del jugador para agregar al equipo
    nuevo_jugador = jugador_info.copy()
    nuevo_jugador["posicion_actual"] = None
    
    # Agregar el jugador al equipo
    equipo["jugadores"].append(nuevo_jugador)

    # Guardar los cambios
    with open(ARCHIVO_EQUIPOS, "w") as f:
        json.dump(equipos, f, indent=4)

    return jsonify({
        "success": True,
        "dinero": equipo["dinero"],
        "mensaje": f"¡Fichaste a {jugador} por ${jugador_info['valor']:,}!"
    })

# Asignar jugador a posición
@app.route("/asignar_posicion/<nombre_equipo>/<nombre_jugador>/<posicion>", methods=["POST"])
def asignar_posicion(nombre_equipo, nombre_jugador, posicion):
    try:
        with open(ARCHIVO_EQUIPOS, "r") as f:
            equipos = json.load(f)

        equipo = equipos.get(nombre_equipo)
        if not equipo:
            return jsonify({"error": "Equipo no encontrado."})

        print(f"DEBUG: Asignando {nombre_jugador} a {posicion} en equipo {nombre_equipo}")

        # Decodificar nombres (pueden venir con espacios o caracteres especiales)
        nombre_jugador = nombre_jugador.replace('+', ' ')
        posicion = posicion.replace('+', ' ')

        # Si nombre_jugador es "VACIO", solo limpiamos la posición
        if nombre_jugador == "VACIO":
            print("DEBUG: Limpiando posición")
            for j in equipo["jugadores"]:
                if j.get("posicion_actual") == posicion:
                    j["posicion_actual"] = None
                    print(f"DEBUG: Limpiada posición {posicion}")
        else:
            # Buscar el jugador
            jugador_encontrado = None
            for j in equipo["jugadores"]:
                if j["nombre"] == nombre_jugador:
                    jugador_encontrado = j
                    break

            if not jugador_encontrado:
                print(f"DEBUG: Jugador {nombre_jugador} no encontrado")
                return jsonify({"error": f"Jugador {nombre_jugador} no encontrado en el equipo."})

            # VERIFICAR COMPATIBILIDAD DE POSICIÓN - SISTEMA SIMPLIFICADO
            rol_jugador = jugador_encontrado["posicion"]
            
            print(f"DEBUG: Jugador {nombre_jugador} es {rol_jugador}, posición deseada: {posicion}")
            
            # Verificar si el jugador puede jugar en esta posición
            posiciones_compatibles = compatibilidad_posiciones.get(rol_jugador, [])
            if posicion not in posiciones_compatibles:
                print(f"DEBUG: Jugador {rol_jugador} no compatible con posición {posicion}")
                return jsonify({"error": f"❌ {nombre_jugador} es {rol_jugador} y no puede jugar como {posicion}"})

            # Quitar cualquier jugador que tenga esa posición
            for j in equipo["jugadores"]:
                if j.get("posicion_actual") == posicion:
                    j["posicion_actual"] = None
                    print(f"DEBUG: Removido jugador de posición {posicion}")

            # Asignar al jugador seleccionado
            jugador_encontrado["posicion_actual"] = posicion
            print(f"DEBUG: Asignado {nombre_jugador} a {posicion}")

        # Guardar los cambios
        with open(ARCHIVO_EQUIPOS, "w") as f:
            json.dump(equipos, f, indent=4)

        print("DEBUG: Cambios guardados exitosamente")
        return jsonify({"ok": True})

    except Exception as e:
        print(f"DEBUG: Error en asignar_posicion: {str(e)}")
        return jsonify({"error": f"Error interno: {str(e)}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)