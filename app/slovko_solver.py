import wordle.Wordle as W
from random import sample

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup





class SlovkoInput(StatesGroup):
    waiting_for_word = State()
    waiting_for_positions = State()




async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    obj = W.Wordle()
    await message.answer(f"Почати можна зі слів *{', '.join(sample(obj.vocabulary, 5))}*\, наприклад\.", parse_mode="MarkdownV2")
    await state.update_data(obj = obj)
    await attempt(message, state)


async def attempt(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    obj = user_data['obj']

    if obj.attempts:
        await SlovkoInput.waiting_for_word.set()
        await message.answer("Яке слово ви ввели?")
    else:
        await message.answer("Спроб більше не залишилось :(\nНатискай /start для нової гри")
        await state.finish()


async def slovko_was_inputed(message: types.Message, state: FSMContext):
    if len(message.text) != 5:
        await message.answer("Потрібно вввести слово з 5 букв")
        return
    await state.update_data(word=message.text.lower())

    await SlovkoInput.next()
    await message.answer("Тепер треба визначити кольори клітинок *\(С/Ж/З\)*\. Наприклад, *ссжсз*", parse_mode="MarkdownV2")


async def input_positions(message: types.Message, state: FSMContext):
    if len(message.text) != 5:
        await message.answer("Потрібно вввести 5 букв")
        return
    user_data = await state.get_data()
    obj = user_data['obj']
    word = user_data['word']
    positions = message.text.upper()
    if positions == 'ЗЗЗЗЗ':
        await message.answer(f"Вітаю\! Загадане слово було *{word}*", parse_mode='MarkdownV2')
        await cmd_game_over(message, state)

    else:
        obj.get_positions(word, positions)
        obj.attempts -= 1
        obj.find_possible_variations()

        if obj.vocabulary:
            variants = ' '.join(sample(obj.vocabulary, 650)) if len(obj.vocabulary) > 650 else ' '.join(obj.vocabulary)
            colours = '\n'.join(obj.colours)
            text = f"{colours}\nЗалишилось спроб *{obj.attempts}*\, а можливих слів \- *{len(obj.vocabulary)}*\, обирай\:\n{variants}"
            await message.answer(text, parse_mode="MarkdownV2")
            await state.update_data(obj = obj)
            await attempt(message, state)
        else:
            await message.answer("Упс.. Щось пішло не так і мені нема що запропонувати :(\nМоже, спробуй спочатку?")
            return


async def cmd_game_over(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Кінець! Щоб розпочати нову гру натискай /start")


async def help(message: types.Message):
    await message.answer("Щоб розпочати нову гру натискай /start")



def register_handlers_attempt(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_message_handler(help, commands="help", state="*")
    dp.register_message_handler(cmd_game_over, commands="game_over", state="*")
    dp.register_message_handler(slovko_was_inputed, state=SlovkoInput.waiting_for_word)
    dp.register_message_handler(input_positions, state=SlovkoInput.waiting_for_positions)

