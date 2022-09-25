# PyTelegramAsync

Uma forma simples de conexão com o Telegram de forma assíncrona em Python.

## Exemplo de Uso

### Como pegar as mensagens

```python
from pytelegramasync import Telegram

class Bot(Telegram):

    async def menu(self, mensagem: dict):
        print(mensagem);
        await self.send_mensagem(
            mensagem=mensagem,
            resposta=f'Respondido - {mensagem_id}',
            marcar=True,
        )
```

Como o PyTelegramAsync é uma classe abstrata tu tens que criar uma classe
que herda dele todos os métodos e fazer apenas o método menu aonde 
será recebia uma mensagem do usuário.
