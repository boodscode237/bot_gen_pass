from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, FSInputFile
from app.password_utils import (
    generate_robust_password,
    save_password_to_json,
    get_passwords_filename,
)
from app.keyboards import confirm_keyboard
import os

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
    if not message.text.strip():
        await message.answer("❗️Merci de renseigner un nom de site non vide.")
        return
    await state.update_data(website=message.text.strip())
    await message.answer("Merci ! Quel est votre email ou identifiant pour ce site ?")
    await state.set_state(Form.email)


@router.message(Form.email)
async def get_email(message: Message, state: FSMContext):
    if not message.text.strip():
        await message.answer("❗️Merci de renseigner un email non vide.")
        return
    await state.update_data(email=message.text.strip())
    await message.answer(
        "Quelle longueur pour le mot de passe ? (min 4, défaut 16)\nTapez juste Entrée pour valeur par défaut."
    )
    await state.set_state(Form.length)


@router.message(Form.length)
async def get_length(message: Message, state: FSMContext):
    txt = message.text.strip()
    length = 16 if not txt else int(txt)
    if length < 4:
        await message.answer("❗️Longueur minimale 4.")
        return
    await state.update_data(length=length)
    data = await state.get_data()
    pwd = generate_robust_password(length)
    await state.update_data(password=pwd)
    await message.answer(
        f"Voici votre mot de passe généré :\n\n<code>{pwd}</code>\n\nVoulez-vous l’enregistrer ?",
        reply_markup=confirm_keyboard(),
        parse_mode="HTML",
    )
    await state.set_state(Form.confirm)


@router.callback_query(Form.confirm)
async def confirm_save(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = call.from_user.id
    if call.data == "yes":
        save_password_to_json(data["website"], data["email"], data["password"], user_id)
        await call.message.answer("💾 Mot de passe enregistré !")
        filename = get_passwords_filename(user_id)
        file = FSInputFile(path=filename)
        await call.bot.send_document(
            chat_id=user_id,
            document=file,
            caption="📁 Voici TON fichier de mots de passe !",
        )
    else:
        await call.message.answer("❌ Mot de passe non enregistré.")
    await state.clear()
    await call.message.answer("Pour recommencer, tapez /start.")


@router.message(F.text == "/passwords")
async def send_passwords(message: Message):
    user_id = message.from_user.id
    filename = get_passwords_filename(user_id)
    if os.path.exists(filename):
        file = FSInputFile(path=filename)
        await message.answer_document(
            file, caption="📁 Voici tous TES mots de passe enregistrés."
        )
    else:
        await message.answer("❗️Tu n'as pas encore enregistré de mots de passe.")


@router.message()
async def fallback(message: Message):
    await message.answer(
        "Envoyez /start pour générer un mot de passe ou /passwords pour récupérer vos mots de passe."
    )
