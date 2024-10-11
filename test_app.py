import pytest
from app import app, get_db_connection

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['DATABASE'] = 'test_database.db'

    with app.test_client() as client:
        # Crear una base de datos en memoria para pruebas
        with app.app_context():
            conn = get_db_connection()
            conn.execute('DROP TABLE IF EXISTS tareas')
            conn.execute('CREATE TABLE tareas (id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT NOT NULL, descripcion TEXT)')
            conn.commit()
            conn.close()
        yield client

def test_index(client):
    response = client.get('/')
    assert response.status_code == 200

def test_create_task(client):
    response = client.post('/create', data={'titulo': 'Tarea de prueba', 'descripcion': 'Descripción de prueba'}, follow_redirects=True)
    assert response.status_code == 200
    assert 'Tarea de prueba' in response.data.decode('utf-8')

def test_create_task_without_title(client):
    response = client.post('/create', data={'titulo': '', 'descripcion': 'Sin título'}, follow_redirects=True)
    assert 'El título es requerido!' in response.data.decode('utf-8')

def test_edit_task(client):
    # Crear una tarea primero
    client.post('/create', data={'titulo': 'Tarea a editar', 'descripcion': 'Descripción inicial'}, follow_redirects=True)
    # Editar la tarea
    conn = get_db_connection()
    tarea = conn.execute('SELECT * FROM tareas WHERE titulo = ?', ('Tarea a editar',)).fetchone()
    conn.close()

    response = client.post(f'/{tarea["id"]}/edit', data={'titulo': 'Tarea editada', 'descripcion': 'Descripción editada'}, follow_redirects=True)
    assert 'Tarea editada' in response.data.decode('utf-8')

def test_delete_task(client):
    # Crear una tarea primero
    client.post('/create', data={'titulo': 'Tarea a eliminar', 'descripcion': 'Descripción de eliminación'}, follow_redirects=True)
    # Eliminar la tarea
    conn = get_db_connection()
    tarea = conn.execute('SELECT * FROM tareas WHERE titulo = ?', ('Tarea a eliminar',)).fetchone()
    conn.close()

    response = client.post(f'/{tarea["id"]}/delete', follow_redirects=True)
    assert f'La tarea con id {tarea["id"]} ha sido eliminada.' in response.data.decode('utf-8')

# Nuevos casos de prueba

def test_create_task_with_long_title(client):
    long_title = 'T' * 300  # Título de 300 caracteres
    response = client.post('/create', data={'titulo': long_title, 'descripcion': 'Descripción con título largo'}, follow_redirects=True)
    assert response.status_code == 200
    assert long_title in response.data.decode('utf-8')

def test_create_duplicate_task_titles(client):
    title = 'Tarea Duplicada'
    # Primera creación
    response1 = client.post('/create', data={'titulo': title, 'descripcion': 'Primera vez'}, follow_redirects=True)
    # Segunda creación
    response2 = client.post('/create', data={'titulo': title, 'descripcion': 'Segunda vez'}, follow_redirects=True)
    assert response1.status_code == 200
    assert response2.status_code == 200
    # Verificar que ambas tareas existen
    conn = get_db_connection()
    tareas = conn.execute('SELECT * FROM tareas WHERE titulo = ?', (title,)).fetchall()
    conn.close()
    assert len(tareas) == 2

def test_edit_nonexistent_task(client):
    nonexistent_id = 9999
    response = client.post(f'/{nonexistent_id}/edit', data={'titulo': 'Nuevo título', 'descripcion': 'Nueva descripción'}, follow_redirects=True)
    assert response.status_code == 404  # Esperamos un error 404

def test_delete_nonexistent_task(client):
    nonexistent_id = 9999
    response = client.post(f'/{nonexistent_id}/delete', follow_redirects=True)
    assert response.status_code == 404  # Esperamos un error 404

def test_access_nonexistent_route(client):
    response = client.get('/ruta_no_existente')
    assert response.status_code == 404

def test_massive_task_creation(client):
    for i in range(1000):
        response = client.post('/create', data={'titulo': f'Tarea {i}', 'descripcion': f'Descripción {i}'}, follow_redirects=True)
        assert response.status_code == 200
    # Verificar que se crearon 1000 tareas
    conn = get_db_connection()
    count = conn.execute('SELECT COUNT(*) FROM tareas').fetchone()[0]
    conn.close()
    assert count == 1000
