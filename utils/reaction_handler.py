from typing import Callable, Dict, List, Optional

import pyrogram
from pyrogram import Client, raw, types, utils
from pyrogram.filters import Filter
from pyrogram.handlers import RawUpdateHandler
from pyrogram.types.object import Object


class PeerReaction(Object):
    """A reaction on a message, sent by a specific peer (user or chat).

    Parameters:
        from_user (:obj:`~pyrogram.types.User`, *optional*):
            The user who reacted, if the reactor is a user.

        sender_chat (:obj:`~pyrogram.types.Chat`, *optional*):
            The chat that sent the reaction, if the reactor is a channel/group.

        date (``int``):
            Date of the reaction.

        reaction (:obj:`~pyrogram.types.Reaction`):
            The reaction type.

        big (``bool``, *optional*):
            True, if the reaction is big (large animation).

        unread (``bool``, *optional*):
            True, if the reaction is unread.

        my (``bool``, *optional*):
            True, if the reaction was sent by the current user.
    """

    def __init__(
        self,
        *,
        client: "pyrogram.Client" = None,
        from_user: Optional["types.User"] = None,
        sender_chat: Optional["types.Chat"] = None,
        date: int = None,
        reaction: "types.Reaction" = None,
        big: bool = None,
        unread: bool = None,
        my: bool = None,
    ):
        super().__init__(client)
        self.from_user = from_user
        self.sender_chat = sender_chat
        self.date = date
        self.reaction = reaction
        self.big = big
        self.unread = unread
        self.my = my

    @staticmethod
    def _parse(
        client: "pyrogram.Client",
        peer_reaction: "raw.types.MessagePeerReaction",
        users: Dict[int, "raw.types.User"],
        chats: Dict[int, "raw.types.Chat"],
    ) -> Optional["PeerReaction"]:
        if not peer_reaction:
            return None

        from_user = None
        sender_chat = None

        if isinstance(peer_reaction.peer_id, raw.types.PeerUser):
            from_user = types.User._parse(
                client, users.get(peer_reaction.peer_id.user_id)
            )
        elif isinstance(peer_reaction.peer_id, raw.types.PeerChannel):
            sender_chat = types.Chat._parse_channel_chat(
                client, chats.get(peer_reaction.peer_id.channel_id)
            )
        elif isinstance(peer_reaction.peer_id, raw.types.PeerChat):
            sender_chat = types.Chat._parse_chat_chat(
                client, chats.get(peer_reaction.peer_id.chat_id)
            )

        return PeerReaction(
            client=client,
            from_user=from_user,
            sender_chat=sender_chat,
            date=peer_reaction.date,
            reaction=types.Reaction._parse(client, peer_reaction.reaction),
            big=peer_reaction.big,
            unread=peer_reaction.unread,
            my=peer_reaction.my,
        )


class MessageReactionsUpdated(Object):
    """Reactions on a message were changed (user-account update).

    This is the parsed form of ``UpdateMessageReactions`` from the Telegram API,
    which is sent to user accounts (as opposed to the bot-only
    ``UpdateBotMessageReaction`` that Pyrofork already handles).

    Parameters:
        chat (:obj:`~pyrogram.types.Chat`):
            The chat containing the message.

        msg_id (``int``):
            Unique identifier of the message inside the chat.

        top_msg_id (``int``, *optional*):
            ID of the top message in the thread (for forum topics).

        reactions (List of :obj:`~pyrogram.types.Reaction`, *optional*):
            Reaction counts on the message. Each item contains the reaction type,
            count, and optionally the chosen order.

        top_reactors (List of :obj:`~pyrogram.types.MessageReactor`, *optional*):
            Top reactors for paid reactions.

        recent_reactions (List of :obj:`PeerReaction`, *optional*):
            Recent individual reactions on the message.

        min (``bool``, *optional*):
            True if the update is minimal (some data may be missing).

        can_see_list (``bool``, *optional*):
            True if the list of reactors is visible.

        reactions_as_tags (``bool``, *optional*):
            True if reactions are used as tags.
    """

    def __init__(
        self,
        *,
        client: "pyrogram.Client" = None,
        chat: "types.Chat" = None,
        msg_id: int = None,
        top_msg_id: Optional[int] = None,
        reactions: Optional[List["types.Reaction"]] = None,
        top_reactors: Optional[List["types.MessageReactor"]] = None,
        recent_reactions: Optional[List["PeerReaction"]] = None,
        min: bool = None,
        can_see_list: bool = None,
        reactions_as_tags: bool = None,
    ):
        super().__init__(client)
        self.chat = chat
        self.msg_id = msg_id
        self.top_msg_id = top_msg_id
        self.reactions = reactions
        self.top_reactors = top_reactors
        self.recent_reactions = recent_reactions
        self.min = min
        self.can_see_list = can_see_list
        self.reactions_as_tags = reactions_as_tags

    @staticmethod
    def _parse(
        client: "pyrogram.Client",
        update: "raw.types.UpdateMessageReactions",
        users: Dict[int, "raw.types.User"],
        chats: Dict[int, "raw.types.Chat"],
    ) -> "MessageReactionsUpdated":
        chat = None
        peer_id = utils.get_peer_id(update.peer)
        raw_peer_id = utils.get_raw_peer_id(update.peer)
        if peer_id > 0:
            chat = types.Chat._parse_user_chat(client, users.get(raw_peer_id))
        elif peer_id < 0:
            chat = types.Chat._parse_channel_chat(client, chats.get(raw_peer_id))

        msg_reactions = update.reactions

        reactions = None
        if msg_reactions and msg_reactions.results:
            reactions = [
                types.Reaction._parse_count(client, rc)
                for rc in msg_reactions.results
            ]

        top_reactors = None
        if msg_reactions and msg_reactions.top_reactors:
            top_reactors = [
                types.MessageReactor._parse(client, mr, users, chats)
                for mr in msg_reactions.top_reactors
            ]

        recent_reactions = None
        if msg_reactions and msg_reactions.recent_reactions:
            recent_reactions = [
                PeerReaction._parse(client, pr, users, chats)
                for pr in msg_reactions.recent_reactions
            ]

        return MessageReactionsUpdated(
            client=client,
            chat=chat,
            msg_id=update.msg_id,
            top_msg_id=getattr(update, "top_msg_id", None),
            reactions=reactions,
            top_reactors=top_reactors,
            recent_reactions=recent_reactions,
            min=getattr(msg_reactions, "min", None) if msg_reactions else None,
            can_see_list=getattr(msg_reactions, "can_see_list", None) if msg_reactions else None,
            reactions_as_tags=getattr(msg_reactions, "reactions_as_tags", None) if msg_reactions else None,
        )


def on_message_reactions_updated(filters: Filter = None, group: int = 0) -> Callable:
    """Decorator for handling ``UpdateMessageReactions`` updates.

    This works like Pyrofork's built-in ``on_message_reaction_updated`` but
    handles the user-account ``UpdateMessageReactions`` update type, which
    Pyrofork does not currently dispatch.

    Parameters:
        filters (:obj:`Filter`, *optional*):
            A filter that receives a ``MessageReactionsUpdated`` object.
            Use ``filters.create(lambda c, u: ...)`` where *u* is the parsed
            ``MessageReactionsUpdated``.

        group (``int``, *optional*):
            The handler group, defaults to 0.

    Usage::

        from utils import on_message_reactions_updated, MessageReactionsUpdated

        @on_message_reactions_updated()
        async def my_handler(client, update: MessageReactionsUpdated):
            print(update.chat.id, update.msg_id, update.reactions)
    """

    def decorator(func: Callable) -> Callable:
        import inspect

        async def raw_callback(client: Client, update, users, chats):
            if not isinstance(update, raw.types.UpdateMessageReactions):
                raise pyrogram.ContinuePropagation

            parsed = MessageReactionsUpdated._parse(client, update, users, chats)

            if filters is not None:
                if callable(filters):
                    if inspect.iscoroutinefunction(filters.__call__):
                        if not await filters(client, parsed):
                            return
                    else:
                        if not filters(client, parsed):
                            return

            await func(client, parsed)

        if not hasattr(func, "handlers"):
            func.handlers = []

        handler = RawUpdateHandler(
            raw_callback,
            filters=lambda _, update: isinstance(update, raw.types.UpdateMessageReactions),
        )
        func.handlers.append((handler, group))

        return func

    return decorator
