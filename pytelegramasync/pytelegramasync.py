"""PyTelegramAsync."""
import asyncio
import json
import urllib.parse
from abc import ABC, abstractmethod

from aiohttp import ClientError, ClientSession


class Telegram(ABC):
    """Telegram

    Nesta classe fazemos a conexão do seu bot com os seus clientes.
    """

    def __init__(
        self, token: str = 'Seu token', limite: int = 10, timeout: int = 0
    ):
        super().__init__()
        self.__token: str = token
        self.__url: str = f'https://api.telegram.org/bot{self.__token}/'
        self.__limite: int = limite
        self.__timeout: int = timeout

    @abstractmethod
    async def menu(self, mensagem: dict):
        """Menu

        Neste método é aonde faremos a lógica de como trataremos
        a mensagem recebida pelo usuário.

        Args:
            mensagem (dict): Aqui receberemos a resposta da API do telegrama
            que contém todas as informações importantes para serem usadas.
        """
        [chat_id, mensagem_id] = await asyncio.gather(
            self.__get_chat_id(mensagem),
            self.__get_mensagem_id(mensagem),
        )
        await self.send_mensagem(
            mensagem=mensagem,
            resposta=f'Respondido - {mensagem_id}',
            marcar=True,
        )
        return chat_id

    async def start(self) -> None:
        """Start

        Neste método fazemos a inicialização da captura das mensagens do
        telegram.
        """
        update_id: int = None
        while True:
            mensagens: list = None
            atualizacao: dict = await self.__get_mensagens(update_id)

            if 'result' in atualizacao:
                mensagens = atualizacao['result']
                tasks_menu = (self.menu(mensagem) for mensagem in mensagens)
                tasks_update_id = (
                    self.__get_update_id(mensagem=mensagem)
                    for mensagem in mensagens
                )
                update_id = await asyncio.gather(*tasks_update_id)
                await asyncio.gather(*tasks_menu)
                print(update_id)
                if update_id:
                    update_id = max(update_id, key=int)

    @staticmethod
    async def __get_mensagem_id(mensagem: dict = None) -> int:
        """Get Mensagem ID.

        Neste método pegamos o id da mensagem recebida pelo telegram.

        Args:
            mensagem (dict): Aqui receberemos a resposta da API do telegrama
            que contém todas as informações importantes para serem usadas.

        Returns:
            int: id da mensagem
        """
        try:
            return int(mensagem['message']['message_id'])
        except TypeError:
            return 0

    @staticmethod
    async def __get_update_id(mensagem: dict = None) -> int:
        """Get Update ID.

        Neste método pegamos o id da atualização da mensagem
        recebida pelo telegram.

        Args:
            mensagem (dict): Aqui receberemos a resposta da API do telegrama
            que contém todas as informações importantes para serem usadas.

        Returns:
            int: id da atualização da mensagem
        """
        try:
            return int(mensagem['update_id'])
        except TypeError:
            return -1

    @staticmethod
    async def __get_chat_id(mensagem: dict = None) -> int | None:
        """Get chat ID.

        Neste método pegamos o id do seu cliente do telegram.

        Args:
            mensagem (dict): Aqui receberemos a resposta da API do telegrama
            que contém todas as informações importantes para serem usadas.

        Returns:
            int: id do seu cliente
        """
        try:
            return int(mensagem['message']['from']['id'])
        except TypeError:
            return None

    async def __get_mensagens(self, update_id: int = None) -> dict | None:
        """Get Mensagens

        Neste método coletamos as mensagens da API do Telegram.

        Args:
            update_id (int): ID da ultima mensagem pega.

        Returns:
            dict | None: mensagens recebidas pela API do Telegram.
        """
        link_requisicao: str = (
            f'{self.__url}getUpdates?'
            f'limit={self.__limite}&'
            f'timeout={self.__timeout}'
        )

        if update_id:
            link_requisicao = f'{link_requisicao}&offset={update_id + 1}'
        try:
            async with ClientSession() as session:
                response = await session.get(link_requisicao)
            return json.loads(await response.content.read())
        except ClientError:
            return None

    async def send_mensagem(
        self,
        mensagem: str = None,
        resposta: str = None,
        marcar: bool = False,
    ) -> None:
        """Send Mensagem.

        Neste método fazemos o envio de mensagem para o seu cliente.

        Args:
            mensagem (str): Mensagem recebida pelo cliente.
            resposta (str): Sua resposta para o cliente.
            marcar (bool): Se deseja marcar a resposta na
            mensagem do cliente.
        """

        try:
            [chat_id, mensagem_id] = await asyncio.gather(
                self.__get_chat_id(mensagem), self.__get_mensagem_id(mensagem)
            )
        except TypeError:
            return False

        resposta = urllib.parse.quote_plus(resposta)

        if marcar:
            link_de_envio = (
                f'{self.__url}sendMessage?'
                f'chat_id={chat_id}&'
                f'text={resposta}&'
                f'reply_to_message_id={mensagem_id}&'
                'parse_mode=Markdown'
            )
        else:
            link_de_envio = (
                f'{self.__url}sendMessage?'
                f'chat_id={chat_id}&'
                f'text={resposta}&'
                'parse_mode=Markdown'
            )

        try:
            async with ClientSession() as session:
                await session.post(link_de_envio)
            return True
        except ClientError:
            return False
