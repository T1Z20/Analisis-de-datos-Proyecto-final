from flask import Flask, render_template, request
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import requests

app = Flask(__name__)
df = pd.read_csv('Dataset/libros-dataset.csv')


# datos  que voy a usar sin necesidad de hacer ninguna transformacion para "medir" similitud
X = df[['paginas', 'valoracion', 'complejidad']]

#escalamos los datos ya que hay valores muy diferentes
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)


#Si dos libros tienen  páginas, valoración y complejidad parecidos entonces seran similares 
Simil = cosine_similarity(X_scaled)
#  1 
#  0
# -1

# Convertir la las similitudes a DataFrame para facilitar la visualización
similaresDF = pd.DataFrame(Simil, index=df['titulo'], columns=df['titulo'])

# Función para obtener la portada del libro
def obtener_portada(titulo_libro):
    url = f"https://www.googleapis.com/books/v1/volumes?q={titulo_libro}&maxResults=1&key=AIzaSyAbHM3KYg6tl8HHzFMUktvsO0lE4BeGT4M"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'items' in data:
            cover_link = data['items'][0].get('volumeInfo', {}).get('imageLinks', {}).get('thumbnail')
            return cover_link
    return None

# Función para mostrar recomendaciones basadas en un libro dado
def recomendar_libros(titulo_libro, n_recomendaciones=3):
    if titulo_libro not in similaresDF.index:
        return f"El libro '{titulo_libro}' no se encuentra en la base de datos."
    
    # Obtener las similitudes del libro dado
    similitudes = similaresDF[titulo_libro]
    
    # Ordenar libros por similitud
    recomendaciones = similitudes.sort_values(ascending=False).head(n_recomendaciones + 1) # puse +1 ya que el primer libro siempre va a hacer el libro que se esta busncado devido a que tiene una valoracion de 1
    
    # Eliminar el libro original de las recomendaciones
    recomendaciones = recomendaciones[recomendaciones.index != titulo_libro]
    
    # Obtener portadas de los libros recomendados
    libros_con_portadas = []
    for libro in recomendaciones.index:
        portada = obtener_portada(libro)
        libros_con_portadas.append({'titulo': libro, 'portada': portada})
    
    return libros_con_portadas

@app.route('/', methods=['GET', 'POST'])
def index():
    recomendaciones = []
    # Obtener la lista de títulos de libros para autocompletar
    libros = df['titulo'].tolist()
    
    if request.method == 'POST':
        titulo_libro = request.form['titulo']
        recomendaciones = recomendar_libros(titulo_libro)
    
    return render_template('index.html', recomendaciones=recomendaciones, libros=libros)

if __name__ == '__main__':
    app.run(debug=True)
