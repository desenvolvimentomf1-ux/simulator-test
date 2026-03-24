from fastapi import FastAPI
from pydantic import BaseModel
import asyncio
from playwright.async_api import async_playwright

app = FastAPI()

class SimulacaoData(BaseModel):
    email_cliente: str
    senha: str
    cpf_cliente: str
    nome_cliente: str
    id_veiculo: str
    id: str = "sem_id"

@app.post("/simular")
async def simular(data: SimulacaoData):
    return await run_simulation(data.dict())

async def run_simulation(data):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        result = {"status": "Falha", "message": "Erro desconhecido", "screenshot_url": None}

        try:
            # 1. Login
            await page.goto("https://site-de-veiculos.com.br/login")
            await page.fill("input[name='email']", data['email_cliente'])
            await page.fill("input[name='password']", data['senha'])
            await page.click("button[type='submit']")
            await page.wait_for_url("**/dashboard", timeout=10000)

            # 2. Navegar e simular
            await page.goto(f"https://site-de-veiculos.com.br/veiculo/{data['id_veiculo']}")
            await page.click("text=Simular Compra")
            await page.fill("#cpf", data['cpf_cliente'])
            await page.fill("#nome_completo", data['nome_cliente'])
            await page.click("button:has-text('Confirmar Simulação')")

            # 3. Capturar resultado
            await page.wait_for_selector(".resultado-simulacao", timeout=15000)
            resultado_texto = await page.locator(".resultado-simulacao").inner_text()

            result = {"status": "Concluído", "message": resultado_texto, "screenshot_url": None}

        except Exception as e:
            result["message"] = f"Erro: {str(e)}"
        finally:
            await context.close()
            await browser.close()

        return result
```

**Arquivo 2 — `requirements.txt`**
```
fastapi
uvicorn
playwright
