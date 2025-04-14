from app import create_app


if __name__ == '__main__':
    server = create_app()
    server.run(debug=True, port=8060, use_reloader=True)

    # dashboard: http://localhost:8060/dashboard/