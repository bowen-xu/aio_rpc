from zero import ZeroServer

app = ZeroServer(port=5559)

@app.register_rpc
async def t(*args) -> str:
    return 1

if __name__ == "__main__":
    app.run()