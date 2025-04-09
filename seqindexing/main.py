from app import create_app


if __name__ == '__main__':
    server = create_app()
    server.run(debug=True, port=8050)