from app import create_app


if __name__ == '__main__':
    server = create_app()
    # server.run(debug=True, port=8050, use_reloader=False)
    server.run(debug=True, port=8050, use_reloader=False, host='0.0.0.0')