from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'clave_secreta_para_sesiones'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    tareas = conn.execute('SELECT * FROM tareas').fetchall()
    conn.close()
    return render_template('index.html', tareas=tareas)

@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']

        if not titulo:
            flash('El título es requerido!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO tareas (titulo, descripcion) VALUES (?, ?)',
                         (titulo, descripcion))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    conn = get_db_connection()
    tarea = conn.execute('SELECT * FROM tareas WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']

        if not titulo:
            flash('El título es requerido!')
        else:
            conn.execute('UPDATE tareas SET titulo = ?, descripcion = ? WHERE id = ?',
                         (titulo, descripcion, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    conn.close()
    return render_template('edit.html', tarea=tarea)

@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM tareas WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash(f'La tarea con id {id} ha sido eliminada.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
