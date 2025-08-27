from app import create_app #, db # Comentado
# from app.models import User # Comentado

app = create_app()

# A função abaixo foi comentada pois depende do banco de dados
# @app.shell_context_processor
# def make_shell_context():
#     return {'db': db, 'User': User}

if __name__ == '__main__':
    app.run(debug=True)