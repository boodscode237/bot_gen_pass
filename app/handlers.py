from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, FSInputFile
import json
import io

from app.password_utils import generate_robust_password
from app.keyboards import confirm_keyboard

router = Router()


class Form(StatesGroup):
    website = State()
    email = State()
    length = State()
    confirm = State()


@router.message(F.text == "/start")
async def start(message: Message, state: FSMContext):
    await message.answer(
        "👋 Bienvenue sur le Générateur de mots de passe sécurisé !\nQuel est le site ou l’application ?"
    )
    await state.set_state(Form.website)


@router.message(Form.website)
async def get_website(message: Message, state: FSMContext):
    website = message.text.strip()
    if not website:
        await message.answer("❗️Merci de renseigner un nom de site non vide.")
        return
    await state.update_data(website=website)
    await message.answer("Merci ! Quel est votre email ou identifiant pour ce site ?")
    await state.set_state(Form.email)


@router.message(Form.email)
async def get_email(message: Message, state: FSMContext):
    email = message.text.strip()
    if not email:
        await message.answer("❗️Merci de renseigner un email/non vide.")
        return
    await state.update_data(email=email)
    await message.answer(
        "Quelle longueur pour le mot de passe ? (min 4, défaut 16)\nTapez juste Entrée pour valeur par défaut."
    )
    await state.set_state(Form.length)


@router.message(Form.length)
async def get_length(message: Message, state: FSMContext):
    txt = message.text.strip()
    if not txt:
        length = 16
    else:
        try:
            length = int(txt)
            if length < 4:
                await message.answer("❗️Longueur minimale 4.")
                return
        except ValueError:
            await message.answer(
                "❗️Veuillez entrer un nombre ou laissez vide pour la valeur par défaut."
            )
            return
    await state.update_data(length=length)
    pwd = generate_robust_password(length)
    await state.update_data(password=pwd)
    await message.answer(
        f"Voici votre mot de passe généré :\n\n<code>{pwd}</code>\n\nVoulez-vous recevoir ce mot de passe sous forme de fichier JSON ?",
        reply_markup=confirm_keyboard(),
        parse_mode="HTML",
    )
    await state.set_state(Form.confirm)


@router.callback_query(Form.confirm)
async def confirm_send_json(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if call.data == "yes":
        json_data = {
            "website": data["website"],
            "email": data["email"],
            "password": data["password"],
        }
        json_str = json.dumps(json_data, indent=4, ensure_ascii=False)
        # Use in-memory file for sending
        file_like = io.BytesIO(json_str.encode("utf-8"))
        filename = f"{data['website'].replace(' ', '_')}.json"
        file_like.seek(0)
        await call.bot.send_document(
            chat_id=call.from_user.id,
            document=types.BufferedInputFile(file=file_like.read(), filename=filename),
            caption="📁 Voici ton mot de passe au format JSON !",
        )
        await call.message.answer("✅ Fichier JSON envoyé !")
    else:
        await call.message.answer("❌ Mot de passe non envoyé.")
    await state.clear()
    await call.message.answer("Pour recommencer, tapez /start.")


@router.message()
async def fallback(message: Message):
    await message.answer("Envoyez /start pour commencer à générer un mot de passe.")
