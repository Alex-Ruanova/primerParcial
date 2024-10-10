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
